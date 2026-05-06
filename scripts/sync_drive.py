"""
Sync automatique vers Google Drive Valeurs Africaines.
Usage : python scripts/sync_drive.py

La 1ere fois : un navigateur s'ouvre pour autoriser l'acces.
Ensuite : synchronisation complete en un clic.
"""

import os
import json
import time
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/drive.file"]
TOKEN_FILE = Path(__file__).parent.parent / "token_drive.json"
CREDENTIALS_FILE = Path(__file__).parent.parent / "credentials.json"
MIROIR = Path(__file__).parent.parent / "_drive-miroir"

DRIVE_FOLDER_ID = "1E3UWo-SL1_9xodXs5ax0uUxrzY4uh-6b"  # Dossier partage

def get_credentials():
    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CREDENTIALS_FILE.exists():
                print("=" * 60)
                print("Configuration necessaire - une seule fois")
                print("=" * 60)
                print()
                print("Va sur https://console.cloud.google.com/apis/credentials")
                print("  → Cree un ID client OAuth (Application de bureau)")
                print("  → Telecharge le JSON")
                print(f"  → Place-le ici : {CREDENTIALS_FILE}")
                print()
                input("Appuie sur Entree quand c'est fait...")
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
            creds = flow.run_local_server(open_browser=True, port=8081)
        TOKEN_FILE.write_text(creds.to_json())
    return creds

def find_or_create_folder(service, parent_id=None):
    """Cree ou recupere le dossier Valeurs-Africaines dans Drive."""
    query = "name='Valeurs-Africaines' and mimeType='application/vnd.google-apps.folder'"
    if parent_id:
        query += f" and '{parent_id}' in parents"
    
    items = service.files().list(q=query, spaces='drive').execute().get('files', [])
    if items:
        return items[0]['id']
    
    folder = service.files().create(body={
        'name': 'Valeurs-Africaines',
        'mimeType': 'application/vnd.google-apps.folder'
    }).execute()
    return folder['id']

def upload_folder(service, local_path, parent_id, recursive=True):
    """Upload un dossier local vers Google Drive."""
    local = Path(local_path)
    name = local.name
    
    # Creer ou trouver le dossier dans Drive
    query = f"name='{name}' and mimeType='application/vnd.google-apps.folder' and '{parent_id}' in parents"
    items = service.files().list(q=query, spaces='drive').execute().get('files', [])
    
    if items:
        folder_id = items[0]['id']
        print(f"  Dossier existe: {name}")
    else:
        folder = service.files().create(body={
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_id]
        }).execute()
        folder_id = folder['id']
        print(f"  Dossier cree: {name}")
    
    # Upload les fichiers
    for item in sorted(local.iterdir()):
        if item.is_file():
            # Verifier si le fichier existe deja
            q = f"name='{item.name}' and '{folder_id}' in parents"
            existing = service.files().list(q=q, spaces='drive').execute().get('files', [])
            if existing:
                # Mettre a jour
                media = MediaFileUpload(str(item))
                service.files().update(fileId=existing[0]['id'], media_body=media).execute()
                print(f"    Mis a jour: {item.name}")
            else:
                media = MediaFileUpload(str(item))
                service.files().create(body={
                    'name': item.name,
                    'parents': [folder_id]
                }, media_body=media).execute()
                print(f"    Ajoute: {item.name}")
            time.sleep(0.3)  # Eviter rate limiting
        elif item.is_dir() and recursive:
            upload_folder(service, item, folder_id)
    
    return folder_id

if __name__ == "__main__":
    print("Sync Valeurs Africaines -> Google Drive")
    print("=" * 50)
    
    creds = get_credentials()
    service = build('drive', 'v3', credentials=creds)
    
    root_id = find_or_create_folder(service)
    print(f"\nDossier racine: Valeurs-Africaines (ID: {root_id})")
    
    for dossier in sorted(MIROIR.iterdir()):
        if dossier.is_dir():
            print(f"\n{'='*40}")
            print(f"Upload: {dossier.name}/")
            print(f"{'='*40}")
            upload_folder(service, dossier, root_id)
    
    print(f"\n{'='*50}")
    print("Sync termine avec succes !")
    print(f"Ouvre : https://drive.google.com/drive/u/3/")
