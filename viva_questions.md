# Viva Preparation: Job Role & Skill Matching Reasoning System

Every answer matches the code as it is now (15 rules, 6 roles, 18 skills, 87 domain facts,
42 unit tests). If the teacher asks about something that is not implemented, say so plainly.
Part E lists those cases.

Numbers you may be asked for (all from `sample_outputs.txt`):

| Scenario | Result | New facts / passes |
|---|---|---|
| A Ali | Data Analyst eligible | 28 in 2 passes |
| B Sara | Data Analyst partial, missing SQL | 23 in 2 passes |
| C Bilal | Frontend eligible (JavaScript inferred from React, no degree needed) | 15 in 2 passes |
| D Zara | ML Engineer and Python Developer eligible (ML inferred from TensorFlow) | 38 in 3 passes |
| E Hamza | Data Scientist partial, needs Masters | 30 in 2 passes |
| F Usman | Data Analyst and Python Developer eligible through the 5-year exception | 35 in 2 passes |
| G Ayesha | Cloud Engineer partial, missing AWS certificate | 26 in 2 passes |
| H Omar | nothing matched | 5 in 2 passes |

---

## Part A: Concept cards (English, Roman Urdu, example)

### Frames
- **English:** a record-like structure for one kind of object. Slots are its attributes, facets describe each slot (type, allowed values, default, if-needed procedure), defaults fill empty slots.
- **Roman Urdu:** Frame ek object ka form hai. Har khana slot hai, facet us khane ke rules batata hai, default khud bhar jata hai, aur if-needed slot zaroorat par calculate hota hai.
- **Our project:** five frames: Candidate, Job Role, Skill, Qualification, Certification. Candidate's `experience_level` is if-needed: 6 years gives "Senior".

### Script
- **English:** a fixed sequence of events for a common situation: entry condition, roles, props, scenes, result.
- **Roman Urdu:** Script kisi kaam ka standard order hai. Hamari script recommendation lene ke 7 scenes hain.
- **Our project:** `RECOMMENDATION_SCRIPT`. Scene 4 is forward chaining, scene 7 is backward chaining.

### Semantic network
- **English:** a graph of concepts with labelled links: IS-A (subclass), HAS-A (owns), PART-OF (component of a whole).
- **Roman Urdu:** concepts ke nodes aur labelled teeron ka jaal.
- **Our project:** Candidate IS-A Person; Candidate HAS-A Qualification; DegreeRequirement PART-OF RequirementProfile; TensorFlow IS-A Deep Learning.

### First-Order Logic
- **English:** predicates, variables and quantifiers (∀, ∃), so one formula covers all individuals.
- **Roman Urdu:** FOL mein variables hain, is liye ek rule sab candidates par lagta hai.
- **Our project:** ∀x ∀s ∀t (IsA(s, t) ∧ HasSkill(x, s) → HasSkill(x, t)).

### Description Logic
- **English:** a decidable logic of concepts (classes) and roles (relations). TBox holds class axioms, ABox holds facts about individuals.
- **Roman Urdu:** DL classes aur rishton ki logic hai. TBox general rules, ABox individuals.
- **Our project:** TensorFlowSkill ⊑ DeepLearningSkill ⊑ MachineLearningSkill; zara : Candidate.

### Horn clauses
- **English:** a clause with at most one positive literal. As a rule: one conclusion, premises joined by AND, no NOT, no OR.
- **Roman Urdu:** ek hi natija, shartein sirf AND se. NOT aur OR allowed nahi.
- **Our project:** `meets_experience(X, R) :- total_experience_years(X, Y), min_experience(R, M), gte(Y, M).`

### Forward chaining
- **English:** data-driven. Start from facts, fire every rule whose premises are all true, add new facts, repeat until a pass adds nothing (fixed point).
- **Roman Urdu:** facts se shuru karo, rules chalao, naye facts jodo, jab tak kuch naya na banay.
- **Our project:** Zara needs 3 passes: pass 1 gives deep_learning, pass 2 gives machine_learning and eligible(zara, ml_engineer), pass 3 adds nothing.

