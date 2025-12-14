# 📋 Plan du Projet - Agent Financier avec RAG et HITL

## 🎯 Objectif du Projet

Créer un agent intelligent d'extraction et d'analyse financière utilisant :
- **RAG (Retrieval-Augmented Generation)** : Recherche d'information dans les documents
- **HITL (Human-In-The-Loop)** : Validation et correction humaine
- **GPT-4o** : Modèle de langage pour l'extraction et les Q&A
- **Mémoire persistante** : Apprentissage des corrections

---

## 📁 Architecture du Projet

```
agent IA Harington/
├── main.py                    # Point d'entrée principal
├── run_agent.py              # Interface interactive
├── requirements.txt          # Dépendances Python
├── data/                     # Documents PDF sources
├── outputs/                  # Résultats d'extraction JSON
├── memory/                   # Corrections et historique
├── src/
│   ├── config.py             # Configuration centralisée
│   ├── document_processor.py # Traitement PDF
│   ├── rag_engine.py         # Moteur RAG (indexation + recherche)
│   ├── extractor.py          # Extraction données financières
│   ├── qa_engine.py          # Moteur Questions/Réponses
│   ├── hitl_manager.py       # Gestionnaire validation humaine
│   └── memory_manager.py    # Gestion mémoire persistante
└── test_hitl_input.py       # Script de test
```

---

## 🔄 Étapes de Développement

### **Étape 1 : Migration vers OpenAI GPT-4o**

**Objectif** : Remplacer l'API Anthropic par OpenAI

**Actions réalisées** :
- ✅ Mise à jour de `requirements.txt` : `langchain-openai`, `openai`
- ✅ Modification de `src/rag_engine.py` :
  - Remplacement de `ChatAnthropic` par `ChatOpenAI`
  - Remplacement de `AnthropicEmbeddings` par `OpenAIEmbeddings`
  - Ajout de la gestion de la clé API OpenAI
- ✅ Mise à jour de `src/config.py` : `llm_model = "gpt-4o"`

**Fichiers modifiés** :
- `requirements.txt`
- `src/rag_engine.py`
- `src/config.py`

---

### **Étape 2 : Refactorisation Complète**

**Objectif** : Transformer le code React/JS en architecture Python modulaire

**Actions réalisées** :
- ✅ Création de la structure modulaire :
  - `src/config.py` : Configuration centralisée
  - `src/document_processor.py` : Traitement PDF avec PyPDF2
  - `src/rag_engine.py` : Indexation vectorielle FAISS + RAG
  - `src/extractor.py` : Extraction structurée des données financières
  - `src/qa_engine.py` : Système de questions/réponses
  - `src/hitl_manager.py` : Validation humaine interactive
  - `src/memory_manager.py` : Stockage des corrections
- ✅ Création de `main.py` : Orchestration du pipeline complet
- ✅ Suppression de l'ancien `agent.py` (React/JS)

**Fichiers créés** :
- `main.py`
- `src/config.py`
- `src/document_processor.py`
- `src/rag_engine.py`
- `src/extractor.py`
- `src/qa_engine.py`
- `src/hitl_manager.py`
- `src/memory_manager.py`

---

### **Étape 3 : Définition du Schéma d'Extraction**

**Objectif** : Définir les 11 champs financiers à extraire

**Actions réalisées** :
- ✅ Mise à jour de `src/config.py` avec le schéma d'extraction :
  ```python
  extraction_schema = {
      "finYear": {"type": "int", "aliases": [...]},
      "finSales": {"type": "float", "aliases": [...]},
      "finProfit": {"type": "float", "aliases": [...]},
      "finEquity": {"type": "float", "aliases": [...]},
      "finCapital": {"type": "float", "aliases": [...]},
      "finBalanceSheet": {"type": "float", "aliases": [...]},
      "finAvailableFunds": {"type": "float", "aliases": [...]},
      "finOperationInc": {"type": "float", "aliases": [...]},
      "finFinancialInc": {"type": "float", "aliases": [...]},
      "finNonRecurring": {"type": "float", "aliases": [...]},
      "finSecurities": {"type": "float", "aliases": [...]}
  }
  ```

