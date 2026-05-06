# Procedure de redaction d'un article — Pas a pas

**A retenir pour chaque article.**

---

## Phase 1 : Veille & Sujet (30 min)

```
1. OUVRE Google Alerts (deja configurees)
2. SCAN les headlines du jour
3. CHERCHE 3 signaux faibles
4. CHOISIS 1 sujet (verifie : 2 sources min.)
```

## Phase 2 : Recherche & Sources

```
1. OUVRE Perplexity.ai
2. COPIE le prompt "recherche sources" dans docs/prompts-ia-pour-articles.md
3. RECUPERE 3-5 sources fiables
4. VERIFIE les sources dans la liste des 25 sources noyau dur
```

## Phase 3 : Redaction

```
1. OUVRE Claude.ai
2. COPIE le prompt "analyse de fond" dans docs/prompts-ia-pour-articles.md
3. AJOUTE le sujet et les sources
4. RECUPERE le texte genere
5. AJOUTE le contexte Valeurs Africaines
```

## Phase 4 : Correction

```
1. OUVRE GPT / ChatGPT
2. COPIE le prompt "correction/relecture"
3. COLLE l'article
4. APPLIQUE les corrections suggerees
```

## Phase 5 : Mise en ligne

```
1. AJOUTE l'article dans data_store.json
2. CHOISIS une illustration (PNG existante ou generation SVG)
3. VERIFIE la grille qualite (6 questions)
4. VALIDE la checklist publication
5. LANCE python run.py → verifie l'affichage
6. COMMIT et PUSH sur GitHub
```

---

**Au total : 2h-3h par article** (selon complexite)

Les outils sont prets :
- Google Alerts : 8 alertes creees
- Prompts IA : docs/prompts-ia-pour-articles.md
- 25 sources : app/data.py
- Sync Drive : scripts/sync_drive.bat
