import csv
import io
import os
from datetime import date

from flask import Blueprint, Response, abort, flash, redirect, render_template, request, session, url_for

from .data import (
    add_subscriber,
    create_article,
    feature_article as set_featured,
    featured_article,
    get_article_by_slug,
    get_any_article_by_slug,
    list_articles,
    list_published,
    list_subscribers,
    publish_article as set_published,
    schedule_article as set_scheduled,
)
from .newsletter_provider import subscribe_email

bp = Blueprint("main", __name__)

COUNTRY_FLAGS = {
    "algerie": "🇩🇿",
    "angola": "🇦🇴",
    "benin": "🇧🇯",
    "burkina faso": "🇧🇫",
    "cameroun": "🇨🇲",
    "cap-vert": "🇨🇻",
    "congo": "🇨🇬",
    "cote d'ivoire": "🇨🇮",
    "cote d’ivoire": "🇨🇮",
    "egypte": "🇪🇬",
    "ethiopie": "🇪🇹",
    "gabon": "🇬🇦",
    "ghana": "🇬🇭",
    "guinee": "🇬🇳",
    "kenya": "🇰🇪",
    "libye": "🇱🇾",
    "madagascar": "🇲🇬",
    "mali": "🇲🇱",
    "maroc": "🇲🇦",
    "mauritanie": "🇲🇷",
    "niger": "🇳🇪",
    "nigeria": "🇳🇬",
    "ouganda": "🇺🇬",
    "rdc": "🇨🇩",
    "rdc congo": "🇨🇩",
    "republique democratique du congo": "🇨🇩",
    "rwanda": "🇷🇼",
    "senegal": "🇸🇳",
    "somalie": "🇸🇴",
    "soudan": "🇸🇩",
    "tchad": "🇹🇩",
    "togo": "🇹🇬",
    "tunisie": "🇹🇳",
}


def _detect_country_flag(text: str) -> str:
    hay = (text or "").lower()
    for country, flag in COUNTRY_FLAGS.items():
        if country in hay:
            return flag
    return ""


def _admin_allowed() -> bool:
    if request.remote_addr in {"127.0.0.1", "::1", "localhost"}:
        return True
    return bool(session.get("admin_ok"))


def _kpi_snapshot() -> dict:
    rows = list_articles()
    total = len(rows)
    published = sum(1 for r in rows if r.get("status") == "published")
    scheduled = sum(1 for r in rows if r.get("status") == "scheduled")
    drafts = sum(1 for r in rows if r.get("status") == "draft")
    subscribers = len(list_subscribers())
    monthly_goal = 16
    progress = min(100, int((scheduled / monthly_goal) * 100)) if monthly_goal else 0
    return {
        "total": total,
        "published": published,
        "scheduled": scheduled,
        "drafts": drafts,
        "subscribers": subscribers,
        "monthly_goal": monthly_goal,
        "progress": progress,
    }


@bp.route("/")
def home():
    featured_row = featured_article()
    featured = {
        "tag": featured_row["rubrique"] if featured_row else "Analyse de fond",
        "title": featured_row["title"] if featured_row else "Article a venir",
        "excerpt": featured_row["excerpt"] if featured_row else "Publication en preparation.",
        "slug": featured_row["slug"] if featured_row else "",
    }

    published_rows = list_published(limit=12)

    headlines = [
        {
            "rubrique": row["rubrique"],
            "title": row["title"],
            "slug": row["slug"],
            "date": row["published_at"] or "A paraitre",
            "reading_time": row["reading_time"],
            "image": row.get("image"),
            "country_flag": _detect_country_flag(f"{row.get('title', '')} {row.get('excerpt', '')}") if "pays" in (row.get("rubrique", "").lower()) else "",
        }
        for row in published_rows[:3]
    ]
    today_iso = date.today().isoformat()
    today_rows = [row for row in published_rows if (row.get("published_at") or "") == today_iso]

    def _card(row):
        return {
            "rubrique": row["rubrique"],
            "title": row["title"],
            "slug": row["slug"],
            "date": row["published_at"] or "A paraitre",
        }

    def _pick(rows, predicate):
        for r in rows:
            if predicate(r):
                return r
        return None

    mali_row = _pick(
        today_rows,
        lambda r: "mali" in f"{r.get('title', '')} {r.get('excerpt', '')} {r.get('body', '')}".lower(),
    )
    sa_row = _pick(
        today_rows,
        lambda r: "afrique du sud" in f"{r.get('country', '')} {r.get('title', '')} {r.get('excerpt', '')}".lower(),
    )
    media_row = sa_row
    lifestyle_row = _pick(today_rows, lambda r: "lifestyle" in (r.get("rubrique", "").lower()))
    tech_row = _pick(today_rows, lambda r: "tech" in (r.get("rubrique", "").lower()))

    today_focus = {
        "mali": _card(mali_row) if mali_row else None,
        "media": _card(media_row) if media_row else None,
        "lifestyle": _card(lifestyle_row) if lifestyle_row else None,
        "tech": _card(tech_row) if tech_row else None,
    }

    return render_template("home.html", featured=featured, headlines=headlines, today_focus=today_focus, meta_description="Revue geopolitique africaine: analyses de fond, diplomatie, securite, ressources et veille strategique.")


