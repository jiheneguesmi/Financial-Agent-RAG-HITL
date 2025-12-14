"""
Agent d'extraction financière avec RAG et HITL - Version GPT-4
Point d'entrée principal du système
"""

from pathlib import Path
from typing import Optional
import json

from src.document_processor import DocumentProcessor
from src.rag_engine import RAGEngine
from src.extractor import FinancialExtractor
from src.qa_engine import QAEngine
from src.hitl_manager import HITLManager
from src.memory_manager import MemoryManager
from src.config import Config


class FinancialAgent:
    """Agent principal orchestrant tout le pipeline"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = Config(config_path)
        self.memory = MemoryManager(self.config.memory_path)
        self.doc_processor = DocumentProcessor(self.config)
        self.rag_engine = RAGEngine(self.config, self.memory)
        self.extractor = FinancialExtractor(self.config, self.rag_engine)
        self.qa_engine = QAEngine(self.config, self.rag_engine)
        self.hitl = HITLManager(self.config, self.memory)
        
    def process_documents(self, document_paths: list[str]) -> dict:
        """
        Pipeline complet: ingestion -> extraction -> validation -> correction
        
        Args:
            document_paths: Chemins vers les documents PDF
            
        Returns:
            Résultat final avec extraction validée et corrections appliquées
        """
        print("Démarrage du pipeline d'extraction financière\n")
        
        # 1. Ingestion des documents
        print("Étape 1/5: Ingestion des documents...")
        documents = self.doc_processor.process_documents(document_paths)
        print(f"   OK: {len(documents)} documents traités\n")
        
        # 2. Indexation RAG
        print("Étape 2/5: Indexation dans la base RAG...")
        self.rag_engine.index_documents(documents)
        print(f"   OK: {len(documents)} documents indexés\n")
        
        # 3. Extraction des données financières
        print("Étape 3/5: Extraction des données financières...")
        extraction_result = self.extractor.extract(documents)
        self._display_extraction(extraction_result)
        
        # 4. Validation et HITL
        print("\nÉtape 4/5: Validation et contrôle qualité...")
        needs_validation = self.hitl.needs_validation(extraction_result)
        
        if needs_validation:
            print("   [ATTENTION] Validation humaine requise")
            validated_result = self.hitl.request_validation(extraction_result)
            
            # Apprendre des corrections
            if validated_result.get("corrections"):
                self.memory.store_corrections(
                    documents,
                    extraction_result,
                    validated_result
                )
                print("   OK: Corrections enregistrées en mémoire")
        else:
            print("   OK: Extraction validée automatiquement")
            validated_result = extraction_result
        
        # 5. Finalisation
        print("\nÉtape 5/5: Finalisation")
        final_result = {
            "extraction": validated_result,
            "documents_processed": len(documents),
            "validation_required": needs_validation,
            "timestamp": self.config.get_timestamp()
        }
        
        # Sauvegarder le résultat
        output_path = self.config.output_path / f"extraction_{final_result['timestamp']}.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(final_result, f, indent=2, ensure_ascii=False)
        
        print(f"   OK: Résultat sauvegardé: {output_path}\n")
        return final_result
    
    def answer_question(self, question: str) -> dict:
        """
        Répond à une question sur l'entreprise en s'appuyant sur le RAG
        
        Args:
            question: Question en langage naturel
            
        Returns:
            Réponse avec score de confiance et sources
        """
        # Recherche dans la mémoire des corrections
        historical_answer = self.memory.search_similar_question(question)
        if historical_answer:
            print(f"\nQuestion: {question}")
            print("   Réponse trouvée dans l'historique des corrections")
            return historical_answer
        
        # Génération de la réponse via RAG
        result = self.qa_engine.answer(question)
        
        # Validation si confiance faible
        if result["confidence"] < self.config.confidence_threshold:
            validated = self.hitl.validate_qa_response(question, result)
            
            if validated.get("corrected"):
                self.memory.store_qa_correction(question, result, validated)
                return validated
            
            return validated
        
        return result
    
    def add_manual_context(self, context_data: dict):
        """
        Ajoute manuellement des informations contextuelles sur l'entreprise
        
        Args:
            context_data: Dictionnaire avec informations supplémentaires
        """
        self.rag_engine.add_manual_context(context_data)
        print("OK: Contexte manuel ajouté à la base RAG")
    
    def _display_extraction(self, result: dict):
        """Affiche les résultats d'extraction de manière lisible"""
        data = result.get("sheet", {})
        confidence = result.get("confidence_score", 0)
        missing = result.get("missing_fields", [])
        
        print(f"   Score de confiance: {confidence:.4f} ({confidence:.2%})")
        print(f"   Champs extraits: {len(data)}")
        if missing:
            print(f"   [ATTENTION] Champs manquants: {', '.join(missing)}")


