# VELMA 2.0

# Français

## Présentation

VELMA 2.0 Visualization, Extraction, Linguistic analysis and Metadata for Archives documents est une application destinée à transformer des fonds de presse numérisés en contenus web statiques, structurés et exploitables.

Il s'agit de la V2 de l'application basé sur l'API MISTRAL OCR

Cette application à été crée pour la Maison de la Fondation de l'Ecologie Politique afin de permettre la mise en valeur de leurs fonds dans le cadre d'un stage de fin d'études du master TNAH de l'Ecole Nationale des Chartes.

Elle a pour objectif de faciliter le traitement des collections de presse historique en automatisant plusieurs fonctionnalités, dont l'OCR, l'extraction d'images, la recherche plein texte, la reconnaissance d'entités nommées et l'ajout de métadonnées au format Dublin Core.

VELMA 2.0 Visualization, Extraction, Linguistic analysis and Metadata for Archives documents combine des méthodes de vision par ordinateur et l'API ALBERT pour le traitement des documents et l'extraction de leur contenu textuel. Les sites web créés sont statiques et utilisent la technologie MkDocs.

L'objectif est de proposer une première lecture de grands volumes de documents.

Les résultats produits ne se substituent cependant pas à une véritable recherche scientifique et fournissent uniquement un aperçu du contenu des fonds soumis.

> Attention : En raison de l'utilisation d'une API externe, ne soumettez aucun document contenant des données à caractère personnel ou provenant de collections protégées par le droit d'auteur.

## Fonctionnement du pipeline

1. **Chargement et prétraitement :** Import des documents au format PDF.

2. **Analyse de la mise en page et extraction du texte :** Extraction des images et OCR du texte via l'API ALBERT. Transformation des résultats en un site MkDocs permettant notamment une recherche plein texte.

3. **Analyse linguistique :** Traitement du texte extrait à l'aide de méthodes de traitement automatique du langage naturel (NLP), reconnaissance d'entités nommées et création d'une datavisualisation des 30 termes les plus fréquents.

4. **Extraction des métadonnées :** Possibilité d'ajouter des métadonnées descriptives au format Dublin Core.

5. **Export des données :** Le site produit peut être exporté sous la forme d'un dossier ZIP. Les datavisualisations peuvent être exportées au format PNG.

---

## Architecture du projet

```text
.
├── app
│   ├── PDF # Dossier ou placer vos PDF
│   ├── run.py # Fichier de lancement de l'application
│   ├── .env # Emplacement de l'API KEY ! A ne jamais communiquer !
│   ├── Site # Site généré
│   │   ├── docs 
│   │   │   ├── assets
│   │   │   │   └── logo.jpg # logo du site
│   │   │   ├── img # images extraites
│   │   │   ├── index.md # index de navigation
│   │   │   ├── page # texte extrait
│   │   │   └── stylesheet
│   │   │       └── custom.css # feuille de style CSS
│   │   └── mkdocs.yml # fichier de configuration
│   └── src
│       ├── archi.py # constitution de l'architecture
│       ├── create_md.py # création des pages du site
│       ├── gradio_app.py # application gradio
│       ├── __init__.py
│       ├── metadata.py # formulaire des métadonnées
│       ├── nlp.py # Reconnaissance d'entité nommée
│       ├── ocr.py # OCR et extraction d'image
│       └── pipeline.py # lien entre le backend et le front end
├── readme.md # vous êtes acutellement ici :) 
└── requirements.txt # liste des dépendances nécessaires
```

---

# Installation

## Prérequis

VELMA 2.0 Visualization, Extraction, Linguistic analysis and Metadata for Archives documents nécessite :

* **Python 3.10 ou supérieur**
* Une connexion Internet pour accéder à l'API ALBERT
* Une **clé API Mistral** configurée via `https://admin.mistral.ai/organization/api-keys` et renseigné dans le fichier `.env`

## Windows — Invite de commandes (`cmd`)

### 1. Se rendre dans le dossier du projet

```cmd
cd chemin\vers\VELMA 2.0 Visualization, Extraction, Linguistic analysis and Metadata for Archives documents
```

### 2. Créer un environnement virtuel

```cmd
python -m venv .venv
```

### 3. Activer l'environnement virtuel

```cmd
.venv\Scripts\activate
```

### 4. Installer les dépendances

