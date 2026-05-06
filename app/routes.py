import csv
import io
import os
import json
from datetime import date, timedelta
from flask import Blueprint, Response, abort, flash, redirect, render_template, request, session, url_for, jsonify

from .data import (
    add_subscriber, create_article, feature_article as set_featured, featured_article,
    get_article_by_slug, get_any_article_by_slug, list_articles, list_published, list_subscribers,
    publish_article as set_published, list_by_status, get_article_by_id, update_article,
    add_signal, list_signals, update_signal, move_to_validation, schedule_article,
    add_quality_filter, detect_country_flag, _kpi_snapshot, PILLARS, FORMATS,
)
from .newsletter_provider import subscribe_email

bp = Blueprint("main", __name__)


def _admin_allowed() -> bool:
    """Vérifier si l'admin est autorisé (localhost ou session)"""
    if request.remote_addr in {"127.0.0.1", "::1", "localhost"}:
        return True
    return bool(session.get("editor_ok"))


# ========== PUBLIC ROUTES ==========

@bp.route("/")
def home():
    featured_row = featured_article()
    featured = {
        "tag": featured_row["rubrique"] if featured_row else "Analyse de fond",
        "title": featured_row["title"] if featured_row else "Article à venir",
        "excerpt": featured_row["excerpt"] if featured_row else "Publication en préparation.",
        "slug": featured_row["slug"] if featured_row else "",
        "flag": detect_country_flag(f"{featured_row.get('title', '')} {featured_row.get('excerpt', '')}") if featured_row else "",
    }

    headlines = [
        {
            "rubrique": row["rubrique"],
            "title": row["title"],
            "slug": row["slug"],
            "date": row["published_at"] or "À paraître",
            "reading_time": row["reading_time"],
            "flag": detect_country_flag(f"{row.get('title', '')} {row.get('excerpt', '')}"),
        }
        for row in list_published(limit=3)
    ]
    return render_template("home.html", featured=featured, headlines=headlines, meta_description="Revue géopolitique africaine: analyses de fond, diplomatie, sécurité, ressources et veille stratégique.")


@bp.route("/articles")
def articles():
    rows = list_published()
    return render_template("articles.html", rows=rows, meta_description="Tous les articles publiés par Valeurs Africaines.")


@bp.route("/articles/<slug>")
def article_detail(slug: str):
    article = get_article_by_slug(slug)
    if not article:
        abort(404)
    return render_template("article_detail.html", article=article, meta_description=article["excerpt"])


@bp.route("/rubriques")
def rubriques():
    return render_template("rubriques.html", meta_description="Rubriques de Valeurs Africaines: diplomatie, sécurité, ressources, économie politique.")


@bp.route("/a-propos")
def about():
    return render_template("about.html", meta_description="À propos de Valeurs Africaines, revue géopolitique francophone.")


@bp.route("/methodologie")
def methodology():
    return render_template("methodology.html", meta_description="Méthodologie éditoriale et standards de vérification de Valeurs Africaines.")


@bp.route("/politique-correction")
def correction_policy():
    return render_template("correction_policy.html", meta_description="Politique de correction et droit de signalement de Valeurs Africaines.")


@bp.route("/newsletter")
def newsletter():
    substack_url = os.getenv("SUBSTACK_URL", "").strip()
    return render_template("newsletter.html", substack_url=substack_url, meta_description="Inscription à la newsletter géopolitique hebdomadaire de Valeurs Africaines.")


@bp.route("/newsletter/subscribe", methods=["POST"])
def newsletter_subscribe():
    email = request.form.get("email", "").strip().lower()
    if "@" not in email:
        flash("Adresse e-mail invalide.")
        return redirect(request.referrer or url_for("main.newsletter"))

    if not add_subscriber(email):
        flash("Adresse déjà inscrite.")
        return redirect(request.referrer or url_for("main.newsletter"))

    pushed, reason = subscribe_email(email)
    if pushed:
        flash("Inscription confirmée.")
    else:
        if reason == "brevo_not_configured":
            flash("Inscription enregistrée (mode local). Configure BREVO_API_KEY et BREVO_LIST_ID pour synchroniser automatiquement.")
        else:
            flash("Inscription enregistrée. Synchronisation externe temporairement indisponible.")

    return redirect(request.referrer or url_for("main.newsletter"))