@bp.route("/articles")
def articles():
    rows = list_published()
    return render_template("articles.html", rows=rows, meta_description="Tous les articles publies par Valeurs Africaines.")


@bp.route("/articles/<slug>")
def article_detail(slug: str):
    article = get_article_by_slug(slug)
    if not article:
        abort(404)
    return render_template("article_detail.html", article=article, meta_description=article["excerpt"])


@bp.route("/rubriques")
def rubriques():
    return render_template("rubriques.html", meta_description="Rubriques de Valeurs Africaines: diplomatie, securite, ressources, economie politique.")


@bp.route("/a-propos")
def about():
    return render_template("about.html", meta_description="A propos de Valeurs Africaines, revue geopolitique francophone.")


@bp.route("/methodologie")
def methodology():
    return render_template("methodology.html", meta_description="Methodologie editoriale et standards de verification de Valeurs Africaines.")


@bp.route("/politique-correction")
def correction_policy():
    return render_template("correction_policy.html", meta_description="Politique de correction et droit de signalement de Valeurs Africaines.")


@bp.route("/newsletter")
def newsletter():
    substack_url = os.getenv("SUBSTACK_URL", "").strip()
    return render_template("newsletter.html", substack_url=substack_url, meta_description="Inscription a la newsletter geopolitique hebdomadaire de Valeurs Africaines.")


@bp.route("/newsletter/subscribe", methods=["POST"])
def newsletter_subscribe():
    email = request.form.get("email", "").strip().lower()
    if "@" not in email:
        flash("Adresse e-mail invalide.")
        return redirect(request.referrer or url_for("main.newsletter"))

    if not add_subscriber(email):
        flash("Adresse deja inscrite.")
        return redirect(request.referrer or url_for("main.newsletter"))

    pushed, reason = subscribe_email(email)
    if pushed:
        flash("Inscription confirmee.")
    else:
        if reason == "brevo_not_configured":
            flash("Inscription enregistree (mode local). Configure BREVO_API_KEY et BREVO_LIST_ID pour synchroniser automatiquement.")
        else:
            flash("Inscription enregistree. Synchronisation externe temporairement indisponible.")

    return redirect(request.referrer or url_for("main.newsletter"))


@bp.route("/contact")
def contact():
    return render_template("contact.html", meta_description="Contacter la redaction de Valeurs Africaines.")


@bp.route("/mentions-legales")
def legal():
    return render_template("legal.html", meta_description="Mentions legales de Valeurs Africaines.")


@bp.route("/sitemap.xml")
def sitemap():
    base = request.url_root.rstrip("/")
    static_paths = ["", "/articles", "/rubriques", "/a-propos", "/methodologie", "/politique-correction", "/newsletter", "/contact", "/mentions-legales"]
    article_paths = [f"/articles/{row['slug']}" for row in list_published()]
    all_paths = static_paths + article_paths

    xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for p in all_paths:
        xml.append("  <url>")
        xml.append(f"    <loc>{base}{p}</loc>")
        xml.append("  </url>")
    xml.append("</urlset>")
    return Response("\n".join(xml), mimetype="application/xml")


@bp.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        password = request.form.get("password", "")
        expected = os.getenv("VA_ADMIN_PASSWORD", "va-admin-2026")
        if password == expected:
            session["admin_ok"] = True
            return redirect(url_for("main.admin"))
        flash("Mot de passe incorrect.")
    return render_template("admin_login.html", meta_description="Connexion administration.")


@bp.route("/admin/logout")
def admin_logout():
    session.pop("admin_ok", None)
    return redirect(url_for("main.admin_login"))


