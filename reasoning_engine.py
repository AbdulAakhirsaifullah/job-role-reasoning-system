"""
reasoning_engine.py
-------------------
The REASONING ENGINE. It works on the facts and rules from knowledge_base.py.
It never imports Streamlit, so it can be tested and explained on its own.

Main functions:
  is_variable(term)                   -> True for "X", "R", "S" (uppercase first letter)
  unify(pattern, fact, binding)       -> tries to match an atom with a fact
  find_bindings(premises, facts)      -> every way a rule body can be satisfied
  forward_chain(facts, rules)         -> data-driven reasoning (facts -> new facts)
  backward_chain(goal, facts, rules)  -> goal-driven reasoning (goal -> sub-goals)
  recommend_all_roles(candidate)      -> runs forward chaining and labels every role
  evaluate_role(candidate, role_id)   -> plain Python check, used by the tests to
                                         confirm the rule-based answer

Scope: function-free Horn clauses plus one built-in comparison, gte(A, B).
It is NOT a full Prolog system: no negation inside rules, no disjunction, no cut.
"Missing requirements" and "Partial match" use the Closed World Assumption
(what cannot be derived is treated as false) and are computed AFTER chaining.
"""

from knowledge_base import (
    BUILTINS,
    CERTIFICATION_FRAMES,
    DEGREE_WAIVER_YEARS,
    JOB_ROLE_FRAMES,
    QUALIFICATION_FRAMES,
    RULES,
    SKILL_FRAMES,
    build_candidate_facts,
    build_domain_facts,
)

STATUS_ELIGIBLE = "Fully eligible"
STATUS_PARTIAL = "Partial match"
STATUS_NOT_MATCHED = "Not matched"


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------

def is_variable(term):
    """A variable is a string that starts with an uppercase letter, e.g. 'X'."""
    return isinstance(term, str) and term[:1].isupper()


def substitute(atom, binding):
    """Replace variables in an atom by their values from the binding."""
    return tuple(binding.get(t, t) if is_variable(t) else t for t in atom)


def unify(pattern, fact, binding):
    """
    Try to match a pattern atom (may contain variables) with a fact.
    Returns a NEW binding dictionary if they match, otherwise None.
      unify(("has_skill","X","python"), ("has_skill","ali","python"), {}) -> {"X": "ali"}
    """
    if len(pattern) != len(fact):
        return None
    new_binding = dict(binding)
    for p_term, f_term in zip(pattern, fact):
        if is_variable(p_term):
            if p_term in new_binding:
                if new_binding[p_term] != f_term:
                    return None
            else:
                new_binding[p_term] = f_term
        elif is_variable(f_term):
            # Only in backward chaining, when a goal still contains a variable.
            if f_term in new_binding and new_binding[f_term] != p_term:
                return None
            new_binding[f_term] = p_term
        elif p_term != f_term:
            return None
    return new_binding


def is_builtin(atom):
    return atom[0] in BUILTINS


def run_builtin(atom, binding):
    """
    Evaluate a built-in such as gte(Y, M) with the current binding.
    Both arguments must already have values (rule order guarantees this).
    Returns True or False.
    """
    args = substitute(atom, binding)[1:]
    if any(is_variable(a) for a in args):
        return False   # not enough information yet: treat as not satisfied
    return BUILTINS[atom[0]](*args)


def find_bindings(premises, facts, binding=None):
    """
    Find every binding that makes ALL premises true.
    Works left to right, like a nested loop. Built-ins are computed, not looked up.
    """
    if binding is None:
        binding = {}
    if not premises:
        return [binding]
    first, rest = premises[0], premises[1:]
    if is_builtin(first):
        return find_bindings(rest, facts, binding) if run_builtin(first, binding) else []
    results = []
    for fact in facts:
        if fact[0] != first[0]:
            continue
        new_binding = unify(first, fact, binding)
        if new_binding is not None:
            results.extend(find_bindings(rest, facts, new_binding))
    return results


def atom_to_text(atom):
    """('has_skill','ali','python') -> 'has_skill(ali, python)'"""
    return f"{atom[0]}({', '.join(str(a) for a in atom[1:])})"


def rule_to_text(rule):
    """A rule in Prolog style: head :- premise1, premise2."""
    return f"{atom_to_text(rule['head'])} :- {', '.join(atom_to_text(p) for p in rule['body'])}."


def sort_key(fact):
    """Sort facts that mix numbers and words without errors."""
    return tuple(str(part) for part in fact)


