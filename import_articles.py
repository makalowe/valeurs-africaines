import zipfile
import xml.etree.ElementTree as ET
import json
from pathlib import Path

def extract_text_from_docx(docx_path):
    try:
        with zipfile.ZipFile(docx_path) as z:
            xml_content = z.read('word/document.xml')
            root = ET.fromstring(xml_content)
            namespace = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
            texts = []
            for elem in root.findall('.//w:t', namespace):
                if elem.text:
                    texts.append(elem.text)
            return ''.join(texts)
    except Exception as e:
        return f'Error: {str(e)}'

# Mapping des fichiers
files = {
    'VA - Article - Dossier special Mali - 2026-05-04.docx': ('Guerres & Conflits', 'Mali', 'article'),
    'VA - Brief Union africaine et puissances exterieures - v1.docx': ('Diplomatie', 'Union africaine', 'brief'),
    'VA - Guerre informationnelle en Afrique - v2 pays influents.docx': ('Renseignement', 'Afrique', 'brief'),
    'VA - Kenya - Tech - Nairobi Pole Numerique - 2026-05-04.docx': ('Economie', 'Kenya', 'brief'),
    'VA - Langues africaines et souverainete narrative - v1.docx': ('Culture', 'Afrique', 'article'),
    'VA - Maroc - Lifestyle - Villes Creation Art de vivre - 2026-05-04.docx': ('Culture', 'Maroc', 'brief'),
}

extracted_docs = {}

for docx_file, (pillar, region, format_type) in files.items():
    text = extract_text_from_docx(docx_file)
    extracted_docs[docx_file] = {
        'pillar': pillar,
        'region': region,
        'format': format_type,
        'text': text[:1000]
    }
    print(f"OK: {docx_file}")
    print(f"  Pilier: {pillar} | Format: {format_type}")
    print()

with open('extracted_articles.json', 'w', encoding='utf-8') as f:
    json.dump(extracted_docs, f, ensure_ascii=False, indent=2)

print("Extraction completed.")