### Backward chaining
- **English:** goal-driven. Start from a goal, find rules that conclude it, prove each premise as a sub-goal.
- **Roman Urdu:** sawal se shuru karo, rule dhoondo, uski har shart sabit karo.
- **Our project:** eligible(hamza, data_scientist) fails because both meets_degree rules fail: gte(1, 2) and gte(3, 5).

### Closed World vs Open World
- **English:** CWA: what is not known is false. OWA: what is not known is unknown.
- **Roman Urdu:** CWA mein jo nahi likha woh false hai. OWA mein jo nahi likha woh "pata nahi" hai.
- **Our project:** "missing AWS certificate" needs CWA. DL (OWA) alone cannot say Ayesha lacks it.

---

## Part B: Core questions

### Problem and policy

**1. What problem does the project solve?**
It decides, for 6 job roles, whether a candidate is Fully eligible, a Partial match or Not matched, lists every met and missing requirement, and shows the reasoning as forward and backward chaining traces.

**2. Is this machine learning?**
No. It is a symbolic, rule-based expert system. Nothing is trained. Knowledge is written by hand.

**3. Why not keyword matching?**
Keyword counting cannot separate mandatory from optional skills, cannot compare degree ranks or years, cannot use a skill hierarchy, and gives no proof. Zara never typed "Machine Learning" but is eligible because TensorFlow IS-A Deep Learning IS-A Machine Learning.

**4. Why not a database with SQL?**
A database stores and retrieves. It does not chain rules or explain answers, and the hierarchy would need a recursive query. Our policy is readable rules with traces.

**5. State the eligibility policy.**
All mandatory skills (directly or inherited), degree rank at least the minimum or 5+ years, experience at least the minimum, and every required certificate. Partial = at least one mandatory skill but not everything. Not matched = no mandatory skill.

**6. Do optional skills change the label?**
No. They are shown as bonus chips only (unit test 7).

**7. What is the percentage on each card?**
Requirements met divided by all requirements (skills + degree + experience + certificates). Display only, no threshold.

**8. Can someone be eligible for two roles?**
Yes. Zara (ML Engineer, Python Developer) and Usman (Data Analyst, Python Developer).

**9. What happens with no skills?**
No crash. Every role is Not matched, a friendly message asks for skills. Omar still derives 5 facts, for example meets_degree(omar, frontend_developer) and person(omar).

### Frames and semantic network

**10. How are frames stored?**
As Python dictionaries. Keys are slots, values are fillers. Facets are in the `*_FRAME_TEMPLATE` dictionaries.

**11. Give a facet, a default and an if-needed slot.**
`total_experience_years`: facet range 0..50, default 0. `experience_level`: if-needed, computed from years. `candidate_id`: if-needed from the name.

**12. Which slots do not affect reasoning?**
`target_role` (only picks the demo goal), `description`, `issuer`, `related_skill`, and `experience_level` (a readable label). Be honest about this.

**13. Where are IS-A, HAS-A and PART-OF?**
Semantic network 1. IS-A: Candidate to Person, JobRole to EmploymentRole, and the skill taxonomy. HAS-A: Candidate to Skill, Qualification, Experience, Certification. PART-OF: each requirement to the RequirementProfile, each skill to its category.

**14. How do you know the diagrams match the code?**
`make_diagrams.py` generates them from the frames, and unit test 39 fails if a file is out of date.

### Logic

**15. Write the hierarchy rule in FOL.**
∀x ∀s ∀t (IsA(s, t) ∧ HasSkill(x, s) → HasSkill(x, t)).

**16. Write general eligibility in FOL.**
∀x ∀r (Candidate(x) ∧ JobRole(r) ∧ ∀s (RequiresSkill(r, s) → HasSkill(x, s)) ∧ MeetsDegree(x, r) ∧ MeetsExperience(x, r) ∧ ∀c (RequiresCert(r, c) → HasCert(x, c)) → Eligible(x, r)).

**17. Give three DL axioms.**
Candidate ⊑ Person; CloudEngineer ⊑ JobRole; Bachelors ⊓ Masters ⊑ ⊥.

**18. Is DataAnalyst ⊓ PythonDeveloper ⊑ ⊥ a contradiction for Usman?**
No. Role classes contain job positions. Eligibility is a relation between a candidate and a role, not membership in the role class.

**19. Why is propositional logic not enough?**
No variables and no numbers. Every candidate needs their own symbols and rules, and "at least 2 years" must be spelled out as a long OR of every possible value.

