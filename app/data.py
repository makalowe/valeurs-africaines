import json
import re
import unicodedata
from datetime import date
from pathlib import Path

STORE_PATH = Path(__file__).resolve().parent / "data_store.json"


def _slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    lowered = normalized.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", lowered).strip("-")
    return slug or "article"


def init_store() -> None:
    if STORE_PATH.exists():
        payload = _load()
        payload.setdefault("subscribers", [])
        payload.setdefault("editions", [])
        changed = False
        for article in payload.get("articles", []):
            if "slug" not in article:
                article["slug"] = _slugify(article.get("title", "article"))
                changed = True
            if "author" not in article:
                article["author"] = "Redaction VA"
                changed = True
            if "scheduled_at" not in article:
                article["scheduled_at"] = None
                changed = True
        if changed:
            _save(payload)
        return

    seed = {
        "articles": [
            {
                "id": 1,
                "rubrique": "Analyse de fond",
                "title": "Le Sahel a la croisee des recompositions strategiques",
                "slug": "le-sahel-a-la-croisee-des-recompositions-strategiques",
                "excerpt": "Entre retrait militaire occidental, partenariats securitaires alternatifs et ressources convoitees, le Sahel devient le theatre d'une nouvelle competition d'influences.",
                "body": "Analyse complete en cours de publication.",
                "reading_time": "10 min de lecture",
                "status": "published",
                "is_featured": 1,
                "published_at": "2026-05-03",
            },
            {
                "id": 2,
                "rubrique": "Diplomatie",
                "title": "L'Union africaine face aux fractures du systeme international",
                "slug": "l-union-africaine-face-aux-fractures-du-systeme-international",
                "excerpt": "La fragmentation geopolitique mondiale reconfigure les marges de manoeuvre institutionnelles africaines.",
                "body": "Contenu en cours de redaction.",
                "reading_time": "8 min de lecture",
                "status": "published",
                "is_featured": 0,
                "published_at": "2026-05-02",
            },
            {
                "id": 3,
                "rubrique": "Ressources",
                "title": "Petrole, gaz et minerais critiques: les nouveaux leviers de puissance",
                "slug": "petrole-gaz-et-minerais-critiques-les-nouveaux-leviers-de-puissance",
                "excerpt": "L'economie politique des ressources devient centrale dans les arbitrages strategiques africains.",
                "body": "Contenu en cours de redaction.",
                "reading_time": "7 min de lecture",
                "status": "published",
                "is_featured": 0,
                "published_at": "2026-05-01",
            },
            {
                "id": 4,
                "rubrique": "Securite",
                "title": "Renseignement et contre-terrorisme: mutations discretes",
                "slug": "renseignement-et-contre-terrorisme-mutations-discretes",
                "excerpt": "Les cooperations informelles et les architectures hybrides gagnent en importance sur le terrain.",
                "body": "Contenu en cours de redaction.",
                "reading_time": "9 min de lecture",
                "status": "published",
                "is_featured": 0,
                "published_at": "2026-04-30",
            },
        ],
        "subscribers": [],
        "editions": [],
    }
    STORE_PATH.write_text(json.dumps(seed, ensure_ascii=True, indent=2), encoding="utf-8")


def _load() -> dict:
    return json.loads(STORE_PATH.read_text(encoding="utf-8"))


def _save(payload: dict) -> None:
    STORE_PATH.write_text(json.dumps(payload, ensure_ascii=True, indent=2), encoding="utf-8")


def list_articles() -> list[dict]:
    payload = _load()
    return sorted(payload["articles"], key=lambda x: x["id"], reverse=True)


def list_editions() -> list[dict]:
    payload = _load()
    editions = payload.get("editions", [])
    return sorted(
        editions,
        key=lambda x: (x.get("published_at") or x.get("date") or "", x.get("id", 0)),
        reverse=True,
    )


def get_edition_by_slug(slug: str) -> dict | None:
    for edition in list_editions():
        if edition.get("slug") == slug:
            return edition
    return None


def current_edition() -> dict | None:
    for edition in list_editions():
        if edition.get("status", "published") == "published":
            return edition
    editions = list_editions()
    return editions[0] if editions else None


