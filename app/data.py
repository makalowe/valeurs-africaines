import json
import re
import unicodedata
from datetime import date, datetime
from pathlib import Path
from typing import Optional

STORE_PATH = Path(__file__).resolve().parent / "data_store.json"

# Piliers éditoriaux
PILLARS = [
    "Économie",
    "Armée & Défense",
    "Renseignement",
    "Guerres & Conflits",
    "Économie politique",
    "Ressources stratégiques",
    "Diplomatie",
    "Culture",
    "Religion"
]

# Formats de contenu
FORMATS = {
    "analyse": "Analyse longue (2000-4000 mots)",
    "brief": "Brief hebdo (500-800 mots)",
    "editorial": "Éditorial (800-1200 mots)",
    "interview": "Interview",
    "data_viz": "Chronologie / Data viz",
    "newsletter": "Newsletter"
}

# Statuts du workflow
STATUSES = ["signal", "draft", "validation", "published", "scheduled", "archived"]

# Blocs de veille
WATCH_BLOCKS = [
    "Sécurité/Conflits",
    "Diplomatie/Institutions",
    "Ressources/Économie politique",
    "Renseignement/Influences extérieures"
]

# SOURCES NOYAU DUR (25-30 sources max)
CORE_SOURCES = [
    # === SÉCURITÉ/CONFLITS ===
    {"id": 1, "name": "UN OCHA ReliefWeb", "country": "International", "type": "primaire", "reliability": "A+", "frequency": "quotidienne", "blocks": ["Sécurité/Conflits"], "themes": ["Conflits", "Crises humanitaires"], "url": "https://reliefweb.int/"},
    {"id": 2, "name": "African Union Peace & Security", "country": "Addis-Abeba", "type": "primaire", "reliability": "A+", "frequency": "hebdomadaire", "blocks": ["Sécurité/Conflits", "Diplomatie/Institutions"], "themes": ["Paix", "Sécurité continentale"], "url": "https://au.int/"},
    {"id": 3, "name": "ACLED (Armed Conflict Location & Event Data)", "country": "International", "type": "secondaire", "reliability": "A", "frequency": "quotidienne", "blocks": ["Sécurité/Conflits"], "themes": ["Données conflits", "Événements violents"], "url": "https://acleddata.com/"},
    {"id": 4, "name": "International Crisis Group (ICG)", "country": "Belgique", "type": "secondaire", "reliability": "A+", "frequency": "hebdomadaire", "blocks": ["Sécurité/Conflits"], "themes": ["Analyse crises"], "url": "https://www.crisisgroup.org/"},
    {"id": 5, "name": "Jane's Defence Weekly", "country": "UK", "type": "secondaire", "reliability": "A+", "frequency": "hebdomadaire", "blocks": ["Sécurité/Conflits", "Armée & Défense"], "themes": ["Défense", "Équipements militaires"], "url": "https://www.janes.com/"},
    
    # === DIPLOMATIE/INSTITUTIONS ===
    {"id": 6, "name": "ECOWAS (Communauté économique)", "country": "Abuja", "type": "primaire", "reliability": "A+", "frequency": "hebdomadaire", "blocks": ["Diplomatie/Institutions"], "themes": ["Intégration régionale", "Diplomatie"], "url": "https://www.ecowas.int/"},
    {"id": 7, "name": "EAC (East African Community)", "country": "Dar es-Salaam", "type": "primaire", "reliability": "A+", "frequency": "hebdomadaire", "blocks": ["Diplomatie/Institutions"], "themes": ["Afrique de l'Est", "Institutions régionales"], "url": "https://www.eac.int/"},
    {"id": 8, "name": "AU Commission Statements", "country": "Addis-Abeba", "type": "primaire", "reliability": "A+", "frequency": "quotidienne", "blocks": ["Diplomatie/Institutions"], "themes": ["Politique africaine", "Positionnements"], "url": "https://au.int/"},
    {"id": 9, "name": "Chatham House", "country": "UK", "type": "secondaire", "reliability": "A", "frequency": "hebdomadaire", "blocks": ["Diplomatie/Institutions"], "themes": ["Politique internationale", "Analyses stratégiques"], "url": "https://chathamhouse.org/"},
    {"id": 10, "name": "Atlantic Council Africa Center", "country": "USA", "type": "secondaire", "reliability": "A", "frequency": "hebdomadaire", "blocks": ["Diplomatie/Institutions"], "themes": ["Diplomatie", "Relations USA-Afrique"], "url": "https://www.atlanticcouncil.org/"},
    
    # === RESSOURCES/ÉCONOMIE POLITIQUE ===
    {"id": 11, "name": "African Development Bank (AfDB)", "country": "Abidjan", "type": "primaire", "reliability": "A+", "frequency": "mensuelle", "blocks": ["Ressources/Économie politique"], "themes": ["Économie", "Développement"], "url": "https://www.afdb.org/"},
    {"id": 12, "name": "IMF Africa Department", "country": "Washington", "type": "primaire", "reliability": "A+", "frequency": "mensuelle", "blocks": ["Ressources/Économie politique"], "themes": ["Macro-économie", "Finances"], "url": "https://www.imf.org/"},
    {"id": 13, "name": "Natural Resource Governance Institute", "country": "International", "type": "secondaire", "reliability": "A", "frequency": "hebdomadaire", "blocks": ["Ressources/Économie politique"], "themes": ["Ressources naturelles", "Gouvernance"], "url": "https://resourcegovernance.org/"},
    {"id": 14, "name": "Reuters Energy/Metals", "country": "International", "type": "secondaire", "reliability": "A", "frequency": "quotidienne", "blocks": ["Ressources/Économie politique"], "themes": ["Commodités", "Cours mondiaux"], "url": "https://www.reuters.com/"},
    {"id": 15, "name": "Brookings Institution Africa", "country": "USA", "type": "secondaire", "reliability": "A", "frequency": "hebdomadaire", "blocks": ["Ressources/Économie politique"], "themes": ["Économie politique", "Investissements"], "url": "https://www.brookings.edu/"},
    
    # === RENSEIGNEMENT/INFLUENCES EXTÉRIEURES ===
    {"id": 16, "name": "Stanford Internet Observatory", "country": "USA", "type": "secondaire", "reliability": "A", "frequency": "hebdomadaire", "blocks": ["Renseignement/Influences extérieures"], "themes": ["Désinformation", "Influence opérations"], "url": "https://io.stanford.edu/"},
    {"id": 17, "name": "EU DisinfoLab", "country": "Belgique", "type": "secondaire", "reliability": "A", "frequency": "hebdomadaire", "blocks": ["Renseignement/Influences extérieures"], "themes": ["Ingérence étrangère", "Désinformation"], "url": "https://www.disinfo.eu/"},
    {"id": 18, "name": "Strategic Studies Institute (AFRICOM)", "country": "USA", "type": "primaire", "reliability": "A+", "frequency": "mensuelle", "blocks": ["Renseignement/Influences extérieures"], "themes": ["Sécurité USA-Afrique", "Stratégie"], "url": "https://www.stratcom.mil/"},
    {"id": 19, "name": "China Africa Project (Johns Hopkins)", "country": "USA", "type": "secondaire", "reliability": "A", "frequency": "hebdomadaire", "blocks": ["Renseignement/Influences extérieures"], "themes": ["Influence chinoise", "Investissements"], "url": "https://chinaafricaproject.com/"},
    {"id": 20, "name": "Russian Institute (RUSI)", "country": "UK", "type": "secondaire", "reliability": "A", "frequency": "hebdomadaire", "blocks": ["Renseignement/Influences extérieures"], "themes": ["Influence russe", "Sécurité"], "url": "https://rusi.org/"},
    
    # === COMPLÉMENTAIRES (5 sources supplémentaires) ===
    {"id": 21, "name": "BBC News Africa", "country": "UK", "type": "secondaire", "reliability": "A", "frequency": "quotidienne", "blocks": ["Sécurité/Conflits", "Diplomatie/Institutions"], "themes": ["Actualité générale"], "url": "https://www.bbc.com/news/world/africa"},
    {"id": 22, "name": "Africa Report (Jeune Afrique)", "country": "France", "type": "secondaire", "reliability": "A", "frequency": "quotidienne", "blocks": ["Ressources/Économie politique", "Diplomatie/Institutions"], "themes": ["Actualité francophone"], "url": "https://www.theafricareport.com/"},
    {"id": 23, "name": "Africa Portal (SAIIA)", "country": "Afrique du Sud", "type": "secondaire", "reliability": "A", "frequency": "hebdomadaire", "blocks": ["Diplomatie/Institutions"], "themes": ["Recherche africaine"], "url": "https://africaportal.org/"},
    {"id": 24, "name": "Oped Index Africa", "country": "International", "type": "secondaire", "reliability": "B+", "frequency": "quotidienne", "blocks": ["Diplomatie/Institutions", "Renseignement/Influences extérieures"], "themes": ["Opinions experts"], "url": "https://www.opedindex.com/"},
    {"id": 25, "name": "Africa Policy Research Institute", "country": "International", "type": "secondaire", "reliability": "A", "frequency": "mensuelle", "blocks": ["Ressources/Économie politique", "Diplomatie/Institutions"], "themes": ["Recherche appliquée"], "url": "https://www.apri.org/"},
]

