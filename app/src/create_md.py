from pathlib import Path as p
import datauri
import re

from src.archi import path_page, path_img
from src.metadata import build_header, build_footer_warning



# Création des pages markdowns des sites webs, en insérant les résultats de l'OCR, les images extraites
# et les liens entre ces deux éléments.

# Sauvegarde de l'image extraite de l'OCR avec datauri.
# Création d'un identifiant à cette image pour pouvoir la lier au document Markdown.
# Correctif sur le nom pour conserver uniquement des png.

def save_image(image, folder_stem, page_index):
    # décodage des données de l'image base 64 avec datauri
    parsed = datauri.parse(image.image_base64)

    p_img_dir = path_img / folder_stem / f"page_{page_index}"
    p_img_dir.mkdir(parents=True, exist_ok=True)

    # Nettoyage de l'extension initiale pour garantir une extension unique en .png avec une regex qui permet de chercher les éléments qui finissent par .jpg jpeg ou png et contraint le .png
    clean_id = re.sub(r"\.(jpeg|jpg|png)$", "", image.id, flags=re.IGNORECASE)
    p_img = p_img_dir / f"{clean_id}.png"
    # écriture des données
    with p_img.open("wb") as f:
        f.write(parsed.data)

# Correction des liens d'images générés automatiquement par l'API de mistral pour les faire correspondre à ceux définis plus haut.

def _replace_image_links(content, pdf_stem, page_index):

    def replace_path(match):
        alt_text = match.group(1) # utilisation de match pour sélectionner uniquement la partie image et la partie texte respectivement
        img_file = match.group(2)
        clean_img = re.sub(r"\.(jpeg|jpg|png)$", "", img_file, flags=re.IGNORECASE)
        # reconstruit un chemin viable vers le stockage d'image
        return f"![{alt_text}](../../img/{pdf_stem}/page_{page_index}/{clean_img}.png)"

    return re.sub(r"!\[(.*?)\]\((.*?)\)", replace_path, content)

# Crée chaque page Markdown avec la division page par page du document.
#  Ajoute les images, la navigation et l'en-tête de métadonnées Dublin Core.
# Ajout de l'encadré d'avertissement.

def create_markdown_file(result_OCR):
    # compteur pour compter les pages des pdf traités
    seq = 0
    # récupération des données ocr et la liste des pages pour chaque pdf
    for pdf_stem, data in result_OCR.items():
        ocr_response = data["ocr"]
        pages = ocr_response.pages
        nb_pages = len(pages)

        for page_index, page in enumerate(pages):
            # parcours chaque page du du pdf
            # ajout de +1 pour éviter page 0
            # création du fichier md et du dossier si non existant
            seq += 1
            output_filename = f"{pdf_stem}_page_{page_index}.md"
            p_md = path_page / pdf_stem / output_filename
            p_md.parent.mkdir(parents=True, exist_ok=True)

            # récupération du md généré
            content = page.markdown
            # correspondance des liens images pour qu'ils redirigent bien vers les images designées
            if content:
                content = _replace_image_links(content, pdf_stem, page_index)
        # écriture du header de chaque page
            with p_md.open("wt", encoding="utf-8") as f:
                f.write(build_header(pdf_stem, page_index, seq))
        # écriture du contenu, ou notification si la page est vide
                if content:
                    f.write(content)
                else:
                    f.write(f"# {pdf_stem} — page {page_index + 1}/{nb_pages}\n\n[Page vide ou non décodée, merci de vous référer à l'original]")
        # sauvegarde des images
                for image in page.images:
                    save_image(image, pdf_stem, page_index)
        # mise en page enre contenus et liens, navigation pages suivantes et précédentes et liens de navigation
                f.write("\n\n---\n\n")
                nav_links = []
                if page_index > 0:
                    nav_links.append(f"[Page précédente]({pdf_stem}_page_{page_index - 1}.md)")
                if page_index < nb_pages - 1:
                    nav_links.append(f"[Page suivante ]({pdf_stem}_page_{page_index + 1}.md)")
                if nav_links:
                    f.write(" · ".join(nav_links) + "\n")

                f.write(build_footer_warning())