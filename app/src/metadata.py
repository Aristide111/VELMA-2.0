from datetime import datetime
import html
import re
import uuid

from src.archi import path_page

# Gestion des métadonnées au format DublinCore, remplies par l'utilisateur.

# Dictionnaire de base pour entrer les métadonnées. 
# On remplit de base le type et le format étant donné que ça n'est pas modifiable

DUBLIN_CORE_METADATA = {
    "title": "",
    "creator": "",
    "subject": "",
    "description": "",
    "publisher": "",
    "contributor": "",
    "date": "",
    "type": "Text",
    "format": "text/markdown",
    "identifier": "",
    "source": "",
    "language": "fr",
    "relation": "",
    "coverage": "",
    "rights": "",
}

# Texte affiché dans l'application gradio pour la saisie.
# On ajoute une traduction des champs classique + des recommandation pour titre et identifier qui ont une fonctionnalité.
# d'auto-incrémentation.


DUBLIN_CORE_LABELS = {
    "title": "Title (Titre) Le titre sera appliqué à l'ensemble des documents, chaque document aura un numéro attribué. Exemple : Titre 01, Titre 02 etc.",
    "creator": "Creator (Auteur)",
    "subject": "Subject (Sujet)",
    "description": "Description (Description)",
    "publisher": "Publisher (Éditeur)",
    "contributor": "Contributor (Contributeur)",
    "date": "Date (Date) Si le champ est laissé vide, la date est appliquée automatiquement ! )",
    "type": "Type (Type)",
    "format": "Format (Format)",
    "identifier": "Identifier (Identifiant) Comme pour le titre, un identifiant est généré automatiquement ( exemple : 12301, 12302, 12303 etc. ) ! Si le champ est laissé vide, un identifiant est généré aléatoirement.)",
    "source": "Source (Source)",
    "language": "Language (Langue)",
    "relation": "Relation (Relation)",
    "coverage": "Coverage (Couverture)",
    "rights": "Rights (Droits)",
}

# Balises de repérage  pour le bloc d'en-tête (head) des pages.

_BLOCK_START = "<!-- début des métadonnées -->"
_BLOCK_END = "<!-- fin des métadonnées -->"
_HEADER_RE = re.compile(re.escape(_BLOCK_START) + r".*?" + re.escape(_BLOCK_END) + r"\n*", re.DOTALL)

## Récupère le nom (stem) et le numéro de page à partir du nom du fichier 
# (ex: "pdf_stem_page_12.md" -> stem="pdf_stem", idx=12)
_FILENAME_RE = re.compile(r"^(?P<stem>.+)_page_(?P<idx>\d+)\.md$")

# Espace de noms pour l'uuid5 : garantit qu'une même page garde toujours le même identifiant d'une exécution à l'autre.
_NAMESPACE = uuid.uuid5(uuid.NAMESPACE_DNS, "fondation-ecologie-politique.org")

# Avertissement affiché sur chaque page concernant les erreurs posisbles issues du traitement par IA.

WARNING = {
    "fr": (
        "L'OCR, l'extraction des images, la mise en page ainsi que la reconnaissance "
        "d'entités nommées de ces documents ont été générés automatiquement via l'API "
        "Albert. Il est donc possible que des erreurs de transcription, des "
        "hallucinations et des biais subsistent. Nous attirons votre attention sur le risque "
        "de biais de sous-représentation concernant la reconnaissance d'entités nommées : "
        "si un terme est absent, il est possible que le logiciel ne l'ait pas détecté. "
        "Ces ressources sont destinées à un usage scientifique contrôlé ; nous vous "
        "invitons à vérifier vos sources avant toute utilisation."
    ),
    "en": (
        "The OCR, image extraction, page layout, and named entity recognition applied to "
        "these documents were automatically generated using the Albert API. As a "
        "result, transcription errors, hallucinations, and biases may persist. We draw your "
        "attention to the risk of under-representation bias regarding named entity recognition: "
        "if a term is absent, it is possible that the software failed to detect it. "
        "These resources are intended for use in a controlled scientific setting; we "
        "invite you to verify your sources before relying on them."
    ),
}

# Mise à jour des métadonnées une fois celles-ci remplies.
def update_metadata(**values) -> None:
    for key, value in values.items():
        if key in DUBLIN_CORE_METADATA:
            DUBLIN_CORE_METADATA[key] = (value or "").strip()

# Construction du header des métadonnées à partir des données renseignées par l'utilisateur

def build_header(pdf_stem: str, page_index: int, seq: int = 1) -> str:
    
    base_title = DUBLIN_CORE_METADATA["title"]
    base_identifier = DUBLIN_CORE_METADATA["identifier"]

    title = f"{base_title}{seq:02d}" if base_title else f"{pdf_stem} — Page {page_index + 1}"
    if base_identifier:
        identifier = f"{base_identifier}{seq:02d}"
    else:
        identifier = f"urn:uuid:{uuid.uuid5(_NAMESPACE, f'{pdf_stem}/page_{page_index}')}"
    date = DUBLIN_CORE_METADATA["date"] or datetime.now().strftime("%Y-%m-%d")

    lines = [_BLOCK_START, "<head>", f"  <title>{html.escape(title)}</title>"]
    for key, value in DUBLIN_CORE_METADATA.items():
        if key == "title":
            value = title
        elif key == "date":
            value = date
        elif key == "identifier":
            value = identifier
        value = html.escape(str(value)).replace("\n", " ")
        lines.append(f'  <meta name="DC.{key}" content="{value}">')
    lines.append(f'  <meta name="warning.fr" content="{html.escape(WARNING["fr"])}">')
    lines.append(f'  <meta name="warning.en" content="{html.escape(WARNING["en"])}">')
    lines.append("</head>")
    lines.append(_BLOCK_END)
    return "\n".join(lines) + "\n\n"

# Affichage du message d'avertissement

def build_footer_warning() -> str:
    
    return f"""

<div style="margin-top: 40px; padding: 10px 15px; border: 1px solid #ffca28; border-radius: 6px; background-color: #fffde7; color: #5d4037; font-size: 0.82em; line-height: 1.4;">
  <strong> Avertissement / Warning :</strong><br>
  <em>FR:</em> {WARNING['fr']}<br>
  <em>EN:</em> {WARNING['en']}
</div>
"""

# Applique les métadonnées à tous les documents

def apply_metadata_to_all_docs() -> int:
    
    if not path_page.exists():
        return 0

    count = 0
    for seq, md_file in enumerate(sorted(path_page.rglob("*.md")), start=1):
        match = _FILENAME_RE.match(md_file.name)
        pdf_stem = match.group("stem") if match else md_file.stem
        page_index = int(match.group("idx")) if match else 0

        content = md_file.read_text(encoding="utf-8")
        new_header = build_header(pdf_stem, page_index, seq)
        if _HEADER_RE.search(content):
            content = _HEADER_RE.sub(new_header, content, count=1)
        else:
            content = new_header + content

        md_file.write_text(content, encoding="utf-8")
        count += 1

    return count