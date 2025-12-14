"""
Configuration centralisée du système
"""

from pathlib import Path
from typing import Optional
import json
from datetime import datetime


class Config:
    """Gestion de la configuration du système"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.base_dir = Path(__file__).parent.parent
        
        # Chemins des répertoires
        self.data_dir = self.base_dir / "data"
        self.output_path = self.base_dir / "outputs"
        self.memory_path = self.base_dir / "memory"
        self.rag_index_path = self.base_dir / "rag_index"  # Dossier pour l'index RAG
        
        # Créer les répertoires
        for path in [self.data_dir, self.output_path, self.memory_path, self.rag_index_path]:
            path.mkdir(exist_ok=True)
        
        # Charger la config depuis fichier si fourni
        if config_path:
            self._load_config(config_path)
        else:
            self._set_defaults()
    
    def _set_defaults(self):
        """Configuration par défaut"""
        
        # LLM Configuration
        self.llm_model = "gpt-4o"
        self.llm_temperature = 0
        self.llm_max_tokens = 4000
        
        # RAG Configuration
        self.chunk_size = 1000
        self.chunk_overlap = 200
        self.top_k_retrieval = 5
        self.embedding_model = "text-embedding-3-small"  # OpenAI
        
        # Extraction Configuration
        self.confidence_threshold = 0.7
        self.missing_field_threshold = 3  # Max champs manquants avant HITL
        
        # HITL Configuration
        self.auto_validate_above = 0.9  # Validation auto si confiance > 0.9
        self.require_validation_below = 0.6  # HITL obligatoire si < 0.6
        
        # Schema d'extraction (structure cible)
        self.extraction_schema = {
            # Données financières selon le format demandé
            "finYear": {"type": "int", "aliases": ["exercice", "année", "année fiscale", "fiscal year"]},
            "finSales": {"type": "float", "aliases": ["chiffre d'affaires", "CA", "ventes", "sales", "revenus"]},
            "finProfit": {"type": "float", "aliases": ["résultat net", "bénéfice", "profit", "net profit"]},
            "finEquity": {"type": "float", "aliases": ["capitaux propres", "fonds propres", "equity", "shareholders equity"]},
            "finCapital": {"type": "float", "aliases": ["capital social", "capital", "share capital"]},
            "finBalanceSheet": {"type": "float", "aliases": ["total actif", "bilan", "balance sheet", "total assets", "actif total"]},
            "finAvailableFunds": {"type": "float", "aliases": ["trésorerie", "disponibilités", "available funds", "cash", "liquidités"]},
            "finOperationInc": {"type": "float", "aliases": ["résultat d'exploitation", "EBIT", "operating income", "résultat opérationnel"]},
            "finFinancialInc": {"type": "float", "aliases": ["résultat financier", "financial income", "résultat financier net"]},
            "finNonRecurring": {"type": "float", "aliases": ["résultat exceptionnel", "exceptional income", "non recurring", "éléments exceptionnels", "résultat exceptionnel net", "charges exceptionnelles", "produits exceptionnels", "éléments non récurrents"]},
            "finSecurities": {"type": "float", "aliases": ["valeurs mobilières", "securities", "titres", "investments"]}
        }
        
        # Fichiers de mémoire
        self.corrections_file = self.memory_path / "corrections.json"
        self.qa_memory_file = self.memory_path / "qa_memory.json"
        self.context_file = self.memory_path / "manual_context.json"
    
    def _load_config(self, config_path: str):
        """Charge la config depuis un fichier JSON"""
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        # Mettre à jour les attributs
        for key, value in config_data.items():
            setattr(self, key, value)
    
    def save_config(self, output_path: str):
        """Sauvegarde la configuration actuelle"""
        config_dict = {
            k: v for k, v in self.__dict__.items()
            if not k.startswith('_') and not isinstance(v, Path)
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, indent=2, ensure_ascii=False)
    
    @staticmethod
    def get_timestamp() -> str:
        """Retourne un timestamp formaté"""
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def get_field_aliases(self, field_name: str) -> list[str]:
        """Retourne les alias d'un champ"""
        schema = self.extraction_schema.get(field_name, {})
        return schema.get("aliases", [])
    
    def get_all_fields(self) -> list[str]:
        """Retourne tous les champs à extraire"""
        return list(self.extraction_schema.keys())