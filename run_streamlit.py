import subprocess
import sys
import os
from pathlib import Path

def main():
    # Vérifier que Streamlit est installé
    try:
        import streamlit
    except ImportError:
        print("[ERREUR] Streamlit n'est pas installé.")
        print("Installation: pip install streamlit")
        sys.exit(1)
    
    # Obtenir le répertoire de l'application
    app_dir = Path(__file__).parent
    app_file = app_dir / "app.py"
    
    if not app_file.exists():
        print(f"[ERREUR] app.py non trouvé dans {app_dir}")
        sys.exit(1)
    
    print("=" * 60)
    print("Agent Financier RAG + HITL - Interface Streamlit")
    print("=" * 60)
    print(f"\\nLancement de l'application...")
    print(f"Fichier: {app_file}")
    print(f"\\nAccès: http://localhost:8501")
    print("\\nAppuyez sur Ctrl+C pour arrêter\\n")
    
    # Lancer Streamlit
    try:
        subprocess.run(
            [sys.executable, "-m", "streamlit", "run", str(app_file)],
            cwd=str(app_dir)
        )
    except KeyboardInterrupt:
        print("\\n\\nArrêt de l'application.")
    except Exception as e:
        print(f"[ERREUR] Impossible de lancer Streamlit: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
