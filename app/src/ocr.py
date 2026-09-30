from tqdm import tqdm
from pathlib import Path as p
import os
from dotenv import load_dotenv
from openai import OpenAI
import time
import base64
import io
import pypdfium2 as pdfium

# Chargement de la clef d'api depuis le .env (ALBERT_API_KEY)
load_dotenv()
api_key = os.environ["ALBERT_API_KEY"]

# Client OpenAI albert API
client = OpenAI(
    base_url="https://albert.api.etalab.gouv.fr/v1",
    api_key=api_key,
)

class OcrPage:
    def __init__(self, markdown_text):
        self.markdown = markdown_text
        self.images = [] 

class OcrResponse:
    def __init__(self, pages):
        self.pages = pages

def OCR(folder):
    result = {}
    pdf_files = list(folder.glob("*.pdf")) 
    for file in tqdm(pdf_files, desc="Traitement OCR des PDF via Albert API..."):
        try:
            pdf_data = file.read_bytes()
            pdf = pdfium.PdfDocument(pdf_data)
            pages_list = []
            
            for page_index, page in enumerate(pdf):
              
                pil_image = page.render(scale=2.77).to_pil()
                buffer = io.BytesIO()
                pil_image.save(buffer, format="PNG")
                image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
                
                response = client.chat.completions.create(
                    model="openweight-ocr",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "Extrait tout le texte de ce document de manière fidèle et restitue-le au format Markdown."},
                                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}}
                            ],
                        }
                    ],
                    max_tokens=4096,
                    temperature=0.1,
                )
                
                page_text = response.choices[0].message.content
                pages_list.append(OcrPage(page_text))
                time.sleep(0.5)

            result[file.stem] = {
                "ocr": OcrResponse(pages_list),  
                "update": "no",       
            }
            print(f"{file.name} : traité avec succès via Albert API")

        except Exception as e:
            print(f"Erreur lors du traitement de {file.name} : {e}")

    return result