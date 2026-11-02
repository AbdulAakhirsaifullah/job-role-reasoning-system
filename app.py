"""
app.py
------
Streamlit interface for the Intelligent Job Role & Skill Matching Reasoning System.

Run locally:   streamlit run app.py

This file only:
  1. collects the candidate profile (sidebar),
  2. calls the reasoning engine (reasoning_engine.py),
  3. shows the results (helpers for HTML and downloads are in ui_helpers.py).
No reasoning happens here.
"""

import os

import streamlit as st
import streamlit.components.v1 as components

from knowledge_base import (
    CANDIDATE_FRAME_TEMPLATE,
    CERTIFICATION_FRAME_TEMPLATE,
    CERTIFICATION_FRAMES,
    DEGREE_WAIVER_YEARS,
    JOB_ROLE_FRAME_TEMPLATE,
    JOB_ROLE_FRAMES,
    QUALIFICATION_FRAME_TEMPLATE,
    QUALIFICATION_FRAMES,
    RECOMMENDATION_SCRIPT,
    RULES,
    SAMPLE_CANDIDATES,
    SKILL_CATEGORIES,
    SKILL_FRAME_TEMPLATE,
    SKILL_FRAMES,
    build_candidate_facts,
    build_domain_facts,
    create_candidate,
)
from reasoning_engine import (
    STATUS_ELIGIBLE,
    STATUS_NOT_MATCHED,
    STATUS_PARTIAL,
    atom_to_text,
    backward_chain,
    recommend_all_roles,
    rule_to_text,
    sort_key,
)
from ui_helpers import (
    CSS,
    network_data,
    network_html,
    proof_tree_html,
    result_json,
    result_pdf,
    role_card_html,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CUSTOM = "Custom profile"


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------

def skill_name(skill_id):
    return SKILL_FRAMES[skill_id]["name"]


def names(skill_ids):
    return ", ".join(skill_name(s) for s in skill_ids) if skill_ids else "none"


def load_profile(data):
    """Copy a profile into the sidebar widgets (through their session_state keys)."""
    st.session_state["name"] = data["name"]
    for category in SKILL_CATEGORIES:
        st.session_state[f"skills_{category}"] = [
            s for s in data["skills"] if SKILL_FRAMES[s]["category"] == category]
    st.session_state["degree"] = data["degree"] or "none"
    st.session_state["years"] = int(data["experience_years"] or 0)
    st.session_state["certs"] = list(data["certifications"])


def on_sample_change():
    key = st.session_state["sample"]
    if key in SAMPLE_CANDIDATES:
        load_profile(SAMPLE_CANDIDATES[key])


def clear_form():
    st.session_state["sample"] = CUSTOM
    load_profile({"name": "", "skills": [], "degree": "none", "experience_years": 0,
                  "certifications": []})


def analyse(data):
    """Build a candidate frame from a profile and run the reasoning."""
    candidate, warnings = create_candidate(data["name"], data["skills"], data["degree"],
                                           data["experience_years"], data["certifications"])
    results, all_facts, derived, trace, unsatisfied = recommend_all_roles(candidate)
    return candidate, warnings, results, all_facts, derived, trace, unsatisfied


# ---------------------------------------------------------------------------
# Page set-up and sidebar form
# ---------------------------------------------------------------------------

st.set_page_config(page_title="Job Role Reasoner", page_icon="🧭", layout="wide")
st.markdown(CSS, unsafe_allow_html=True)

if "name" not in st.session_state:
    first = next(iter(SAMPLE_CANDIDATES))
    st.session_state["sample"] = first
    load_profile(SAMPLE_CANDIDATES[first])

with st.sidebar:
    st.header("Candidate profile")
    st.selectbox("Load a sample candidate", [CUSTOM] + list(SAMPLE_CANDIDATES),
                 key="sample", on_change=on_sample_change)
    st.text_input("Name", key="name", placeholder="e.g. Ayesha Khan")
    st.caption("Skills, grouped by category")
    for category, label in SKILL_CATEGORIES.items():
        options = [s for s, f in SKILL_FRAMES.items() if f["category"] == category]
        st.multiselect(label, options, format_func=skill_name, key=f"skills_{category}")
    st.selectbox("Highest degree", list(QUALIFICATION_FRAMES),
                 format_func=lambda d: QUALIFICATION_FRAMES[d]["name"], key="degree")
    st.number_input("Years of experience", min_value=0, max_value=50, step=1, key="years")
    st.multiselect("Certifications", list(CERTIFICATION_FRAMES),
                   format_func=lambda c: CERTIFICATION_FRAMES[c]["name"], key="certs")
    st.button("Clear form", on_click=clear_form)
    st.caption("Results update as you change the profile.")

profile = {
    "name": st.session_state["name"],
    "skills": [s for c in SKILL_CATEGORIES for s in st.session_state[f"skills_{c}"]],
    "degree": st.session_state["degree"],
    "experience_years": st.session_state["years"],
    "certifications": st.session_state["certs"],
}
candidate, warnings, results, all_facts, derived, trace, unsatisfied = analyse(profile)
cid = candidate["candidate_id"]


# ---------------------------------------------------------------------------
# Hero, verdict and downloads
# ---------------------------------------------------------------------------

st.markdown(
    """
<div class="hero">
  <h1>Intelligent Job Role &amp; Skill Matching</h1>
  <div class="clause">recommended(X, R) :- eligible(X, R).</div>
  <p>A rule-based reasoning system. It checks a profile against six job roles with
  Horn-clause rules, then shows every step: what was inferred, what is missing, and why.</p>
</div>
""", unsafe_allow_html=True)

if not profile["name"].strip():
    st.warning("Add a name in the sidebar. The profile is shown as 'Candidate' until then.")
for warning in warnings:
    st.warning(warning)
if not candidate["skills"]:
    st.info("Choose at least one skill in the sidebar. Until then every role shows Not matched.")

eligible = [r["role_name"] for r in results if r["status"] == STATUS_ELIGIBLE]
partial = [r for r in results if r["status"] == STATUS_PARTIAL]
if eligible:
    verdict = (f"{candidate['name']} is fully eligible for {len(eligible)} of "
               f"{len(results)} roles: {', '.join(eligible)}.")
elif partial:
    best = partial[0]
    verdict = (f"{candidate['name']} is not yet fully eligible for any role. Closest: "
               f"{best['role_name']}, missing {', '.join(best['unmet'])}.")
else:
    verdict = f"{candidate['name']} does not match any role yet."
st.markdown(f'<div class="verdict">{verdict}</div>', unsafe_allow_html=True)

col_json, col_pdf, _ = st.columns([1, 1, 3])
col_json.download_button("Download JSON", result_json(candidate, results),
                         file_name=f"{cid}_result.json", mime="application/json")
try:
    col_pdf.download_button("Download PDF", result_pdf(candidate, results),
                            file_name=f"{cid}_result.pdf", mime="application/pdf")
except ImportError:
    col_pdf.caption("PDF export needs the reportlab package.")

tabs = st.tabs(["Recommendations", "Explanation", "Forward chaining", "Backward chaining",
                "Knowledge base", "Semantic network", "Compare", "About"])


# ---------------------------------------------------------------------------
# Tab 1: Recommendations
# ---------------------------------------------------------------------------

with tabs[0]:
    show = st.radio("Show", ["All roles", STATUS_ELIGIBLE, STATUS_PARTIAL, STATUS_NOT_MATCHED],
                    horizontal=True, label_visibility="collapsed")
    shown = [r for r in results if show == "All roles" or r["status"] == show]
    if not shown:
        st.info(f"No role is '{show}' for this profile.")
    columns = st.columns(2)
    for i, result in enumerate(shown):
        columns[i % 2].markdown(role_card_html(result), unsafe_allow_html=True)
    st.caption("Green: requirement met. Red: requirement missing. Blue: optional bonus, "
               "which never changes the label. Role requirements are illustrative, not "
               "official industry standards.")


# ---------------------------------------------------------------------------
# Tab 2: Explanation
# ---------------------------------------------------------------------------

with tabs[1]:
    st.subheader("Why each role got its label")
    rule_for = {r["head"][2]: r for r in RULES if r["head"][0] == "eligible"}
    missing_at_end = {u["goal"]: u["missing"] for u in unsatisfied}
    for result in results:
        rule = rule_for[result["role_id"]]
        with st.expander(f"{result['role_name']}: {result['status']}",
                         expanded=result["status"] != STATUS_NOT_MATCHED):
            st.write(result["explanation"])
            st.markdown(f"The deciding rule is **{rule['id']}**:")
            st.code(rule_to_text(rule), language="prolog")
            goal = f"eligible({cid}, {result['role_id']})"
            if goal in missing_at_end:
                st.markdown("These premises were still not facts when forward chaining "
                            "stopped, so the rule could not fire (Closed World Assumption):")
                st.code("\n".join(missing_at_end[goal]), language="prolog")
            else:
                st.markdown("Every premise became a fact, so the rule fired.")


# ---------------------------------------------------------------------------
# Tab 3: Forward chaining
# ---------------------------------------------------------------------------

with tabs[2]:
    passes = max(step["pass"] for step in trace)
    st.subheader("Forward chaining (data-driven)")
    st.write(f"Started from {len(build_candidate_facts(candidate))} candidate facts and "
             f"{len(build_domain_facts())} domain facts. Derived {len(derived)} new facts "
             f"in {passes} passes, then stopped because a full pass added nothing.")
    with st.expander("Initial candidate facts"):
        st.code("\n".join(atom_to_text(f) + "."
                          for f in sorted(build_candidate_facts(candidate), key=sort_key)),
                language="prolog")
    for number in range(1, passes + 1):
        steps = [s for s in trace if s["pass"] == number and s["new_facts"]]
        count = sum(len(s["new_facts"]) for s in steps)
        title = (f"Pass {number}: {count} new facts" if count
                 else f"Pass {number}: no new facts, fixed point reached")
        with st.expander(title, expanded=(number == 1)):
            if not steps:
                st.write("Every rule was checked again and nothing new could be derived.")
            for step in steps:
                st.markdown(f"**{step['rule_id']}** `{step['rule']}`")
                st.code("\n".join(f"{item['fact']}    because {', '.join(item['because'])}"
                                  for item in step["new_facts"]), language="text")
    st.markdown("**Eligibility rules that never fired, and what they were missing**")
    if unsatisfied:
        st.table([{"Rule": u["rule_id"], "Goal": u["goal"], "Missing premises": ", ".join(u["missing"])}
                  for u in unsatisfied])
    else:
        st.write("None. Every eligibility rule fired.")


# ---------------------------------------------------------------------------
# Tab 4: Backward chaining
# ---------------------------------------------------------------------------

with tabs[3]:
    st.subheader("Backward chaining (goal-driven)")
    st.write("Pick a question. The engine starts from the goal, finds rules that could prove "
             "it, and tries to prove each premise in turn.")
    goal_type = st.selectbox("Question", ["eligible", "recommended", "meets_degree",
                                          "meets_experience", "has_skill"],
                             format_func=lambda g: {
                                 "eligible": "Is the candidate eligible for a role?",
                                 "recommended": "Is a role recommended?",
                                 "meets_degree": "Does the candidate meet a role's degree requirement?",
                                 "meets_experience": "Does the candidate meet a role's experience requirement?",
                                 "has_skill": "Does the candidate have a skill (directly or inherited)?",
                             }[g])
    if goal_type == "has_skill":
        target = st.selectbox("Skill", list(SKILL_FRAMES), format_func=skill_name,
                              index=list(SKILL_FRAMES).index("machine_learning"))
    else:
        target = st.selectbox("Role", list(JOB_ROLE_FRAMES) + ["R"],
                              format_func=lambda r: "Any role (variable R)" if r == "R"
                              else JOB_ROLE_FRAMES[r]["name"])
    goal = (goal_type, cid, target)
    proved, answers, lines, tree = backward_chain(goal, build_domain_facts() |
                                                  build_candidate_facts(candidate), RULES)
    st.markdown(f"Query: `?- {atom_to_text(goal)}.`")
    if proved:
        st.success(f"{atom_to_text(goal)} is PROVED")
        if target == "R":
            st.write("Values of R that make it true: " +
                     ", ".join(JOB_ROLE_FRAMES[a["R"]]["name"] for a in answers))
    else:
        st.error(f"{atom_to_text(goal)} is NOT PROVED")
    st.markdown("**Proof tree** (click a line to open or close it; failed branches start open)")
    st.markdown(proof_tree_html(tree), unsafe_allow_html=True)
    with st.expander(f"Full text trace ({len(lines) - 2} lines)"):
        st.code("\n".join(lines), language="text")


# ---------------------------------------------------------------------------
# Tab 5: Knowledge base
# ---------------------------------------------------------------------------

with tabs[4]:
    st.subheader("Knowledge base")
    st.caption("All requirements are illustrative, written for an academic project.")
    st.markdown("**Job Role frames**")
    st.table([{"Role": r["name"], "Mandatory skills": names(r["required_skills"]),
               "Min degree": QUALIFICATION_FRAMES[r["min_degree"]]["name"],
               "Min years": r["min_experience"],
               "Required certification": ", ".join(CERTIFICATION_FRAMES[c]["name"]
                                                   for c in r["required_certifications"]) or "none",
               "Optional skills": names(r["optional_skills"])}
              for r in JOB_ROLE_FRAMES.values()])
    left, right = st.columns(2)
    with left:
        st.markdown("**Skill frames** (is_a = parent skill)")
        st.table([{"Skill": f["name"], "Category": SKILL_CATEGORIES[f["category"]],
                   "is_a": skill_name(f["is_a"]) if f["is_a"] else ""}
                  for f in SKILL_FRAMES.values()])
    with right:
        st.markdown("**Qualification frames**")
        st.table([{"Degree": q["name"], "Rank": q["rank"]} for q in QUALIFICATION_FRAMES.values()])
        st.markdown("**Certification frames**")
        st.table([{"Certification": c["name"], "Issuer": c["issuer"]}
                  for c in CERTIFICATION_FRAMES.values()])
        st.markdown(f"**Exception:** {DEGREE_WAIVER_YEARS}+ years of experience meets any "
                    "degree requirement.")
    with st.expander("Facets and defaults of every frame"):
        facet_tabs = st.tabs(["Candidate", "Job Role", "Skill", "Qualification", "Certification"])
        for tab, template in zip(facet_tabs, [CANDIDATE_FRAME_TEMPLATE, JOB_ROLE_FRAME_TEMPLATE,
                                              SKILL_FRAME_TEMPLATE, QUALIFICATION_FRAME_TEMPLATE,
                                              CERTIFICATION_FRAME_TEMPLATE]):
            tab.json(template, expanded=False)
    with st.expander("This candidate's filled frame"):
        st.json(candidate)
    with st.expander("Script: " + RECOMMENDATION_SCRIPT["script_name"]):
        st.write("**Entry condition:** " + "; ".join(RECOMMENDATION_SCRIPT["entry_conditions"]))
        st.write("**Roles:** " + ", ".join(RECOMMENDATION_SCRIPT["roles_in_script"]))
        st.write("**Props:** " + ", ".join(RECOMMENDATION_SCRIPT["props"]))
        for scene in RECOMMENDATION_SCRIPT["scenes"]:
            st.write(scene)
        st.write("**Result:** " + "; ".join(RECOMMENDATION_SCRIPT["results"]))
    st.markdown(f"**Rules** ({len(RULES)} Horn clauses)")
    st.code("\n".join(f"% {r['id']}: {r['meaning']}\n{rule_to_text(r)}\n" for r in RULES),
            language="prolog")
    with st.expander(f"All {len(build_domain_facts())} domain facts"):
        st.code("\n".join(atom_to_text(f) + "." for f in sorted(build_domain_facts(), key=sort_key)),
                language="prolog")


# ---------------------------------------------------------------------------
# Tab 6: Semantic network
# ---------------------------------------------------------------------------

def static_dot(candidate, results, all_facts):
    """Graphviz version of the same network, for use without internet."""
    nodes, edges = network_data(candidate, results, all_facts)
    lines = ['digraph G { rankdir=LR; node [fontname="Helvetica", fontsize=10, style=filled, '
             'fillcolor="#F4F6F9"]; edge [fontname="Helvetica", fontsize=8, color="#7A8496"];']
    for n in nodes:
        fill = n.get("color") or {"candidate": "#FFF3C4", "skill": "#EAF6F2",
                                  "inferred": "#FFFFFF", "class": "#E8EBF5"}.get(n["group"], "#F4F6F9")
        font = "white" if n["group"] == "role" else "black"
        lines.append(f'"{n["id"]}" [label="{n["label"]}", fillcolor="{fill}", fontcolor="{font}", '
                     f'shape={"ellipse" if n["group"] in ("skill", "inferred", "missing") else "box"}];')
    for e in edges:
        style = ", style=dashed" if e.get("dashes") else ""
        lines.append(f'"{e["from"]}" -> "{e["to"]}" [label="{e["label"]}"{style}];')
    lines.append("}")
    return "\n".join(lines)


with tabs[5]:
    st.subheader(f"Semantic network for {candidate['name']}")
    view = st.radio("View", ["Interactive graph", "Static graph (works offline)"], horizontal=True)
    if view == "Interactive graph":
        components.html(network_html(candidate, results, all_facts), height=680)
    else:
        st.graphviz_chart(static_dot(candidate, results, all_facts))
    with st.expander("The four semantic network diagrams of the whole domain"):
        for filename, caption in [
                ("semantic_network_1_concepts.png", "1. Concepts: IS-A, HAS-A, PART-OF"),
                ("semantic_network_2_skills.png", "2. Skill taxonomy and categories"),
                ("semantic_network_3_roles.png", "3. Roles and requirements"),
                ("frame_architecture.png", "Frame architecture")]:
            path = os.path.join(BASE_DIR, "diagrams", filename)
            if os.path.exists(path):
                st.image(path, caption=caption)


# ---------------------------------------------------------------------------
# Tab 7: Compare two candidates
# ---------------------------------------------------------------------------

with tabs[6]:
    st.subheader("Compare two candidates")
    choices = ["Current profile"] + list(SAMPLE_CANDIDATES)
    col_a, col_b = st.columns(2)
    pick_a = col_a.selectbox("Candidate A", choices, index=0)
    pick_b = col_b.selectbox("Candidate B", choices, index=min(4, len(choices) - 1))

    def results_for(pick):
        if pick == "Current profile":
            return candidate, results
        cand, _, res, *_ = analyse(SAMPLE_CANDIDATES[pick])
        return cand, res

    cand_a, res_a = results_for(pick_a)
    cand_b, res_b = results_for(pick_b)
    by_a = {r["role_id"]: r for r in res_a}
    by_b = {r["role_id"]: r for r in res_b}
    st.table([{"Role": JOB_ROLE_FRAMES[rid]["name"],
               f"A: {cand_a['name']}": f"{by_a[rid]['status']} ({by_a[rid]['match_percent']}%)",
               f"B: {cand_b['name']}": f"{by_b[rid]['status']} ({by_b[rid]['match_percent']}%)",
               "Only A meets": ", ".join(c["text"] for c, d in zip(by_a[rid]["checks"], by_b[rid]["checks"])
                                         if c["met"] and not d["met"]) or "",
               "Only B meets": ", ".join(d["text"] for c, d in zip(by_a[rid]["checks"], by_b[rid]["checks"])
                                         if d["met"] and not c["met"]) or ""}
              for rid in JOB_ROLE_FRAMES])
    if cand_a["candidate_id"] == cand_b["candidate_id"]:
        st.caption("Both sides use the same name, so the comparison may show the same person twice.")


# ---------------------------------------------------------------------------
# Tab 8: About and limitations
# ---------------------------------------------------------------------------

with tabs[7]:
    st.subheader("About this system")
    st.markdown(
        f"""
This is a **symbolic, rule-based expert system**, not a trained machine learning model.
All knowledge is written by hand in `knowledge_base.py`; the engine in `reasoning_engine.py`
applies {len(RULES)} Horn-clause rules.

**Eligibility policy.** A candidate is *Fully eligible* for a role only if they have every
mandatory skill (directly or through the skill hierarchy), meet the degree requirement (or
have {DEGREE_WAIVER_YEARS}+ years of experience), meet the minimum years of experience, and
hold every required certification. *Partial match* means at least one mandatory skill but not
everything. *Not matched* means none of the mandatory skills.

**Knowledge representation used**
- Frames with slots, facets, defaults and if-needed procedures (Candidate, Job Role, Skill,
  Qualification, Certification), plus a recommendation script.
- Semantic networks with IS-A, HAS-A and PART-OF links.
- First-Order Logic and Description Logic in the report, to describe the domain formally.
- Horn clauses R1 to R{len(RULES)}, executed by forward and backward chaining.

**Limitations**
- Role requirements are simplified examples, not official hiring standards.
- Skills are yes or no; there are no skill levels.
- "Missing" and "Partial match" use the Closed World Assumption: anything not stated is false.
- The program has no full FOL prover and no Description Logic reasoner.
- The skill hierarchy only goes upward: TensorFlow implies Machine Learning, not the reverse.
- The interactive graph loads Cytoscape.js from a CDN, so it needs internet. The static view
  works offline.
""")
