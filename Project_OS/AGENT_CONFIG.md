# Agent Config - Valeurs africaines

## Configuration par defaut

- Modele: GPT-5.5
- Niveau: medium
- Vitesse: standard
- Mode execution: rapide
- Choix final: l'agent decide dynamiquement selon la tache.

## Quand changer

- Taches simples: GPT-5.5 / low / fast
- Travail courant: GPT-5.5 / medium / standard
- Strategie, statistiques, rapports importants: GPT-5.5 / high / standard

## Regle de decision automatique

L'agent choisit le meilleur modele, niveau et vitesse selon:

- complexite de la demande;
- besoin de qualite;
- besoin de rapidite;
- presence de statistiques ou donnees;
- importance du livrable;
- risque d'erreur.
- cout/tokens necessaires.

Le reglage par defaut reste GPT-5.5 / medium / standard, mais il peut etre augmente ou allege sans demander confirmation.

## Optimisation tokens

Objectif: obtenir le meilleur resultat utile avec le moins de tokens possible.

Regles:

- Repondre court quand la demande est simple.
- Ne pas relire ou recreer des fichiers inutilement.
- Ne pas produire de longues explications si une action suffit.
- Utiliser `low / fast` pour tri, reformulation, petites notes et classement.
- Utiliser `medium / standard` pour production normale.
- Utiliser `high` seulement pour statistiques, strategie, rapports ou decisions importantes.
- Eviter les recherches web sauf lien fourni ou besoin vraiment actuel.

## Regles locales

- Reponses courtes.
- Actions directes.
- Priorite au dossier `J-Tub/Valeurs africaines`.
- Garder les visualisations statistiques comme capacite importante.
- Ne pas ajouter de grosse structure sans demande explicite.