**Champs extraits** :
1. `finYear` - Année de l'exercice
2. `finSales` - Chiffre d'affaires
3. `finProfit` - Résultat net
4. `finEquity` - Capitaux propres
5. `finCapital` - Capital social
6. `finBalanceSheet` - Total du bilan
7. `finAvailableFunds` - Trésorerie disponible
8. `finOperationInc` - Résultat d'exploitation
9. `finFinancialInc` - Résultat financier
10. `finNonRecurring` - Résultat exceptionnel
11. `finSecurities` - Valeurs mobilières

---

### **Étape 4 : Format JSON de Sortie**

**Objectif** : Définir le format JSON exact pour les résultats

**Actions réalisées** :
- ✅ Modification de `src/extractor.py` pour produire :
  ```json
  {
    "sheet": {
      "finYear": 2024,
      "finSales": 56734.0,
      ...
    },
    "confidence_score": 0.9500,
    "missing_fields": [],
    "additional_information": []
  }
  ```
- ✅ Ajout de métadonnées (timestamp, fichiers traités)

**Format final** :
- `sheet` : Objet contenant les données extraites
- `confidence_score` : Score global (0-1)
- `missing_fields` : Liste des champs manquants
- `additional_information` : Informations additionnelles

---

### **Étape 5 : Test d'Extraction Automatique**

**Objectif** : Tester l'extraction sur les fichiers PDF du dossier `data/`

**Actions réalisées** :
- ✅ Ajout d'un bloc de test dans `src/extractor.py` :
  - Scan automatique des PDF dans `data/`
  - Extraction des 11 champs
  - Sauvegarde dans `outputs/extraction_TIMESTAMP.json`
  - Affichage des résultats
- ✅ Gestion des chemins relatifs
- ✅ Gestion de l'encodage UTF-8 pour Windows

**Commandes** :
```bash
python src/extractor.py
```

**Résultat** : Fichiers JSON générés dans `outputs/`

---

### **Étape 6 : Adaptation HITL au Nouveau Format**

**Objectif** : Adapter le système HITL au format JSON `sheet` et `confidence_score`

**Actions réalisées** :
- ✅ Mise à jour de `src/hitl_manager.py` :
  - Utilisation de `confidence_score` au lieu de `global_confidence`
  - Utilisation de `sheet` au lieu de `data`
  - Adaptation des règles de validation
- ✅ Mise à jour de `main.py` :
  - Affichage adapté au nouveau format
  - Gestion des résultats validés

**Critères de validation** :
- Confiance < 0.6 → Validation obligatoire
- Confiance > 0.9 → Auto-validation
- Champs critiques manquants → Validation obligatoire
- Plus de 3 champs manquants → Validation obligatoire

---

### **Étape 7 : Interface Interactive pour Questions**

**Objectif** : Permettre la saisie interactive de questions en temps réel

**Actions réalisées** :
- ✅ Modification de `main.py` :
  - Remplacement des questions hardcodées par une boucle interactive
  - Commandes spéciales : `quit`, `exit`, `help`
  - Affichage des réponses avec sources et confiance
- ✅ Amélioration de `run_agent.py` :
  - Menu interactif amélioré
  - Mode questions avec possibilité de revenir au menu

**Fonctionnalités** :
- Saisie de questions en temps réel
- Affichage des réponses avec score de confiance
- Liste des sources utilisées
- Avertissement si validation nécessaire

---

### **Étape 8 : HITL Interactif pour Extraction**

**Objectif** : Rendre le système HITL vraiment interactif pour la validation

**Actions réalisées** :
- ✅ Implémentation de `_ask_correction()` dans `src/hitl_manager.py` :
  - Options : `o` (accepter), `n` (rejeter), `c` (corriger), `s` (skip)
  - Affichage de la valeur, du champ, et de la confiance
  - Saisie de nouvelles valeurs avec conversion automatique de type
- ✅ Implémentation de `_ask_missing_field()` :
  - Affichage des alias du champ pour aider l'utilisateur
  - Conversion automatique selon le type (int, float, year)
  - Validation des formats (ex: année entre 1900-2100)
