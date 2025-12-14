"""
Gestionnaire de mémoire persistante pour apprentissage
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class MemoryManager:
    """Gestion de la mémoire persistante des corrections"""
    
    def __init__(self, memory_dir: Path):
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(exist_ok=True)
        
        # Fichiers de mémoire
        self.corrections_file = self.memory_dir / "extraction_corrections.json"
        self.qa_memory_file = self.memory_dir / "qa_corrections.json"
        self.context_file = self.memory_dir / "manual_context.json"
        
        # Initialiser si nécessaire
        self._init_memory_files()
    
    def _init_memory_files(self):
        """Initialise les fichiers de mémoire s'ils n'existent pas"""
        for file in [self.corrections_file, self.qa_memory_file, self.context_file]:
            if not file.exists():
                with open(file, 'w', encoding='utf-8') as f:
                    json.dump([], f)
    
    def store_corrections(
        self, 
        documents: list, 
        original_result: dict, 
        validated_result: dict
    ):
        """
        Stocke les corrections d'extraction en mémoire
        
        Args:
            documents: Documents sources
            original_result: Extraction originale
            validated_result: Résultat validé
        """
        # Charger la mémoire existante
        corrections = self._load_json(self.corrections_file)
        
        # Créer l'enregistrement
        record = {
            "timestamp": datetime.now().isoformat(),
            "document_sources": [d.metadata.get("source") for d in documents],
            "document_types": list(set(d.metadata.get("doc_type") for d in documents)),
            "original": {
                "data": original_result.get("data", {}),
                "confidence": original_result.get("global_confidence", 0),
                "missing_fields": original_result.get("missing_fields", [])
            },
            "validated": {
                "data": validated_result.get("data", {}),
                "confidence": validated_result.get("global_confidence", 0),
                "missing_fields": validated_result.get("missing_fields", [])
            },
            "corrections": self._identify_corrections(
                original_result.get("data", {}),
                validated_result.get("data", {})
            )
        }
        
        # Ajouter et sauvegarder
        corrections.append(record)
        self._save_json(self.corrections_file, corrections)
        
        print(f"💾 {len(record['corrections'])} corrections enregistrées")
    
    def store_qa_correction(
        self, 
        question: str, 
        original_answer: dict, 
        corrected_answer: dict
    ):
        """
        Stocke une correction de réponse Q&A
        
        Args:
            question: Question posée
            original_answer: Réponse originale
            corrected_answer: Réponse corrigée
        """
        qa_memory = self._load_json(self.qa_memory_file)
        
        record = {
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "original_answer": original_answer.get("answer"),
            "original_confidence": original_answer.get("confidence", 0),
            "corrected_answer": corrected_answer.get("answer"),
            "corrected_confidence": corrected_answer.get("confidence", 1.0),
            "sources": corrected_answer.get("sources", [])
        }
        
        qa_memory.append(record)
        self._save_json(self.qa_memory_file, qa_memory)
        
        print("💾 Correction Q&A enregistrée")
    
    def store_manual_context(self, context_data: dict):
        """
        Stocke du contexte manuel ajouté
        
        Args:
            context_data: Données contextuelles
        """
        contexts = self._load_json(self.context_file)
        
        record = {
            "timestamp": datetime.now().isoformat(),
            **context_data
        }
        
        contexts.append(record)
        self._save_json(self.context_file, contexts)
        
        print("💾 Contexte manuel enregistré")
    
    def search_similar_extraction(self, current_documents: list) -> List[dict]:
        """
        Recherche des corrections similaires dans l'historique
        
        Args:
            current_documents: Documents actuels
            
        Returns:
            Liste de corrections pertinentes
        """
        corrections = self._load_json(self.corrections_file)
        
        # Extraire types de documents actuels
        current_types = set(d.metadata.get("doc_type") for d in current_documents)
        
        # Filtrer les corrections avec contexte similaire
        similar = []
        for record in corrections:
            record_types = set(record.get("document_types", []))
            
            # Si intersection de types de documents
            if current_types & record_types:
                # Extraire les corrections individuelles
                for correction in record.get("corrections", []):
                    similar.append({
                        "field": correction["field"],
                        "corrected_value": correction["new_value"],
                        "confidence": record["validated"]["confidence"],
                        "timestamp": record["timestamp"]
                    })
        
        return similar
    
    def search_similar_question(self, question: str) -> Optional[dict]:
        """
        Recherche une réponse à une question similaire
        
        Args:
            question: Question actuelle
            
        Returns:
            Réponse mémorisée si trouvée
        """
        qa_memory = self._load_json(self.qa_memory_file)
        
        question_lower = question.lower()
        
        # Recherche par similarité simple (mots-clés)
        for record in reversed(qa_memory):  # Plus récent d'abord
            stored_question = record.get("question", "").lower()
            
            # Similarité basique: mots communs
            if self._calculate_similarity(question_lower, stored_question) > 0.7:
                return {
                    "question": question,
                    "answer": record["corrected_answer"],
                    "confidence": record["corrected_confidence"],
                    "sources": record.get("sources", []),
                    "from_memory": True
                }
        
        return None
    
    def get_correction_stats(self) -> dict:
        """Retourne des statistiques sur les corrections"""
        corrections = self._load_json(self.corrections_file)
        qa_memory = self._load_json(self.qa_memory_file)
        
        total_field_corrections = sum(
            len(r.get("corrections", [])) for r in corrections
        )
        
        return {
            "total_extraction_corrections": len(corrections),
            "total_field_corrections": total_field_corrections,
            "total_qa_corrections": len(qa_memory),
            "most_corrected_fields": self._get_most_corrected_fields(corrections)
        }
    
    def _identify_corrections(self, original: dict, validated: dict) -> List[dict]:
        """Identifie les différences entre original et validé"""
        corrections = []
        
        all_fields = set(list(original.keys()) + list(validated.keys()))
        
        for field in all_fields:
            orig_val = original.get(field)
            valid_val = validated.get(field)
            
            if orig_val != valid_val:
                corrections.append({
                    "field": field,
                    "old_value": orig_val,
                    "new_value": valid_val,
                    "correction_type": self._get_correction_type(orig_val, valid_val)
                })
        
        return corrections
    
    def _get_correction_type(self, old_val, new_val) -> str:
        """Détermine le type de correction"""
        if old_val is None and new_val is not None:
            return "added"
        elif old_val is not None and new_val is None:
            return "removed"
        else:
            return "modified"
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calcule similarité simple entre deux textes"""
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union)
    
    def _get_most_corrected_fields(self, corrections: List[dict]) -> dict:
        """Identifie les champs les plus souvent corrigés"""
        field_counts = {}
        
        for record in corrections:
            for correction in record.get("corrections", []):
                field = correction["field"]
                field_counts[field] = field_counts.get(field, 0) + 1
        
        # Trier par fréquence
        sorted_fields = sorted(
            field_counts.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        return dict(sorted_fields[:5])  # Top 5
    
    def _load_json(self, file_path: Path) -> list:
        """Charge un fichier JSON"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []
    
    def _save_json(self, file_path: Path, data: list):
        """Sauvegarde en JSON"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def export_memory(self, output_path: str):
        """Exporte toute la mémoire dans un fichier unique"""
        export = {
            "timestamp": datetime.now().isoformat(),
            "extraction_corrections": self._load_json(self.corrections_file),
            "qa_corrections": self._load_json(self.qa_memory_file),
            "manual_context": self._load_json(self.context_file),
            "stats": self.get_correction_stats()
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Mémoire exportée vers {output_path}")
