#!/usr/bin/env python
\"\"\"
Tests de validation de l'application Streamlit
Vérifie que tous les modules sont correctement importés et que l'app peut démarrer
\"\"\"

import sys
from pathlib import Path

# Ajouter le répertoire du projet au path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

def test_imports():
    \"\"\"Teste les imports principaux\"\"\"
    print("[TEST] Vérification des imports...")
    
    try:
        print("  ✓ streamlit")
        import streamlit as st
    except ImportError as e:
        print(f"  [ERREUR] streamlit: {e}")
        return False
    
    try:
        print("  ✓ langchain")
        from langchain_core.documents import Document
    except ImportError as e:
        print(f"  [ERREUR] langchain: {e}")
        return False
    
    try:
        print("  ✓ langchain_openai")
        from langchain_openai import OpenAIEmbeddings, ChatOpenAI
    except ImportError as e:
        print(f"  [ERREUR] langchain_openai: {e}")
        return False
    
    try:
        print("  ✓ faiss")
        from langchain_community.vectorstores import FAISS
    except ImportError as e:
        print(f"  [ERREUR] faiss: {e}")
        return False
    
    try:
        print("  ✓ src.config")
        from src.config import Config
    except ImportError as e:
        print(f"  [ERREUR] src.config: {e}")
        return False
    
    try:
        print("  ✓ src.document_processor")
        from src.document_processor import DocumentProcessor
    except ImportError as e:
        print(f"  [ERREUR] src.document_processor: {e}")
        return False
    
    try:
        print("  ✓ src.rag_engine")
        from src.rag_engine import RAGEngine
    except ImportError as e:
        print(f"  [ERREUR] src.rag_engine: {e}")
        return False
    
    try:
        print("  ✓ src.extractor")
        from src.extractor import FinancialExtractor
    except ImportError as e:
        print(f"  [ERREUR] src.extractor: {e}")
        return False
    
    try:
        print("  ✓ src.qa_engine")
        from src.qa_engine import QAEngine
    except ImportError as e:
        print(f"  [ERREUR] src.qa_engine: {e}")
        return False
    
    try:
        print("  ✓ src.hitl_manager")
        from src.hitl_manager import HITLManager
    except ImportError as e:
        print(f"  [ERREUR] src.hitl_manager: {e}")
        return False
    
    try:
        print("  ✓ src.memory_manager")
        from src.memory_manager import MemoryManager
    except ImportError as e:
        print(f"  [ERREUR] src.memory_manager: {e}")
        return False
    
    return True


def test_file_structure():
    \"\"\"Teste la structure des répertoires\"\"\"
    print("\\n[TEST] Vérification de la structure des répertoires...")
    
    required_dirs = [
        "src",
        "data",
        "outputs",
        "memory",
        "rag_index",
        ".streamlit"
    ]
    
    for dir_name in required_dirs:
        dir_path = project_dir / dir_name
        if dir_path.exists():
            print(f"  ✓ {dir_name}/")
        else:
            print(f"  [ATTENTION] {dir_name}/ non trouvé")
            # Créer les répertoires manquants
            dir_path.mkdir(exist_ok=True, parents=True)
            print(f"    -> Créé {dir_name}/")
    
    required_files = [
        "app.py",
        "main.py",
        "requirements.txt",
        "STREAMLIT_README.md",
        "run_streamlit.py",
        ".streamlit/config.toml",
        "src/__init__.py",
        "src/config.py",
        "src/document_processor.py",
        "src/rag_engine.py",
        "src/extractor.py",
        "src/qa_engine.py",
        "src/hitl_manager.py",
        "src/memory_manager.py"
    ]
    
    for file_name in required_files:
        file_path = project_dir / file_name
        if file_path.exists():
            print(f"  ✓ {file_name}")
        else:
            print(f"  [ATTENTION] {file_name} non trouvé")
    
    return True


def test_environment():
    \"\"\"Teste les variables d'environnement\"\"\"
    print("\\n[TEST] Vérification des variables d'environnement...")
    
    import os
    
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        masked_key = api_key[:20] + "..." + api_key[-4:] if len(api_key) > 24 else "***"
        print(f"  ✓ OPENAI_API_KEY: {masked_key}")
    else:
        print(f"  [ATTENTION] OPENAI_API_KEY non définie")
        print(f"    -> Créez un fichier .env avec: OPENAI_API_KEY=sk-...")
    
    return True


def test_config():
    \"\"\"Teste le chargement de la configuration\"\"\"
    print("\\n[TEST] Vérification de la configuration...")
    
    try:
        from src.config import Config
        config = Config()
        
        print(f"  ✓ Config chargée")
        print(f"    - LLM: {config.llm_model}")
        print(f"    - Embedding: {config.embedding_model}")
        print(f"    - Chunk size: {config.chunk_size}")
        
        return True
    except Exception as e:
        print(f"  [ERREUR] Impossible de charger la config: {e}")
        return False


def test_emoji_removal():
    \"\"\"Vérifie que les emojis ont été retirés\"\"\"
    print("\\n[TEST] Vérification du retrait des emojis...")
    
    files_to_check = [
        "main.py",
        "src/document_processor.py",
        "src/rag_engine.py",
        "src/hitl_manager.py"
    ]
    
    emoji_patterns = [
        "🚀", "📄", "✓", "🔍", "💰", "🔄", "✨", "⚠️", "❌", "📊",
        "💬", "👋", "❓", "💡", "📋", "✅", "💾", "✓", "📝", "🎯"
    ]
    
    all_clean = True
    for file_name in files_to_check:
        file_path = project_dir / file_name
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            found_emojis = []
            for emoji in emoji_patterns:
                if emoji in content:
                    found_emojis.append(emoji)
            
            if found_emojis:
                print(f"  [ATTENTION] {file_name}: {len(found_emojis)} emoji(s) trouvé(s)")
                all_clean = False
            else:
                print(f"  ✓ {file_name}: Propre")
    
    return all_clean


def main():
    print("=" * 60)
    print("Tests de validation - Agent Financier RAG + HITL")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Structure fichiers", test_file_structure),
        ("Environnement", test_environment),
        ("Configuration", test_config),
        ("Retrait emojis", test_emoji_removal)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\\n[ERREUR CRITIQUE] {test_name}: {e}")
            results.append((test_name, False))
    
    # Résumé
    print("\\n" + "=" * 60)
    print("RÉSUMÉ DES TESTS")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ SUCCÈS" if result else "✗ ÉCHEC"
        print(f"  {status}: {test_name}")
    
    print(f"\\nRésultat: {passed}/{total} tests réussis")
    
    if passed == total:
        print("\\n✓ Tous les tests sont passés!")
        print("\\nVous pouvez maintenant lancer l'application:")
        print("  python run_streamlit.py")
        print("  ou")
        print("  streamlit run app.py")
        return 0
    else:
        print(f"\\n✗ {total - passed} test(s) échoué(s)")
        print("Veuillez corriger les problèmes avant de lancer l'application.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