# Drapeaux des pays africains
COUNTRY_FLAGS = {
    "algerie": "🇩🇿", "angola": "🇦🇴", "benin": "🇧🇯", "burkina faso": "🇧🇫",
    "cameroun": "🇨🇲", "cap-vert": "🇨🇻", "congo": "🇨🇬", "cote d'ivoire": "🇨🇮",
    "egypte": "🇪🇬", "ethiopie": "🇪🇹", "gabon": "🇬🇦", "ghana": "🇬🇭",
    "guinee": "🇬🇳", "kenya": "🇰🇪", "libye": "🇱🇾", "madagascar": "🇲🇬",
    "mali": "🇲🇱", "maroc": "🇲🇦", "mauritanie": "🇲🇷", "niger": "🇳🇪",
    "nigeria": "🇳🇬", "ouganda": "🇺🇬", "rdc": "🇨🇩", "rdc congo": "🇨🇩",
    "republique democratique du congo": "🇨🇩", "rwanda": "🇷🇼", "senegal": "🇸🇳",
    "somalie": "🇸🇴", "soudan": "🇸🇩", "tchad": "🇹🇩", "togo": "🇹🇬", "tunisie": "🇹🇳",
}

def _slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    lowered = normalized.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", lowered).strip("-")
    return slug or "article"


