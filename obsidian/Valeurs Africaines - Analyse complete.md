# Valeurs Africaines — Analyse complète

**Date** : 2026-05-06
**Statut** : MVP fonctionnel — 6 articles en validation, 2 publiés
**Tags** : #projet #journalisme #geopolitique #flask #ia

---

## 1. Vision

**Valeurs Africaines** est un magazine géopolitique francophone de haut niveau consacré à l'Afrique. Objectif : devenir la référence en langue française pour l'analyse stratégique africaine (diplomatie, sécurité, ressources, renseignement). Le projet a une **méthodologie journalistique exigeante** avec grille qualité en 6 axes, 25 sources noyau dur classées par fiabilité, et workflow éditorial complet.

---

## 2. Architecture du projet

```
Valeurs Africaines/
│
├── run.py                         # Point d'entrée Flask
├── config.py                      # (à créer) Configuration DATABASE_URL
├── requirements.txt               # Flask, gunicorn, requests, flask-caching
│
├── app/
│   ├── __init__.py                # Factory create_app() + cache
│   ├── routes.py                  # 25+ routes : publiques, éditeur, API, admin
│   ├── data.py                    # Couche données (JSON) + 25 sources noyau dur
│   ├── newsletter_provider.py     # Intégration Brevo API
│   ├── data_store.json            # Base de données JSON
│   ├── site.db                    # SQLite (inutilisé, résidu)
│   ├── static/
│   │   ├── css/main.css           # Charte graphique (rouge #E30613, Georgia)
│   │   └── img/
│   │       ├── logo-va-a.svg      # Logo officiel
│   │       └── logos/             # 6 propositions de logos
│   └── templates/
│       ├── base.html              # Layout (Georgia, rouge #E30613)
│       ├── home.html              # Une + 3 headlines + newsletter strip
│       ├── articles.html          # Liste articles publiés
│       ├── article_detail.html    # Affichage article (minimal)
│       ├── rubriques.html         # Rubriques éditoriales
│       ├── about.html             # À propos
│       ├── methodology.html       # Méthodologie journalistique
│       ├── correction_policy.html # Politique de correction
│       ├── newsletter.html        # Inscription newsletter
│       ├── contact.html           # Contact
│       ├── legal.html             # Mentions légales
│       ├── editor_dashboard.html  # Dashboard éditeur (KPI, workflow)
│       ├── editor_login.html      # Connexion éditeur
│       ├── article_editor.html    # Éditeur d'articles
│       ├── quality_filter.html    # Grille qualité (6 questions)
│       ├── admin.html             # Back-office legacy
│       ├── admin_login.html       # Login legacy
│       ├── sources_core.html      # 25 sources noyau dur
│       ├── watch_board.html       # Tableau de veille
│       └── components/
│           ├── header.html
│           └── footer.html
│
├── extracted/valeurs africaines/  # 📄 7 articles DOCX
│   ├── VA - Article - Dossier special Mali - 2026-05-04.docx
│   ├── VA - Brief Union africaine et puissances exterieures - v1.docx
│   ├── VA - Guerre informationnelle en Afrique - v1.docx
│   ├── VA - Guerre informationnelle en Afrique - v2 pays influents.docx
│   ├── VA - Kenya - Tech - Nairobi Pole Numerique - 2026-05-04.docx
│   ├── VA - Langues africaines et souverainete narrative - v1.docx
│   └── VA - Maroc - Lifestyle - Villes Creation Art de vivre - 2026-05-04.docx
│
├── scripts/
│   ├── import_articles.py         # Import DOCX → base de données
│   ├── full_import.py             # Import complet
│   ├── docx_reader.py             # Lecteur DOCX
│   └── routes_watch_append.py     # Route veille additionnelle
│
├── docs/
│   ├── site-architecture.md       # Architecture MVP
│   ├── branding-va.md             # Charte graphique verrouillée
│   └── newsletter-setup.md        # Configuration Brevo
│
├── Dockerfile                     # Python 3.12-slim, multi-stage
├── docker-compose.yml             # Volume JSON + healthcheck
│
└── obsidian/
    └── Valeurs-Africaine-suivi.md # Note de suivi projet
```

---

## 3. Stack technique

| Technologie | Version | Usage |
|---|---|---|
| **Python** | 3.12 | Langage |
| **Flask** | 3.x | Framework web (Factory, Blueprint, Jinja2) |
| **Gunicorn** | 21.x | Serveur WSGI (4 workers) |
| **Flask-Caching** | 2.x | Cache mémoire |
| **Brevo API** | REST | Newsletter |
| **Docker** | Compose v3.9 | Conteneurisation |
| **Nginx** | — | Reverse proxy (production) |
| **SQLite** | — | Présent mais inutilisé par le code |

