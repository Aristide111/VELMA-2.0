import os
import re
import json
import time
import random
from pathlib import Path as p
from tqdm import tqdm
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI

from src.archi import path_site, path_docs, path_img, path_page

# utilisation du client OPENAI albert API
load_dotenv()
api_key = os.environ["ALBERT_API_KEY"]
client = OpenAI(
    base_url="https://albert.api.etalab.gouv.fr/v1",
    api_key=api_key,
)

tools = [
    {
        "type": "function",
        "function": {
            "name": "extract_entities",
            "description": "Extrait les entités nommées du texte.",
            "parameters": {
                "type": "object",
                "properties": {
                    "entities": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "word": {"type": "string"},
                                "type": {"type": "string", "enum": ["PERS", "ORG", "EVENT", "PLACE"]},
                                "document_name": {"type": "string"}
                            },
                            "required": ["word", "type", "document_name"]
                        }
                    }
                },
                "required": ["entities"]
            }
        }
    }
]


# Extraction d'entité nommée sur le corpus via le formulaire d'interrogation de l'API
# On applique cette opération sur tout le corpus de document markdown
# On vérifie qu'ils existent bien
# On utilise des délais et des retry pour éviter un bug de limitation de ressource de l'API


# Evite l'erreur 429 en ajoutant un délai exponentiel (backoff). 
# Ce bloc n'est plus nécessaire, il c'est avéré que l'erreur 429 était produite par la limitation de l'API gratuite de Mistral depuis l'été 2026, mais il peut être utile en cas de dépassement des quotats 

def call_with_retry(func, max_retries=5):
    
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if "429" not in str(e) and "rate_limited" not in str(e):
                raise  
            if attempt == max_retries - 1:
                raise
            wait = (2 ** attempt) + random.uniform(0, 1)
            print(f"Débit limité (rate limit), nouvelle tentative dans {wait:.1f}s (essai {attempt + 1}/{max_retries})")
            time.sleep(wait)



def extract_entities():
    
    path_pages = p("Site/docs/page")
    
    corpus = list(path_pages.rglob("*.md")) if path_pages.exists() else []

    if not corpus:
        print("Aucun fichier Markdown trouvé dans Site/docs/page.")
        return []

    results = []

    for texte in tqdm(corpus, desc="Extraction des entités nommées..."):
        
        try:
            with open(p(texte), "r", encoding="utf-8") as f:
                document_content = f.read()
        except FileNotFoundError:
            print(f"\n[Avertissement] Le fichier {texte} n'existe plus, passage au suivant.")
            continue
        except Exception as e:
            print(f"\n[Erreur] Impossible de lire {texte} : {e}")
            continue

        # Récupération d'un modèle text-generation disponible sur Albert API
        try:
            models = client.models.list().data
            text_models = [m.id for m in models if m.type == "text-generation"]
            model_to_use = text_models[0] if text_models else "albert-base"
        except Exception:
            model_to_use = "albert-base"

        # Remplacement de tool_choice="any" par tool_choice="required" (compatible OpenAI / vLLM)
        response = call_with_retry(lambda: client.chat.completions.create(
            model=model_to_use,
            messages=[
                {
                    "role": "user",
                    "content": f"Extrait les entités nommées du document suivant au format JSON via l'outil fourni.\n\nDocument : {texte.name}\nContenu : {document_content}"
                }
            ],
            tools=tools,
            tool_choice="required"  
        ))

        message = response.choices[0].message
        if message.tool_calls:
            tool_call = message.tool_calls[0]
            extracted_data = json.loads(tool_call.function.arguments)
            results.append({
                "file": texte.name,
                "entities": extracted_data.get("entities", [])
            })

        time.sleep(2)  

    return results

# Création des datavisualisations et de la page de synthèse de la NLP

# Dictionnaires de correspondance pour le graph et couleurs

