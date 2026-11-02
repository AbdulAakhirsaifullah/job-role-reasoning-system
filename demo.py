"""
demo.py
-------
Runs every sample scenario in the terminal (no Streamlit needed).
Use it as a backup during the viva. Its output is saved in sample_outputs.txt,
and every trace in the report is copied from that file.

Run:  python demo.py
"""

from knowledge_base import (
    JOB_ROLE_FRAMES,
    RULES,
    SAMPLE_CANDIDATES,
    build_candidate_facts,
    build_domain_facts,
    create_sample_candidate,
)
from reasoning_engine import atom_to_text, backward_chain, recommend_all_roles, sort_key


def print_forward_trace(trace, derived, unsatisfied):
    print("\n  Forward chaining trace (only rules that produced new facts are listed):")
    last_pass = max(step["pass"] for step in trace)
    for step in trace:
        for item in step["new_facts"]:
            print(f"    [pass {step['pass']}] {step['rule_id']} -> {item['fact']}"
                  f"   because {', '.join(item['because'])}")
    print(f"    [pass {last_pass}] no new facts: fixed point reached")
    print(f"  Total new facts derived: {len(derived)} in {last_pass} passes")
    print("  Eligibility rules still unsatisfied at the fixed point:")
    for item in unsatisfied:
        print(f"    {item['rule_id']} {item['goal']} missing: {', '.join(item['missing'])}")


def run_scenario(title):
    candidate, warnings = create_sample_candidate(title)
    cid = candidate["candidate_id"]
    print("=" * 78)
    print("Scenario " + title)
    print("=" * 78)
    facts = sorted(build_candidate_facts(candidate), key=sort_key)
    print("  Initial candidate facts: " + ", ".join(atom_to_text(f) for f in facts))
    for warning in warnings:
        print("  Warning: " + warning)

    results, all_facts, derived, trace, unsatisfied = recommend_all_roles(candidate)
    print("\n  Role results:")
    print(f"    {'Role':<26} {'Status':<15} {'Req. met':>8}  {'Skills':>6}  Missing")
    for r in results:
        skills = f"{len(r['matched'])}/{len(r['matched']) + len(r['missing'])}"
        print(f"    {r['role_name']:<26} {r['status']:<15} {r['match_percent']:>7}%  {skills:>6}  "
              f"{', '.join(r['unmet']) if r['unmet'] else 'nothing'}")
    print_forward_trace(trace, derived, unsatisfied)

    role = candidate["target_role"] or "data_analyst"
    goal = ("eligible", cid, role)
    initial = build_domain_facts() | build_candidate_facts(candidate)
    _, _, lines, _ = backward_chain(goal, initial, RULES)
    print(f"\n  Backward chaining for {atom_to_text(goal)}:")
    for line in lines:
        print("    " + line if line else "")

    target = next(r for r in results if r["role_id"] == role)
    print(f"\n  Explanation ({JOB_ROLE_FRAMES[role]['name']}): {target['explanation']}")
    eligible = [r["role_name"] for r in results if r["status"] == "Fully eligible"]
    print(f"  FINAL RECOMMENDATION: {', '.join(eligible) if eligible else 'No role fully eligible yet'}")
    print()


if __name__ == "__main__":
    print(f"Knowledge base: {len(JOB_ROLE_FRAMES)} roles, {len(RULES)} rules, "
          f"{len(build_domain_facts())} domain facts\n")
    for title in SAMPLE_CANDIDATES:
        run_scenario(title)
