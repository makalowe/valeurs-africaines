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
    echo 1. Un navigateur va s'ouvrir
    echo 2. Connecte-toi avec ton compte Google
    echo 3. Autorise l'acces
    echo 4. Ferme la page, reviens ici
    pause
    "%RCLONE%" config create gdrive drive scope drive.file
)

echo.
echo 1/3 - Sync articles et documents...
"%RCLONE%" sync "C:\Users\MIMBI\OneDrive\Bureau\Valeurs Africaines\_drive-miroir" "gdrive:Valeurs-Africaines" --progress

echo.
echo 2/3 - Sync illustrations...
"%RCLONE%" sync "C:\Users\MIMBI\OneDrive\Bureau\Valeurs Africaines\VA-Illustrations" "gdrive:Valeurs-Africaines/03_Illustrations" --progress

echo.
echo 3/3 - Sync site web...
"%RCLONE%" sync "C:\Users\MIMBI\OneDrive\Bureau\Valeurs Africaines\site" "gdrive:Valeurs-Africaines/06_Site" --progress 2>nul

echo.
echo ============================================
echo  Sync termine !
echo  Voir : https://drive.google.com/drive/u/3/
echo ============================================
pause