TYPE_LABELS = {
    "PERS": "Personnes",
    "ORG": "Organisations",
    "EVENT": "Événements",
    "PLACE": "Lieux",
}
TYPE_COLORS = {
    "PERS": "#36AD58",
    "ORG": "#3B3D7B",
    "EVENT": "#ee8a76",
    "PLACE": "#ccda56",
}

# Extraction du nom du pdf et de l'index de page correspondant
def _parse_location(filename):
    
    match = re.match(r"^(.*)_page_(\d+)\.md$", filename)
    if not match:
        return None, None
    return match.group(1), int(match.group(2))


# Génération de la datavisualisation en prenant les 30 entités pour éviter un graphique illisible
# Crée la page Markdown qui liste les occurences avec les liens

def graph(detection):
   
    rows = []
    for doc in detection:
        file_name = doc.get("file")
        for entity in doc.get("entities", []):
            rows.append({
                "word": entity.get("word"),
                "type": entity.get("type"),
                "file": file_name,
            })

    df_entities = pd.DataFrame(rows)
    if df_entities.empty:
        print("Aucune entité détectée.")
        return

    # Nettoyage des lignes comportant des valeurs nulles ou des chaînes vides
    df_entities = df_entities.dropna(subset=['word', 'type'])
    df_entities = df_entities[df_entities['word'].str.strip() != ""]

    if df_entities.empty:
        print("Aucune entité exploitable après nettoyage.")
        return

  # comptage du nombre d'entités, du total, du type majoritairement associé (permet de prendre en compte en cas de termes polysémiques) et enfin le plus fréquent pour la limitation à 30
    counts = df_entities.groupby(['word', 'type']).size().reset_index(name='count')
    totals = df_entities.groupby('word').size().reset_index(name='total')
    dominant = counts.loc[counts.groupby('word')['count'].idxmax(), ['word', 'type']]
    merged = totals.merge(dominant, on='word').sort_values('total', ascending=False).head(30)
# attribution de couleurs par type et couleur grise si type inconnu
    colors = merged['type'].map(TYPE_COLORS).fillna("#888888")

    plt.figure(figsize=(15, 10))
    plt.bar(merged['word'], merged['total'], color=colors)
    plt.xticks(rotation=60, ha='right')
    plt.xlabel("Entité")
    plt.ylabel("Nombre d'occurrences")
    plt.title("Entités les plus récurentes")
# rectangle coloré pour la légende
    legend_elements = [
        Patch(facecolor=TYPE_COLORS[t], label=TYPE_LABELS[t])
        for t in TYPE_LABELS if t in merged['type'].values
    ]
    plt.legend(handles=legend_elements, title="Type d'entité")
    plt.tight_layout()

    # Sauvegarde de l'image du graphique
    path_viz_img = path_img / "visualisation"
    path_viz_img.mkdir(parents=True, exist_ok=True)
    img_path = path_viz_img / "frequence_entites.png"
    plt.savefig(img_path, format="png")
    plt.close()
    print(f"Graphique enregistré sous '{img_path}'")

    # Génération de la page Markdown de visualisation
    
    lines = [
        "# Visualisation des entités nommées\n",
        "![Fréquence des entités](img/visualisation/frequence_entites.png)\n",
        "## Détail des occurrences\n",
        "| Entité | Type | Emplacement |",
        "|---|---|---|",
    ]
# tri par ordre alphabétique pour rendr eplus visible 
    df_sorted = df_entities.sort_values(['type', 'word'])
    for _, row in df_sorted.iterrows():
        pdf_stem, page_index = _parse_location(row['file'])
    # si l'entité est viable, on ajoute un lien vers son origine, sinon seulement son nom
        if pdf_stem is not None:
            link = f"page/{pdf_stem}/{row['file']}"
            emplacement = f"[{pdf_stem} — page {page_index + 1}]({link})"
        else:
            emplacement = row['file']

        type_label = TYPE_LABELS.get(row['type'], row['type'])
        lines.append(f"| {row['word']} | {type_label} | {emplacement} |")

    path_viz_md = path_docs / "visualisation.md"
    with path_viz_md.open("wt", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"Page de visualisation créée : '{path_viz_md}'")