def main():
    """Exemple d'utilisation"""
    agent = FinancialAgent()
    
    # Documents à traiter
    docs = [
        "data/CONSULTING ENERGIES LF 2024 Def envoi EDI.pdf",
        "data/description_entreprise_atelier.pdf",
        "data/bilan_synthetique_atelier.pdf"
    ]
    
    # 1. Extraction financière
    result = agent.process_documents(docs)
    
    # Mode interactif pour les questions
    print("\n" + "="*80)
    print("MODE INTERACTIF - QUESTIONS/RÉPONSES")
    print("="*80)
    print("\nEntrez vos questions sur l'entreprise (tapez 'quit' ou 'exit' pour quitter)")
    print("   Tapez 'help' pour voir des exemples de questions\n")
    
    while True:
        try:
            question = input("Votre question: ").strip()
            
            # Commandes spéciales
            if question.lower() in ['quit', 'exit', 'q']:
                print("\nAu revoir!")
                break
            
            if question.lower() == 'help':
                print("\nExemples de questions:")
                print("   - Quel est le secteur d'activité de l'entreprise ?")
                print("   - Quelle est la stratégie de l'entreprise ?")
                print("   - Qui sont les gérants de l'entreprise ?")
                print("   - Quel est le chiffre d'affaires 2024 ?")
                print("   - Quel est le résultat net ?")
                print("   - Quels sont les capitaux propres ?")
                print()
                continue
            
            if not question:
                print("[ATTENTION] Veuillez entrer une question.\n")
                continue
            
            # Traiter la question
            print("\nRecherche en cours...")
            answer = agent.answer_question(question)
            
            # Afficher la réponse seulement si elle n'a pas déjà été affichée par HITL
            if not answer.get('validated_by_human'):
                print("\n" + "-"*80)
                print(f"Réponse:")
                print(f"   {answer.get('answer', 'Aucune réponse disponible')}")
                print(f"\nConfiance: {answer.get('confidence', 0):.2%}")
                
                sources = answer.get('sources', [])
                if sources:
                    unique_sources = list(set(sources))
                    print(f"Sources: {len(unique_sources)} document(s)")
                    for i, source in enumerate(unique_sources[:3], 1):  # Limiter à 3 sources
                        print(f"   {i}. {source}")
                
                print("-"*80 + "\n")
            else:
                # Si validé par HITL, afficher un résumé final
                if answer.get('corrected'):
                    print("\nRéponse corrigée et validée par l'utilisateur\n")
                else:
                    print("\nRéponse acceptée par l'utilisateur\n")
            
        except KeyboardInterrupt:
            print("\n\nInterruption détectée. Au revoir!")
            break
        except Exception as e:
            print(f"\nErreur: {e}\n")
            continue
    
    # 3. Ajout de contexte manuel
    agent.add_manual_context({
        "type": "company_info",
        "content": "L'entreprise prévoit une expansion à l'international en 2026"
    })


if __name__ == "__main__":
    main()