def detect_country_flag(text: str) -> str:
    """Détecte le pays et retourne le flag emoji"""
    hay = (text or "").lower()
    for country, flag in COUNTRY_FLAGS.items():
        if country in hay:
            return flag
    return ""


def get_sources_by_block(block: str) -> list[dict]:
    """Récupérer les sources pour un bloc spécifique"""
    return [s for s in CORE_SOURCES if block in s.get("blocks", [])]


def _kpi_snapshot() -> dict:
    """Snapshot des KPI pour le dashboard"""
    rows = list_articles()
    total = len(rows)
    published = sum(1 for r in rows if r.get("status") == "published")
    scheduled = sum(1 for r in rows if r.get("status") == "scheduled")
    drafts = sum(1 for r in rows if r.get("status") == "draft")
    validation = sum(1 for r in rows if r.get("status") == "validation")
    subscribers = len(list_subscribers())
    monthly_goal = 16
    progress = min(100, int(((published + scheduled) / monthly_goal) * 100)) if monthly_goal else 0
    
    return {
        "total": total,
        "published": published,
        "scheduled": scheduled,
        "drafts": drafts,
        "validation": validation,
        "subscribers": subscribers,
        "monthly_goal": monthly_goal,
        "progress": progress,
    }


def init_store() -> None:
    if STORE_PATH.exists():
        return

    seed = {
        "articles": [],
        "signals": [],
        "watch_entries": [],
        "subscribers": [],
        "settings": {
            "double_check_required": True,
            "min_sources": 3,
            "daily_ritual_duration": 90,  # minutes
            "publication_cadence": {
                "briefs_per_week": 2,
                "analyses_per_week": 1,
                "country_notes_per_week": 1
            }
        }
    }
    STORE_PATH.write_text(json.dumps(seed, ensure_ascii=True, indent=2), encoding="utf-8")


