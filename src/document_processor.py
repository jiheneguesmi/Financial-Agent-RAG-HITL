"""
Traitement et ingestion des documents PDF
"""

from pathlib import Path
from typing import List, Dict
import PyPDF2
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


class DocumentProcessor:
    """Gestion de l'ingestion et du découpage des documents"""
    
    def __init__(self, config):
        self.config = config
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def process_documents(self, file_paths: List[str]) -> List[Document]:
        """
        Traite une liste de documents PDF
        
        Args:
            file_paths: Chemins vers les fichiers PDF
            
        Returns:
            Liste de documents LangChain avec métadonnées
        """
        all_documents = []
        
        for file_path in file_paths:
            path = Path(file_path)
            
            if not path.exists():
                print(f"[ATTENTION] Fichier non trouvé: {file_path}")
                continue
            
            if path.suffix.lower() == '.pdf':
                docs = self._process_pdf(path)
            elif path.suffix.lower() == '.json':
                docs = self._process_json(path)
            else:
                print(f"[ATTENTION] Format non supporté: {path.suffix}")
                continue
            
            all_documents.extend(docs)
        
        return all_documents
    
    def _process_pdf(self, file_path: Path) -> List[Document]:
        """Extrait et découpe le contenu d'un PDF"""
        documents = []
        
        try:
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                
                # Extraire le texte de chaque page
                full_text = ""
                for page_num, page in enumerate(pdf_reader.pages):
                    text = page.extract_text()
                    full_text += f"\n--- Page {page_num + 1} ---\n{text}"
                
                # Découper en chunks
                chunks = self.text_splitter.split_text(full_text)
                
                # Créer les documents LangChain
                for i, chunk in enumerate(chunks):
                    doc = Document(
                        page_content=chunk,
                        metadata={
                            "source": file_path.name,
                            "chunk_id": i,
                            "total_chunks": len(chunks),
                            "file_type": "pdf",
                            "doc_type": self._infer_document_type(file_path.name)
                        }
                    )
                    documents.append(doc)
        
        except Exception as e:
            print(f"❌ Erreur lors du traitement de {file_path.name}: {e}")
        
        return documents
    
    def _process_json(self, file_path: Path) -> List[Document]:
        """Traite un fichier JSON comme document"""
        import json
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Convertir le JSON en texte structuré
            content = self._json_to_text(data)
            
            doc = Document(
                page_content=content,
                metadata={
                    "source": file_path.name,
                    "file_type": "json",
                    "doc_type": "structured_data"
                }
            )
            
            return [doc]
        
        except Exception as e:
            print(f"❌ Erreur lors du traitement de {file_path.name}: {e}")
            return []
    
    def _json_to_text(self, data: dict, prefix: str = "") -> str:
        """Convertit un JSON en texte structuré pour l'indexation"""
        lines = []
        
        for key, value in data.items():
            if isinstance(value, dict):
                lines.append(f"{prefix}{key}:")
                lines.append(self._json_to_text(value, prefix + "  "))
            elif isinstance(value, list):
                lines.append(f"{prefix}{key}: {', '.join(map(str, value))}")
            else:
                lines.append(f"{prefix}{key}: {value}")
        
        return "\n".join(lines)
    
    def _infer_document_type(self, filename: str) -> str:
        """Infère le type de document depuis le nom de fichier"""
        filename_lower = filename.lower()
        
        if any(kw in filename_lower for kw in ["2065", "liasse", "fiscal"]):
            return "tax_declaration"
        elif any(kw in filename_lower for kw in ["2033", "bilan", "balance"]):
            return "financial_statement"
        elif any(kw in filename_lower for kw in ["description", "présentation"]):
            return "company_description"
        elif "synthétique" in filename_lower or "synthetique" in filename_lower:
            return "summary_report"
        else:
            return "unknown"
    
    def extract_tables(self, file_path: Path) -> List[Dict]:
        """
        Extrait les tableaux structurés d'un PDF (optionnel, avancé)
        Utile pour les liasses fiscales
        """
        # TODO: Implémenter avec camelot ou tabula-py si besoin
        pass