"""
Verificateur de procedure de publication.
Utilisation : python -m app.check_publication
"""

import json
from pathlib import Path

STORE = Path(__file__).resolve().parent / "data_store.json"


def check_articles():
    data = json.loads(STORE.read_text(encoding="utf-8"))
    articles = data["articles"]

    print(f"\n{'='*60}")
    print(f"  Verification de {len(articles)} articles")
    print(f"{'='*60}\n")

    for a in articles:
        issues = []
        status = a.get("status", "?")

        # Verifier les sources
        sources = a.get("sources") or []
        if len(sources) < 2:
            issues.append(f"Sources: {len(sources)}/2 minimum")

        # Verifier les tags (axe pays + theme)
        tags = a.get("tags") or []
        if len(tags) < 2:
            issues.append(f"Tags: {len(tags)} (2 min : pays + theme)")

        # Verifier la checklist
        checklist = a.get("verification_checklist") or {}
        if not all(checklist.values()):
            issues.append("Checklist incomplete")

        # Verifier la grille qualite
        qf = a.get("quality_filter")
        if not qf:
            issues.append("Grille qualite manquante")

        # Verifier l'image
        if not a.get("image"):
            issues.append("Illustration manquante")

        # Verifier l'auteur
        if not a.get("author") or a.get("author") == "VA Desk":
            issues.append("Auteur generique (VA Desk)")

        if issues:
            print(f"  #{a['id']:2d} [{status:10s}] {a['title'][:55]}")
            for i in issues:
                print(f"       ⚠️  {i}")
            print()

    # Stats
    total = len(articles)
    publies = len([a for a in articles if a.get("status") == "published"])
    without_issues = 0
    for a in articles:
        sources = a.get("sources") or []
        tags = a.get("tags") or []
        if len(sources) >= 2 and len(tags) >= 2 and a.get("image"):
            without_issues += 1

    print(f"\nStats : {publies}/{total} publies, {without_issues}/{total} conformes")
    print(f"\nProchaine etape : appliquer la procedure de publication (voir docs/procedure-publication-complete.md)")


if __name__ == "__main__":
    check_articles()