def _load() -> dict:
    return json.loads(STORE_PATH.read_text(encoding="utf-8"))


def _save(payload: dict) -> None:
    STORE_PATH.write_text(json.dumps(payload, ensure_ascii=True, indent=2), encoding="utf-8")


# ============ ARTICLES ============

def list_articles() -> list[dict]:
    payload = _load()
    return sorted(payload["articles"], key=lambda x: x["id"], reverse=True)


def list_by_status(status: str) -> list[dict]:
    return [a for a in list_articles() if a.get("status") == status]


def list_published(limit: int | None = None) -> list[dict]:
    rows = list_by_status("published")
    return rows[:limit] if limit else rows


def get_article_by_slug(slug: str) -> dict | None:
    for row in list_published():
        if row.get("slug") == slug:
            return row
    return None


def get_any_article_by_slug(slug: str) -> dict | None:
    """Récupère un article quel que soit son statut (pour preview admin)"""
    for row in list_articles():
        if row.get("slug") == slug:
            return row
    return None


def get_article_by_id(article_id: int) -> dict | None:
    for row in list_articles():
        if row["id"] == article_id:
            return row
    return None


def featured_article() -> dict | None:
    for row in list_published():
        if row.get("is_featured") == 1:
            return row
    rows = list_published(limit=1)
    return rows[0] if rows else None


def create_article(rubrique: str, title: str, excerpt: str, body: str, 
                  reading_time: str, format: str = "brief", author: str = "VA Desk",
                  sources: list = None, scheduled_at: str = None) -> int:
    payload = _load()
    next_id = max((a["id"] for a in payload["articles"]), default=0) + 1
    base_slug = _slugify(title)
    slug = base_slug
    existing = {a.get("slug") for a in payload["articles"]}
    i = 2
    while slug in existing:
        slug = f"{base_slug}-{i}"
        i += 1

    payload["articles"].append({
        "id": next_id,
        "rubrique": rubrique,
        "title": title,
        "slug": slug,
        "excerpt": excerpt,
        "body": body,
        "format": format,
        "reading_time": reading_time,
        "status": "scheduled" if scheduled_at else "draft",
        "is_featured": 0,
        "published_at": None,
        "scheduled_at": scheduled_at,
        "created_at": str(date.today()),
        "author": author,
        "sources": sources or [],
        "tags": [],
        "quality_filter": None,
        "verification_checklist": {
            "sources_verified": bool(sources and len(sources) >= 3),
            "facts_checked": False,
            "peer_reviewed": False
        }
    })
    _save(payload)
    return next_id


def update_article(article_id: int, **kwargs) -> bool:
    payload = _load()
    for row in payload["articles"]:
        if row["id"] == article_id:
            row.update(kwargs)
            _save(payload)
            return True
    return False


