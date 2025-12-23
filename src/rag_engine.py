"""
Moteur RAG: indexation et recherche vectorielle
"""

from typing import List, Dict, Optional
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
import json
import os
from pathlib import Path

try:
    from langchain_openai import OpenAIEmbeddings, ChatOpenAI
except ImportError:
    raise ImportError("Veuillez installer langchain-openai: pip install langchain-openai")

from src.config import Config


class RAGEngine:
    """Gestion de l'indexation vectorielle et de la recherche"""
    
    def __init__(self, config, memory_manager):
        self.config = config
        self.memory = memory_manager
        
        # Clé API OpenAI
        api_key = os.getenv("OPENAI_API_KEY") or ""
        
        # Embeddings
        self.embeddings = OpenAIEmbeddings(
            model=config.embedding_model,
            openai_api_key=api_key
        )
        
        # LLM pour génération
        self.llm = ChatOpenAI(
            model=config.llm_model,
            temperature=config.llm_temperature,
            max_tokens=config.llm_max_tokens,
            openai_api_key=api_key
        )
        
        # Vectorstore
        self.vectorstore: Optional[FAISS] = None
        self.documents: List[Document] = []
        
        # Charger l'index existant au démarrage
        self._load_persisted_index()
    
    def index_documents(self, documents: List[Document], save_to_disk: bool = True):
        """
        Indexe les documents dans le vectorstore
        
        Args:
            documents: Liste de documents LangChain
            save_to_disk: Si True, sauvegarde l'index sur disque après indexation
        """
        self.documents = documents
        
        if not documents:
            print("⚠️  Aucun document à indexer")
            return
        
        # Créer ou mettre à jour le vectorstore
        if self.vectorstore is None:
            self.vectorstore = FAISS.from_documents(
                documents=documents,
                embedding=self.embeddings
            )
        else:
            self.vectorstore.add_documents(documents)
        
        print(f"✓ {len(documents)} documents indexés")
        
        # Sauvegarder sur disque si demandé
        if save_to_disk:
            self.save_index()
    
    def save_index(self, index_name: str = "rag_index"):
        """
        Sauvegarde l'index RAG sur disque
        
        Args:
            index_name: Nom de l'index à sauvegarder
        """
        if self.vectorstore is None:
            print("⚠️  Aucun index à sauvegarder")
            return
        
        try:
            index_path = Path(self.config.rag_index_path)
            index_path.mkdir(exist_ok=True, parents=True)
            
            # Sauvegarder l'index FAISS
            self.vectorstore.save_local(
                folder_path=str(index_path),
                index_name=index_name
            )
            
            # Sauvegarder les métadonnées des documents
            import pickle
            documents_file = index_path / f"{index_name}_documents.pkl"
            with open(documents_file, 'wb') as f:
                pickle.dump(self.documents, f)
            
            print(f"💾 Index RAG sauvegardé dans: {index_path}")
            print(f"   - {index_name}.faiss (index vectoriel)")
            print(f"   - {index_name}.pkl (docstore)")
            print(f"   - {index_name}_documents.pkl (métadonnées)")
            
        except Exception as e:
            print(f"❌ Erreur lors de la sauvegarde de l'index: {e}")
    
    def _load_persisted_index(self, index_name: str = "rag_index"):
        """
        Charge automatiquement l'index RAG persisté au démarrage
        
        Args:
            index_name: Nom de l'index à charger
        """
        try:
            index_path = Path(self.config.rag_index_path)
            index_file = index_path / f"{index_name}.faiss"
            
            if not index_file.exists():
                return False
            
            # Charger l'index FAISS
            self.vectorstore = FAISS.load_local(
                folder_path=str(index_path),
                embeddings=self.embeddings,
                index_name=index_name,
                allow_dangerous_deserialization=True
            )
            
            # Charger les métadonnées des documents
            import pickle
            documents_file = index_path / f"{index_name}_documents.pkl"
            if documents_file.exists():
                with open(documents_file, 'rb') as f:
                    self.documents = pickle.load(f)
            
            print(f"✅ Index FAISS restauré: {len(self.documents)} documents chargés")
            return True
            
        except Exception as e:
            print(f"⚠️  Impossible de restaurer l'index FAISS: {e}")
            return False
    
    def load_index(self, index_name: str = "rag_index"):
        """
        Charge l'index RAG depuis le disque
        
        Args:
            index_name: Nom de l'index à charger
            
        Returns:
            True si l'index a été chargé, False sinon
        """
        try:
            index_path = Path(self.config.rag_index_path)
            index_file = index_path / f"{index_name}.faiss"
            
            if not index_file.exists():
                print(f"⚠️  Aucun index trouvé dans {index_path}")
                return False
            
            # Charger l'index FAISS
            self.vectorstore = FAISS.load_local(
                folder_path=str(index_path),
                embeddings=self.embeddings,
                index_name=index_name,
                allow_dangerous_deserialization=True
            )
            
            # Charger les métadonnées des documents
            import pickle
            documents_file = index_path / f"{index_name}_documents.pkl"
            if documents_file.exists():
                with open(documents_file, 'rb') as f:
                    self.documents = pickle.load(f)
            
            print(f"✅ Index RAG chargé depuis: {index_path}")
            print(f"   ✓ {len(self.documents)} documents chargés")
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors du chargement de l'index: {e}")
            return False
    
    def add_manual_context(self, context_data: dict):
        """
        Ajoute manuellement du contexte à la base RAG
        
        Args:
            context_data: Informations supplémentaires structurées
        """
        # Convertir en document texte
        content = self._format_context(context_data)
        
        doc = Document(
            page_content=content,
            metadata={
                "source": "manual_context",
                "type": context_data.get("type", "unknown"),
                "added_at": Config.get_timestamp()
            }
        )
        
        # Indexer
        if self.vectorstore:
            self.vectorstore.add_documents([doc])
        
        # Sauvegarder en mémoire persistante
        self.memory.store_manual_context(context_data)
    
    def retrieve(self, query: str, k: Optional[int] = None) -> List[Document]:
        """
        Recherche les documents les plus pertinents
        
        Args:
            query: Requête de recherche
            k: Nombre de résultats (défaut: config.top_k_retrieval)
            
        Returns:
            Liste des documents pertinents
        """
        if not self.vectorstore:
            return []
        
        k = k or self.config.top_k_retrieval
        
        # Recherche avec scores de similarité
        results = self.vectorstore.similarity_search_with_score(query, k=k)
        
        # Filtrer les résultats faibles (score > 1.5 pour cosine distance)
        filtered_results = [
            doc for doc, score in results if score < 1.5
        ]
        
        return filtered_results
    
    def retrieve_by_type(self, doc_type: str, k: int = 5) -> List[Document]:
        """Recherche par type de document"""
        if not self.documents:
            return []
        
        filtered = [
            doc for doc in self.documents
            if doc.metadata.get("doc_type") == doc_type
        ]
        
        return filtered[:k]
    
    def generate_with_context(self, query: str, context_docs: List[Document]) -> dict:
        """
        Génère une réponse en utilisant le contexte récupéré
        
        Args:
            query: Question ou instruction
            context_docs: Documents de contexte
            
        Returns:
            Dictionnaire avec réponse et métadonnées
        """
        # Construire le contexte
        context = self._build_context(context_docs)
        
        # Construire le prompt
        prompt = self._build_prompt(query, context)
        
        # Générer la réponse
        response = self.llm.invoke(prompt)
        
        return {
            "response": response.content,
            "context_used": len(context_docs),
            "sources": [doc.metadata.get("source") for doc in context_docs]
        }
    
    def _build_context(self, documents: List[Document]) -> str:
        """Construit le contexte depuis les documents récupérés"""
        context_parts = []
        
        for i, doc in enumerate(documents, 1):
            source = doc.metadata.get("source", "Unknown")
            content = doc.page_content
            context_parts.append(
                f"[Document {i} - {source}]\n{content}\n"
            )
        
        return "\n---\n".join(context_parts)
    
    def _build_prompt(self, query: str, context: str) -> str:
        """Construit le prompt pour le LLM"""
        return f"""Tu es un assistant d'analyse financière. Réponds à la question en te basant UNIQUEMENT sur le contexte fourni.

CONTEXTE:
{context}

QUESTION: {query}

INSTRUCTIONS:
- Réponds de manière précise et factuelle
- Cite les sources quand c'est pertinent
- Si l'information n'est pas dans le contexte, dis "Information non disponible dans les documents"
- Ne fais AUCUNE supposition ou hallucination

RÉPONSE:"""
    
    def _format_context(self, context_data: dict) -> str:
        """Formate le contexte manuel pour l'indexation"""
        lines = [f"Type: {context_data.get('type', 'Information')}"]
        
        if "content" in context_data:
            lines.append(f"Contenu: {context_data['content']}")
        
        for key, value in context_data.items():
            if key not in ["type", "content"]:
                lines.append(f"{key}: {value}")
        
        return "\n".join(lines)
    
    def get_document_stats(self) -> dict:
        """Retourne des statistiques sur les documents indexés"""
        if not self.documents:
            return {"total": 0}
        
        types = {}
        sources = set()
        
        for doc in self.documents:
            doc_type = doc.metadata.get("doc_type", "unknown")
            types[doc_type] = types.get(doc_type, 0) + 1
            sources.add(doc.metadata.get("source", "unknown"))
        
        return {
            "total_chunks": len(self.documents),
            "unique_sources": len(sources),
            "types": types
        }