# ---------------------------------------------------------------------------
# FORWARD CHAINING (data-driven)
# ---------------------------------------------------------------------------

def missing_premises(rule, candidate_id, facts):
    """
    For the trace: bind X to the candidate and list the premises of an
    eligibility rule that are not facts in working memory.
    """
    missing = []
    for premise in rule["body"]:
        pattern = substitute(premise, {"X": candidate_id})
        if pattern not in facts:
            missing.append(atom_to_text(pattern))
    return missing


def forward_chain(initial_facts, rules, candidate_id=None, max_passes=20):
    """
    Forward chaining.

      working_memory = initial facts
      repeat (one PASS):
          for each rule, in order:
              find every binding that makes all premises true
              for each binding: build the conclusion
                  if it is new: add it to working memory and record why
      until a whole pass adds nothing new   (FIXED POINT)

    Returns (all_facts, new_facts_in_order, trace, unsatisfied_at_end).
      trace: one entry per (pass, rule) with the new facts it produced.
      unsatisfied_at_end: for each eligibility rule that never fired, the premises
                          that are still missing at the fixed point.
    """
    working_memory = set(initial_facts)
    derived_in_order = []
    trace = []

    for pass_number in range(1, max_passes + 1):
        added_this_pass = False
        for rule in rules:
            bindings = find_bindings(rule["body"], sorted(working_memory, key=sort_key))
            new_facts = []
            for binding in bindings:
                conclusion = substitute(rule["head"], binding)
                if conclusion not in working_memory:
                    working_memory.add(conclusion)
                    derived_in_order.append(conclusion)
                    new_facts.append({
                        "fact": atom_to_text(conclusion),
                        "because": [atom_to_text(substitute(p, binding)) for p in rule["body"]],
                    })
                    added_this_pass = True
            trace.append({"pass": pass_number, "rule_id": rule["id"],
                          "rule": rule_to_text(rule), "satisfied": bool(bindings),
                          "new_facts": new_facts})
        if not added_this_pass:
            break

    unsatisfied = []
    if candidate_id is not None:
        for rule in rules:
            if rule["head"][0] != "eligible":
                continue
            goal = substitute(rule["head"], {"X": candidate_id})
            if goal not in working_memory:
                unsatisfied.append({"rule_id": rule["id"], "goal": atom_to_text(goal),
                                    "missing": missing_premises(rule, candidate_id,
                                                                working_memory)})
    return working_memory, derived_in_order, trace, unsatisfied


# ---------------------------------------------------------------------------
# BACKWARD CHAINING (goal-driven)
# ---------------------------------------------------------------------------

def rename_rule(rule, counter):
    """Give the rule fresh variable names (X -> X_3) so separate uses do not clash."""
    def rename(atom):
        return tuple(f"{t}_{counter}" if is_variable(t) else t for t in atom)
    return {"id": rule["id"], "head": rename(rule["head"]),
            "body": [rename(p) for p in rule["body"]]}


def resolve(binding, atom):
    """Replace variables by values, following chains such as X_3 -> X -> ali."""
    result = []
    for term in atom:
        seen = set()
        while is_variable(term) and term in binding and term not in seen:
            seen.add(term)
            term = binding[term]
        result.append(term)
    return tuple(result)