def articles_for_edition(slug: str, include_unpublished: bool = False) -> list[dict]:
    edition = get_edition_by_slug(slug)
    if not edition:
        return []
    source_rows = list_articles() if include_unpublished else list_published()
    by_slug = {row.get("slug"): row for row in source_rows}
    ordered = []
    for article_slug in edition.get("article_slugs", []):
        row = by_slug.get(article_slug)
        if row:
            ordered.append(row)
    attached = [
        row
        for row in source_rows
        if row.get("edition_slug") == slug and row.get("slug") not in {item.get("slug") for item in ordered}
    ]
    return ordered + attached


def promote_scheduled_articles() -> None:
    payload = _load()
    today = str(date.today())
    changed = False
    for row in payload.get("articles", []):
        if row.get("status") == "scheduled" and row.get("scheduled_at") and row["scheduled_at"] <= today:
            row["status"] = "published"
            row["published_at"] = row["scheduled_at"]
            changed = True
    if changed:
        _save(payload)


def list_published(limit: int | None = None) -> list[dict]:
    promote_scheduled_articles()
    rows = [a for a in list_articles() if a["status"] == "published"]
    return rows[:limit] if limit else rows


def get_article_by_slug(slug: str) -> dict | None:
    for row in list_published():
        if row.get("slug") == slug:
            return row
    return None


def get_any_article_by_slug(slug: str) -> dict | None:
    for row in list_articles():
        if row.get("slug") == slug:
            return row
    return None


def featured_article() -> dict | None:
    for row in list_published():
        if row.get("is_featured") == 1:
            return row
    rows = list_published(limit=1)
    return rows[0] if rows else None


def create_article(
    rubrique: str,
    title: str,
    excerpt: str,
    body: str,
    reading_time: str,
    author: str = "Redaction VA",
    scheduled_at: str | None = None,
    sources: list[str] | None = None,
    country: str | None = None,
    theme: str | None = None,
    format_label: str | None = None,
    strategic_question: str | None = None,
    methodology: dict | None = None,
    key_points: list[str] | None = None,
    implications: list[str] | None = None,
    limitations: str | None = None,
    confidence_level: str | None = None,
    notes_label: str | None = None,
    citation_style: str | None = None,
    edition_slug: str | None = None,
) -> None:
    payload = _load()
    next_id = max((a["id"] for a in payload["articles"]), default=0) + 1
    base_slug = _slugify(title)
    slug = base_slug
    existing = {a.get("slug") for a in payload["articles"]}
    i = 2
    while slug in existing:
        slug = f"{base_slug}-{i}"
        i += 1

    article = {
        "id": next_id,
        "rubrique": rubrique,
        "title": title,
        "slug": slug,
        "excerpt": excerpt,
        "body": body,
        "author": author or "Redaction VA",
        "reading_time": reading_time,
        "status": "scheduled" if scheduled_at else "draft",
        "is_featured": 0,
        "published_at": None,
        "scheduled_at": scheduled_at or None,
        "sources": sources or ["Source a renseigner avant publication"],
        "format_label": format_label or "Research Brief",
        "notes_label": notes_label or "Notes",
        "citation_style": citation_style or "french-footnotes",
    }
    optional_fields = {
        "country": country,
        "theme": theme,
        "strategic_question": strategic_question,
        "methodology": methodology,
        "key_points": key_points,
        "implications": implications,
        "limitations": limitations,
        "confidence_level": confidence_level,
        "edition_slug": edition_slug,
    }
    article.update({key: value for key, value in optional_fields.items() if value})
    payload["articles"].append(article)
    _save(payload)


def publish_article(article_id: int) -> None:
    payload = _load()
    for row in payload["articles"]:
        if row["id"] == article_id:
            row["status"] = "published"
            row["published_at"] = str(date.today())
    _save(payload)


def schedule_article(article_id: int, scheduled_at: str) -> None:
    payload = _load()
    for row in payload["articles"]:
        if row["id"] == article_id:
            row["status"] = "scheduled"
            row["scheduled_at"] = scheduled_at
            row["published_at"] = None
    _save(payload)


def feature_article(article_id: int) -> None:
    payload = _load()
    for row in payload["articles"]:
        row["is_featured"] = 1 if row["id"] == article_id else 0
    _save(payload)


def add_subscriber(email: str) -> bool:
    payload = _load()
    payload.setdefault("subscribers", [])
    normalized = email.strip().lower()
    if not normalized or normalized in payload["subscribers"]:
        return False
    payload["subscribers"].append(normalized)
    _save(payload)
    return True


def list_subscribers() -> list[str]:
    payload = _load()
    return payload.get("subscribers", [])

