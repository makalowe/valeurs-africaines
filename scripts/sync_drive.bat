@echo off
title Sync Valeurs Africaines -> Drive
echo ============================================
echo  Sync Valeurs Africaines - Google Drive
echo ============================================
echo.

set RCLONE=C:\Users\MIMBI\rclone\rclone.exe

"%RCLONE%" listremotes 2>&1 | findstr "gdrive" >nul
if errorlevel 1 (
    echo Premiere utilisation - Configuration necessaire.
    echo.
    echo 1. Un navigateur va s'ouvrir pour Connecter Google Drive
    echo 2. Connecte-toi avec ton compte Google
    echo 3. Autorise l'acces
    echo 4. Ferme la page, reviens ici
    echo.
    pause
    "%RCLONE%" config create gdrive drive scope drive.file
)

echo Sync en cours...
"%RCLONE%" sync "C:\Users\MIMBI\OneDrive\Bureau\Valeurs Africaines\_drive-miroir" "gdrive:Valeurs-Africaines" --progress

echo.
echo Sync termine !
echo Voir : https://drive.google.com/drive/u/3/
pause
