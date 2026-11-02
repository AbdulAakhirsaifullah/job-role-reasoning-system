"""
ui_helpers.py
-------------
Small helpers for the interface. No reasoning happens here: every function
only turns results from reasoning_engine.py into HTML, JSON or PDF.

  role_card_html(result)          -> one role card (badge, bar, chips)
  proof_tree_html(tree)           -> backward chaining proof as a collapsible tree
  network_html(candidate, ...)    -> interactive semantic network (Cytoscape.js)
  result_json(candidate, ...)     -> JSON text for download
  result_pdf(candidate, ...)      -> PDF bytes for download (uses reportlab)
"""

import datetime
import html
import io
import json

from knowledge_base import (
    CERTIFICATION_FRAMES,
    JOB_ROLE_FRAMES,
    QUALIFICATION_FRAMES,
    SKILL_FRAMES,
)
from reasoning_engine import STATUS_ELIGIBLE, STATUS_NOT_MATCHED, STATUS_PARTIAL

BADGE = {STATUS_ELIGIBLE: ("Eligible", "ok"),
         STATUS_PARTIAL: ("Partial", "partial"),
         STATUS_NOT_MATCHED: ("Not matched", "none")}

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap');
:root { --ink:#1E2B45; --muted:#5B6880; --paper:#F4F6F9; --line:#D9DEE7;
        --ok:#17806D; --partial:#B7791F; --none:#A8443A; --accent:#3949AB; }
html, body, [class*="css"], .stMarkdown, .stText { font-family: 'IBM Plex Sans', sans-serif; }
code, .atom { font-family: 'IBM Plex Mono', monospace; }
.block-container { padding-top: 2rem; max-width: 1180px; }
.hero { border-left: 4px solid var(--accent); padding: .4rem 0 .6rem 1.1rem; margin-bottom: 1.2rem; }
.hero h1 { font-size: 2.05rem; line-height: 1.15; margin: 0 0 .35rem 0; color: var(--ink); font-weight: 700; }
.hero .clause { font-family: 'IBM Plex Mono', monospace; font-size: 1.02rem; color: var(--accent);
                margin: .2rem 0 .5rem 0; }
.hero p { color: var(--muted); max-width: 70ch; margin: 0; }
.verdict { font-size: 1.08rem; color: var(--ink); margin: .2rem 0 1rem 0; }
.card { border: 1px solid var(--line); border-left: 6px solid var(--line); border-radius: 6px;
        padding: .85rem 1rem .8rem 1rem; background: #fff; margin-bottom: .9rem; }
.card.ok { border-left-color: var(--ok); }
.card.partial { border-left-color: var(--partial); }
.card.none { border-left-color: var(--none); }
.card .top { display: flex; justify-content: space-between; align-items: baseline; gap: .6rem; }
.card h3 { font-size: 1.06rem; margin: 0; color: var(--ink); font-weight: 600; }
.badge { font-size: .78rem; font-weight: 600; padding: .12rem .55rem; border-radius: 999px; white-space: nowrap; }
.badge.ok { background: #E3F3EF; color: var(--ok); }
.badge.partial { background: #FBF0DC; color: #8A5A10; }
.badge.none { background: #F6E4E1; color: var(--none); }
.bar { height: 7px; background: #E9ECF2; border-radius: 4px; margin: .65rem 0 .25rem 0; overflow: hidden; }
.bar span { display: block; height: 100%; }
.bar.ok span { background: var(--ok); } .bar.partial span { background: var(--partial); }
.bar.none span { background: var(--none); }
.meta { font-size: .8rem; color: var(--muted); margin-bottom: .45rem; }
.chips { display: flex; flex-wrap: wrap; gap: .3rem; margin: .15rem 0; }
.chip { font-size: .78rem; padding: .1rem .5rem; border-radius: 4px; border: 1px solid; }
.chip.met { color: #0F5E50; background: #EAF6F2; border-color: #BFE3D8; }
.chip.miss { color: #8C3027; background: #FBEDEA; border-color: #EFC9C2; }
.chip.bonus { color: #3A4373; background: #EEF0FA; border-color: #CDD2EE; }
.note { font-size: .8rem; color: var(--muted); margin-top: .45rem; }
.tree details { margin-left: 1.1rem; border-left: 1px dashed var(--line); padding-left: .6rem; }
.tree summary { cursor: pointer; font-family: 'IBM Plex Mono', monospace; font-size: .86rem; padding: .1rem 0; }
.tree .leaf { margin-left: 1.1rem; padding-left: .6rem; font-family: 'IBM Plex Mono', monospace; font-size: .86rem; }
.tree .ok { color: var(--ok); } .tree .fail { color: var(--none); }
.tree .how { color: var(--muted); font-family: 'IBM Plex Sans', sans-serif; font-size: .78rem; }
@media (max-width: 640px) { .hero h1 { font-size: 1.5rem; } .card .top { flex-direction: column; } }
</style>
"""


def esc(text):
    return html.escape(str(text))


def chip(text, kind):
    return f'<span class="chip {kind}">{esc(text)}</span>'


def role_card_html(result):
    """One role card: name, badge, requirements bar, met (green) and missing (red) chips."""
    label, kind = BADGE[result["status"]]
    met = [c for c in result["checks"] if c["met"]]
    missing = [c for c in result["checks"] if not c["met"]]
    skills_total = len(result["matched"]) + len(result["missing"])
    bonus = ([SKILL_FRAMES[s]["name"] for s in result["optional_matched"]] +
             [CERTIFICATION_FRAMES[c]["name"] for c in result["optional_certs_held"]])
    notes = []
    if result["inherited_skills"]:
        notes.append("Inferred through the skill hierarchy: " +
                     ", ".join(SKILL_FRAMES[s]["name"] for s in result["inherited_skills"]))
    if result["degree_by_exception"]:
        notes.append("Degree requirement met by the 5-year experience exception")
    parts = [
        f'<div class="card {kind}">',
        f'<div class="top"><h3>{esc(result["role_name"])}</h3>'
        f'<span class="badge {kind}">{label}</span></div>',
        f'<div class="bar {kind}"><span style="width:{result["match_percent"]}%"></span></div>',
        f'<div class="meta">{len(met)} of {len(result["checks"])} requirements met '
        f'({result["match_percent"]}%), {len(result["matched"])} of {skills_total} skills</div>',
    ]
    if met:
        parts.append('<div class="chips">' + "".join(chip(c["text"], "met") for c in met) + "</div>")
    if missing:
        parts.append('<div class="chips">' + "".join(chip(c["text"], "miss") for c in missing) + "</div>")
    if bonus:
        parts.append('<div class="chips">' + "".join(chip("Bonus: " + b, "bonus") for b in bonus) + "</div>")
    for note in notes:
        parts.append(f'<div class="note">{esc(note)}</div>')
    parts.append("</div>")
    return "".join(parts)


def proof_tree_html(tree, depth=0):
    """Backward chaining proof tree as nested <details> blocks. Failed branches start open."""
    mark = "✔" if tree["status"] == "ok" else "✘"
    css = "ok" if tree["status"] == "ok" else "fail"
    how = f' <span class="how">{esc(tree["how"])}</span>' if tree["how"] else ""
    title = f'<span class="{css}">{mark}</span> {esc(tree["goal"])}{how}'
    if not tree["children"]:
        html_text = f'<div class="leaf">{title}</div>'
    else:
        # failed branches start open so the failing premise is visible at once
        is_open = " open" if tree["status"] != "ok" or depth < 1 else ""
        inner = "".join(proof_tree_html(child, depth + 1) for child in tree["children"])
        html_text = f"<details{is_open}><summary>{title}</summary>{inner}</details>"
    return f'<div class="tree">{html_text}</div>' if depth == 0 else html_text


def network_data(candidate, results, all_facts):
    """Nodes and edges of the candidate's semantic network (stored and inferred links)."""
    cid = candidate["candidate_id"]
    color = {STATUS_ELIGIBLE: "#17806D", STATUS_PARTIAL: "#B7791F", STATUS_NOT_MATCHED: "#A8443A"}
    nodes, edges = [], []

    def add_node(node_id, label, group, **extra):
        if all(n["id"] != node_id for n in nodes):
            nodes.append({"id": node_id, "label": label, "group": group, **extra})

    add_node("Person", "Person", "class")
    add_node("Candidate", "Candidate", "class")
    add_node("JobRole", "JobRole", "class")
    edges.append({"from": "Candidate", "to": "Person", "label": "IS-A"})
    add_node(cid, candidate["name"], "candidate")
    edges.append({"from": cid, "to": "Candidate", "label": "INSTANCE-OF"})
    deg = "deg_" + candidate["degree"]
    add_node(deg, QUALIFICATION_FRAMES[candidate["degree"]]["name"], "degree")
    edges.append({"from": cid, "to": deg, "label": "HAS-A degree"})
    years = f"{candidate['total_experience_years']} years"
    add_node("years", years, "degree")
    edges.append({"from": cid, "to": "years", "label": "HAS-A experience"})
    for cert in candidate["certifications"]:
        add_node("cert_" + cert, CERTIFICATION_FRAMES[cert]["name"], "cert")
        edges.append({"from": cid, "to": "cert_" + cert, "label": "HAS-CERT"})

    held = {f[2] for f in all_facts if f[0] == "has_skill" and f[1] == cid}
    for skill in sorted(held):
        stored = skill in candidate["skills"]
        add_node(skill, SKILL_FRAMES[skill]["name"], "skill" if stored else "inferred")
        edges.append({"from": cid, "to": skill,
                      "label": "HAS-SKILL" if stored else "inferred HAS-SKILL",
                      "dashes": not stored})
        parent = SKILL_FRAMES[skill]["is_a"]
        if parent and parent in held:
            edges.append({"from": skill, "to": parent, "label": "IS-A", "width": 2})

    for r in results:
        role_id = r["role_id"]
        add_node(role_id, r["role_name"], "role", color=color[r["status"]])
        edges.append({"from": role_id, "to": "JobRole", "label": "IS-A"})
        for skill in JOB_ROLE_FRAMES[role_id]["required_skills"]:
            add_node(skill, SKILL_FRAMES[skill]["name"], "missing")
            edges.append({"from": role_id, "to": skill, "label": "REQUIRES-SKILL"})
        for cert in JOB_ROLE_FRAMES[role_id]["required_certifications"]:
            add_node("cert_" + cert, CERTIFICATION_FRAMES[cert]["name"], "cert")
            edges.append({"from": role_id, "to": "cert_" + cert, "label": "REQUIRES-CERT"})
        if r["status"] == STATUS_ELIGIBLE:
            edges.append({"from": cid, "to": role_id, "label": "inferred ELIGIBLE-FOR",
                          "dashes": True, "color": "#17806D", "width": 3})
    return nodes, edges


CYTOSCAPE_URL = "https://cdn.jsdelivr.net/npm/cytoscape@3.34.1/dist/cytoscape.min.js"


def network_html(candidate, results, all_facts, height=620, script_url=CYTOSCAPE_URL):
    """A self-contained HTML block with a draggable, zoomable Cytoscape.js graph."""
    nodes, edges = network_data(candidate, results, all_facts)
    elements = ([{"data": {"id": n["id"], "label": n["label"], "group": n["group"],
                           "color": n.get("color", "")}} for n in nodes] +
                [{"data": {"id": f"e{i}", "source": e["from"], "target": e["to"],
                           "label": e["label"],
                           "kind": "inferred" if e.get("dashes") else
                                   ("isa" if e["label"] == "IS-A" else "plain")}}
                 for i, e in enumerate(edges)])
    return f"""
<div id="net" style="height:{height}px;border:1px solid #D9DEE7;border-radius:6px;background:#fff"></div>
<p style="font:12px sans-serif;color:#5B6880;margin:4px 0">Drag nodes, scroll to zoom.
Dashed links and dashed skills are inferred by the rules; solid ones are stored facts.</p>
<script src="{script_url}"></script>
<script>
  const ink = "#1E2B45";
  cytoscape({{
    container: document.getElementById("net"),
    elements: {json.dumps(elements)},
    layout: {{name: "cose", animate: false, randomize: false, nodeRepulsion: 400000,
              idealEdgeLength: 110, edgeElasticity: 80, gravity: 0.2, numIter: 2500,
              nodeOverlap: 20, componentSpacing: 80, padding: 20, fit: true}},
    style: [
      {{selector: "node", style: {{"label": "data(label)", "font-size": 11, "color": ink,
        "text-valign": "center", "text-halign": "center", "text-wrap": "wrap",
        "text-max-width": 90, "width": "label", "height": "label", "padding": 8,
        "shape": "round-rectangle", "background-color": "#F4F6F9",
        "border-width": 1, "border-color": "#A0A8B4"}}}},
      {{selector: "node[group = 'class']", style: {{"background-color": "#E8EBF5", "border-color": "#3949AB"}}}},
      {{selector: "node[group = 'candidate']", style: {{"background-color": "#FFF3C4",
        "border-color": "#B7791F", "border-width": 2, "font-size": 14, "font-weight": 600}}}},
      {{selector: "node[group = 'skill']", style: {{"shape": "ellipse", "background-color": "#EAF6F2",
        "border-color": "#17806D"}}}},
      {{selector: "node[group = 'inferred']", style: {{"shape": "ellipse", "background-color": "#FFFFFF",
        "border-color": "#17806D", "border-style": "dashed", "border-width": 2}}}},
      {{selector: "node[group = 'missing']", style: {{"shape": "ellipse"}}}},
      {{selector: "node[group = 'cert']", style: {{"shape": "hexagon", "background-color": "#EEF0FA",
        "border-color": "#3949AB"}}}},
      {{selector: "node[group = 'role']", style: {{"background-color": "data(color)", "color": "#FFFFFF",
        "border-width": 0, "font-weight": 600}}}},
      {{selector: "edge", style: {{"label": "data(label)", "font-size": 8, "color": "#5B6880",
        "curve-style": "bezier", "target-arrow-shape": "triangle", "width": 1,
        "line-color": "#A0A8B4", "target-arrow-color": "#A0A8B4",
        "text-background-color": "#FFFFFF", "text-background-opacity": 0.85,
        "text-background-padding": 1}}}},
      {{selector: "edge[kind = 'isa']", style: {{"width": 2.5, "line-color": "#3949AB",
        "target-arrow-color": "#3949AB"}}}},
      {{selector: "edge[kind = 'inferred']", style: {{"line-style": "dashed", "width": 2,
        "line-color": "#17806D", "target-arrow-color": "#17806D"}}}}
    ]
  }});
</script>
"""


def result_dict(candidate, results):
    """Everything the user may want to keep, as plain Python data."""
    return {
        "generated": datetime.datetime.now().isoformat(timespec="seconds"),
        "system": "Intelligent Job Role & Skill Matching Reasoning System (rule-based)",
        "note": "Role requirements are illustrative, not official industry standards.",
        "candidate": candidate,
        "roles": [{
            "role": r["role_name"],
            "status": r["status"],
            "requirements_met_percent": r["match_percent"],
            "met": [c["text"] for c in r["checks"] if c["met"]],
            "missing": r["unmet"],
            "inferred_skills": r["inherited_skills"],
            "degree_by_experience_exception": r["degree_by_exception"],
            "explanation": r["explanation"],
        } for r in results],
    }


def result_json(candidate, results):
    return json.dumps(result_dict(candidate, results), indent=2)


def result_pdf(candidate, results):
    """A one-to-two page PDF summary. Returns the PDF as bytes."""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import cm
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    data = result_dict(candidate, results)
    styles = getSampleStyleSheet()
    small = styles["BodyText"].clone("small", fontSize=8.5, leading=11)
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=1.8 * cm, rightMargin=1.8 * cm,
                            topMargin=1.6 * cm, bottomMargin=1.6 * cm,
                            title="Job role reasoning result")
    c = candidate
    profile = (f"Skills: {', '.join(SKILL_FRAMES[s]['name'] for s in c['skills']) or 'none'}<br/>"
               f"Degree: {QUALIFICATION_FRAMES[c['degree']]['name']}. "
               f"Experience: {c['total_experience_years']} years ({c['experience_level']}).<br/>"
               f"Certifications: "
               f"{', '.join(CERTIFICATION_FRAMES[x]['name'] for x in c['certifications']) or 'none'}")
    story = [Paragraph("Job role reasoning result", styles["Title"]),
             Paragraph(f"Candidate: <b>{esc(c['name'])}</b>", styles["Heading2"]),
             Paragraph(profile, styles["BodyText"]), Spacer(1, 10)]
    rows = [["Role", "Status", "Met", "Missing requirements"]]
    for r in data["roles"]:
        rows.append([Paragraph(esc(r["role"]), small), Paragraph(r["status"], small),
                     f"{r['requirements_met_percent']}%",
                     Paragraph(esc(", ".join(r["missing"]) or "nothing"), small)])
    table = Table(rows, colWidths=[4.2 * cm, 2.8 * cm, 1.3 * cm, 9.1 * cm], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#DCE3F0")),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#A0A8B4")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5)]))
    story += [table, Spacer(1, 12), Paragraph("Explanations", styles["Heading2"])]
    for r in data["roles"]:
        story.append(Paragraph(f"<b>{esc(r['role'])}</b>: {esc(r['explanation'])}", small))
    story += [Spacer(1, 12), Paragraph(
        f"Generated {data['generated']} by a rule-based system using forward chaining over "
        f"Horn clauses. {data['note']}", small)]
    doc.build(story)
    return buffer.getvalue()