@bp.route("/admin", methods=["GET", "POST"])
def admin():
    if not _admin_allowed():
        return redirect(url_for("main.admin_login"))

    if request.method == "POST":
        rubrique = request.form.get("rubrique", "").strip()
        title = request.form.get("title", "").strip()
        excerpt = request.form.get("excerpt", "").strip()
        body = request.form.get("body", "").strip()
        reading_time = request.form.get("reading_time", "6 min de lecture").strip()
        author = request.form.get("author", "Redaction VA").strip()
        scheduled_at = request.form.get("scheduled_at", "").strip() or None
        sources_raw = request.form.get("sources", "").strip()
        sources = [line.strip() for line in sources_raw.splitlines() if line.strip()]

        if rubrique and title and excerpt and body and reading_time and sources:
            create_article(rubrique, title, excerpt, body, reading_time, author=author or "Redaction VA", scheduled_at=scheduled_at, sources=sources)
            flash("Article cree en brouillon.")
            return redirect(url_for("main.admin"))
        flash("Tous les champs sont obligatoires, y compris les sources.")

    rows = list_articles()
    return render_template("admin.html", rows=rows, kpi=_kpi_snapshot(), meta_description="Back-office Valeurs Africaines.")


@bp.route("/admin/verified-draft", methods=["POST"])
def create_verified_draft():
    if not _admin_allowed():
        return redirect(url_for("main.admin_login"))

    rubrique = request.form.get("rubrique", "").strip()
    title = request.form.get("title", "").strip()
    actor = request.form.get("actor", "").strip()
    agenda = request.form.get("agenda", "").strip()
    evidence = request.form.get("evidence", "").strip()
    contradiction = request.form.get("contradiction", "").strip()
    consequence = request.form.get("consequence", "").strip()
    angle = request.form.get("angle", "").strip()
    reading_time = request.form.get("reading_time", "7 min de lecture").strip()
    author = request.form.get("author", "Redaction VA").strip()
    scheduled_at = request.form.get("scheduled_at", "").strip() or None
    sources_raw = request.form.get("sources", "").strip()
    sources = [line.strip() for line in sources_raw.splitlines() if line.strip()]

    if not all([rubrique, title, actor, agenda, evidence, contradiction, consequence, angle]) or not sources:
        flash("Filtre qualite incomplet: tous les champs sont obligatoires.")
        return redirect(url_for("main.admin"))

    excerpt = f"{angle} Acteur: {actor}. Consequence geopolitique: {consequence}"
    body = (
        "Pipeline editorial: Collecte -> Tri -> Verification -> Angle -> Redaction\n\n"
        "Filtre qualite (double verification requise avant publication)\n"
        f"- Qui parle ? (acteur): {actor}\n"
        f"- Quel interet ? (agenda): {agenda}\n"
        f"- Quelle preuve ? (document/donnee/citation): {evidence}\n"
        f"- Quelle contradiction ? (contre-source): {contradiction}\n"
        f"- Quelle consequence geopolitique ? {consequence}\n\n"
        f"Angle editorial propose:\n{angle}\n"
    )
    create_article(rubrique, title, excerpt, body, reading_time, author=author or "Redaction VA", scheduled_at=scheduled_at, sources=sources)
    flash("Sujet verifie transforme en brouillon.")
    return redirect(url_for("main.admin"))


@bp.route("/admin/newsletter-subscribers.csv")
def export_subscribers_csv():
    if not _admin_allowed():
        return redirect(url_for("main.admin_login"))

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["email"])
    for email in list_subscribers():
        writer.writerow([email])

    csv_data = output.getvalue()
    return Response(csv_data, mimetype="text/csv", headers={"Content-Disposition": "attachment; filename=newsletter-subscribers.csv"})


@bp.route("/admin/publish/<int:article_id>", methods=["POST"])
def publish_article(article_id: int):
    if not _admin_allowed():
        return redirect(url_for("main.admin_login"))
    article = next((r for r in list_articles() if r.get("id") == article_id), None)
    if not article or not article.get("sources"):
        flash("Publication bloquee: ajoutez les sources de l'article.")
        return redirect(url_for("main.admin"))
    set_published(article_id)
    return redirect(url_for("main.admin"))


@bp.route("/admin/feature/<int:article_id>", methods=["POST"])
def feature_article(article_id: int):
    if not _admin_allowed():
        return redirect(url_for("main.admin_login"))
    set_featured(article_id)
    return redirect(url_for("main.admin"))


@bp.route("/admin/schedule/<int:article_id>", methods=["POST"])
def schedule_article(article_id: int):
    if not _admin_allowed():
        return redirect(url_for("main.admin_login"))
    scheduled_at = request.form.get("scheduled_at", "").strip()
    if not scheduled_at:
        flash("Date de publication requise.")
        return redirect(url_for("main.admin"))
    set_scheduled(article_id, scheduled_at)
    flash("Article planifie.")
    return redirect(url_for("main.admin"))


@bp.route("/admin/preview/<slug>")
def admin_preview(slug: str):
    if not _admin_allowed():
        return redirect(url_for("main.admin_login"))
    article = get_any_article_by_slug(slug)
    if not article:
        abort(404)
    return render_template("article_detail.html", article=article, meta_description=article.get("excerpt", "Preview article"))