### Stockage
> ⚠️ **Stockage fichier JSON** (`data_store.json`) — pas de base de données relationnelle.
> Le fichier est lu/écrit intégralement à chaque opération. SQLite (`site.db`) est un résidu.

---

## 4. Routes détaillées

### Publiques (15)
| Route | Template | Rôle |
|---|---|---|
| `/` | `home.html` | Une + 3 headlines + newsletter |
| `/articles` | `articles.html` | Tous les articles publiés |
| `/articles/<slug>` | `article_detail.html` | Article complet |
| `/rubriques` | `rubriques.html` | Rubriques éditoriales |
| `/a-propos` | `about.html` | Mission, équipe |
| `/methodologie` | `methodology.html` | Standards de vérification |
| `/politique-correction` | `correction_policy.html` | Droit de signalement |
| `/newsletter` | `newsletter.html` | Inscription |
| `/newsletter/subscribe` | POST | Abonnement Brevo |
| `/contact` | `contact.html` | Contact rédaction |
| `/mentions-legales` | `legal.html` | Mentions légales |
| `/sitemap.xml` | XML | Sitemap dynamique |

### Éditeur (8)
| Route | Rôle |
|---|---|
| `/editor` | Dashboard KPI + workflow |
| `/editor/login` | Connexion mot de passe |
| `/editor/logout` | Déconnexion |
| `/editor/article/new` | Création article |
| `/editor/article/<id>` | Édition article |
| `/editor/quality-filter/<id>` | Grille qualité |
| `/admin/preview/<slug>` | Preview admin |

### API (5)
| Endpoint | Rôle |
|---|---|
| `POST /api/article/<id>/move-validation` | Draft → Validation |
| `POST /api/article/<id>/publish` | Validation → Publié |
| `POST /api/article/<id>/feature` | Mettre à la une |
| `POST /api/article/<id>/schedule` | Planifier |
| `POST /api/article/<id>/checklist` | MàJ checklist |
| `POST /api/signal` | Ajouter signal de veille |
| `POST /api/signal/<id>/status` | MàJ statut signal |

### Admin legacy (doublon)
| Route | Rôle |
|---|---|
| `/admin/login` | Login (identique à /editor) |
| `/admin` | Dashboard (identique à /editor) |
| `/admin/publish/<id>` | Publier |
| `/admin/feature/<id>` | À la une |
| `/admin/schedule/<id>` | Planifier |
| `/admin/newsletter-subscribers.csv` | Export CSV abonnés |

---

## 5. Workflow éditorial

```
SIGNAL (veille)
    │
    ▼
DRAFT (brouillon)
    │
    ├── Checklist vérification (3 items)
    │   ├── sources_verified (3+ sources)
    │   ├── facts_checked
    │   └── peer_reviewed
    │
    ▼
VALIDATION
    │
    ├── Grille qualité (6 questions)
    │   ├── Quel est l'acteur principal ?
    │   ├── Quel est son agenda ?
    │   ├── Quelles sont les preuves ?
    │   ├── Quelle est la contradiction centrale ?
    │   ├── Quelles sont les conséquences ?
    │   └── Quel est l'angle éditorial ?
    │
    ▼
SCHEDULED (programmé)
    │
    ▼
PUBLISHED (publié)
    │
    └── Possibilité de mettre À LA UNE
```

---

## 6. Grille qualité (Quality Filter)

Les 6 questions que tout article doit passer avant publication :

| Question | Rôle |
|---|---|
| **Acteur** | Qui est l'acteur principal ? |
| **Agenda** | Quel est son agenda ? |
| **Preuve** | Quelles sont les preuves ? |
| **Contradiction** | Quelle est la contradiction centrale ? |
| **Conséquence** | Quelles sont les conséquences ? |
| **Angle** | Quel est l'angle éditorial ? |

---

## 7. Les 25 sources noyau dur

| Bloc | Sources | Fiabilité |
|---|---|---|
| **Sécurité/Conflits** | UN OCHA ReliefWeb, AU Peace & Security, ACLED, ICG, Jane's Defence | A+ à A |
| **Diplomatie/Institutions** | ECOWAS, EAC, AU Commission, Chatham House, Atlantic Council | A+ à A |
| **Ressources/Économie politique** | AfDB, IMF Africa, NRGI, Reuters Energy, Brookings | A+ à A |
| **Renseignement/Influences** | Stanford IO, EU DisinfoLab, AFRICOM, China Africa Project, RUSI | A+ à A |
| **Complémentaires** | BBC Africa, Africa Report, Africa Portal, Oped Index, APRI | A à B+ |

