# Interface Streamlit - Agent Financier RAG + HITL

## Installation

### Prérequis
- Python 3.11+
- Clé API OpenAI

### Étapes d'installation

1. **Installer les dépendances**:
```bash
pip install -r requirements.txt
```

2. **Configurer les variables d'environnement**:
Créez un fichier `.env` à la racine du projet:
```
OPENAI_API_KEY=sk-...
```

## Utilisation

### Lancer l'application Streamlit

```bash
streamlit run app.py
```

L'application s'ouvrira à `http://localhost:8501`

## Navigation

### 1. Accueil
- Vue d'ensemble du système
- État du fonctionnement
- Documentation rapide

### 2. Extraction de Données
- **Charger les documents**: Importez des fichiers PDF ou JSON
- **Lancer l'extraction**: Traite les documents et extrait les données financières
- **Validation HITL**: Corrigez les données extraites si nécessaire
- **Exporter les résultats**: Téléchargez les résultats en JSON

**Processus**:
1. Téléchargez vos documents (PDF ou JSON)
2. Cliquez sur "Lancer l'extraction"
3. Validez les données ou effectuez des corrections
4. Téléchargez les résultats

### 3. Questions/Réponses
- Posez des questions sur l'entreprise
- L'agent recherche les informations dans les documents indexés
- Validez ou corrigez les réponses si nécessaire

**Exemple de questions**:
- "Quel est le secteur d'activité?"
- "Quels sont les principaux produits?"
- "Quel est le chiffre d'affaires 2024?"

### 4. Gestion Mémoire
- Consultez les corrections d'extraction enregistrées
- Consultez les questions/réponses enregistrées
- Réinitialisez la mémoire si nécessaire

### 5. Paramètres
- Consultez la configuration du système
- Modèle LLM utilisé (GPT-4o)
- Paramètres de validation et de recherche

## Caractéristiques

### Extraction Automatique
- Extraction des données financières clés
- Score de confiance automatique
- Identification des champs manquants

### Validation Humaine (HITL)
- Correction interactive des données
- Intégration des retours utilisateur
- Apprentissage en temps réel

### Mémoire Persistante
- Enregistrement des corrections
- Enregistrement des Q&A validées
- Amélioration continue du système

### RAG (Retrieval-Augmented Generation)
- Indexation vectorielle des documents
- Recherche sémantique
- Contexte augmenté pour le LLM

## Architecture

```
app.py (Streamlit)
    ↓
    ├── DocumentProcessor (Traitement PDF/JSON)
    ├── RAGEngine (Indexation + Recherche)
    ├── FinancialExtractor (Extraction structurée)
    ├── QAEngine (Questions/Réponses)
    ├── HITLManager (Validation humaine)
    └── MemoryManager (Persistence)
```

## Formats Supportés

### Documents
- **PDF**: Extraction textuelle avec PyPDF2
- **JSON**: Conversion en documents textuels structurés

### Sortie
- **JSON**: Résultats d'extraction structurés
- **Affichage Web**: Interface Streamlit interactive

## Configuration

Les paramètres de l'application sont définis dans `src/config.py`:

```python
# Extraction
extraction_schema = {...}     # Définition des champs à extraire
chunk_size = 1000             # Taille des chunks de texte
chunk_overlap = 100           # Chevauchement des chunks

# RAG
llm_model = "gpt-4o"          # Modèle LLM à utiliser
embedding_model = "text-embedding-3-small"

# Validation
require_validation_below = 0.7  # Seuil de validation obligatoire
auto_validate_above = 0.95      # Seuil d'auto-validation
confidence_threshold = 0.7      # Seuil de confiance pour les Q&A
```

## Dépannage

### Erreur "Index RAG non trouvé"
→ Vous devez d'abord charger et traiter des documents dans la page "Extraction"

### Erreur de clé API OpenAI
→ Vérifiez que votre `OPENAI_API_KEY` est correctement définie dans le fichier `.env`

### Lenteur lors de l'extraction
→ Les modèles LLM peuvent prendre du temps. C'est normal.

## Performance

- **Extraction**: 1-2 minutes par document (selon la taille)
- **Q&A**: 10-30 secondes par question
- **Indexation**: Dépend du nombre de documents

## Sécurité

- Les fichiers temporaires sont supprimés après traitement
- Les clés API ne sont pas exposées
- Les corrections sont stockées localement dans `memory/`

## Roadmap

Fonctionnalités futures:
- [ ] Support de plus de formats (Excel, CSV)
- [ ] Visualisation des données extraites
- [ ] Export en PDF/Excel
- [ ] Intégration d'autres LLM (Anthropic, Llama)
- [ ] API REST pour intégration
- [ ] Dashboard d'analytics
