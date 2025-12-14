"""
Moteur de réponse aux questions qualitatives
"""

import re
from typing import Dict, List


class QAEngine:
    """Gestion des questions-réponses sur l'entreprise"""
    
    def __init__(self, config, rag_engine):
        self.config = config
        self.rag = rag_engine
    
    def answer(self, question: str) -> dict:
        """
        Répond à une question en s'appuyant sur le RAG
        
        Args:
            question: Question en langage naturel
            
        Returns:
            Dictionnaire avec réponse, confiance, sources
        """
        # Récupérer le contexte pertinent
        relevant_docs = self.rag.retrieve(question, k=5)
        
        if not relevant_docs:
            return {
                "question": question,
                "answer": "Je ne trouve pas d'information dans les documents fournis pour répondre à cette question.",
                "confidence": 0.0,
                "sources": [],
                "needs_validation": True
            }
        
        # Générer la réponse
        result = self.rag.generate_with_context(question, relevant_docs)
        
        # Évaluer la confiance
        confidence = self._assess_confidence(
            question, 
            result["response"], 
            relevant_docs
        )
        
        return {
            "question": question,
            "answer": result["response"],
            "confidence": confidence,
            "sources": result["sources"],
            "context_chunks": result["context_used"],
            "needs_validation": confidence < self.config.confidence_threshold
        }
    
    def _assess_confidence(self, question: str, answer: str, context_docs: List) -> float:
        """
        Évalue la confiance dans la réponse
        
        Critères:
        - Présence d'incertitude dans la réponse
        - Qualité de la similarité des documents récupérés
        - Longueur et spécificité de la réponse
        """
        confidence = 0.5  # Baseline
        
        # Indicateurs d'incertitude (pénalité)
        uncertainty_patterns = [
            r"je ne suis pas sûr",
            r"il semble que",
            r"peut-être",
            r"probablement",
            r"information non disponible",
            r"pas d'information",
            r"ne trouve pas"
        ]
        
        answer_lower = answer.lower()
        for pattern in uncertainty_patterns:
            if re.search(pattern, answer_lower):
                confidence -= 0.2
                break
        
        # Réponse substantielle (bonus)
        if len(answer) > 100 and not any(p in answer_lower for p in ["non disponible", "ne trouve pas"]):
            confidence += 0.3
        
        # Qualité du contexte (bonus)
        if len(context_docs) >= 3:
            confidence += 0.2
        
        # Borner entre 0 et 1
        return max(0.0, min(1.0, round(confidence, 2)))
    
    def batch_answer(self, questions: List[str]) -> List[dict]:
        """Répond à plusieurs questions en batch"""
        return [self.answer(q) for q in questions]
    
    def answer_with_memory(self, question: str) -> dict:
        """
        Répond en tenant compte de la mémoire des corrections
        
        Args:
            question: Question
            
        Returns:
            Réponse enrichie par l'historique
        """
        # Chercher dans la mémoire des Q&A
        historical = self.rag.memory.search_similar_question(question)
        
        if historical and historical.get("confidence", 0) > 0.8:
            return {
                **historical,
                "from_memory": True,
                "needs_validation": False
            }
        
        # Sinon, réponse classique
        result = self.answer(question)
        result["from_memory"] = False
        
        return result
    
    def explain_answer(self, question: str, answer_result: dict) -> str:
        """
        Génère une explication détaillée de la réponse
        
        Utile pour la validation humaine
        """
        explanation_parts = [
            f"Question: {question}",
            f"\nRéponse: {answer_result['answer']}",
            f"\nConfiance: {answer_result['confidence']:.2f}",
            f"\nSources utilisées: {', '.join(answer_result['sources'])}",
        ]
        
        if answer_result['confidence'] < self.config.confidence_threshold:
            explanation_parts.append(
                f"\n⚠️ Confiance faible (< {self.config.confidence_threshold})"
            )
        
        if not answer_result['sources']:
            explanation_parts.append(
                "\n⚠️ Aucune source trouvée dans les documents"
            )
        
        return "\n".join(explanation_parts)
    
    def suggest_questions(self, documents: List) -> List[str]:
        """
        Suggère des questions pertinentes basées sur les documents
        
        Utile pour guider l'utilisateur
        """
        # Analyser les types de documents disponibles
        doc_types = set()
        for doc in documents:
            doc_types.add(doc.metadata.get("doc_type", "unknown"))
        
        suggestions = []
        
        if "company_description" in doc_types:
            suggestions.extend([
                "Quel est le secteur d'activité de l'entreprise ?",
                "Quelle est la stratégie de l'entreprise ?",
                "Quelles sont les activités principales ?",
            ])
        
        if "financial_statement" in doc_types or "tax_declaration" in doc_types:
            suggestions.extend([
                "Quel est le chiffre d'affaires de l'exercice ?",
                "Quel est le résultat net ?",
                "Qui sont les dirigeants ?",
                "Quel est le montant des capitaux propres ?",
            ])
        
        return suggestions[:5]  # Limiter à 5 suggestions