### Horn clauses and chaining

**20. How many rules? Group them.**
15. R1 hierarchy; R2 and R3 degree; R4 experience; R5 to R10 eligibility (one per role); R11 recommended; R12 matched_skill; R13 relevant_to; R14 knows_category; R15 person.

**21. How is a rule stored in Python?**
`{"id": "R11", "head": ("recommended", "X", "R"), "body": [("eligible", "X", "R")]}`. Uppercase strings are variables.

**22. Explain forward chaining in the code.**
`forward_chain()` loops in passes. In each pass, for every rule, `find_bindings()` finds all bindings that make the premises true; new conclusions are added and recorded. It stops when a pass adds nothing.

**23. Explain backward chaining in the code.**
`backward_chain()` checks facts first, then each rule whose head unifies with the goal, renames the rule's variables, and proves premises left to right recursively. A ground goal stops after its first proof.

**24. What does unify() do?**
Matches an atom with a fact and returns variable bindings. `has_skill(X, python)` with `has_skill(ali, python)` gives X = ali.

**25. Why rename variables (X_3)?**
So two uses of the same rule in one proof do not share variables by accident (standardising apart). R1 is used twice for Zara.

### Manual traces (practise on paper)

**26. Forward-chain a candidate with only HTML, no degree, 0 years.**
R2: meets_degree(x, frontend_developer) because gte(0, 0). R4: meets_experience for data_analyst, frontend_developer, python_developer. R12: matched_skill(x, frontend_developer, html). R13: relevant_to(x, frontend_developer). R14: knows_category(x, web). R15: person(x). 8 new facts. Label: Frontend Partial, missing CSS and JavaScript.

**27. Sara adds SQL. What changes?**
has_skill(sara, sql) becomes a fact, so R5 fires (she already meets degree and experience): eligible(sara, data_analyst), then R11 recommended. Data Analyst becomes Fully eligible.

**28. Backward-chain eligible(bilal, frontend_developer).**
R8: has_skill(bilal, html) fact; css fact; javascript not a fact, so R1: is_a(react, javascript) then has_skill(bilal, react) fact, proved; meets_degree via R2 with gte(0, 0); meets_experience via R4 with gte(1, 0). PROVED.

**29. Hamza has 5 years instead of 3. What happens?**
R3 now succeeds with gte(5, 5), so meets_degree(hamza, data_scientist) holds and he becomes Fully eligible for Data Scientist. (Checked by running the engine.)

**30. A candidate has PyTorch, Python, Data Structures, Bachelors, 1 year.**
R1 gives deep_learning in pass 1, machine_learning in pass 2; ML Engineer and Python Developer are Fully eligible. 3 passes.

### Testing and limitations

**31. How did you test correctness?**
42 unit tests. Test 35 compares the rules with a plain Python checker on 1,500 random candidates. Deleting the `gte` from R3 made 5 tests fail, which shows the tests can catch errors.

**32. Main limitations?**
Illustrative requirements, small domain, yes/no skills, upward-only hierarchy, CWA for missing items, no full FOL or DL reasoner, hand-edited knowledge.

---

## Part C: 15 new questions on the new parts

**N1. Why is `is_a` placed before `has_skill` in R1?**
R1 is recursive. If `has_skill(X, S)` came first, backward chaining would call `has_skill` again with S unknown, which matches R1 again, forever: left recursion. With `is_a(S, T)` first, S is bound to a real child skill from the facts, so each recursive call moves one level down a finite, acyclic taxonomy and must stop.

**N2. Does forward chaining have the left recursion problem?**
No. Forward chaining works bottom-up from facts and stops at the fixed point. The order inside R1 matters only for backward chaining.

**N3. Why does machine_learning appear in pass 2 for Zara, not pass 1?**
In pass 1, R1 matches against working memory as it was when R1 started, which has tensorflow but not deep_learning. deep_learning is added during pass 1, so the next step (deep_learning to machine_learning) happens in pass 2.

**N4. What stops the hierarchy from looping forever if someone adds a cycle?**
Unit test 14 checks the taxonomy has no cycles. Forward chaining would still stop, because only a finite number of facts exist, but backward chaining could loop until the depth limit of 12.