def publish_article(article_id: int) -> bool:
    article = get_article_by_id(article_id)
    if not article:
        return False
    
    if not article.get("sources") or len(article.get("sources", [])) < 3:
        return False
    
    checklist = article.get("verification_checklist", {})
    if not all(checklist.values()):
        return False
    
    return update_article(article_id, 
                         status="published",
                         published_at=str(date.today()))


def schedule_article(article_id: int, scheduled_at: str) -> bool:
    """Planifier un article pour une date donnée"""
    return update_article(article_id, status="scheduled", scheduled_at=scheduled_at)


def move_to_validation(article_id: int) -> bool:
    return update_article(article_id, status="validation")


def feature_article(article_id: int) -> None:
    payload = _load()
    for row in payload["articles"]:
        row["is_featured"] = 1 if row["id"] == article_id else 0
    _save(payload)


# ============ QUALITY FILTER ============

def add_quality_filter(article_id: int, actor: str, agenda: str, evidence: str, 
                       contradiction: str, consequence: str, angle: str) -> bool:
    """Ajouter les filtres de qualité à un article"""
    quality_filter = {
        "actor": actor,
        "agenda": agenda,
        "evidence": evidence,
        "contradiction": contradiction,
        "consequence": consequence,
        "angle": angle,
        "verified_at": str(datetime.now())
    }
    return update_article(article_id, quality_filter=quality_filter)


# ============ WATCH ENTRIES (Veille quotidienne) ============

def add_watch_entry(block: str, headline: str, source_id: int, alert_type: str = "signal", notes: str = "") -> int:
    """Ajouter une entrée de veille (headline, signal faible, etc.)"""
    payload = _load()
    entries = payload.setdefault("watch_entries", [])
    next_id = max((e["id"] for e in entries), default=100) + 1
    
    source = next((s for s in CORE_SOURCES if s["id"] == source_id), None)
    
    entries.append({
        "id": next_id,
        "date": str(date.today()),
        "time": str(datetime.now().strftime("%H:%M")),
        "block": block,
        "headline": headline,
        "source": source.get("name") if source else "Unknown",
        "source_id": source_id,
        "alert_type": alert_type,  # "headline", "weak_signal", "validation"
        "notes": notes,
        "status": "new"
    })
    _save(payload)
    return next_id


def list_watch_entries(block: str = None, alert_type: str = None, status: str = "new") -> list[dict]:
    """Lister les entrées de veille"""
    payload = _load()
    entries = payload.get("watch_entries", [])
    
    filtered = entries
    if block:
        filtered = [e for e in filtered if e.get("block") == block]
    if alert_type:
        filtered = [e for e in filtered if e.get("alert_type") == alert_type]
    if status:
        filtered = [e for e in filtered if e.get("status") == status]
    
    return sorted(filtered, key=lambda x: x["date"], reverse=True)


def update_watch_entry(entry_id: int, status: str) -> bool:
    payload = _load()
    for entry in payload.get("watch_entries", []):
        if entry["id"] == entry_id:
            entry["status"] = status
            _save(payload)
            return True
    return False


# ============ SIGNALS (Veille) ============

def add_signal(headline: str, source: str, pillar: str, notes: str = "") -> int:
    payload = _load()
    signals = payload.setdefault("signals", [])
    next_id = max((s["id"] for s in signals), default=100) + 1
    
    signals.append({
        "id": next_id,
        "date": str(date.today()),
        "headline": headline,
        "source": source,
        "pillar": pillar,
        "status": "new",
        "notes": notes
    })
    _save(payload)
    return next_id


def list_signals(status: str = "new") -> list[dict]:
    payload = _load()
    signals = payload.get("signals", [])
    return sorted([s for s in signals if s.get("status") == status], 
                 key=lambda x: x["date"], reverse=True)


def update_signal(signal_id: int, status: str) -> bool:
    payload = _load()
    for sig in payload.get("signals", []):
        if sig["id"] == signal_id:
            sig["status"] = status
            _save(payload)
            return True
    return False


# ============ NEWSLETTER ============

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