@bp.route("/contact")
def contact():
    return render_template("contact.html", meta_description="Contacter la rédaction de Valeurs Africaines.")


@bp.route("/mentions-legales")
def legal():
    return render_template("legal.html", meta_description="Mentions légales de Valeurs Africaines.")


@bp.route("/sitemap.xml")
def sitemap():
    base = request.url_root.rstrip("/")
    static_paths = [
        "", "/articles", "/rubriques", "/a-propos", "/methodologie", "/politique-correction",
        "/newsletter", "/contact", "/mentions-legales",
    ]
    article_paths = [f"/articles/{row['slug']}" for row in list_published()]
    all_paths = static_paths + article_paths

    xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for p in all_paths:
        xml.append("  <url>")
        xml.append(f"    <loc>{base}{p}</loc>")
        xml.append("  </url>")
    xml.append("</urlset>")
    return Response("\n".join(xml), mimetype="application/xml")


# ========== EDITOR DASHBOARD & ARTICLE EDITOR ==========

@bp.route("/editor", methods=["GET", "POST"])
def editor_dashboard():
    if not _admin_allowed():
        return redirect(url_for("main.editor_login"))

    drafts = list_by_status("draft")
    validations = list_by_status("validation")
    scheduled = list_by_status("scheduled")
    published = list_published()
    signals_new = list_signals("new")
    kpi = _kpi_snapshot()

    publications_by_day = [[] for _ in range(7)]
    for pub in published[:30]:
        pub_date = pub.get("published_at")
        if pub_date:
            try:
                pub_dt = date.fromisoformat(pub_date)
                today = date.today()
                days_ago = (today - pub_dt).days
                if 0 <= days_ago < 7:
                    publications_by_day[days_ago].append(pub)
            except:
                pass

    return render_template(
        "editor_dashboard.html",
        drafts=drafts,
        validations=validations,
        scheduled=scheduled,
        published=published,
        signals_new=signals_new,
        publications_by_day=publications_by_day,
        kpi=kpi,
        pillars=PILLARS,
        formats=FORMATS,
    )


@bp.route("/editor/login", methods=["GET", "POST"])
def editor_login():
    if request.method == "POST":
        password = request.form.get("password", "")
        expected = os.getenv("VA_ADMIN_PASSWORD", "va-admin-2026")
        if password == expected:
            session["editor_ok"] = True
            return redirect(url_for("main.editor_dashboard"))
        flash("Mot de passe incorrect.")
    return render_template("editor_login.html", meta_description="Connexion éditeur.")


@bp.route("/editor/logout")
def editor_logout():
    session.pop("editor_ok", None)
    return redirect(url_for("main.editor_login"))


@bp.route("/editor/article/new", methods=["GET", "POST"])
def editor_new_article():
    if not _admin_allowed():
        return redirect(url_for("main.editor_login"))

    if request.method == "POST":
        rubrique = request.form.get("rubrique", "").strip()
        title = request.form.get("title", "").strip()
        excerpt = request.form.get("excerpt", "").strip()
        body = request.form.get("body", "").strip()
        reading_time = request.form.get("reading_time", "7 min").strip()
        format_type = request.form.get("format", "brief").strip()
        author = request.form.get("author", "VA Desk").strip()
        tags = request.form.get("tags", "").split(",")
        tags = [t.strip() for t in tags if t.strip()]
        sources_raw = request.form.get("sources", "").strip()
        sources = [line.strip() for line in sources_raw.splitlines() if line.strip()]
        scheduled_at = request.form.get("scheduled_at", "").strip() or None

        if rubrique and title and excerpt and body:
            article_id = create_article(
                rubrique=rubrique, title=title, excerpt=excerpt, body=body,
                reading_time=reading_time, format=format_type, author=author,
                sources=sources, scheduled_at=scheduled_at
            )
            article = get_article_by_id(article_id)
            if article:
                update_article(article_id, tags=tags)
            flash("Article créé en brouillon.")
            return redirect(url_for("main.editor_dashboard"))
        flash("Tous les champs obligatoires doivent être remplis.")

    return render_template(
        "article_editor.html",
        article=None,
        pillars=PILLARS,
        formats=FORMATS,
    )