- ✅ Implémentation de `validate_qa_response()` :
  - Validation interactive des réponses Q&A
  - Options : accepter, rejeter, corriger, skip
  - Enregistrement des corrections en mémoire

**Interactions disponibles** :
- Validation des champs extraits
- Ajout manuel de champs manquants
- Correction de valeurs incorrectes
- Validation des réponses Q&A

---

### **Étape 9 : Résolution des Problèmes d'Import**

**Objectif** : Corriger les erreurs d'import et de compatibilité

**Actions réalisées** :
- ✅ Correction des imports LangChain :
  - `from langchain.schema import Document` → `from langchain_core.documents import Document`
- ✅ Résolution des conflits de versions :
  - Mise à jour de `requirements.txt` avec versions compatibles
  - Installation de `langchain-openai`, `langchain-text-splitters`
- ✅ Correction des chemins :
  - Utilisation de `Path` objects au lieu de strings
  - Gestion des chemins relatifs dans les tests
- ✅ Gestion de l'encodage UTF-8 pour Windows

**Fichiers corrigés** :
- `src/document_processor.py`
- `src/extractor.py`
- `src/rag_engine.py`
- `requirements.txt`

---

### **Étape 10 : Amélioration du Flux HITL Q&A**

**Objectif** : Corriger les problèmes d'interaction dans la validation Q&A

**Actions réalisées** :
- ✅ Suppression de la duplication d'affichage
- ✅ Ajout de `sys.stdout.flush()` pour forcer l'affichage
- ✅ Amélioration de la gestion des erreurs
- ✅ Simplification du flux d'affichage
- ✅ Création de `test_hitl_input.py` pour tester l'input

**Améliorations** :
- Affichage unique de la question et réponse
- Options clairement affichées avant l'input
- Gestion des interruptions (Ctrl+C)
- Validation de l'input (non vide)

---

## 🏗️ Architecture Technique

### **Composants Principaux**

#### 1. **Config (`src/config.py`)**
- Configuration centralisée
- Schéma d'extraction
- Paramètres RAG (chunk_size, top_k)
- Seuils de confiance
- Chemins des répertoires

#### 2. **DocumentProcessor (`src/document_processor.py`)**
- Extraction de texte depuis PDF
- Découpage en chunks avec overlap
- Métadonnées (source, type, page)

#### 3. **RAGEngine (`src/rag_engine.py`)**
- Indexation vectorielle (FAISS)
- Embeddings OpenAI (`text-embedding-3-small`)
- Recherche de similarité
- Génération avec contexte (GPT-4o)
- Sauvegarde/chargement de l'index

#### 4. **FinancialExtractor (`src/extractor.py`)**
- Extraction des 11 champs financiers
- Calcul du score de confiance global
- Détection des champs manquants
- Collecte d'informations additionnelles
- Format JSON structuré

#### 5. **QAEngine (`src/qa_engine.py`)**
- Réponses aux questions en langage naturel
- Évaluation de la confiance
- Recherche dans la mémoire historique
- Suggestions de questions

#### 6. **HITLManager (`src/hitl_manager.py`)**
- Décision de validation nécessaire
- Validation interactive des extractions
- Validation interactive des réponses Q&A
- Application des corrections

#### 7. **MemoryManager (`src/memory_manager.py`)**
- Stockage des corrections d'extraction
- Stockage des corrections Q&A
- Recherche dans l'historique
- Statistiques de corrections

---

## 📊 Pipeline Complet

### **1. Extraction Financière**

```
Documents PDF (data/)
    ↓
DocumentProcessor
    ↓
RAGEngine (Indexation)
    ↓
FinancialExtractor
    ↓
Résultat JSON (outputs/)
    ↓
HITLManager (Validation si nécessaire)
    ↓
Résultat Validé
```

### **2. Questions/Réponses**

```
Question utilisateur
    ↓
MemoryManager (Recherche historique)
    ↓
QAEngine (Génération réponse)
    ↓
HITLManager (Validation si confiance faible)
    ↓
Réponse validée
```

---

## 🔧 Configuration

### **Paramètres Clés** (`src/config.py`)

