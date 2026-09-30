import shutil
from pathlib import Path as p
import yaml
from tqdm import tqdm

# Création générale de l'architecture au fil du pipeline 
# (définition de chemins généraux,  vérification de l'existence de site précédent, 
# création des nouveaux sites, adaptation des chemins de navigation au cours des différents traitements).


# Dossier d'entrée des documents 
Input = p.cwd() / "PDF"

# Architecture du site produit par le pipeline

# éléments qui vont accueillir les images et les transcriptions

path_site = p.cwd() / "Site"
path_docs = path_site / "docs"
path_img = path_docs / "img"
path_page = path_docs / "page"

# éléments qui seront conservés à chaque nouveau site
path_assets = path_docs / "assets"
path_stylesheet = path_docs / "stylesheet"

# Configuration MkDocs + page de sommaire
path_index = path_docs / "index.md"
path_config = path_site / "mkdocs.yml"

# vérification de l'existence d'un site web préexistant pour suppression avec accord de l'opérateur

# si le site existe, question à l'utilisateur
def verify_site_folder():
    if path_site.exists():
        answer = (
            input("Un site web existe déjà. Le supprimer ? (oui/non) : ")
        )

        if answer in ("oui"):
            shutil.rmtree(path_site) # suppression récursive du site et de son contenu
            print("Site supprimé.")
        else:
            print("Le site web est conservé, sauvegarder le et relancer le processus.")

# Création des dossiers du site à partir du nom des pdfs du dossier PDF et conservation des configurations graphiques

def architecture(folder):
    path_assets.mkdir(parents=True, exist_ok=True) # Création des dossiers et leurs éléments parents si ils n'existent pas
    path_stylesheet.mkdir(parents=True, exist_ok=True)
    pdf_files = [f for f in folder.iterdir() if f.is_file() and f.suffix.lower() == ".pdf"] # parcours et liste le dossier, avec la vérification qu'ils sont bien des pdf, permet de prendre en charge les sous dossiers, normalise aussi le .pdf en minuscule en cas d'erreur sur le nom du fichier 
    total_files = len(pdf_files) # compte le résultats de pdf files pour estimer le % de réalisation avec tqdm

# Création des fichiers qui accueillerons les images et le texte pour chaque pdf
    for pdf in tqdm(
        pdf_files,
        desc="Création de l'arborescence du site...",
        total=total_files,
    ):
        (path_page / pdf.stem).mkdir(parents=True, exist_ok=True)
        (path_img / pdf.stem).mkdir(parents=True, exist_ok=True)

# Construction du site MkDocs avec les résultats de l'OCR et de l'extraction d'image.
# écriture des fichiers de configuration MkDocs et index avec les bons éléments graphiques.
# Ajout également des fonctionnalité de navigation : Une entrée de navigation + une ligne d'index par PDF traité
# Ajout du CSS, conservé à chaque génération

def build_mkdocs_site(result_OCR):
    # création des liens de navigation, l'index et la datavisualisation
    nav = [
        {"Accueil": "index.md"},
        {"Visualisation": "visualisation.md"},
    ]
    # création du sommaire à partir de la liste des documents, triés par ordre alphabétique
    # comptage du nombre de pages pour la navigation
    index_lines = ["# Sommaire\n"]
    for pdf_stem in sorted(result_OCR.keys()):
        nb_pages = len(result_OCR[pdf_stem]["ocr"].pages)
# lien de navigation pour chaque page de navigation, +1 pour ne pas commencer à 0 et autocomplétion avec stem et index.
        pages_nav = [
            {
                f"Page {page_index + 1}": f"page/{pdf_stem}/{pdf_stem}_page_{page_index}.md"
            }
            for page_index in range(nb_pages)
        ]
        nav.append({pdf_stem: pages_nav})
# chemin vers la première page du pdf, et nom transformé en lien vers la première page
        first_page = f"page/{pdf_stem}/{pdf_stem}_page_0.md"
        index_lines.append(f"- [{pdf_stem}]({first_page})")

# Dictionnaire de configuration qui reste le même à chaque fois, en étant écrit dans configuration.yml
    config = {
    "site_name": "Site",
    "docs_dir": "docs",
    "theme": {
        "name": "material",
        "features": ["navigation.footer"],
        "logo": "assets/logo.png",
    },
    "nav": nav,
}


   # réutilisation du du css à chaque génération

    css_file = path_stylesheet / "custom.css"
    if css_file.exists():
        config["extra_css"] = ["stylesheet/custom.css"]

# écriture ds fichiers d'index et de configuration : d'abord mkdocs yml avec le contenu config,puis index md avec la liste index_line

    with path_config.open("wt", encoding="utf-8") as f:
        yaml.dump(config, f, allow_unicode=True, sort_keys=False)

    with path_index.open("wt", encoding="utf-8") as f:
        f.write("\n".join(index_lines) + "\n")