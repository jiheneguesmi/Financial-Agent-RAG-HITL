"""
Application Streamlit pour l'Agent d'Extraction Financière
Interface utilisateur interactive pour le pipeline RAG + HITL
"""

import streamlit as st
import json
from pathlib import Path
from typing import Optional
import sys

# Ajouter le répertoire du projet au path
sys.path.insert(0, str(Path(__file__).parent))

from src.document_processor import DocumentProcessor
from src.rag_engine import RAGEngine
from src.extractor import FinancialExtractor
from src.qa_engine import QAEngine
from src.hitl_manager import HITLManager
from src.memory_manager import MemoryManager
from src.config import Config


# Configuration Streamlit
st.set_page_config(
    page_title="Agent Financier RAG + HITL",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .section-header {
        font-size: 1.8rem;
        font-weight: bold;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 0.5rem;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)


@st.cache_resource
def initialize_agent():
    """Initialise l'agent financier avec cache"""
    try:
        config = Config()
        memory = MemoryManager(config.memory_path)
        
        agent_components = {
            'config': config,
            'memory': memory,
            'doc_processor': DocumentProcessor(config),
            'rag_engine': RAGEngine(config, memory),
            'extractor': None,  # Sera initialisé après le RAG
            'qa_engine': None,  # Sera initialisé après le RAG
            'hitl': HITLManager(config, memory)
        }
        
        return agent_components
    except Exception as e:
        st.error(f"Erreur lors de l'initialisation: {e}")
        return None


def display_extraction_results(result: dict):
    """Affiche les résultats d'extraction de manière structurée"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        confidence = result.get("confidence_score", 0)
        st.metric("Score de confiance", f"{confidence:.2%}", f"{confidence:.4f}")
    
    with col2:
        extracted = len(result.get("sheet", {}))
        st.metric("Champs extraits", extracted)
    
    with col3:
        missing = len(result.get("missing_fields", []))
        st.metric("Champs manquants", missing)
    
    # Afficher les données extraites
    if result.get("sheet"):
        st.subheader("Données Extraites")
        data_df = json.dumps(result.get("sheet"), indent=2, ensure_ascii=False)
        st.json(result.get("sheet"))
    
    # Afficher les champs manquants
    if result.get("missing_fields"):
        with st.expander("Champs manquants", expanded=False):
            st.write(", ".join(result.get("missing_fields")))
    
    # Afficher les informations supplémentaires
    if result.get("additional_information"):
        with st.expander("Informations supplémentaires", expanded=False):
            for info in result.get("additional_information"):
                st.write(f"- {info}")


def display_qa_results(answer: dict):
    """Affiche les résultats Q&A de manière structurée"""
    st.subheader("Réponse")
    st.write(answer.get("answer", "Aucune réponse disponible"))
    
    col1, col2 = st.columns(2)
    
    with col1:
        confidence = answer.get("confidence", 0)
        st.metric("Confiance", f"{confidence:.2%}")
    
    with col2:
        needs_validation = answer.get("needs_validation", False)
        validation_status = "Requise" if needs_validation else "Validée"
        st.metric("Validation", validation_status)
    
    # Afficher les sources
    sources = answer.get("sources", [])
    if sources:
        with st.expander(f"Sources ({len(set(sources))} document(s))", expanded=False):
            for i, source in enumerate(set(sources), 1):
                st.write(f"{i}. {source}")


def main():
    # En-tête principal
    st.markdown("<div class='main-header'>Agent Financier RAG + HITL</div>", unsafe_allow_html=True)
    st.markdown("Extraction et analyse de données financières avec validation humaine")
    
    # Initialiser la session
    if 'agent' not in st.session_state:
        st.session_state.agent = initialize_agent()
    
    if st.session_state.agent is None:
        st.error("Impossible d'initialiser l'application")
        return
    
    agent = st.session_state.agent
    
    # Barre latérale avec navigation
    st.sidebar.markdown("## Navigation")
    page = st.sidebar.radio(
        "Sélectionnez une page",
        ["Accueil", "Extraction de Données", "Questions/Réponses", "Gestion Mémoire", "Paramètres"]
    )
    
    # PAGE 1: ACCUEIL
    if page == "Accueil":
        st.markdown("<div class='section-header'>Bienvenue</div>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### À propos
            Cet agent intelligent combiner plusieurs technologies:
            - **RAG**: Recherche d'information vectorielle dans les documents
            - **LLM**: Extraction et génération avec GPT-4o
            - **HITL**: Validation et correction humaine
            - **Mémoire**: Apprentissage des corrections passées
            """)
        
        with col2:
            st.markdown("""
            ### Fonctionnalités
            1. **Extraction financière**: Extrait automatiquement les données clés
            2. **Q&A intelligent**: Répond à des questions sur l'entreprise
            3. **Validation HITL**: Correction et amélioration avec intervention humaine
            4. **Mémoire persistante**: Apprend des corrections pour améliorer les futures extractions
            """)
        
        st.markdown("---")
        st.markdown("### État du système")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info("✓ Agent initialisé")
        with col2:
            st.info("✓ RAG disponible")
        with col3:
            st.info("✓ Mémoire chargée")
    
    # PAGE 2: EXTRACTION
    elif page == "Extraction de Données":
        st.markdown("<div class='section-header'>Extraction de Données Financières</div>", unsafe_allow_html=True)
        
        # Uploader les fichiers
        st.subheader("1. Charger les documents")
        uploaded_files = st.file_uploader(
            "Sélectionnez les fichiers PDF ou JSON",
            type=["pdf", "json"],
            accept_multiple_files=True
        )
        
        if uploaded_files:
            st.success(f"{len(uploaded_files)} fichier(s) chargé(s)")
            
            # Afficher un aperçu des fichiers
            with st.expander("Fichiers chargés"):
                for file in uploaded_files:
                    st.write(f"- {file.name} ({file.size / 1024:.1f} KB)")
            
            # Bouton de traitement
            if st.button("Lancer l'extraction", key="extract_button"):
                with st.spinner("Traitement des documents..."):
                    # Sauvegarder les fichiers temporairement
                    temp_dir = Path("temp_uploads")
                    temp_dir.mkdir(exist_ok=True)
                    
                    file_paths = []
                    for uploaded_file in uploaded_files:
                        file_path = temp_dir / uploaded_file.name
                        with open(file_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        file_paths.append(str(file_path))
                    
                    try:
                        # Traiter les documents
                        documents = agent['doc_processor'].process_documents(file_paths)
                        
                        # Indexer les documents
                        agent['rag_engine'].index_documents(documents)
                        
                        # Initialiser les moteurs d'extraction et Q&A
                        if agent['extractor'] is None:
                            agent['extractor'] = FinancialExtractor(agent['config'], agent['rag_engine'])
                        if agent['qa_engine'] is None:
                            agent['qa_engine'] = QAEngine(agent['config'], agent['rag_engine'])
                        
                        # Extraire les données
                        extraction_result = agent['extractor'].extract(documents)
                        
                        # Sauvegarder le résultat
                        st.session_state.last_extraction = extraction_result
                        st.session_state.last_documents = documents
                        
                        # Afficher les résultats
                        st.markdown("---")
                        st.subheader("Résultats d'extraction")
                        display_extraction_results(extraction_result)
                        
                        # Vérifier si validation nécessaire
                        needs_validation = agent['hitl'].needs_validation(extraction_result)
                        
                        if needs_validation:
                            st.markdown("<div class='warning-box'>⚠️ Validation humaine requise</div>", unsafe_allow_html=True)
                            
                            # Interface de validation
                            st.subheader("Validation et Corrections")
                            
                            # Afficher les champs pour validation
                            data = extraction_result.get("sheet", {})
                            corrections = {}
                            
                            for field, value in data.items():
                                col1, col2 = st.columns([3, 1])
                                with col1:
                                    corrected_value = st.text_input(
                                        f"Corrigez si nécessaire: {field}",
                                        value=str(value),
                                        key=f"field_{field}"
                                    )
                                    if corrected_value != str(value):
                                        corrections[field] = corrected_value
                                
                                with col2:
                                    st.write(f"Valeur: {value}")
                            
                            # Bouton validation
                            if st.button("Valider et enregistrer"):
                                st.success("Extraction validée et enregistrée")
                                if corrections:
                                    agent['memory'].store_corrections(
                                        st.session_state.last_documents,
                                        extraction_result,
                                        {"corrections": corrections}
                                    )
                                    st.info("Corrections enregistrées en mémoire")
                        else:
                            st.markdown("<div class='success-box'>✓ Extraction validée automatiquement</div>", unsafe_allow_html=True)
                        
                        # Télécharger les résultats
                        st.subheader("Exporter les résultats")
                        json_str = json.dumps(extraction_result, ensure_ascii=False, indent=2)
                        st.download_button(
                            "Télécharger les résultats (JSON)",
                            json_str,
                            "extraction_results.json",
                            "application/json"
                        )
                        
                    except Exception as e:
                        st.markdown(f"<div class='error-box'>Erreur: {e}</div>", unsafe_allow_html=True)
                    
                    finally:
                        # Nettoyer les fichiers temporaires
                        import shutil
                        if temp_dir.exists():
                            shutil.rmtree(temp_dir)
        else:
            st.info("Veuillez charger au moins un fichier PDF ou JSON")
    
    # PAGE 3: Q&A
    elif page == "Questions/Réponses":
        st.markdown("<div class='section-header'>Questions et Réponses</div>", unsafe_allow_html=True)
        
        # Vérifier que l'index RAG est chargé
        if st.session_state.agent['rag_engine'].vectorstore is None:
            st.warning("Veuillez d'abord charger et indexer les documents dans la page 'Extraction'")
            st.stop()
        
        # Champ de question
        question = st.text_area(
            "Posez votre question",
            placeholder="Ex: Quel est le secteur d'activité de l'entreprise?",
            height=100
        )
        
        if st.button("Rechercher une réponse"):
            if question:
                with st.spinner("Recherche en cours..."):
                    try:
                        # Initialiser QA si pas déjà fait
                        if agent['qa_engine'] is None:
                            agent['qa_engine'] = QAEngine(agent['config'], agent['rag_engine'])
                        
                        # Obtenir la réponse
                        answer = agent['qa_engine'].answer(question)
                        st.session_state.last_answer = answer
                        
                        # Afficher les résultats
                        st.markdown("---")
                        display_qa_results(answer)
                        
                        # Validation si nécessaire
                        if answer.get("needs_validation"):
                            st.markdown("<div class='warning-box'>⚠️ Réponse à faible confiance - Validation recommandée</div>", unsafe_allow_html=True)
                            
                            user_feedback = st.radio(
                                "Êtes-vous satisfait de cette réponse?",
                                ["Oui", "Non", "Corriger"],
                                key="feedback"
                            )
                            
                            if user_feedback == "Corriger":
                                corrected_answer = st.text_area("Fournir la réponse correcte:")
                                if st.button("Enregistrer la correction"):
                                    agent['memory'].store_qa_correction(
                                        question,
                                        answer,
                                        {"corrected_answer": corrected_answer}
                                    )
                                    st.success("Correction enregistrée")
                    
                    except Exception as e:
                        st.markdown(f"<div class='error-box'>Erreur: {e}</div>", unsafe_allow_html=True)
            else:
                st.warning("Veuillez entrer une question")
    
    # PAGE 4: GESTION MÉMOIRE
    elif page == "Gestion Mémoire":
        st.markdown("<div class='section-header'>Gestion de la Mémoire</div>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Corrections d'extraction")
            corrections_file = Path("memory/extraction_corrections.json")
            if corrections_file.exists():
                with open(corrections_file, 'r', encoding='utf-8') as f:
                    corrections = json.load(f)
                st.metric("Corrections enregistrées", len(corrections.get("corrections", [])))
                with st.expander("Voir les corrections"):
                    st.json(corrections)
            else:
                st.info("Aucune correction enregistrée")
        
        with col2:
            st.subheader("Corrections Q&A")
            qa_file = Path("memory/qa_corrections.json")
            if qa_file.exists():
                with open(qa_file, 'r', encoding='utf-8') as f:
                    qa = json.load(f)
                st.metric("Q&A enregistrées", len(qa.get("qa_corrections", [])))
                with st.expander("Voir les Q&A"):
                    st.json(qa)
            else:
                st.info("Aucune Q&A enregistrée")
        
        st.markdown("---")
        
        # Boutons de gestion
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Réinitialiser les corrections"):
                if st.checkbox("Confirmer la réinitialisation"):
                    corrections_file.unlink(missing_ok=True)
                    st.success("Corrections réinitialisées")
        
        with col2:
            if st.button("Réinitialiser les Q&A"):
                if st.checkbox("Confirmer la réinitialisation Q&A"):
                    qa_file.unlink(missing_ok=True)
                    st.success("Q&A réinitialisées")
    
    # PAGE 5: PARAMÈTRES
    elif page == "Paramètres":
        st.markdown("<div class='section-header'>Paramètres</div>", unsafe_allow_html=True)
        
        config = agent['config']
        
        st.subheader("Configuration RAG")
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"**Modèle LLM**: {config.llm_model}")
            st.info(f"**Température**: {config.llm_temperature}")
            st.info(f"**Top-K retrieval**: {config.top_k_retrieval}")
        
        with col2:
            st.info(f"**Modèle embedding**: {config.embedding_model}")
            st.info(f"**Chunk size**: {config.chunk_size}")
            st.info(f"**Chunk overlap**: {config.chunk_overlap}")
        
        st.subheader("Paramètres de validation")
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"**Seuil validation obligatoire**: {config.require_validation_below:.2%}")
            st.info(f"**Seuil auto-validation**: {config.auto_validate_above:.2%}")
        
        with col2:
            st.info(f"**Seuil confiance**: {config.confidence_threshold:.2%}")
            st.info(f"**Champs critiques**: {len(config.extraction_schema)} champs")


if __name__ == "__main__":
    main()