def backward_chain(goal, facts, rules, max_depth=12):
    """
    Backward chaining.

      prove(goal):
          0. if goal is a built-in (gte), just compute it
          1. if goal matches known facts -> each match is a solution
          2. for each rule whose head matches the goal:
                 prove every premise in order (recursively)
                 if all premises are proved -> solution
          3. no solution -> failure (recorded with the reason)
      A goal with no variables stops after its first proof (one proof is enough).

    Returns (proved, answers, trace_lines, proof_tree).
      answers: values of the goal's variables for every proof found.
      proof_tree: nested dictionaries for the user interface.
    """
    lines = []
    counter = [0]

    def prove(goal_atom, binding, depth):
        indent = "    " * depth
        current = resolve(binding, goal_atom)
        node = {"goal": atom_to_text(current), "status": "fail", "how": "", "children": []}
        if depth > max_depth:
            lines.append(f"{indent}STOP: depth limit reached for {node['goal']}")
            node["how"] = "depth limit reached"
            return [], node

        if is_builtin(current):
            ok = run_builtin(current, {})
            lines.append(f"{indent}BUILT-IN: {node['goal']} is {'true' if ok else 'false'}")
            node.update(status="ok" if ok else "fail", how="built-in comparison")
            return ([binding] if ok else []), node

        lines.append(f"{indent}GOAL: {node['goal']}")
        solutions = []
        ground = not any(is_variable(t) for t in current)

        # Step 1: known facts
        for fact in sorted(facts, key=sort_key):
            if fact[0] != current[0]:
                continue
            new_binding = unify(current, fact, binding)
            if new_binding is not None:
                lines.append(f"{indent}  FACT found: {atom_to_text(fact)}")
                node["children"].append({"goal": atom_to_text(fact), "status": "ok",
                                         "how": "known fact", "children": []})
                solutions.append(new_binding)
                if ground:
                    break

        # Step 2: rules (skipped when a ground goal is already proved)
        for rule in rules:
            if ground and solutions:
                break
            if rule["head"][0] != current[0] or len(rule["head"]) != len(current):
                continue
            counter[0] += 1
            fresh = rename_rule(rule, counter[0])
            head_binding = unify(fresh["head"], current, binding)
            if head_binding is None:
                continue
            lines.append(f"{indent}  TRY rule {rule['id']}: {rule_to_text(rule)}")
            rule_node = {"goal": f"rule {rule['id']}", "status": "fail",
                         "how": rule_to_text(rule), "children": []}
            partial = [head_binding]
            for premise in fresh["body"]:
                next_partial = []
                for b in partial:
                    found, child = prove(premise, b, depth + 2)
                    rule_node["children"].append(child)
                    next_partial.extend(found)
                    if ground and found:
                        break
                if not next_partial:
                    # show the failed premise with the values known at that moment
                    lines.append(f"{indent}  FAIL rule {rule['id']}: could not prove "
                                 f"{atom_to_text(resolve(partial[0], premise))}")
                    partial = []
                    break
                partial = next_partial
            if partial:
                lines.append(f"{indent}  SUCCESS rule {rule['id']} proves "
                             f"{atom_to_text(resolve(partial[0], current))}")
                rule_node["status"] = "ok"
                solutions.extend(partial)
            node["children"].append(rule_node)

        if solutions:
            node["status"] = "ok"
        else:
            lines.append(f"{indent}  NOT PROVED: {node['goal']} "
                         f"(not a known fact, and no rule could prove it)")
            node["how"] = "not a known fact, and no rule could prove it"
        return solutions, node

    raw_solutions, tree = prove(goal, {}, 0)
    answers = []
    for solution in raw_solutions:
        answer = {t: resolve(solution, (t,))[0] for t in goal if is_variable(t)}
        if answer not in answers:
            answers.append(answer)
    proved = bool(raw_solutions)
    lines.append("")
    lines.append(f"RESULT: {atom_to_text(goal)} is {'PROVED' if proved else 'NOT PROVED'}")
    return proved, answers, lines, tree


# ---------------------------------------------------------------------------
# Role labels used by the interface
# ---------------------------------------------------------------------------

def role_requirements(role_id):
    """The list of requirements of one role, in display order."""
    role = JOB_ROLE_FRAMES[role_id]
    reqs = [("skill", s) for s in role["required_skills"]]
    reqs.append(("degree", role["min_degree"]))
    reqs.append(("experience", role["min_experience"]))
    reqs += [("certification", c) for c in role["required_certifications"]]
    return reqs


def requirement_text(kind, value):
    if kind == "skill":
        return SKILL_FRAMES[value]["name"]
    if kind == "degree":
        return f"Degree: {QUALIFICATION_FRAMES[value]['name']} or higher"
    if kind == "experience":
        return f"Experience: {value}+ years"
    return f"Certification: {CERTIFICATION_FRAMES[value]['name']}"


def label(eligible, any_skill_matched):
    if eligible:
        return STATUS_ELIGIBLE
    return STATUS_PARTIAL if any_skill_matched else STATUS_NOT_MATCHED