@bp.route("/editor/article/<int:article_id>", methods=["GET", "POST"])
def editor_edit_article(article_id):
    if not _admin_allowed():
        return redirect(url_for("main.editor_login"))

    article = get_article_by_id(article_id)
    if not article:
        abort(404)

    if request.method == "POST":
        rubrique = request.form.get("rubrique", "").strip()
        title = request.form.get("title", "").strip()
        excerpt = request.form.get("excerpt", "").strip()
        body = request.form.get("body", "").strip()
        reading_time = request.form.get("reading_time", "7 min").strip()
        format_type = request.form.get("format", "brief").strip()
        author = request.form.get("author", "VA Desk").strip()
        tags = request.form.get("tags", "").split(",")
        tags = [t.strip() for t in tags if t.strip()]
        sources_raw = request.form.get("sources", "").strip()
        sources = [line.strip() for line in sources_raw.splitlines() if line.strip()]
        scheduled_at = request.form.get("scheduled_at", "").strip() or None

        if rubrique and title and excerpt and body:
            update_article(
                article_id,
                rubrique=rubrique, title=title, excerpt=excerpt, body=body,
                reading_time=reading_time, format=format_type, author=author,
                tags=tags, sources=sources, scheduled_at=scheduled_at
            )
            flash("Article mise à jour.")
            return redirect(url_for("main.editor_dashboard"))
        flash("Tous les champs obligatoires doivent être remplis.")

    return render_template(
        "article_editor.html",
        article=article,
        pillars=PILLARS,
        formats=FORMATS,
    )


# ========== QUALITY FILTER ==========

@bp.route("/editor/quality-filter/<int:article_id>", methods=["GET", "POST"])
def quality_filter(article_id):
    if not _admin_allowed():
        return redirect(url_for("main.editor_login"))

    article = get_article_by_id(article_id)
    if not article:
        abort(404)

    if request.method == "POST":
        actor = request.form.get("actor", "").strip()
        agenda = request.form.get("agenda", "").strip()
        evidence = request.form.get("evidence", "").strip()
        contradiction = request.form.get("contradiction", "").strip()
        consequence = request.form.get("consequence", "").strip()
        angle = request.form.get("angle", "").strip()

        if all([actor, agenda, evidence, contradiction, consequence, angle]):
            add_quality_filter(article_id, actor, agenda, evidence, contradiction, consequence, angle)
            flash("Filtres de qualité appliqués.")
            return redirect(url_for("main.editor_dashboard"))
        flash("Tous les champs sont obligatoires.")

    return render_template("quality_filter.html", article=article)


# ========== EDITOR API ==========

@bp.route("/api/article/<int:article_id>/move-validation", methods=["POST"])
def api_move_validation(article_id):
    if not _admin_allowed():
        return jsonify({"error": "Unauthorized"}), 403
    if move_to_validation(article_id):
        return jsonify({"status": "ok"})
    return jsonify({"error": "Article not found"}), 404


@bp.route("/api/article/<int:article_id>/publish", methods=["POST"])
def api_publish(article_id):
    if not _admin_allowed():
        return jsonify({"error": "Unauthorized"}), 403
    
    article = get_article_by_id(article_id)
    if not article or not article.get("sources"):
        return jsonify({"error": "Publication blocked: add sources"}), 400
    
    if set_published(article_id):
        return jsonify({"status": "published"})
    return jsonify({"error": "Cannot publish - validation incomplete"}), 400


@bp.route("/api/article/<int:article_id>/feature", methods=["POST"])
def api_feature(article_id):
    if not _admin_allowed():
        return jsonify({"error": "Unauthorized"}), 403
    set_featured(article_id)
    return jsonify({"status": "featured"})


