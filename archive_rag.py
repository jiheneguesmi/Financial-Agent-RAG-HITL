"""
Script pour archiver (sauvegarder) l'index RAG
"""

import sys
import io
from pathlib import Path

# Configurer l'encodage UTF-8 pour Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Ajouter le répertoire parent au path
parent_dir = Path(__file__).parent
sys.path.insert(0, str(parent_dir))

from src.config import Config
from src.document_processor import DocumentProcessor
from src.rag_engine import RAGEngine
from src.memory_manager import MemoryManager


def archive_rag():
    """Archive l'index RAG en indexant tous les documents du dossier data/"""
    print("📦 Archivage de l'index RAG\n")
    
    try:
        # Initialisation
        print("📋 Initialisation...")
        config = Config()
        memory = MemoryManager(config.memory_path)
        doc_processor = DocumentProcessor(config)
        rag_engine = RAGEngine(config, memory)
        print("   ✓ Composants initialisés\n")
        
        # Chargement des documents
        print("📄 Chargement des documents depuis data/...")
        data_dir = parent_dir / "data"
        
        if not data_dir.exists():
            print(f"   ❌ Le dossier {data_dir} n'existe pas!")
            return
        
        doc_paths = list(data_dir.glob("*.pdf"))
        
        if not doc_paths:
            print("   ❌ Aucun fichier PDF trouvé!")
            return
        
        existing_docs = [str(p) for p in doc_paths]
        print(f"   ✓ {len(existing_docs)} fichier(s) PDF trouvé(s):")
        for doc_path in existing_docs:
            print(f"      - {Path(doc_path).name}")
        
        documents = doc_processor.process_documents(existing_docs)
        print(f"   ✓ {len(documents)} documents traités\n")
        
        # Indexation et archivage
        print("🔍 Indexation et archivage dans la base RAG...")
        rag_engine.index_documents(documents, save_to_disk=True)
        
        print("\n✅ Archivage terminé!")
        print(f"   📁 Index sauvegardé dans: {config.rag_index_path}")
        print(f"   📊 {len(documents)} documents archivés")
        
        # Afficher les statistiques
        stats = rag_engine.get_document_stats()
        print(f"\n📈 Statistiques de l'index:")
        print(f"   - Chunks totaux: {stats.get('total_chunks', 0)}")
        print(f"   - Sources uniques: {stats.get('unique_sources', 0)}")
        print(f"   - Types de documents: {stats.get('types', {})}")
        
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    archive_rag()

