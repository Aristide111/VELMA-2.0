from pathlib import Path as p
import shutil
import subprocess
import webbrowser
import sys
import time
import zipfile
import gradio as gr

from src.archi import verify_site_folder, architecture, build_mkdocs_site, Input, path_site, path_docs, path_img, path_page
from src.ocr import OCR
from src.create_md import create_markdown_file
from src.nlp import extract_entities, graph
from src.metadata import update_metadata, apply_metadata_to_all_docs, DUBLIN_CORE_METADATA


# Fonctions éxecutées par Gradio, fichier de transition entre le back end et le front end

# Emplacement de sauvegarde de la datavisualisation

PATH_DATAVIZ_IMG = p("Site/docs/img/visualisation/frequence_entites.png")

# Suivi du processus du serveur MkDocs, pour éviter lancement de 2 site sur le même serveur

mkdocs_process = None

# Effacement de l'ancien site si préexistant

def clean_generated_content_only():
    
    if not path_site.exists():
        return

    if path_page.exists():
        shutil.rmtree(path_page)
    if path_img.exists():
        shutil.rmtree(path_img)

    index_md = path_docs / "index.md"
    viz_md = path_docs / "visualisation.md"

    if index_md.exists():
        index_md.unlink()
    if viz_md.exists():
        viz_md.unlink()

# Vérification de l'existence des sites et avertissement si c'est le cas

def check_existing_site(files):
    if not files:
        return (
            "Veuillez sélectionner au moins un fichier PDF.",
            gr.update(visible=False),
        )

    if path_site.exists():
        return (
            f"Attention : le dossier '{path_site.name}' contient déjà des données. "
            f"Voulez-vous réinitialiser les pages tout en conservant le squelette (logo, CSS) ?",
            gr.update(visible=True),
        )

    return run_ocr_and_build(files, clean_site=False)

# OCR et construction du site Web

def run_ocr_and_build(files, clean_site, progress=gr.Progress()):
    
    if not files:
        return (
            "Veuillez sélectionner au moins un fichier PDF.",
            gr.update(visible=False),
        )

    # Préparation
    progress(0.0, desc="Configuration des dossiers...")

    if clean_site:
        clean_generated_content_only()

    # Nettoyage et création du dossier Input
    progress(0.1, desc="Préparation des fichiers...")

    if Input.exists():
        shutil.rmtree(Input)

    Input.mkdir(parents=True, exist_ok=True)

    # Copie des fichiers PDF
    total_files = len(files)

    for i, file_obj in enumerate(files):
        file_path = p(file_obj.name)
        shutil.copy(file_path, Input / file_path.name)

        progress(
            0.1 + (0.1 * (i + 1) / total_files),
            desc=f"Copie du fichier {i + 1}/{total_files}, pour centraliser les données en vue du traitement général..."
        )

    # Création de l'arborescence
    progress(0.2, desc="Création de l'arborescence des dossiers...")
    architecture(Input)

    # OCR
    progress(0.25, desc="Exécution de l'OCR via l'API Albert...")

    results_ocr = OCR(Input)

    progress(0.75, desc="OCR terminé.")

    # Création des fichiers Markdown
    progress(0.80, desc="Génération des pages Markdown...")
    create_markdown_file(results_ocr)

    # Construction du site MkDocs
    progress(0.90, desc="Mise à jour de la navigation MkDocs...")
    build_mkdocs_site(results_ocr)

    # Fin
    progress(1.0, desc="Terminé !")

    return (
        "OCR et génération MkDocs terminés avec succès ! Le squelette CSS/logo a été préservé.",
        gr.update(visible=False),
    )


# NER et datavisualisation

def run_ner_pipeline(progress=gr.Progress()):
    
    if not path_site.exists():
        return (
            "Aucun site généré pour le moment. Lancez d'abord la transformation.",
            None,
        )

    # Extraction des entités
    progress(0.0, desc="Préparation de l'extraction des entités...")

    progress(0.1, desc="Extraction des entités avec Albert...")
    extracted_data = extract_entities()

    progress(0.8, desc="Génération du graphique de datavisualisation...")
    graph(extracted_data)

    progress(1.0, desc="Extraction NER terminée !")

    dataviz_export = (
        str(PATH_DATAVIZ_IMG)
        if PATH_DATAVIZ_IMG.exists()
        else None
    )

    return (
        "Extraction des entités et génération de la datavisualisation réussies !",
        dataviz_export,
    )


# Démarre un serveur local MkDocs et ouvre automatiquement le navigateur web.
# en vérifiant si le port 8000 est déjà utilisé
def deploy_site():
    
    global mkdocs_process

    if not path_site.exists():
        return "Impossible de déployer : le dossier 'Site' n'existe pas."

    
    if mkdocs_process is not None and mkdocs_process.poll() is None:
        webbrowser.open("http://127.0.0.1:8000")
        return "Le site est déjà en cours d'exécution à l'adresse http://127.0.0.1:8000"

    try:
        mkdocs_process = subprocess.Popen(
            [sys.executable, "-m", "mkdocs", "serve", "-a", "127.0.0.1:8000"],
            cwd=str(path_site),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True
        )

        time.sleep(2)

        if mkdocs_process.poll() is not None:
            stderr_out = mkdocs_process.stderr.read()
            return f"Échec du démarrage de MkDocs : {stderr_out}"

        webbrowser.open("http://127.0.0.1:8000")
        return "Serveur MkDocs démarré avec succès sur http://127.0.0.1:8000 !"

    except Exception as e:
        return f"Échec du démarrage de MkDocs : {str(e)}"

# Compression en ZIP du site pour téléchargement

def save_website_archive():
    
    if not path_site.exists():
        return None, "Aucun site généré à archiver."

    zip_path = p("Site_Export.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for file in path_site.rglob("*"):
            zip_file.write(file, file.relative_to(path_site))

    return str(zip_path), "Archive ZIP du site générée avec succès."

#Enregistrement des dans DUBLIN_CORE_METADATA et mise à jour des en-têtes
def save_and_apply_metadata(*values):
    
    keys = list(DUBLIN_CORE_METADATA.keys())
    update_metadata(**dict(zip(keys, values)))

    nb_updated = apply_metadata_to_all_docs()
    if nb_updated:
        return f"Métadonnées enregistrées et appliquées à {nb_updated} page(s) Markdown existante(s)."
    return "Métadonnées enregistrées. Elles seront appliquées lors de la prochaine génération (TRANSFORM)."