**N5. Why is a universal quantifier inside a condition not Horn?**
"∀s (RequiresSkill(r, s) → HasSkill(x, s)) → Eligible(x, r)". Moving the inner ∀ out of the condition of an implication turns it into ∃, and the inner implication becomes a disjunction with negation. The result has more than one positive literal, so it is not a Horn clause.

**N6. So how do you execute that formula?**
Each role's required skills and certificates are a fixed, known list, so we compile it into one Horn rule per role (R5 to R10), generated from the frames. It is equivalent as long as the requires_skill and requires_cert facts are complete, which they are because they come from the same frame.

**N7. How do you express "degree OR 5 years" without OR?**
Two Horn rules with the same head: R2 (degree rank) and R3 (experience). (A ∨ B) → C is equivalent to (A → C) ∧ (B → C).

**N8. What is gte and why does its position matter?**
A built-in comparison, gte(A, B) means A ≥ B. The engine computes it instead of looking it up, so A and B must already have values. It is always placed after the premises that bind them; unit test 37 checks this for every rule.

**N9. Explain CWA vs OWA in this project.**
The engine uses CWA after chaining: if has_cert(ayesha, aws_solutions_architect) is not in working memory, it is treated as false, so the certificate is listed as missing. Description Logic uses OWA: not stated means unknown, so DL alone cannot conclude she is missing it or that she is a partial match.

**N10. Why are "missing" and "partial match" not rules?**
They need negation (¬Eligible, ¬HasSkill). Horn clauses have no negation, so they are computed once after the fixed point, under the CWA, like Prolog's negation as failure.

**N11. Why is there no Description Logic reasoner in the code?**
DL reasoning (for example tableau algorithms for ALC) is far more complex than our Horn engine, and the course goal is to explain the reasoning by hand. We use DL to describe the domain formally, and execute only its Horn-expressible part: Candidate ⊑ Person as R15, the skill subsumptions as is_a facts plus R1, the ⊔ in MeetsDegree as R2 plus R3, and the eligibility definitions as R5 to R10.

**N12. What would a DL reasoner conclude about Zara?**
From zara : ∃hasSkill.TensorFlowSkill and TensorFlowSkill ⊑ DeepLearningSkill ⊑ MachineLearningSkill, it would conclude zara : ∃hasSkill.MachineLearningSkill, the same result as two uses of R1.

**N13. Why can Bilal be eligible with no degree?**
Frontend Developer has min_degree none (rank 0). R2 gives gte(0, 0), true. JavaScript comes from React through R1.

**N14. Does 5 years of experience also replace missing skills or certificates?**
No. R3 only concludes meets_degree. A candidate with Python only and 6 years is still a Partial match for Python Developer, missing Data Structures (unit test 21).

**N15. Why is the expressive logic only documented and the restricted logic executed?**
Trade-off between expressivity and tractability. Full FOL is semi-decidable and DL can be EXPTIME-hard; function-free Horn clauses with a finite set of constants always reach a fixed point and every step can be traced by hand. So FOL and DL describe everything precisely, and Horn clauses run the part that must be fast, guaranteed to finish and explainable.

---

## Part D: Hard follow-ups

**33. If you add a 7th role, what changes?**
Only a new entry in `JOB_ROLE_FRAMES`. Its eligibility rule, facts and diagram edges are generated. Then rerun `make_diagrams.py`, `demo.py` and `build_report.py`.

**34. Is naive forward chaining efficient?**
Fine for 15 rules. It re-checks every rule each pass; semi-naive evaluation or Rete would only re-check what new facts affect.

**35. Do forward and backward chaining always agree?**
For function-free Horn clauses over finite facts both are sound and complete. Test 35 checks they agree on eligibility for sampled candidates.

**36. Could gte make forward chaining infinite?**
No. gte only tests numbers already in the facts; it never creates a new constant, so the set of possible facts stays finite.

---

## Part E: Not implemented (say this honestly if asked)

- No machine learning and no learning from data.
- No full FOL prover and no DL reasoner.
- No skill levels or per-skill experience.
- The hierarchy only goes upward; no partial credit for sibling skills (PyTorch does not count as TensorFlow).
- No database, login or saved profiles.
- The interactive graph needs internet (CDN); the static view works offline.