```cmd
pip install -r requirements.txt
```

---

# Lancement de VELMA 2.0 Visualization, Extraction, Linguistic analysis and Metadata for Archives documents

Une fois l'environnement virtuel activé et les dépendances installées, lancer l'application avec :

```cmd
python run.py
```

L'interface de l'application est alors disponible localement via le serveur **Gradio**, généralement à l'adresse :

```text
http://127.0.0.1:7860
```

Cette adresse peut également être affichée directement dans le terminal lors du lancement de l'application.

---


# VELMA 2.0 Visualization, Extraction, Linguistic analysis and Metadata for Archives documents : 

---

# English

## Overview

VELMA 2.0 Visualization, Extraction, Linguistic analysis and Metadata for Archives documents is an application designed to transform digitized press collections into static, structured, and usable web content.

Its goal is to facilitate the processing of historical press collections by automating several features, including OCR, image extraction, full-text search, named entity recognition, and the addition of Dublin Core metadata.

VELMA 2.0 Visualization, Extraction, Linguistic analysis and Metadata for Archives documents combines computer vision methods and the ALBERT API for document processing and text content extraction. The websites created are static and use MkDocs technology.

The objective is to offer a preliminary reading of large volumes of documents.

However, the results produced do not substitute for genuine scientific research and only provide an overview of the contents of the submitted collections.

> Warning: Due to the use of an external API, do not submit any documents containing personal data or originating from copyright-protected collections.

---

## Pipeline Workflow

1. **Loading and preprocessing:** Import of documents in PDF format.
2. **Layout analysis and text extraction:** Image extraction and text OCR via the ALBERT API. Transformation of results into an MkDocs site allowing full-text search, among other features.
3. **Linguistic analysis:** Processing of the extracted text using Natural Language Processing (NLP) methods, named entity recognition, and creation of a data visualization of the 30 most frequent terms.
4. **Metadata extraction:** Ability to add descriptive metadata in Dublin Core format.
5. **Data export:** The generated site can be exported as a ZIP folder. Data visualizations can be exported in PNG format.

---

## Project Architecture

```text
.
├── app
│   ├── PDF # Folder where you place your PDFs
│   ├── run.py # Application launch file
│   ├── Site # Generated site
│   │   ├── docs 
│   │   │   ├── assets
│   │   │   │   └── logo.jpg # site logo
│   │   │   ├── img # extracted images
│   │   │   ├── index.md # navigation index
│   │   │   ├── page # extracted text
│   │   │   └── stylesheet
│   │   │       └── custom.css # CSS stylesheet
│   │   └── mkdocs.yml # configuration file
│   └── src
│       ├── archi.py # architecture construction
│       ├── create_md.py # site page creation
│       ├── gradio_app.py # gradio application
│       ├── __init__.py
│       ├── metadata.py # metadata form
│       ├── nlp.py # Named Entity Recognition
│       ├── ocr.py # OCR and image extraction
│       └── pipeline.py # link between backend and frontend
├── readme.md # you are currently here :) 
└── requirements.txt # list of necessary dependencies

```

---

# Installation

## Prerequisites

VELMA 2.0 Visualization, Extraction, Linguistic analysis and Metadata for Archives documents requires:

* **Python 3.10 or higher**
* An Internet connection to access the ALBERT API
* A **Mistral API key** configured via `[https://admin.mistral.ai/organization/api-keys](https://admin.mistral.ai/organization/api-keys)` and entered in the `.env` file

## Windows — Command Prompt (`cmd`)

### 1. Navigate to the project folder

```cmd
cd path\to\VELMA 2.0 2.0 Visualization, Extraction, Linguistic analysis and Metadata for Archives documents

```

### 2. Create a virtual environment

```cmd
python -m venv .venv

```

### 3. Activate the virtual environment

```cmd
.venv\Scripts\activate

```

### 4. Install dependencies

```cmd
pip install -r requirements.txt

```

---

# Launching VELMA 2.0 2.0 Visualization, Extraction, Linguistic analysis and Metadata for Archives documents

Once the virtual environment is activated and dependencies are installed, launch the application with:

```cmd
python run.py

```

The application interface is then available locally via the **Gradio** server, usually at:

```text
http://127.0.0.1:7860

```

This address can also be displayed directly in the terminal when launching the application.
