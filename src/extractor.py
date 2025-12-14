"""
Extraction structurée des données financières
"""

from typing import List, Dict, Any
import json
import re
from langchain_core.documents import Document


class FinancialExtractor:
    """Extraction des données financières avec scores de confiance"""
    
    def __init__(self, config, rag_engine):
        self.config = config
        self.rag = rag_engine
    
    def extract(self, documents: List[Document]) -> dict:
        """
        Extrait les données financières des documents
        
        Args:
            documents: Documents sources
            
        Returns:
            Résultat structuré avec données, confiance et champs manquants
        """
        # Récupérer les documents financiers pertinents
        financial_docs = self._get_financial_documents(documents)
        
        # Extraire chaque champ
        extracted_data = {}
        field_confidences = {}
        missing_fields = []
        
        for field_name in self.config.get_all_fields():
            result = self._extract_field(field_name, financial_docs)
            
            if result["value"] is not None:
                extracted_data[field_name] = result["value"]
                field_confidences[field_name] = result["confidence"]
            else:
                missing_fields.append(field_name)
        
        # Calculer la confiance globale
        if field_confidences:
            global_confidence = sum(field_confidences.values()) / len(field_confidences)
        else:
            global_confidence = 0.0
        
        # Collecter les informations additionnelles avec explications
        additional_info = self._collect_additional_info(extracted_data, field_confidences, financial_docs)
        
        return {
            "sheet": extracted_data,
            "confidence_score": round(global_confidence, 4),
            "missing_fields": missing_fields if missing_fields else [],
            "additional_information": additional_info if additional_info else []
        }
    
    def _get_financial_documents(self, documents: List[Document]) -> List[Document]:
        """Filtre les documents pertinents pour l'extraction financière"""
        relevant_types = ["financial_statement", "tax_declaration", "summary_report"]
        
        financial_docs = [
            doc for doc in documents
            if doc.metadata.get("doc_type") in relevant_types
        ]
        
        # Si aucun doc spécifique, prendre tous les documents
        if not financial_docs:
            financial_docs = documents
        
        return financial_docs
    
    def _extract_field(self, field_name: str, documents: List[Document]) -> dict:
        """
        Extrait un champ spécifique avec score de confiance
        
        Args:
            field_name: Nom du champ à extraire
            documents: Documents sources
            
        Returns:
            Dictionnaire avec valeur et confiance
        """
        # Construire la requête de recherche
        aliases = self.config.get_field_aliases(field_name)
        search_query = f"{field_name} {' '.join(aliases)}"
        
        # Recherche RAG
        relevant_docs = self.rag.retrieve(search_query, k=3)
        
        if not relevant_docs:
            return {"value": None, "confidence": 0.0, "source": None}
        
        # Extraction via LLM
        context = self._build_extraction_context(relevant_docs)
        prompt = self._build_extraction_prompt(field_name, aliases, context)
        
        response = self.rag.llm.invoke(prompt)
        
        # Parser la réponse
        return self._parse_extraction_response(response.content, field_name)
    
    def _build_extraction_context(self, documents: List[Document]) -> str:
        """Construit le contexte pour l'extraction"""
        parts = []
        for doc in documents:
            parts.append(doc.page_content)
        return "\n\n".join(parts)
    
    def _build_extraction_prompt(self, field_name: str, aliases: List[str], context: str) -> str:
        """Construit le prompt d'extraction"""
        field_type = self.config.extraction_schema[field_name]["type"]
        
        return f"""Tu dois extraire une information financière précise depuis le contexte fourni.

CHAMP À EXTRAIRE: {field_name}
TYPE ATTENDU: {field_type}
ALIASES POSSIBLES: {', '.join(aliases)}

CONTEXTE:
{context}

INSTRUCTIONS:
1. Cherche la valeur exacte du champ demandé dans le contexte
2. Si tu trouves la valeur, retourne-la au format JSON strict suivant:
   {{"value": <valeur>, "confidence": <0.0-1.0>, "source": "<extrait court du texte source>"}}
3. Si la valeur n'est pas dans le contexte: {{"value": null, "confidence": 0.0, "source": null}}
4. Confiance = 1.0 si valeur explicite, 0.7-0.9 si déduite, 0.5-0.6 si ambiguë
5. Pour les montants: ne retourne que le nombre (sans € ou espaces)
6. Réponds UNIQUEMENT avec le JSON, rien d'autre

RÉPONSE JSON:"""
    
    def _parse_extraction_response(self, response: str, field_name: str) -> dict:
        """Parse la réponse JSON du LLM"""
        try:
            # Nettoyer la réponse (enlever markdown si présent)
            response = response.strip()
            if response.startswith("```"):
                response = re.sub(r"```json\n?|\n?```", "", response)
            
            # Parser le JSON
            data = json.loads(response)
            
            # Valider et typer la valeur
            value = data.get("value")
            if value is not None:
                field_type = self.config.extraction_schema[field_name]["type"]
                value = self._cast_value(value, field_type)
            
            return {
                "value": value,
                "confidence": float(data.get("confidence", 0.0)),
                "source": data.get("source")
            }
        
        except Exception as e:
            print(f"⚠️  Erreur parsing pour {field_name}: {e}")
            return {"value": None, "confidence": 0.0, "source": None}
    
    def _cast_value(self, value: Any, target_type: str) -> Any:
        """Cast la valeur au type cible"""
        if value is None:
            return None
        
        try:
            if target_type == "float":
                # Nettoyer les espaces et convertir
                if isinstance(value, str):
                    value = value.replace(" ", "").replace(",", ".")
                return float(value)
            
            elif target_type == "int":
                if isinstance(value, str):
                    value = value.replace(" ", "")
                return int(float(value))
            
            elif target_type == "str":
                return str(value).strip()
            
            else:
                return value
        
        except Exception:
            return value
    
    def enrich_with_corrections(self, extraction_result: dict, documents: List[Document]) -> dict:
        """
        Enrichit l'extraction avec les corrections historiques
        
        Args:
            extraction_result: Résultat brut d'extraction
            documents: Documents sources
            
        Returns:
            Résultat enrichi avec corrections appliquées
        """
        # Rechercher des corrections similaires en mémoire
        similar_corrections = self.rag.memory.search_similar_extraction(documents)
        
        if not similar_corrections:
            return extraction_result
        
        # Appliquer les corrections
        data = extraction_result["data"].copy()
        confidences = extraction_result["field_confidences"].copy()
        
        for correction in similar_corrections:
            field = correction["field"]
            if field in data:
                # Augmenter la confiance si la correction confirme
                if data[field] == correction["corrected_value"]:
                    confidences[field] = min(1.0, confidences[field] + 0.2)
                else:
                    # Appliquer la correction si haute confiance historique
                    if correction.get("confidence", 0) > 0.8:
                        data[field] = correction["corrected_value"]
                        confidences[field] = correction["confidence"]
        
        # Recalculer confiance globale
        global_confidence = sum(confidences.values()) / len(confidences) if confidences else 0
        
        return {
            **extraction_result,
            "data": data,
            "field_confidences": confidences,
            "global_confidence": round(global_confidence, 2),
            "corrections_applied": len(similar_corrections)
        }
    
    def _collect_additional_info(self, extracted_data: dict, field_confidences: dict, documents: List[Document]) -> List[dict]:
        """
        Collecte des informations additionnelles avec explications
        
        Returns:
            Liste d'informations additionnelles avec raison d'ajout
        """
        additional_info = []
        
        # Vérifier les champs avec confiance moyenne (0.5-0.8)
        for field, confidence in field_confidences.items():
            if 0.5 <= confidence < 0.8:
                additional_info.append({
                    "field": field,
                    "type": "medium_confidence",
                    "value": extracted_data.get(field),
                    "confidence": confidence,
                    "reason": f"Valeur extraite avec confiance moyenne ({confidence:.2%}). Vérification recommandée.",
                    "suggestion": "Vérifier manuellement cette valeur dans les documents sources."
                })
        
        # Vérifier les valeurs déduites ou calculées
        if "finProfit" in extracted_data and "finOperationInc" in extracted_data and "finFinancialInc" in extracted_data:
            calculated_profit = extracted_data.get("finOperationInc", 0) + extracted_data.get("finFinancialInc", 0)
            actual_profit = extracted_data.get("finProfit")
            if actual_profit and abs(calculated_profit - actual_profit) > 1000:
                additional_info.append({
                    "field": "finProfit",
                    "type": "calculation_verification",
                    "value": actual_profit,
                    "calculated_value": calculated_profit,
                    "difference": abs(calculated_profit - actual_profit),
                    "reason": f"Le résultat net (finProfit: {actual_profit}) diffère significativement de la somme calculée (finOperationInc + finFinancialInc = {calculated_profit}). Il peut y avoir des éléments exceptionnels (finNonRecurring) non pris en compte.",
                    "suggestion": "Vérifier s'il existe des résultats exceptionnels (finNonRecurring) ou des impôts non pris en compte."
                })
        
        # Vérifier la cohérence des dates
        if "finYear" in extracted_data:
            fiscal_year = extracted_data.get("finYear")
            if fiscal_year and (fiscal_year < 2000 or fiscal_year > 2030):
                additional_info.append({
                    "field": "finYear",
                    "type": "data_validation",
                    "value": fiscal_year,
                    "reason": f"L'année fiscale (finYear: {fiscal_year}) semble inhabituelle. Vérification recommandée.",
                    "suggestion": "Vérifier que l'année est correcte dans les documents."
                })
        
        # Vérifier les montants négatifs
        financial_fields = ["finSales", "finOperationInc", "finFinancialInc", "finProfit", "finBalanceSheet", "finEquity", "finAvailableFunds"]
        for field in financial_fields:
            if field in extracted_data:
                value = extracted_data[field]
                if isinstance(value, (int, float)) and value < 0:
                    additional_info.append({
                        "field": field,
                        "type": "negative_value",
                        "value": value,
                        "reason": f"Valeur négative détectée pour {field}. Cela peut être normal (pertes, dettes) mais mérite vérification.",
                        "suggestion": "Vérifier que la valeur négative est attendue selon le contexte financier."
                    })
        
        return additional_info
    
    def _get_confidence_explanation(self, global_confidence: float, field_confidences: dict) -> str:
        """Génère une explication du score de confiance global"""
        if global_confidence >= 0.9:
            return "Confiance très élevée. La plupart des valeurs sont explicites dans les documents."
        elif global_confidence >= 0.7:
            return "Confiance élevée. La majorité des valeurs sont fiables, quelques vérifications peuvent être nécessaires."
        elif global_confidence >= 0.5:
            return "Confiance modérée. Plusieurs valeurs nécessitent une vérification manuelle."
        else:
            return "Confiance faible. La plupart des valeurs nécessitent une validation humaine."