def recommend_all_roles(candidate):
    """
    Run forward chaining once for this candidate and label every role.
    Labels come from the derived facts:
        eligible(X, R)                      -> Fully eligible
        relevant_to(X, R) but not eligible  -> Partial match   (Closed World Assumption)
        neither                             -> Not matched
    A requirement is "met" if its fact is in working memory, otherwise "missing" (CWA).
    """
    cid = candidate["candidate_id"]
    initial = build_domain_facts() | build_candidate_facts(candidate)
    all_facts, derived, trace, unsatisfied = forward_chain(initial, RULES, candidate_id=cid)
    rank = QUALIFICATION_FRAMES[candidate["degree"]]["rank"]

    results = []
    for role_id, role in JOB_ROLE_FRAMES.items():
        checks = []
        for kind, value in role_requirements(role_id):
            if kind == "skill":
                fact = ("has_skill", cid, value)
            elif kind == "degree":
                fact = ("meets_degree", cid, role_id)
            elif kind == "experience":
                fact = ("meets_experience", cid, role_id)
            else:
                fact = ("has_cert", cid, value)
            checks.append({"kind": kind, "value": value, "text": requirement_text(kind, value),
                           "met": fact in all_facts})

        skill_checks = [c for c in checks if c["kind"] == "skill"]
        inherited = [c["value"] for c in skill_checks
                     if c["met"] and c["value"] not in candidate["skills"]]
        degree_by_exception = (("meets_degree", cid, role_id) in all_facts
                               and rank < QUALIFICATION_FRAMES[role["min_degree"]]["rank"])
        status = label(("eligible", cid, role_id) in all_facts,
                       ("relevant_to", cid, role_id) in all_facts)
        met_count = sum(c["met"] for c in checks)
        result = {
            "role_id": role_id,
            "role_name": role["name"],
            "status": status,
            "checks": checks,
            "matched": [c["value"] for c in skill_checks if c["met"]],
            "missing": [c["value"] for c in skill_checks if not c["met"]],
            "unmet": [c["text"] for c in checks if not c["met"]],
            "inherited_skills": inherited,
            "degree_by_exception": degree_by_exception,
            "optional_matched": [s for s in role["optional_skills"]
                                 if ("has_skill", cid, s) in all_facts],
            "optional_certs_held": [c for c in role["optional_certifications"]
                                    if c in candidate["certifications"]],
            "match_percent": round(100 * met_count / len(checks)),
        }
        result["explanation"] = explain(result, candidate)
        results.append(result)

    order = {STATUS_ELIGIBLE: 0, STATUS_PARTIAL: 1, STATUS_NOT_MATCHED: 2}
    results.sort(key=lambda r: (order[r["status"]], -r["match_percent"]))
    return results, all_facts, derived, trace, unsatisfied


def explain(result, candidate):
    """A short plain-English reason for the label of one role."""
    name = result["role_name"]
    notes = []
    for skill in result["inherited_skills"]:
        children = [s for s in candidate["skills"] if implies(s, skill)]
        notes.append(f"{SKILL_FRAMES[skill]['name']} was inferred from "
                     f"{', '.join(SKILL_FRAMES[c]['name'] for c in children)} (skill hierarchy)")
    if result["degree_by_exception"]:
        notes.append(f"the degree requirement is met through the experience exception "
                     f"({DEGREE_WAIVER_YEARS}+ years)")
    note_text = (" Note: " + "; ".join(notes) + ".") if notes else ""

    if result["status"] == STATUS_ELIGIBLE:
        return f"Recommended. Every requirement for {name} is met.{note_text}"
    if result["status"] == STATUS_PARTIAL:
        return (f"Not yet eligible for {name}. Missing: {', '.join(result['unmet'])}."
                f"{note_text}")
    return f"Not matched. The candidate has none of the mandatory skills for {name}."


# ---------------------------------------------------------------------------
# Independent checker (plain Python, no rules). Used only by the tests.
# ---------------------------------------------------------------------------

def implies(child, parent):
    """True if skill 'child' is the same as, or below, 'parent' in the taxonomy."""
    current = child
    while current is not None:
        if current == parent:
            return True
        current = SKILL_FRAMES[current]["is_a"]
    return False


def evaluate_role(candidate, role_id):
    """Compute the label of one role directly from the frames, without any rules."""
    role = JOB_ROLE_FRAMES[role_id]
    owned = set(candidate["skills"])
    has = {s: any(implies(o, s) for o in owned) for s in role["required_skills"]}
    rank = QUALIFICATION_FRAMES[candidate["degree"]]["rank"]
    years = candidate["total_experience_years"]
    degree_ok = (rank >= QUALIFICATION_FRAMES[role["min_degree"]]["rank"]
                 or years >= DEGREE_WAIVER_YEARS)
    experience_ok = years >= role["min_experience"]
    certs_ok = all(c in candidate["certifications"] for c in role["required_certifications"])
    eligible = all(has.values()) and degree_ok and experience_ok and certs_ok
    return {"status": label(eligible, any(has.values())),
            "missing": [s for s in role["required_skills"] if not has[s]]}
