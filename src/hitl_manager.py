"""
Gestionnaire de validation humaine (Human-in-the-Loop)
"""

from typing import Dict, Optional
import json
from src.config import Config


class HITLManager:
    """Gestion de la validation humaine et des corrections"""
    
    def __init__(self, config, memory_manager):
        self.config = config
        self.memory = memory_manager
    
    def needs_validation(self, extraction_result: dict) -> bool:
        """
        Détermine si une validation humaine est nécessaire
        
        Critères:
        - Confiance globale < seuil
        - Trop de champs manquants
        - Champs critiques avec faible confiance
        
        Args:
            extraction_result: Résultat d'extraction
            
        Returns:
            True si validation nécessaire
        """
        confidence = extraction_result.get("confidence_score", 0)
        missing = extraction_result.get("missing_fields", [])
        # Pour le nouveau format, on utilise confidence_score global uniquement
        # Les confidences par champ ne sont plus dans le format de sortie
        
        # Règle 1: Confiance globale trop faible
        if confidence < self.config.require_validation_below:
            return True
        
        # Règle 2: Trop de champs manquants
        if len(missing) > self.config.missing_field_threshold:
            return True
        
        # Règle 3: Champs critiques manquants
        critical_fields = ["finSales", "finProfit", "finYear"]
        for field in critical_fields:
            if field in missing:
                return True
        
        # Règle 4: Auto-validation si confiance élevée
        if confidence >= self.config.auto_validate_above:
            return False
        
        # Règle 5: Entre les deux seuils -> validation par défaut
        if self.config.require_validation_below <= confidence < self.config.auto_validate_above:
            return True
        
        return False
    
    def request_validation(self, extraction_result: dict) -> dict:
        """
        Lance le processus de validation humaine
        
        En production: interface web/CLI interactive
        Pour ce POC: simulation avec inputs
        
        Args:
            extraction_result: Résultat à valider
            
        Returns:
            Résultat validé avec corrections
        """
        print("\n" + "="*60)
        print("VALIDATION HUMAINE REQUISE")
        print("="*60)
        
        data = extraction_result.get("sheet", {})
        confidence = extraction_result.get("confidence_score", 0)
        missing = extraction_result.get("missing_fields", [])
        
        print(f"\nScore de confiance: {confidence:.4f} ({confidence:.2%})")
        print(f"Champs extraits: {len(data)}")
        print(f"[ATTENTION] Champs manquants: {len(missing)}")
        
        # Afficher les données extraites
        print("\n" + "-"*60)
        print("DONNÉES EXTRAITES (SHEET):")
        print("-"*60)
        
        corrections = {}
        for field, value in sorted(data.items()):
            print(f"\nOK: {field}: {value}")
            
            # Demander validation si confiance globale faible
            if confidence < self.config.confidence_threshold:
                correction = self._ask_correction(field, value, confidence)
                if correction:
                    corrections[field] = correction
        
        # Demander les champs manquants
        if missing:
            print("\n" + "-"*60)
            print("CHAMPS MANQUANTS:")
            print("-"*60)
            
            for field in missing:
                print(f"\n[ERREUR] {field}: Non trouvé")
                correction = self._ask_missing_field(field)
                if correction:
                    corrections[field] = correction
        
        # Appliquer les corrections
        validated_result = self._apply_corrections(extraction_result, corrections)
        
        print("\nValidation terminée")
        return validated_result
    
    def _ask_correction(self, field: str, current_value, confidence: float) -> Optional[dict]:
        """
        Demande une correction pour un champ de manière interactive
        
        Args:
            field: Nom du champ
            current_value: Valeur actuelle extraite
            confidence: Score de confiance
            
        Returns:
            Dictionnaire de correction ou None si accepté
        """
        print(f"\n   Champ: {field}")
        print(f"   Valeur extraite: {current_value}")
        print(f"   Confiance: {confidence:.2%}")
        
        while True:
            response = input(f"   > Valider cette valeur ? (o/n/corriger/skip): ").strip().lower()
            
            if response in ['o', 'oui', 'y', 'yes', '']:
                # Accepter la valeur
                return None
            
            elif response in ['n', 'non', 'no']:
                # Rejeter la valeur (la retirer)
                return {
                    "action": "remove",
                    "field": field,
                    "reason": "Rejeté par l'utilisateur"
                }
            
            elif response in ['c', 'corriger', 'corrige', 'edit']:
                # Corriger la valeur
                new_value = input(f"   > Nouvelle valeur pour {field}: ").strip()
                if new_value:
                    try:
                        # Essayer de convertir en nombre si c'est un nombre
                        if isinstance(current_value, (int, float)):
                            new_value = float(new_value) if '.' in new_value else int(new_value)
                    except ValueError:
                        pass  # Garder comme string
                    
                    return {
                        "action": "correct",
                        "field": field,
                        "original_value": current_value,
                        "new_value": new_value,
                        "reason": "Corrigé par l'utilisateur"
                    }
                else:
                    print("   [ATTENTION] Valeur vide, annulation de la correction")
                    continue
            
            elif response in ['s', 'skip', 'passer']:
                # Passer ce champ
                return None
            
            else:
                print("   [ATTENTION] Réponse invalide. Utilisez: o (oui), n (non), c (corriger), s (skip)")
                continue
    
    def _ask_missing_field(self, field: str) -> Optional[dict]:
        """
        Demande de renseigner un champ manquant de manière interactive
        
        Args:
            field: Nom du champ manquant
            
        Returns:
            Dictionnaire avec la valeur à ajouter ou None si ignoré
        """
        # Obtenir les alias du champ pour aider l'utilisateur
        field_info = self._get_field_info(field)
        
        print(f"\n   📋 Champ manquant: {field}")
        if field_info:
            print(f"   ℹ️  Description: {field_info.get('description', 'N/A')}")
            if field_info.get('aliases'):
                print(f"   🔍 Aussi connu sous: {', '.join(field_info['aliases'][:3])}")
        
        while True:
            response = input(f"   ➤ Souhaitez-vous renseigner ce champ ? (o/n/skip): ").strip().lower()
            
            if response in ['o', 'oui', 'y', 'yes']:
                # Demander la valeur
                value_input = input(f"   ➤ Valeur pour {field}: ").strip()
                
                if not value_input:
                    print("   ⚠️  Valeur vide, champ ignoré")
                    return None
                
                # Convertir selon le type attendu
                value = self._convert_field_value(field, value_input, field_info)
                
                return {
                    "action": "add",
                    "field": field,
                    "value": value,
                    "reason": "Ajouté manuellement par l'utilisateur"
                }
            
            elif response in ['n', 'non', 'no', 's', 'skip', 'passer', '']:
                # Ignorer le champ
                return None
            
            else:
                print("   ⚠️  Réponse invalide. Utilisez: o (oui), n (non), s (skip)")
                continue
    
    def _get_field_info(self, field: str) -> Optional[dict]:
        """Récupère les informations sur un champ depuis la config"""
        try:
            schema = self.config.extraction_schema
            if field in schema:
                field_def = schema[field]
                return {
                    "description": field_def.get("description", ""),
                    "aliases": field_def.get("aliases", []),
                    "type": field_def.get("type", "string")
                }
        except:
            pass
        return None
    
    def _convert_field_value(self, field: str, value_str: str, field_info: Optional[dict]) -> any:
        """Convertit la valeur selon le type attendu du champ"""
        if not field_info:
            # Essayer de deviner le type
            try:
                if '.' in value_str:
                    return float(value_str)
                else:
                    return int(value_str)
            except ValueError:
                return value_str
        
        field_type = field_info.get("type", "string")
        
        if field_type in ["integer", "int"]:
            try:
                return int(value_str)
            except ValueError:
                print(f"   ⚠️  Impossible de convertir en entier, gardé comme string")
                return value_str
        
        elif field_type in ["float", "number"]:
            try:
                return float(value_str)
            except ValueError:
                print(f"   ⚠️  Impossible de convertir en nombre, gardé comme string")
                return value_str
        
        elif field_type == "year" and field == "finYear":
            try:
                year = int(value_str)
                if 1900 <= year <= 2100:
                    return year
                else:
                    print(f"   ⚠️  Année invalide, gardé comme string")
                    return value_str
            except ValueError:
                return value_str
        
        else:
            return value_str
    
    def _apply_corrections(self, original_result: dict, corrections: dict) -> dict:
        """Applique les corrections à l'extraction"""
        validated = original_result.copy()
        data = validated.get("sheet", {}).copy()
        missing = list(validated.get("missing_fields", []))
        original_confidence = validated.get("confidence_score", 0)
        
        # Appliquer chaque correction
        for field, correction in corrections.items():
            if correction["action"] == "correct":
                data[field] = correction["new_value"]
            
            elif correction["action"] == "add":
                data[field] = correction["value"]
                if field in missing:
                    missing.remove(field)
            
            elif correction["action"] == "remove":
                if field in data:
                    del data[field]
        
        # Après validation humaine, confiance = 1.0
        validated.update({
            "sheet": data,
            "confidence_score": 1.0,  # Validation humaine = confiance maximale
            "missing_fields": missing if missing else [],
            "corrections": corrections,
            "validated_by_human": True,
            "original_confidence": original_confidence
        })
        
        return validated
    
    def validate_qa_response(self, question: str, answer_result: dict) -> dict:
        """
        Valide une réponse Q&A avec intervention humaine
        
        Args:
            question: Question posée
            answer_result: Résultat initial
            
        Returns:
            Résultat validé/corrigé
        """
        import sys
        
        print("\n" + "="*60)
        print("🔍 VALIDATION RÉPONSE Q&A")
        print("="*60)
        
        print(f"\n❓ Question: {question}")
        print(f"\n💬 Réponse actuelle: {answer_result['answer']}")
        print(f"📊 Confiance: {answer_result['confidence']:.2%}")
        
        sources = answer_result.get('sources', [])
        if sources:
            unique_sources = list(set(sources))
            print(f"📚 Sources: {len(unique_sources)} document(s) unique(s)")
            for i, source in enumerate(unique_sources[:3], 1):
                print(f"   {i}. {source}")
        
        print("\n" + "-"*60)
        print("💡 Options:")
        print("   o / oui  → Accepter la réponse")
        print("   n / non  → Rejeter et fournir la bonne réponse")
        print("   c / corriger → Modifier la réponse")
        print("   s / skip → Passer sans valider")
        print("-"*60)
        
        # S'assurer que tout est affiché avant de demander l'input
        sys.stdout.flush()
        sys.stderr.flush()
        
        while True:
            try:
                # Forcer l'affichage avant l'input
                sys.stdout.flush()
                sys.stderr.flush()
                
                # Demander l'input
                response = input("\n➤ Votre choix (o/n/c/s): ").strip().lower()
                
                if not response:
                    print("⚠️  Veuillez entrer une réponse (o/n/c/s)")
                    continue
                    
            except (EOFError, KeyboardInterrupt):
                print("\n⚠️  Validation annulée")
                validated = answer_result.copy()
                validated["validated_by_human"] = False
                validated["corrected"] = False
                return validated
            except Exception as e:
                print(f"\n❌ Erreur lors de la saisie: {e}")
                print("⚠️  Veuillez réessayer")
                import traceback
                traceback.print_exc()
                continue
            
            # Traiter la réponse
            if response in ['o', 'oui', 'y', 'yes', '']:
                # Accepter la réponse
                validated = answer_result.copy()
                validated["validated_by_human"] = True
                validated["corrected"] = False
                return validated
            
            elif response in ['n', 'non', 'no']:
                # Rejeter la réponse
                new_answer = input("➤ Quelle est la bonne réponse ? (ou 'skip' pour ignorer): ").strip()
                
                if new_answer.lower() == 'skip':
                    validated = answer_result.copy()
                    validated["validated_by_human"] = False
                    validated["corrected"] = False
                    return validated
                
                validated = answer_result.copy()
                validated["answer"] = new_answer
                validated["validated_by_human"] = True
                validated["corrected"] = True
                validated["original_answer"] = answer_result['answer']
                return validated
            
            elif response in ['c', 'corriger', 'corrige', 'edit']:
                # Corriger partiellement
                print("\n💡 Vous pouvez modifier la réponse:")
                current = answer_result['answer']
                print(f"   Réponse actuelle: {current}")
                new_answer = input("➤ Nouvelle réponse (ou 'skip' pour annuler): ").strip()
                
                if new_answer.lower() == 'skip' or not new_answer:
                    continue
                
                validated = answer_result.copy()
                validated["answer"] = new_answer
                validated["validated_by_human"] = True
                validated["corrected"] = True
                validated["original_answer"] = current
                return validated
            
            elif response in ['s', 'skip', 'passer']:
                # Passer
                validated = answer_result.copy()
                validated["validated_by_human"] = False
                validated["corrected"] = False
                return validated
            
            else:
                print("⚠️  Réponse invalide. Utilisez: o (oui), n (non), c (corriger), s (skip)")
                continue
    
    def create_correction_record(
        self, 
        extraction_result: dict,
        validated_result: dict,
        documents: list
    ) -> dict:
        """
        Crée un enregistrement de correction pour la mémoire
        
        Args:
            extraction_result: Résultat original
            validated_result: Résultat après validation
            documents: Documents sources
            
        Returns:
            Enregistrement structuré de correction
        """
        corrections = []
        
        original_data = extraction_result.get("data", {})
        validated_data = validated_result.get("data", {})
        
        # Identifier les corrections
        for field in set(list(original_data.keys()) + list(validated_data.keys())):
            original_val = original_data.get(field)
            validated_val = validated_data.get(field)
            
            if original_val != validated_val:
                corrections.append({
                    "field": field,
                    "original_value": original_val,
                    "corrected_value": validated_val,
                    "confidence": validated_result["field_confidences"].get(field, 1.0)
                })
        
        # Contexte documentaire
        doc_context = [
            {
                "source": doc.metadata.get("source"),
                "type": doc.metadata.get("doc_type")
            }
            for doc in documents
        ]
        
        return {
            "timestamp": Config.get_timestamp(),
            "corrections": corrections,
            "document_context": doc_context,
            "original_confidence": extraction_result.get("global_confidence", 0),
            "validated_confidence": validated_result.get("global_confidence", 0)
        }