# ==================== CODE DE TEST ====================

if __name__ == "__main__":
    """
    Test de l'extraction sur tous les fichiers PDF du dossier data/
    Sauvegarde les résultats dans outputs/
    """
    import sys
    import io
    import json
    from pathlib import Path
    from datetime import datetime
    
    # Configurer l'encodage UTF-8 pour Windows
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    
    print(" Démarrage de l'extraction financière\n")
    
    try:
        # Ajouter le répertoire parent au path
        import os
        parent_dir = Path(__file__).parent.parent
        sys.path.insert(0, str(parent_dir))
        
        # Import des dépendances
        from src.config import Config
        from src.document_processor import DocumentProcessor
        from src.rag_engine import RAGEngine
        from src.memory_manager import MemoryManager
        
        # 1. Initialisation
        print("📋 Étape 1/4: Initialisation...")
        config = Config()
        memory = MemoryManager(config.memory_path)
        doc_processor = DocumentProcessor(config)
        rag_engine = RAGEngine(config, memory)
        extractor = FinancialExtractor(config, rag_engine)
        print("   ✓ Composants initialisés\n")
        
        # 2. Chargement des documents depuis data/
        print("📄 Étape 2/4: Chargement des documents depuis data/...")
        # Utiliser le chemin relatif depuis le répertoire parent
        parent_dir = Path(__file__).parent.parent
        data_dir = parent_dir / "data"
        
        if not data_dir.exists():
            print(f"    Le dossier {data_dir} n'existe pas!")
            sys.exit(1)
        
        # Scanner tous les fichiers PDF dans le dossier data/
        doc_paths = list(data_dir.glob("*.pdf"))
        
        if not doc_paths:
            print("    Aucun fichier PDF trouvé dans le dossier data/!")
            sys.exit(1)
        
        existing_docs = [str(p) for p in doc_paths]
        print(f"   ✓ {len(existing_docs)} fichier(s) PDF trouvé(s):")
        for doc_path in existing_docs:
            print(f"      - {Path(doc_path).name}")
        
        documents = doc_processor.process_documents(existing_docs)
        print(f"   ✓ {len(documents)} documents traités\n")
        
        # 3. Indexation RAG
        print("🔍 Étape 3/4: Indexation dans la base RAG...")
        
        # Essayer de charger un index existant
        if not rag_engine.load_index():
            # Si pas d'index existant, créer un nouvel index
            print("   Création d'un nouvel index...")
            rag_engine.index_documents(documents, save_to_disk=True)
        else:
            # Vérifier si de nouveaux documents doivent être ajoutés
            existing_sources = {doc.metadata.get("source") for doc in rag_engine.documents}
            new_docs = [doc for doc in documents if doc.metadata.get("source") not in existing_sources]
            if new_docs:
                print(f"   Ajout de {len(new_docs)} nouveaux documents...")
                rag_engine.index_documents(new_docs, save_to_disk=True)
            else:
                print("   ✓ Index existant utilisé (pas de nouveaux documents)")
        
        print(f"   ✓ {len(rag_engine.documents)} documents disponibles dans l'index\n")
        
        # 4. Extraction
        print("💰 Étape 4/4: Extraction des données financières...")
        print("   (Cela peut prendre quelques instants...)\n")
        
        extraction_result = extractor.extract(documents)
        
        # Afficher les résultats
        print("\n" + "="*80)
        print("📊 RÉSULTATS D'EXTRACTION FINANCIÈRE")
        print("="*80)
        
        # Format avec confidence_score
        global_conf = extraction_result.get("confidence_score", 0)
        
        print(f"\n🎯 Score de confiance global: {global_conf:.4f} ({global_conf:.2%})")
        
        data = extraction_result.get("sheet", {})
        missing = extraction_result.get("missing_fields", [])
        additional_info = extraction_result.get("additional_information", [])
        
        print(f"\n✅ Champs extraits: {len(data)}")
        print(f"❌ Champs manquants: {len(missing)}")
        
        print(f"\n✅ Champs extraits: {len(data)}")
        print(f"❌ Champs manquants: {len(missing)}")
        
        if data:
            print("\n" + "-"*80)
            print("DONNÉES EXTRAITES (SHEET):")
            print("-"*80)
            
            for field, value in sorted(data.items()):
                if isinstance(value, float):
                    value_str = f"{value:,.0f}" if value else "N/A"
                else:
                    value_str = str(value) if value else "N/A"
                
                print(f"  {field}: {value_str}")
        
        # Afficher les champs manquants
        print("\n" + "-"*80)
        print("CHAMPS MANQUANTS:")
        print("-"*80)
        if missing:
            for field in missing:
                print(f"  ❌ {field}")
        else:
            print("  ✓ Aucun champ manquant")
        
        # Afficher les informations additionnelles
        if additional_info:
            print("\n" + "-"*80)
            print("INFORMATIONS ADDITIONNELLES:")
            print("-"*80)
            for info in additional_info:
                print(f"\n  ⚠️  {info.get('field', 'N/A')} ({info.get('type', 'info')})")
                print(f"     Valeur: {info.get('value', 'N/A')}")
                print(f"     Raison: {info.get('reason', 'N/A')}")
                if 'suggestion' in info:
                    print(f"     Suggestion: {info.get('suggestion')}")
        
        print("\n" + "="*80)
        
        # Sauvegarder les résultats dans outputs/
        output_dir = parent_dir / "outputs"
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"extraction_{timestamp}.json"
        
        # Ajouter les métadonnées
        extraction_result["metadata"] = {
            "timestamp": timestamp,
            "files_processed": [Path(p).name for p in existing_docs],
            "total_files": len(existing_docs),
            "total_documents": len(documents)
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(extraction_result, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Résultats sauvegardés dans: {output_file}")
        print(f"   📁 Dossier: {output_dir.absolute()}")
        
        # Afficher un résumé JSON
        print("\n" + "="*80)
        print("📄 RÉSUMÉ JSON:")
        print("="*80)
        print(json.dumps(extraction_result, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)