```python
# LLM
llm_model = "gpt-4o"
llm_temperature = 0
llm_max_tokens = 4000

# RAG
chunk_size = 1000
chunk_overlap = 200
top_k_retrieval = 5
embedding_model = "text-embedding-3-small"

# Extraction
confidence_threshold = 0.7
missing_field_threshold = 3

# HITL
auto_validate_above = 0.9
require_validation_below = 0.6
```

---

## 📝 Utilisation

### **1. Extraction Simple**

```bash
python src/extractor.py
```

### **2. Pipeline Complet**

```bash
python main.py
```

### **3. Interface Interactive**

```bash
python run_agent.py
```

---

## 🎯 Fonctionnalités Implémentées

### ✅ **Extraction**
- [x] Extraction des 11 champs financiers
- [x] Calcul du score de confiance
- [x] Détection des champs manquants
- [x] Format JSON structuré
- [x] Sauvegarde automatique

### ✅ **RAG**
- [x] Indexation vectorielle FAISS
- [x] Recherche de similarité
- [x] Génération avec contexte
- [x] Persistance de l'index

### ✅ **Q&A**
- [x] Réponses en langage naturel
- [x] Évaluation de confiance
- [x] Recherche dans l'historique
- [x] Affichage des sources

### ✅ **HITL**
- [x] Validation interactive extraction
- [x] Validation interactive Q&A
- [x] Correction manuelle des valeurs
- [x] Ajout de champs manquants

### ✅ **Mémoire**
- [x] Stockage des corrections
- [x] Historique Q&A
- [x] Statistiques
- [x] Recherche similaire

---

## 🚀 Prochaines Étapes Possibles

### **Améliorations Techniques**
- [ ] Interface web (Streamlit/Gradio)
- [ ] API REST (FastAPI)
- [ ] Support multi-langues
- [ ] Extraction de tableaux complexes
- [ ] Amélioration de la détection de champs

### **Fonctionnalités Métier**
- [ ] Calculs de ratios financiers
- [ ] Comparaisons temporelles
- [ ] Alertes sur anomalies
- [ ] Export Excel/CSV
- [ ] Rapports automatiques

### **Optimisations**
- [ ] Cache des embeddings
- [ ] Parallélisation de l'extraction
- [ ] Optimisation des prompts
- [ ] Fine-tuning du modèle

---

## 📚 Dépendances Principales

```
langchain==0.1.0
langchain-openai==0.0.5
langchain-community==0.0.20
openai==1.12.0
faiss-cpu==1.7.4
PyPDF2==3.0.1
python-dotenv==1.0.0
```

---

## 📅 Chronologie

1. **Migration OpenAI** → Remplacement Anthropic par OpenAI
2. **Refactorisation** → Architecture Python modulaire
3. **Schéma Extraction** → Définition des 11 champs
4. **Format JSON** → Structure de sortie standardisée
5. **Tests Extraction** → Validation sur fichiers réels
6. **HITL Extraction** → Validation interactive
7. **Q&A Interactif** → Saisie de questions en temps réel
8. **HITL Q&A** → Validation des réponses
9. **Résolution Bugs** → Corrections imports et compatibilité
10. **Amélioration UX** → Flux d'interaction optimisé

---

## 🎓 Concepts Utilisés

- **RAG (Retrieval-Augmented Generation)** : Recherche + Génération
- **Vector Store (FAISS)** : Indexation vectorielle
- **Embeddings** : Représentation sémantique
- **HITL (Human-In-The-Loop)** : Validation humaine
- **Confidence Scoring** : Évaluation de la fiabilité
- **Memory Management** : Apprentissage des corrections
- **Prompt Engineering** : Optimisation des prompts LLM

---

## 📖 Documentation des Fichiers

- **`main.py`** : Point d'entrée, orchestration complète
- **`run_agent.py`** : Interface interactive avec menu
- **`src/extractor.py`** : Extraction + test automatique
- **`src/rag_engine.py`** : Moteur RAG complet
- **`src/hitl_manager.py`** : Validation interactive
- **`src/config.py`** : Configuration centralisée

---

**Date de création** : 2024-12-13  
**Dernière mise à jour** : 2024-12-13  
**Version** : 1.0

