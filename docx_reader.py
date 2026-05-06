#!/usr/bin/env python
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

def extract_docx(path):
    with zipfile.ZipFile(path) as z:
        xml = z.read('word/document.xml')
        root = ET.fromstring(xml)
        ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        texts = [e.text for e in root.findall('.//w:t', ns) if e.text]
        return ''.join(texts)

base = Path(r'C:\Users\MIMBI\OneDrive\Bureau\Valeurs Africaines\extracted\valeurs  africaines')
files = {
    'VA - Article - Dossier special Mali - 2026-05-04.docx': 'Mali - Crise Securitaire',
    'VA - Brief Union africaine et puissances exterieures - v1.docx': 'Union Africaine - Diplomatie',
    'VA - Guerre informationnelle en Afrique - v2 pays influents.docx': 'Guerre Informationnelle',
    'VA - Kenya - Tech - Nairobi Pole Numerique - 2026-05-04.docx': 'Kenya - Nairobi Tech Hub',
    'VA - Langues africaines et souverainete narrative - v1.docx': 'Langues Africaines',
    'VA - Maroc - Lifestyle - Villes Creation Art de vivre - 2026-05-04.docx': 'Maroc - Art de Vivre',
}

for f, title in files.items():
    try:
        text = extract_docx(base / f)
        print(f'\n\n=== {title} ===')
        print(text[:2000])
    except Exception as e:
        print(f'ERROR {f}: {e}')
