import sys
import zipfile
import xml.etree.ElementTree as ET
import json
import re
import unicodedata
from pathlib import Path
from datetime import date

sys.path.insert(0, 'C:\\Users\\MIMBI\\OneDrive\\Bureau\\Valeurs Africaines')

from app.data import create_article, _load, _save

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

def parse_article_metadata(text):
    lines = text.split('\n')
    metadata = {}
    body_start = 0
    
    for i, line in enumerate(lines[:20]):
        if 'Rubrique:' in line:
            metadata['rubrique'] = line.split('Rubrique:')[-1].strip()
        elif 'Auteur:' in line or 'Signature:' in line:
            metadata['author'] = line.split('Auteur:' if 'Auteur:' in line else 'Signature:')[-1].strip()
        elif 'Temps de lecture:' in line:
            metadata['reading_time'] = line.split('Temps de lecture:')[-1].strip()
        elif 'Chapo' in line or 'Article' in line or 'Brief:' in line:
            body_start = i
            break
    
    body = '\n'.join(lines[body_start:]).strip()
    if len(body) > 500:
        excerpt = body[:300]
    else:
        excerpt = body[:len(body)//2]
    
    return metadata, body[:2000], excerpt

# Mapping
files = {
    'VA - Article - Dossier special Mali - 2026-05-04.docx': 'Guerres & Conflits',
    'VA - Brief Union africaine et puissances exterieures - v1.docx': 'Diplomatie',
    'VA - Guerre informationnelle en Afrique - v2 pays influents.docx': 'Renseignement',
    'VA - Kenya - Tech - Nairobi Pole Numerique - 2026-05-04.docx': 'Economie',
    'VA - Langues africaines et souverainete narrative - v1.docx': 'Culture',
    'VA - Maroc - Lifestyle - Villes Creation Art de vivre - 2026-05-04.docx': 'Culture',
}

docx_dir = Path('C:\\Users\\MIMBI\\OneDrive\\Bureau\\Valeurs Africaines\\extracted\\valeurs  africaines')

print("Importing articles...")
for docx_file, pillar in files.items():
    docx_path = docx_dir / docx_file
    if not docx_path.exists():
        print(f"SKIP: {docx_file} (not found)")
        continue
    
    text = extract_text_from_docx(str(docx_path))
    if len(text) < 50:
        print(f"SKIP: {docx_file} (no content)")
        continue
    
    metadata, body, excerpt = parse_article_metadata(text)
    
    rubrique = metadata.get('rubrique', pillar)
    title = docx_file.replace('VA - ', '').replace(' - 2026-05-04.docx', '').replace(' - v1.docx', '').replace(' - v2 pays influents.docx', '')
    author = metadata.get('author', 'VA Desk')
    reading_time = metadata.get('reading_time', '7 min')
    
    create_article(
        rubrique=rubrique,
        title=title,
        excerpt=excerpt,
        body=body,
        reading_time=reading_time,
        format='article' if len(text) > 2000 else 'brief',
        author=author
    )
    
    print(f"OK: {title}")
    print(f"   Rubrique: {rubrique} | Auteur: {author}")

print("\nImport completed!")