@bp.route("/api/article/<int:article_id>/schedule", methods=["POST"])
def api_schedule(article_id):
    if not _admin_allowed():
        return jsonify({"error": "Unauthorized"}), 403
    
    scheduled_at = request.get_json().get("scheduled_at")
    if not scheduled_at:
        return jsonify({"error": "Date required"}), 400
    
    if schedule_article(article_id, scheduled_at):
        return jsonify({"status": "scheduled"})
    return jsonify({"error": "Article not found"}), 404


@bp.route("/api/article/<int:article_id>/checklist", methods=["POST"])
def api_update_checklist(article_id):
    if not _admin_allowed():
        return jsonify({"error": "Unauthorized"}), 403
    
    data = request.get_json()
    article = get_article_by_id(article_id)
    if not article:
        return jsonify({"error": "Article not found"}), 404

    field = data.get("field")
    value = data.get("value")
    
    checklist = article.get("verification_checklist", {})
    checklist[field] = value
    update_article(article_id, verification_checklist=checklist)
    
    return jsonify({"status": "updated", "checklist": checklist})


@bp.route("/api/signal", methods=["POST"])
def api_add_signal():
    if not _admin_allowed():
        return jsonify({"error": "Unauthorized"}), 403
    
    data = request.get_json()
    signal_id = add_signal(
        headline=data.get("headline"),
        source=data.get("source"),
        pillar=data.get("pillar"),
        notes=data.get("notes", "")
    )
    return jsonify({"status": "created", "id": signal_id})


@bp.route("/api/signal/<int:signal_id>/status", methods=["POST"])
def api_signal_status(signal_id):
    if not _admin_allowed():
        return jsonify({"error": "Unauthorized"}), 403
    
    status = request.get_json().get("status")
    if update_signal(signal_id, status):
        return jsonify({"status": "updated"})
    return jsonify({"error": "Signal not found"}), 404


# ========== ADMIN PREVIEW ==========

@bp.route("/admin/preview/<slug>")
def admin_preview(slug: str):
    if not _admin_allowed():
        return redirect(url_for("main.editor_login"))
    
    article = get_any_article_by_slug(slug)
    if not article:
        abort(404)
    
    return render_template("article_detail.html", article=article, preview=True, meta_description="Admin preview")


# ========== LEGACY ADMIN ==========

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
        reading_time = request.form.get("reading_time", "7 min").strip()
        author = request.form.get("author", "VA Desk").strip()
        sources_raw = request.form.get("sources", "").strip()
        sources = [line.strip() for line in sources_raw.splitlines() if line.strip()]
        scheduled_at = request.form.get("scheduled_at", "").strip() or None

        if rubrique and title and excerpt and body and sources:
            create_article(rubrique, title, excerpt, body, reading_time, author=author, sources=sources, scheduled_at=scheduled_at)
            flash("Article créé en brouillon.")
            return redirect(url_for("main.admin"))
        flash("Tous les champs obligatoires doivent être remplis, y compris les sources.")

    rows = list_articles()
    kpi = _kpi_snapshot()
    return render_template("admin.html", rows=rows, kpi=kpi, meta_description="Back-office Valeurs Africaines.")


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
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=newsletter-subscribers.csv"},
    )


@bp.route("/admin/publish/<int:article_id>", methods=["POST"])
def publish_article(article_id: int):
    if not _admin_allowed():
        return redirect(url_for("main.admin_login"))
    
    article = get_article_by_id(article_id)
    if not article or not article.get("sources"):
        flash("Publication bloquée: ajoutez les sources de l'article.")
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
def schedule_one_article(article_id: int):
    if not _admin_allowed():
        return redirect(url_for("main.admin_login"))
    
    scheduled_at = request.form.get("scheduled_at", "").strip()
    if not scheduled_at:
        flash("Date de publication requise.")
        return redirect(url_for("main.admin"))
    
    schedule_article(article_id, scheduled_at)
    flash("Article planifié.")
    return redirect(url_for("main.admin"))