---

## 8. Piliers éditoriaux

| Pilier | Description |
|---|---|
| **Économie** | Analyse macro-économique, développement |
| **Armée & Défense** | Équipements, doctrines, budgets |
| **Renseignement** | Cyber, désinformation, influences |
| **Guerres & Conflits** | Conflits en cours, peacekeeping |
| **Économie politique** | Ressources, gouvernance, corruption |
| **Ressources stratégiques** | Pétrole, gaz, minerais rares, terres |
| **Diplomatie** | Relations internationales, organisations |
| **Culture** | Langues, souveraineté narrative |
| **Religion** | Géopolitique religieuse |

---

## 9. Articles existants

### Publiés (2)
| Titre | Auteur | Statut |
|---|---|---|
| Le Sahel à la croisée des recompositions stratégiques | VA Desk | ✅ Publié + Une |
| L'Union africaine face aux fractures du système international | VA Desk | ✅ Publié |

### En validation (4)
| Titre | Auteur | Corps |
|---|---|---|
| Dossier spécial Mali : situation au 4 mai 2026 | Nael T. Koffi | ✅ Rédigé |
| Brief : Union africaine et puissances extérieures | Selene B. Okoro | ✅ Rédigé |
| Guerre informationnelle en Afrique : nouveaux acteurs | Nael T. Koffi | ✅ Rédigé |
| Langues africaines et souveraineté narrative | Jonas E. Makena | ✅ Rédigé |

### Projets DOCX (3)
| Fichier | Contenu |
|---|---|
| Kenya - Tech - Nairobi Pôle Numérique | Tech kényane |
| Maroc - Lifestyle - Villes Création | Maroc lifestyle |
| Guerre informationnelle v2 | Version enrichie |

---

## 10. KPI Dashboard éditeur

| Indicateur | Source |
|---|---|
| Total articles | `len(list_articles())` |
| Publiés | `list_by_status("published")` |
| Programmés | `list_by_status("scheduled")` |
| Brouillons | `list_by_status("draft")` |
| En validation | `list_by_status("validation")` |
| Abonnés newsletter | `len(list_subscribers())` |
| Objectif mensuel | 16 articles |
| Progression | `min(100, (publiés + programmés) / 16 * 100)` |
| Publications 7 jours | Graphique jour par jour |

---

## 11. Points forts

### Éditorial
- Méthodologie rigoureuse : 6 filtres qualité, 25 sources noyau dur classées par fiabilité
- Workflow complet : Signal → Brouillon → Validation → Programmé → Publié
- Contenu de qualité : articles sérieux, bien sourcés, ton académique
- Auteurs multiples (Nael T. Koffi, Selene B. Okoro, Jonas E. Makena)
- Checklist vérification en 3 points avant publication

