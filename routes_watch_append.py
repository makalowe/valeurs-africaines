# Appends aux routes.py existantes - Ajouter ces routes après les routes existantes

@bp.route("/editor/watch-board")
def watch_board():
    """Dashboard de veille avec 4 blocs"""
    if not _admin_allowed():
        return redirect(url_for("main.editor_login"))
    
    watch_blocks = {
        "Sécurité/Conflits": list_watch_entries("Sécurité/Conflits", "headline"),
        "Diplomatie/Institutions": list_watch_entries("Diplomatie/Institutions", "headline"),
        "Ressources/Économie politique": list_watch_entries("Ressources/Économie politique", "headline"),
        "Renseignement/Influences extérieures": list_watch_entries("Renseignement/Influences extérieures", "headline"),
    }
    
    weak_signals = {
        "Sécurité/Conflits": list_watch_entries("Sécurité/Conflits", "weak_signal"),
        "Diplomatie/Institutions": list_watch_entries("Diplomatie/Institutions", "weak_signal"),
        "Ressources/Économie politique": list_watch_entries("Ressources/Économie politique", "weak_signal"),
        "Renseignement/Influences extérieures": list_watch_entries("Renseignement/Influences extérieures", "weak_signal"),
    }
    
    validations = {
        "Sécurité/Conflits": list_watch_entries("Sécurité/Conflits", "validation"),
        "Diplomatie/Institutions": list_watch_entries("Diplomatie/Institutions", "validation"),
        "Ressources/Économie politique": list_watch_entries("Ressources/Économie politique", "validation"),
        "Renseignement/Influences extérieures": list_watch_entries("Renseignement/Influences extérieures", "validation"),
    }
    
    from .data import WATCH_BLOCKS, CORE_SOURCES
    
    return render_template(
        "watch_board.html",
        watch_blocks=WATCH_BLOCKS,
        headlines=watch_blocks,
        weak_signals=weak_signals,
        validations=validations,
        core_sources=CORE_SOURCES,
    )


@bp.route("/editor/watch/sources")
def sources_core():
    """Tableau des 25 sources noyau dur"""
    if not _admin_allowed():
        return redirect(url_for("main.editor_login"))
    
    from .data import CORE_SOURCES, WATCH_BLOCKS
    
    return render_template(
        "sources_core.html",
        sources=CORE_SOURCES,
        blocks=WATCH_BLOCKS,
    )


@bp.route("/editor/pipeline")
def pipeline_editor():
    """Pipeline éditorial: Collecte → Tri → Vérification → Angle → Rédaction"""
    if not _admin_allowed():
        return redirect(url_for("main.editor_login"))
    
    # Collecte: signaux nouveaux
    collect = list_watch_entries(status="new")
    
    # Tri: entrées traitées (tagged par bloc)
    sort_entries = list_watch_entries(status="sorted")
    
    # Vérification: entrées en validation
    verify_entries = list_watch_entries(status="verified")
    
    # Angle: brouillons en préparation
    angle_drafts = list_by_status("draft")
    
    # Rédaction: articles en validation/scheduled/published
    writing = list_by_status("validation") + list_by_status("scheduled") + list_by_status("published")
    
    return render_template(
        "pipeline_editor.html",
        collect=collect,
        sort_entries=sort_entries,
        verify_entries=verify_entries,
        angle_drafts=angle_drafts,
        writing=writing,
    )


@bp.route("/editor/ritual/<phase>")
def watch_ritual(phase):
    """Rituel quotidien: morning (9h), noon (12h), evening (18h)"""
    if not _admin_allowed():
        return redirect(url_for("main.editor_login"))
    
    from .data import WATCH_BLOCKS
    
    ritual_info = {
        "morning": {
            "title": "🌅 Ritual du Matin (30 min)",
            "duration": "30 minutes",
            "task": "Scan rapide headlines + alertes",
            "instructions": [
                "1. Parcourir les 5 sources principales par bloc",
                "2. Identifier les 5-10 headlines majeures",
                "3. Taguer par bloc de veille",
                "4. Créer signaux majeurs"
            ]
        },
        "noon": {
            "title": "☀️ Ritual du Midi (30 min)",
            "duration": "30 minutes",
            "task": "Sélection 3 signaux faibles",
            "instructions": [
                "1. Relire les headlines du matin",
                "2. Chercher les angles non-évidents",
                "3. Creuser 2-3 pistes secondaires",
                "4. Créer 3 signaux faibles prioritaires"
            ]
        },
        "evening": {
            "title": "🌙 Ritual du Soir (30 min)",
            "duration": "30 minutes",
            "task": "Validation des faits + notes demain",
            "instructions": [
                "1. Double-vérifier les 3 signaux faibles",
                "2. Recouper avec sources indépendantes",
                "3. Appliquer filtre qualité si pertinent",
                "4. Créer brouillon si validation OK"
            ]
        }
    }
    
    ritual = ritual_info.get(phase, ritual_info["morning"])
    
    return render_template(
        "watch_ritual.html",
        phase=phase,
        ritual=ritual,
        watch_blocks=WATCH_BLOCKS,
        watch_entries=list_watch_entries(),
        core_sources=CORE_SOURCES,
    )


@bp.route("/api/watch/add-entry", methods=["POST"])
def api_add_watch_entry():
    """Ajouter une entrée de veille"""
    if not _admin_allowed():
        return jsonify({"error": "Unauthorized"}), 403
    
    data = request.get_json()
    entry_id = add_watch_entry(
        block=data.get("block"),
        headline=data.get("headline"),
        source_id=data.get("source_id"),
        alert_type=data.get("alert_type", "headline"),
        notes=data.get("notes", "")
    )
    return jsonify({"status": "created", "id": entry_id})


@bp.route("/api/watch/entry/<int:entry_id>/status", methods=["POST"])
def api_watch_entry_status(entry_id):
    """Mettre à jour le statut d'une entrée de veille"""
    if not _admin_allowed():
        return jsonify({"error": "Unauthorized"}), 403
    
    status = request.get_json().get("status")
    if update_watch_entry(entry_id, status):
        return jsonify({"status": "updated"})
    return jsonify({"error": "Entry not found"}), 404