### Technique
- Architecture Flask Factory + Blueprint propre
- Sitemap XML dynamique (toutes les pages + articles)
- Docker production-ready : multi-stage build, non-root user, healthcheck
- Charte graphique verrouillée (couleurs #E30613, typo Georgia)
- Newsletter via Brevo API avec fallback local + export CSV
- Cache Flask-Caching
- Dashboard KPI éditeur complet

### Contenu
- 9 piliers éditoriaux couvrant toute la géopolitique africaine
- Drapeaux pays africains codés (30+ pays)
- 7 articles DOCX prêts à être importés
- Signaux de veille pour la curation

---

## 12. Problèmes identifiés

### 🔴 Critique

| Problème | Détail | Solution |
|---|---|---|
| **Stockage JSON** | `data_store.json` lu/écrit intégralement à chaque requête. Pas de concurrence, pas de scaling. | Migrer vers SQLite ou PostgreSQL |
| **Articles publiés sans corps** | Les 2 articles publiés ont `body: "Analyse complète en cours..."` — corps vide | Copier le vrai contenu depuis les DOCX |
| **Checkletter bloque publication** | 4 articles en validation avec checklist à `false` → impossible à publier | Cocher la checklist |
| **2 systèmes admin** | `/editor/` et `/admin/` font la même chose | Supprimer le legacy `/admin/` |
| **Template article minimal** | `article_detail.html` affiche le body en un seul `<p>` — pas de mise en page | Enrichir avec image, tags, sources, partage |

### 🟡 Forte priorité

| Problème | Solution |
|---|---|
| **Pas de SEO avancé** (OG, Twitter Cards, JSON-LD article) | Ajouter dans `base.html` et `article_detail.html` |
| **Pas de flux RSS** | Ajouter `/feed.xml` |
| **Pas de robots.txt** | Créer — pour l'instant le site n'est pas crawlé |
| **0 abonné newsletter** | `data_store.json` montre 0 abonné — Brevo pas configuré |
| **Pas de formulaire contact fonctionnel** | Route `/contact` existe mais template sûrement vide |
| **Routes en double** (éditeur vs admin) | Refactorer, garder uniquement `/editor/` |
| **Aucun responsive design** | CSS sans `@media` queries |
| **Body stocké en texte brut** | Pas de Markdown → pas de formatting possible |

### 🟢 Priorité moyenne

| Problème | Solution |
|---|---|
| Pas de pagination articles | Ajouter `?page=N` |
| Pas de recherche | Barre de recherche SQL |
| Pas de catégories visuelles | Page rubriques à enrichir |
| Pas de profiling auteur | Page auteur dédiée |
| Pas de partage réseaux sociaux | Boutons dans `article_detail.html` |
| Pas de commentaires | Disqus ou solution légère |
| Pas de mode sombre | CSS `prefers-color-scheme: dark` |

---

## 13. Plan d'exécution recommandé

### Phase 0 — Corrections immédiates (1 jour)
| Action | Temps |
|---|---|
| Copier le contenu des 4 articles DOCX vers la BDD | 1h |
| Cocher la checklist des 4 articles → les publier | 5 min |
| Mettre à jour les 2 articles publiés avec contenu réel | 30 min |
| Créer `robots.txt` | 2 min |

### Phase 1 — Technique (semaine 1)
| Jour | Action |
|---|---|
| J1 | Migrer JSON → SQLite (SQLAlchemy) |
| J2 | Enrichir `article_detail.html` (image, tags, sources, partage) |
| J3 | Ajouter SEO (OG, JSON-LD, RSS, canonicals) |
| J4 | Supprimer legacy `/admin/`, unifier sous `/editor/` |
| J5 | Configurer Brevo + lead magnet |

### Phase 2 — Contenu & Audience (semaine 2-3)
| Jour | Action |
|---|---|
| J6-7 | Publier les 3 articles DOCX (Kenya, Maroc, guerre info v2) |
| J8 | Créer flux RSS + soumettre aux agrégateurs |
| J9 | Configurer Google Search Console + GA4 |
| J10 | Responsive design (media queries) |
| J11-12 | Landing page "Qui sommes-nous" + page auteur |
| J13-14 | Newsletter : premier envoi + lead magnet carte Sahel |

---

## 14. Dashboard KPI cible

| Indicateur | Cible J30 | Cible J90 |
|---|---|---|
| Articles publiés | 10 | 30 |
| Abonnés newsletter | 50 | 500 |
| Visiteurs mensuels | 500 | 5 000 |
| Pages indexées Google | 15 | 50 |
| Taux de rebond | — | < 60% |
| Temps moyen sur article | — | > 3 min |

---

## 15. Concurrence & positionnement

| Concurrent | Positionnement | Différence VA |
|---|---|---|
| **Jeune Afrique** | Hebdo généraliste, payant | **Gratuit**, analyse pure, veille |
| **The Africa Report** | Anglais, business | **Francophone**, géopolitique stricte |
| **Le Monde Afrique** | Généraliste, grand public | **Spécialisé**, méthodologie transparente |
| **African Arguments** | Anglais, société | **Francophone**, sécurité/défense |

---

## 16. Liens utiles

- Dossier projet : `C:\Users\MIMBI\OneDrive\Bureau\Valeurs Africaines`
- Site (dev) : `python run.py` → `http://localhost:5000`
- Dashboard éditeur : `/editor` (mdp: `va-admin-2026`)
- Docker : `docker-compose up -d`

Projets connexes :
- [[Campus Plus]] — Partage de l'infra VPS Hostinger
- [[Email Campaign Manager]] — Module newsletter (Brevo déjà configuré)

---

## 17. Journal de mise à jour

- 2026-05-06 : Analyse complète du projet
- 2026-05-04 : Import articles DOCX (Mali, Kenya, Maroc, langues)
- 2026-05-03 : Charte branding verrouillée + suivi Obsidian
- 2026-05-01 : Création des 2 premiers articles
- 2026-04-23 : Newsletter Brevo configurée
