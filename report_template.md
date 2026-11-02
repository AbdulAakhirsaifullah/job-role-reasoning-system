# Intelligent Job Role & Skill Matching Reasoning System

**A rule-based KR system that models candidates, skills, qualifications, experience, certifications and job requirements using Frames and Semantic Networks, formalizes eligibility and skill-matching constraints through First-Order Logic and Description Logic, and applies Horn clause reasoning with Forward and Backward Chaining to determine suitable job roles and give explainable decisions.**

Complex Computing Problem (CCP) Report

| Field | Value |
|---|---|
| Course | CT-351 Knowledge Representation & Reasoning |
| Department | Department of Computer Science and IT, NED University of Engineering & Technology |
| CLO / PLO | CLO 3 (Taxonomy Level C6, Design/Analysis); PLO-10 (Lifelong Learning) |
| Group | Group 9 |
| Members | [PLACEHOLDER: Student 1 name, roll number] |
| | [PLACEHOLDER: Student 2 name, roll number] |
| | [PLACEHOLDER: Student 3 name, roll number] |
| | [PLACEHOLDER: Student 4 name, roll number] |
| Instructor | [PLACEHOLDER: instructor name] |
| Submission date | [PLACEHOLDER: date] |

---

## Grading Rubric Sheet

Course Code: CT-351 | Course Title: Knowledge Representation & Reasoning
Complex Computing Problem (CCP) - Grading Rubric

| Student No. | Name | Roll No. |
|---|---|---|
| S1 | [PLACEHOLDER] | [PLACEHOLDER] |
| S2 | [PLACEHOLDER] | [PLACEHOLDER] |
| S3 | [PLACEHOLDER] | [PLACEHOLDER] |
| S4 | [PLACEHOLDER] | [PLACEHOLDER] |

| Criteria and scales | 0 (Unsatisfactory) | 1 (Developing) | 2 (Proficient) | S1 | S2 | S3 | S4 |
|------------|--------------|--------------|--------------|---|---|---|---|
| Criterion 1: Problem Statement & Motivation | Objective of the project and domain requirements are not clear or described. | Some lack of clarity in objectives/purpose or domain justification. | The project's objectives and domain motivation are clearly stated and justified. | | | | |
| Criterion 2: Structural KR (Frames & Semantic Networks) | Model fails to represent necessary concepts, frames, slots, or semantic relationships. | Model includes frames and semantic networks but lacks complete slots, facets, or default values. | Model meets Proficient criteria with comprehensive, accurate frame structures and semantic networks. | | | | |
| Criterion 3: Formal Logic (FOL & Description Logic) | Logical representations contain major syntax/semantic errors or are missing. | FOL and DL formulas are present but contain minor syntax/quantifier errors. | Model represents domain constraints perfectly using correct FOL formulas and Description Logic axioms. | | | | |
| Criterion 4: Inference Engine (Horn Clauses & Chaining) | Rules are not converted to Horn clauses; failure to execute chaining. | Rules are in Horn clauses, but Forward/Backward chaining traces have minor logical gaps. | Horn clauses are correctly formulated with flawless, detailed Forward and Backward chaining traces. | | | | |
| Criterion 5: Team Participation & Individual Viva | The individual did not contribute to the project and failed to answer viva questions. | The individual contributed partially and demonstrated basic understanding during viva. | The individual contributed significantly and demonstrated mastery of KR concepts during viva. | | | | |
| **Total Marks (Out of 10):** | | | | | | | |

Teacher's Signature: ___________________________ Date: _______________

---

## Contents

1. Text Summary
    - 1.1 Problem statement and motivation
    - 1.2 Domain requirements
    - 1.3 Problem challenge
    - 1.4 Limitations of traditional databases
    - 1.5 Team participation statement
2. Semantic Network and Frame Architecture
    - 2.1 Semantic networks (is-a, has-a, part-of)
    - 2.2 Frame architecture
    - 2.3 Frames: slots, facets and defaults
    - 2.4 Script
3. Formal Logic Definitions
    - 3.1 Predicates
    - 3.2 First-Order Logic formulas
    - 3.3 Description Logic axioms
    - 3.4 Limitations analysis: propositional logic, FOL, expressivity and tractability
4. Horn Clause Knowledge Base and Chaining Trace Sheets
    - 4.1 Facts
    - 4.2 Rules R1 to R15
    - 4.3 Why every rule is a Horn clause
    - 4.4 Closed World Assumption for "missing" and "partial match"
    - 4.5 Queries and answers
    - 4.6 Forward chaining: algorithm and trace sheet
    - 4.7 Backward chaining: algorithm and trace sheets
5. Sample Execution Output and Code Snippets
    - 5.1 System architecture
    - 5.2 Results for all sample candidates
    - 5.3 Code snippets
    - 5.4 Testing
    - 5.5 User interface
6. Limitations and Future Work
7. Conclusion
8. References


---

## 1. Text Summary

### 1.1 Problem statement and motivation

A candidate knows their own skills, degree, experience and certificates, but often does not
know which job roles these qualify them for, or what exactly is missing. A keyword overlap
count ("you match 3 of 5 words") cannot tell a mandatory skill from an optional one, cannot
handle a degree or experience threshold, and cannot explain its answer.

This project builds a knowledge-based system that:

- stores knowledge about skills (with a skill hierarchy), degrees, certifications and 6 job roles,
- takes one candidate's profile as input,
- decides for each role whether the candidate is **Fully eligible**, a **Partial match** or **Not matched**,
- lists every met and missing requirement, and
- explains each decision with a forward chaining trace and a backward chaining proof.

The system is symbolic and rule-based. Nothing is trained. It runs as a Python rule engine with
a Streamlit interface.

**Objectives.** (1) Acquire and structure the domain knowledge. (2) Represent it with Frames,
a Script and Semantic Networks. (3) Formalise it in FOL and Description Logic. (4) Encode the
executable part as Horn clauses. (5) Implement forward and backward chaining with traces.
(6) Use one eligibility policy everywhere. (7) Analyse expressivity versus tractability.
(8) Test the engine against an independent check.

### 1.2 Domain requirements

**Entities.** Candidates, skills (18), skill categories (5), degree levels (4), certifications
(3) and job roles (6).

**Knowledge sources and honesty statement.** The roles, skills and thresholds were chosen by
the group from common entry-level technology job titles. They are **illustrative and
simplified for teaching**. They were not validated against hiring data or an official
standard. The system's correctness claim is only this: *given the stated knowledge base, every
conclusion follows logically from the rules.*

**Job roles (from `JOB_ROLE_FRAMES`).**

| Role | Mandatory skills | Min degree | Min experience | Required certification | Optional (bonus only) |
|---|---|---|---|---|---|
| Data Analyst | python, sql, pandas | Bachelors | 0 | none | data_visualization, statistics; google_data_analytics |
| Machine Learning Engineer | python, machine_learning, data_structures | Bachelors | 1 | none | deep_learning, statistics; tensorflow_developer |
| Python Developer | python, data_structures | Bachelors | 0 | none | sql |
| Frontend Developer | html, css, javascript | No degree | 0 | none | react |
| Data Scientist | python, statistics, machine_learning, pandas | Masters | 1 | none | data_visualization, sql |
| Cloud Engineer | python, linux, cloud_computing | Bachelors | 2 | aws_solutions_architect | none |

**Skill hierarchy (from the `is_a` slot of `SKILL_FRAMES`).** tensorflow is_a deep_learning;
pytorch is_a deep_learning; deep_learning is_a machine_learning; scikit_learn is_a
machine_learning; react is_a javascript; postgresql is_a sql. Knowing a child skill implies
knowing its parent. The link only goes upward: knowing machine_learning does not imply
tensorflow.

**Degree ranks.** none = 0, bachelors = 1, masters = 2, phd = 3. A higher degree satisfies a
lower requirement.

**Eligibility policy (one policy, used in the code, the interface and this report).**
A candidate *x* is **Fully eligible** for role *r* if and only if all of these hold:

1. *x* has every mandatory skill of *r*, either directly or through the skill hierarchy;
2. *x* meets the degree requirement: rank(degree of *x*) >= minimum rank of *r*, **or** *x* has 5 or more years of experience (the exception rule);
3. years of experience of *x* >= minimum experience of *r*;
4. *x* holds every required certification of *r*.

**Partial match:** not fully eligible, but *x* has at least one mandatory skill of *r*.
**Not matched:** *x* has none of the mandatory skills of *r*.
Optional skills and optional certifications are shown as a bonus and never change the label.

**Displayed percentage.** Requirements met = (met requirements) / (total requirements) x 100,
rounded, where the requirements of a role are its mandatory skills, its degree requirement, its
experience requirement and its required certifications. Example: Data Analyst has 3 skills +
degree + experience = 5 requirements. The percentage is for display only. No threshold is used.

### 1.3 Problem challenge

- **Many-to-many links.** Python is mandatory for 5 of the 6 roles, and one candidate can satisfy several roles at once.
- **Conjunctive conditions with mixed types.** Eligibility combines symbolic facts (skills, certificates) with numeric comparisons (degree rank, years).
- **Inheritance.** A candidate who lists only TensorFlow must be recognised as knowing Machine Learning. This needs a recursive rule, and in goal-driven reasoning a badly ordered recursive rule loops forever (Section 4.3).
- **Exceptions.** Five years of experience replaces the degree requirement. This is a disjunction ("degree OR experience"), which Horn clauses cannot state in one rule (Section 4.3).
- **Negative information.** "Missing requirement" and "partial match" depend on what the candidate does *not* have. Horn rules cannot contain negation, so a stated assumption is needed (Section 4.4).
- **Explanation.** The user must see why, so every inference step is recorded.

### 1.4 Limitations of traditional databases

A relational database could store `candidate_skill(candidate, skill)` and
`role_skill(role, skill)` and answer matching questions in SQL. Its limits for this problem:

- **The policy is hidden in a query.** Eligibility would live inside `GROUP BY ... HAVING COUNT(...)` and `WHERE rank >= ...` clauses, not as readable rules that can be inspected and explained.
- **No inference.** A database returns stored rows. It does not chain rules (skill hierarchy, then eligibility, then recommendation) or derive new facts with a record of why.
- **Recursive knowledge is awkward.** The skill hierarchy needs a recursive query (`WITH RECURSIVE`). A rule engine states it as one rule.
- **No explanation.** A query result is not a proof.
- **No class semantics.** "Candidate IS-A Person" and inheritance of slot defaults are not native to tables.
- **Fixed closed world.** A database always treats missing rows as false. In KRR we can state the assumption and compare it with the open-world view of Description Logic (Section 3.3.6).

### 1.5 Team participation statement

Group 9.

| Member | Roll No. | Responsibilities |
|---|---|---|
| Abdul Aakhir Saifullah | AI-23041 | [PLACEHOLDER: responsibilities] |
| Mustufa Asad | AI-23042 | [PLACEHOLDER: responsibilities] |
| Munawwer Khan | AI-23035 | [PLACEHOLDER: responsibilities] |
| Muhammad Ashir Iqbal | AI-23039 | [PLACEHOLDER: responsibilities] |

---

## 2. Semantic Network and Frame Architecture

### 2.1 Semantic networks

The network is split into four diagrams so that each one stays readable. All four are generated
by `make_diagrams.py` from the frames in `knowledge_base.py`, and unit tests 39 and 40 check
that the files match the knowledge base and that IS-A, HAS-A and PART-OF are all present.

**Link types used**

| Link | Meaning | Where it lives in the code |
|---|---|---|
| IS-A (class) | subclass: every member of the lower class is a member of the upper class | DL axioms; rule R15 `person(X) :- candidate(X)` |
| IS-A (skill taxonomy) | knowing the lower skill implies knowing the upper skill | `is_a` slot of Skill frames; facts `is_a(S, T)`; rule R1 |
| HAS-A | an entity owns or holds another entity | Candidate frame slots `skills`, `degree`, `total_experience_years`, `certifications`; facts `has_skill`, `has_degree`, `total_experience_years`, `has_cert` |
| PART-OF | a component belongs to a whole | each requirement is part of a role's requirement profile (Job Role frame slots); each skill is part of a skill category (`belongs_to` facts) |
| REQUIRES-SKILL / REQUIRES-CERT | role needs this skill or certificate | facts `requires_skill`, `requires_cert` |
| INSTANCE-OF | an individual belongs to a class | facts `candidate(zara)`, `skill(python)`, `job_role(data_analyst)` |
| dotted links | **inferred** by the rules, not stored | e.g. derived `has_skill(zara, machine_learning)`, `eligible(zara, ml_engineer)` |

**Semantic network 1: concept level (IS-A, HAS-A, PART-OF)**

![Semantic network 1](diagrams/semantic_network_1_concepts.png)

A Candidate IS-A Person and a JobRole IS-A EmploymentRole. A Candidate HAS-A Skill,
Qualification, Experience and Certification. A JobRole HAS-A RequirementProfile, whose
parts (skill, degree, experience and certification requirements) are PART-OF that profile; each
requirement refers to the matching concept on the candidate side. A Skill is PART-OF a
SkillCategory, and the IS-A loop on Skill stands for the skill taxonomy drawn in network 2.

**Semantic network 2: skill taxonomy and categories**

![Semantic network 2](diagrams/semantic_network_2_skills.png)

Thick arrows are IS-A links between skills. Top-level skills are PART-OF one of five
categories; child skills reach their category through their parent.

**Semantic network 3: job roles and their requirements**

![Semantic network 3](diagrams/semantic_network_3_roles.png)

Each role box states IS-A JobRole and its minimum degree and experience. Arrows show the
mandatory skills (REQUIRES-SKILL) and the one required certificate (REQUIRES-CERT, Cloud
Engineer).

**Semantic network 4: instance level (sample candidate Zara)**

![Semantic network 4](diagrams/semantic_network_4_instance.png)

**How the network supports reasoning (example).** Is Zara eligible for Machine Learning
Engineer? Network 3 shows the role REQUIRES-SKILL python, machine_learning and
data_structures. Network 4 shows HAS-SKILL links from Zara to python and data_structures, but
not to machine_learning. Following the IS-A path tensorflow → deep_learning →
machine_learning from a skill Zara has fills the gap (two applications of rule R1). Her degree
(Bachelors) and experience (2 years) meet the role's minimums, so the dotted ELIGIBLE-FOR link
is inferred (rule R6). The same reasoning appears as a machine trace in Sections 4.6 and 4.7.

### 2.2 Frame architecture

![Frame architecture](diagrams/frame_architecture.png)

Class frames are boxes with their slots and facets in brackets. Hollow-triangle arrows are IS-A
(the lower frame inherits the slots of the upper frame: Candidate inherits `name` from Person;
JobRole inherits `name` and `description` from EmploymentRole). Dotted arrows marked
INSTANCE-OF link instance frames (`ali`, `data_analyst`, `tensorflow`) to their class frames.
Plain arrows are the relations between frames (`has_skill`, `requires_skill`, ...).

### 2.3 Frames: slots, facets and defaults

| Frame concept | Python representation |
|---|---|
| Frame | a dictionary, e.g. `JOB_ROLE_FRAMES["cloud_engineer"]` |
| Slot | a key, e.g. `"required_certifications"` |
| Filler | the value, e.g. `["aws_solutions_architect"]` |
| Facets | the `*_FRAME_TEMPLATE` dictionaries: `type`, `required`, `default`, `allowed_values`, `range`, `min_items`, `if_needed` |
| Default | copied into an empty slot by `create_candidate()` |
| If-needed procedure | a function that computes a slot when it is asked for: `make_candidate_id(name)`, `experience_level_if_needed(years)` |

**Candidate frame**

| Slot | Facets | Default / if-needed |
|---|---|---|
| candidate_id | type text; required | if-needed: `make_candidate_id(name)`, e.g. "Omar Ali" → `omar_ali` |
| name | type text; required | "Candidate" |
| skills | list of skill IDs; allowed_values: the 18 skills | `[]` |
| degree | degree ID; allowed_values: none, bachelors, masters, phd | `none` |
| total_experience_years | integer; range 0..50 | `0` |
| experience_level | text | if-needed from years: <2 Entry level, 2 to 4 Mid level, 5+ Senior |
| certifications | list of certification IDs; allowed_values: the 3 certificates | `[]` |
| target_role | role ID or None; allowed_values: the 6 roles | `None` |

Facets are enforced: an unknown skill, certificate or degree is removed and reported, a
duplicate is kept once, and an experience value that is not a whole number from 0 to 50 is
replaced by the default 0 with a warning (unit test 26).

**Job Role frame** (IS-A EmploymentRole)

| Slot | Facets | Default |
|---|---|---|
| role_id | text; required | none |
| name | text; required | none |
| description | text | "No description." |
| required_skills | list of skill IDs; required; **min_items 1** | none |
| optional_skills | list of skill IDs | `[]` |
| min_degree | degree ID; allowed_values: the 4 degrees | `none` |
| min_experience | integer (years) | `0` |
| required_certifications | list of certification IDs | `[]` |
| optional_certifications | list of certification IDs | `[]` |

**Skill frame**

| Slot | Facets | Default |
|---|---|---|
| name | text; required | none |
| category | allowed_values: programming, data, ai, web, cloud | none |
| is_a | parent skill ID or None; allowed_values: the 18 skills | `None` (top-level skill) |

**Qualification frame**

| Slot | Facets | Values |
|---|---|---|
| name | text; required | No degree, Bachelors, Masters, PhD |
| rank | integer; allowed_values 0..3 | 0, 1, 2, 3 |

**Certification frame**

| Slot | Facets | Default |
|---|---|---|
| name | text; required | none |
| issuer | text | "Unknown issuer" |
| related_skill | skill ID | `None` |

Every frame slot now feeds the reasoning, except `target_role` (used only to pick the default
backward chaining goal in the demo), `description`, `issuer` and `related_skill` (display only),
and `experience_level` (a readable label computed from the years).

### 2.4 Script

`RECOMMENDATION_SCRIPT` describes the stereotyped sequence of events for one recommendation.

| Script part | Content |
|---|---|
| Entry condition | A candidate wants to know which roles suit their profile |
| Roles | Candidate, Reasoning System |
| Props | Skill list, degree, experience, certifications, job role frames, rules |
| Scene 1 | Candidate enters a name, skills, degree, years of experience and certifications |
| Scene 2 | System fills the Candidate frame (defaults, if-needed slots, invalid values removed): `create_candidate()` |
| Scene 3 | System turns the frame into facts: `build_candidate_facts()` |
| Scene 4 | Forward chaining derives inherited skills, meets_degree, meets_experience, eligible and recommended facts: `forward_chain()` |
| Scene 5 | System labels each role: `recommend_all_roles()` |
| Scene 6 | System lists met and missing requirements (Closed World Assumption) and explains them: `explain()` |
| Scene 7 | Candidate asks a specific question; backward chaining tries to prove it: `backward_chain()` |
| Result | Candidate sees recommended roles, missing requirements and the reasoning trace |

---

## 3. Formal Logic Definitions

### 3.1 Predicates

Variables: *x* candidate, *r* job role, *s, t* skills, *c* certification, *d* degree,
*n, m, y, w* integers. Constants are lowercase (zara, tensorflow, data_analyst, 5).

| Predicate | Meaning | Stored or derived |
|---|---|---|
| Candidate(x), Person(x) | x is a candidate / a person | stored / derived (R15) |
| Skill(s), JobRole(r), Certification(c) | type facts | stored |
| IsA(s, t) | skill s is a kind of skill t | stored (Skill frames) |
| HasSkill(x, s) | x has skill s | stored, and derived through IsA (R1) |
| HasDegree(x, d) | x's highest degree is d | stored |
| DegreeRank(d, n) | degree d has rank n | stored |
| MinDegreeRank(r, m) | role r needs degree rank at least m | stored |
| TotalExperienceYears(x, y) | x has y years of experience | stored |
| MinExperience(r, m) | role r needs at least m years | stored |
| DegreeWaiverYears(w) | w years of experience waive the degree requirement (w = 5) | stored |
| HasCert(x, c) | x holds certification c | stored |
| RequiresSkill(r, s), RequiresCert(r, c) | mandatory skill / required certificate of r | stored |
| BelongsTo(s, k) | skill s is part of category k | stored |
| n ≥ m | integer comparison (built-in `gte`) | computed |
| MeetsDegree(x, r) | x meets the degree requirement of r | derived (R2, R3) |
| MeetsExperience(x, r) | x meets the experience requirement of r | derived (R4) |
| Eligible(x, r) | x is fully eligible for r | derived (R5 to R10) |
| Recommended(x, r) | r is recommended to x | derived (R11) |
| MatchedSkill(x, r, s) | r requires s and x has s | derived (R12) |
| RelevantTo(x, r) | x has at least one mandatory skill of r | derived (R13) |
| KnowsCategory(x, k) | x has a skill in category k | derived (R14) |
| PartialMatch(x, r), Missing(x, r, q) | not eligible but relevant / requirement q not met | computed after chaining (CWA) |

### 3.2 First-Order Logic formulas

**F1. Skill hierarchy (universal rule).**
∀x ∀s ∀t ( IsA(s, t) ∧ HasSkill(x, s) → HasSkill(x, t) )
*If s is a kind of t and x has s, x also has t.* Rule R1. Applying F1 repeatedly gives the
effect of transitivity: from IsA(tensorflow, deep_learning) and IsA(deep_learning,
machine_learning), HasSkill(zara, tensorflow) yields HasSkill(zara, machine_learning) in two steps.

**F2. Degree requirement.**
∀x ∀r ∀d ∀n ∀m ( HasDegree(x, d) ∧ DegreeRank(d, n) ∧ MinDegreeRank(r, m) ∧ n ≥ m → MeetsDegree(x, r) )
*x meets the degree requirement if the rank of x's degree is at least the role's minimum.* Rule R2.

**F3. Experience exception for the degree requirement.**
∀x ∀r ∀y ∀w ( TotalExperienceYears(x, y) ∧ DegreeWaiverYears(w) ∧ y ≥ w ∧ JobRole(r) → MeetsDegree(x, r) )
*Five or more years of experience counts as meeting the degree requirement of every role.* Rule R3.
F2 and F3 together say MeetsDegree(x, r) ← (degree condition ∨ experience condition), written
as two Horn clauses with the same head (Section 4.3).

**F4. Experience requirement.**
∀x ∀r ∀y ∀m ( TotalExperienceYears(x, y) ∧ MinExperience(r, m) ∧ y ≥ m → MeetsExperience(x, r) )
Rule R4.

**F5. General eligibility policy (not a Horn clause).**
∀x ∀r ( Candidate(x) ∧ JobRole(r) ∧ ∀s ( RequiresSkill(r, s) → HasSkill(x, s) ) ∧ MeetsDegree(x, r) ∧ MeetsExperience(x, r) ∧ ∀c ( RequiresCert(r, c) → HasCert(x, c) ) → Eligible(x, r) )
*x is eligible for r if x has every skill r requires, meets the degree and experience
requirements, and holds every certificate r requires.* The two inner universal quantifiers sit
inside the condition of an implication. Moving them out turns them into existentials, so F5
is **not** a Horn clause and cannot be executed directly by our engine (Section 3.4).

**F6. Compiled instance of F5 for Cloud Engineer (Horn).**
∀x ( HasSkill(x, python) ∧ HasSkill(x, linux) ∧ HasSkill(x, cloud_computing) ∧ MeetsDegree(x, cloud_engineer) ∧ MeetsExperience(x, cloud_engineer) ∧ HasCert(x, aws_solutions_architect) → Eligible(x, cloud_engineer) )
Rule R10. Because each role's required skills and certificates are a fixed, finite, known list,
F5 is compiled into one Horn rule per role (R5 to R10). This is equivalent to F5 **provided the
`requires_skill` and `requires_cert` facts are complete**, which holds by construction: rules
and facts are both generated from the same Job Role frame (unit test 38).

**F7. Recommendation.** ∀x ∀r ( Eligible(x, r) → Recommended(x, r) ). Rule R11.

**F8. Matched skill.** ∀x ∀r ∀s ( RequiresSkill(r, s) ∧ HasSkill(x, s) → MatchedSkill(x, r, s) ). Rule R12.

**F9. Relevance (existential in the condition).**
∀x ∀r ( ∃s MatchedSkill(x, r, s) → RelevantTo(x, r) ), which is logically equivalent to
∀x ∀r ∀s ( MatchedSkill(x, r, s) → RelevantTo(x, r) ). The second form is Horn: rule R13.

**F10. Partial match (uses negation, not Horn).**
∀x ∀r ( PartialMatch(x, r) ↔ RelevantTo(x, r) ∧ ¬Eligible(x, r) )
Computed after chaining under the Closed World Assumption.

**F11. Missing skill (uses negation, not Horn).**
∀x ∀r ∀s ( MissingSkill(x, r, s) ↔ RequiresSkill(r, s) ∧ ¬HasSkill(x, s) )
Computed after chaining under the CWA, after the hierarchy rule has added inherited skills, so
an inherited skill is never reported as missing. Missing degree, experience and certificate are
defined the same way with ¬MeetsDegree, ¬MeetsExperience and ¬HasCert.

**F12. Class hierarchy.** ∀x ( Candidate(x) → Person(x) ). Rule R15.

**F13. Category knowledge.** ∀x ∀s ∀k ( HasSkill(x, s) ∧ BelongsTo(s, k) → KnowsCategory(x, k) ). Rule R14.

**F14. Every role requires at least one skill (integrity constraint).**
∀r ( JobRole(r) → ∃s RequiresSkill(r, s) )
Not run by the engine. Enforced by the `min_items: 1` facet and unit test 27. It guarantees
"Fully eligible" can never come from an empty requirement list.

**F15. A candidate has exactly one recorded degree (integrity constraint, uses equality).**
∀x ∀d1 ∀d2 ( HasDegree(x, d1) ∧ HasDegree(x, d2) → d1 = d2 )
Enforced by the Candidate frame, whose `degree` slot holds one value.

**Concrete instances from the knowledge base**

| Formula | Instance | Conclusion |
|---|---|---|
| F1 | IsA(tensorflow, deep_learning) ∧ HasSkill(zara, tensorflow) | HasSkill(zara, deep_learning) |
| F1 | IsA(deep_learning, machine_learning) ∧ HasSkill(zara, deep_learning) | HasSkill(zara, machine_learning) |
| F2 | HasDegree(hamza, bachelors) ∧ DegreeRank(bachelors, 1) ∧ MinDegreeRank(data_scientist, 2) ∧ 1 ≥ 2 | premise 1 ≥ 2 is false: no conclusion |
| F3 | TotalExperienceYears(usman, 6) ∧ DegreeWaiverYears(5) ∧ 6 ≥ 5 ∧ JobRole(python_developer) | MeetsDegree(usman, python_developer) |
| F6 | ayesha meets all premises except HasCert(ayesha, aws_solutions_architect) | Eligible(ayesha, cloud_engineer) not derived |
| F10 | RelevantTo(ayesha, cloud_engineer) ∧ ¬Eligible(ayesha, cloud_engineer) | PartialMatch(ayesha, cloud_engineer) |

### 3.3 Description Logic axioms

Notation: ⊑ subsumption, ≡ equivalence, ⊓ intersection, ⊔ union, ⊥ empty concept, ⊤ top,
∃R.C existential restriction, ∀R.C value restriction, ≤1 R number restriction, {a} nominal,
a : C concept membership, R(a, b) role membership.
Roles (DL properties): hasSkill, hasDegree, hasCert, requiresSkill, requiresCert, belongsTo.
Concrete (data) property: experienceYears, with integer facets such as ≥5 (as in ALC(D) or OWL 2 datatype restrictions).

In the DL model, **skills are concepts** (PythonSkill, TensorFlowSkill, ...), so the skill
taxonomy becomes ordinary subsumption. The Python fact `has_skill(zara, tensorflow)` corresponds
to the assertion zara : ∃hasSkill.TensorFlowSkill.

#### 3.3.1 Subsumption (TBox)

| Axiom | Meaning |
|---|---|
| Candidate ⊑ Person | every candidate is a person |
| JobRole ⊑ EmploymentRole | every job role is an employment role |
| DataAnalyst ⊑ JobRole, MLEngineer ⊑ JobRole, PythonDeveloper ⊑ JobRole, FrontendDeveloper ⊑ JobRole, DataScientist ⊑ JobRole, CloudEngineer ⊑ JobRole | the six role classes |
| TensorFlowSkill ⊑ DeepLearningSkill, PyTorchSkill ⊑ DeepLearningSkill | skill taxonomy |
| DeepLearningSkill ⊑ MachineLearningSkill, ScikitLearnSkill ⊑ MachineLearningSkill | skill taxonomy |
| ReactSkill ⊑ JavaScriptSkill, PostgreSQLSkill ⊑ SQLSkill | skill taxonomy |
| PythonSkill ⊑ Skill, ..., CloudComputingSkill ⊑ Skill (all 18) | every skill class is a Skill |
| Bachelors ⊑ Degree, Masters ⊑ Degree, PhD ⊑ Degree, NoDegree ⊑ Degree | degree levels |
| BachelorsOrHigher ≡ Bachelors ⊔ Masters ⊔ PhD | defined concept used by role axioms |
| MastersOrHigher ≡ Masters ⊔ PhD | defined concept |

**Entailment that mirrors rule R1.** From zara : ∃hasSkill.TensorFlowSkill and
TensorFlowSkill ⊑ DeepLearningSkill ⊑ MachineLearningSkill, a DL reasoner concludes
zara : ∃hasSkill.MachineLearningSkill, because ∃R.C ⊑ ∃R.D whenever C ⊑ D.

#### 3.3.2 Disjointness

| Axiom | Justification |
|---|---|
| Person ⊓ Skill ⊑ ⊥ | nothing is both a person and a skill |
| Person ⊓ JobRole ⊑ ⊥ | a person is not a job role |
| Skill ⊓ Certification ⊑ ⊥, Skill ⊓ Degree ⊑ ⊥, Degree ⊓ Certification ⊑ ⊥ | different kinds of thing |
| Bachelors ⊓ Masters ⊑ ⊥ (and every other pair of degree levels) | a degree record has exactly one level |
| DataAnalyst ⊓ PythonDeveloper ⊑ ⊥ (and every other pair of the six role classes) | the role classes contain **job positions**, and each position in our model has one role type. This does **not** stop a candidate from qualifying for two roles: eligibility is a relation between a candidate and a role, not class membership. Usman is eligible for both Data Analyst and Python Developer and the axiom still holds. |
| (no disjointness along the taxonomy) | TensorFlowSkill and DeepLearningSkill are deliberately **not** disjoint: one is a subclass of the other |

#### 3.3.3 Restrictions

| Axiom | Meaning |
|---|---|
| JobRole ⊑ ∃requiresSkill.Skill | every role requires at least one skill (F14) |
| ∃hasSkill.⊤ ⊑ Candidate | only candidates have skills (domain of hasSkill) |
| ⊤ ⊑ ∀hasSkill.Skill | anything had as a skill is a Skill (range of hasSkill) |
| Candidate ⊑ ≤1 hasDegree | a candidate has at most one recorded degree (F15) |
| Skill ⊑ ∃belongsTo.SkillCategory | every skill belongs to a category |
| CloudEngineer ⊑ ∃requiresSkill.PythonSkill ⊓ ∃requiresSkill.LinuxSkill ⊓ ∃requiresSkill.CloudComputingSkill ⊓ ∃requiresCert.{aws_solutions_architect} | Cloud Engineer requirements (one axiom of this form per role) |

#### 3.3.4 Defined eligibility concepts

MeetsDegreeBachelorsRole ≡ Candidate ⊓ ( ∃hasDegree.BachelorsOrHigher ⊔ ∃experienceYears.≥5 )
*A candidate meets a Bachelors-level requirement if they hold a Bachelors or higher, or have at
least 5 years of experience.* This is rules R2 and R3 in one DL axiom: DL allows ⊔ inside a
definition, Horn clauses do not.

EligibleCloudEngineer ≡ Candidate ⊓ ∃hasSkill.PythonSkill ⊓ ∃hasSkill.LinuxSkill ⊓
∃hasSkill.CloudComputingSkill ⊓ ( ∃hasDegree.BachelorsOrHigher ⊔ ∃experienceYears.≥5 ) ⊓
∃experienceYears.≥2 ⊓ ∃hasCert.{aws_solutions_architect}

EligibleMLEngineer ≡ Candidate ⊓ ∃hasSkill.PythonSkill ⊓ ∃hasSkill.MachineLearningSkill ⊓
∃hasSkill.DataStructuresSkill ⊓ ( ∃hasDegree.BachelorsOrHigher ⊔ ∃experienceYears.≥5 ) ⊓
∃experienceYears.≥1

#### 3.3.5 Membership (ABox)

| Assertion | Meaning |
|---|---|
| zara : Candidate | Zara is a candidate |
| zara : ∃hasSkill.PythonSkill ⊓ ∃hasSkill.TensorFlowSkill ⊓ ∃hasSkill.DataStructuresSkill ⊓ ∃hasSkill.StatisticsSkill ⊓ ∃hasSkill.PandasSkill | Zara's listed skills |
| hasDegree(zara, deg_zara), deg_zara : Bachelors | Zara holds a Bachelors |
| experienceYears(zara, 2) | 2 years of experience |
| usman : Candidate, hasDegree(usman, deg_usman), deg_usman : NoDegree, experienceYears(usman, 6) | Usman |
| aws_solutions_architect : Certification | an individual certificate |

**Expected entailments:** zara : Person; zara : ∃hasSkill.MachineLearningSkill;
zara : EligibleMLEngineer; usman : MeetsDegreeBachelorsRole (through the ⊔ branch
∃experienceYears.≥5). These match the engine's results for scenarios D and F.

**Consistency check (by hand).** No individual is asserted into two disjoint concepts: each
degree record has one level; candidates are only Persons; skills, degrees and certificates are
separate. The taxonomy has no cycles (unit test 14).

#### 3.3.6 Open world versus closed world

DL uses the **Open World Assumption**: if the ABox does not say Ayesha holds the AWS
certificate, a DL reasoner concludes neither that she has it nor that she lacks it. So DL alone
cannot conclude "Ayesha is missing the certificate" or "Ayesha is a partial match". Our engine
adds the **Closed World Assumption** on purpose, only for those outputs (Section 4.4).

**Scope statement.** These axioms formally describe the domain. **The Python program does not
contain a Description Logic reasoner.** The parts of the model that are Horn-expressible are
executed as rules: Candidate ⊑ Person (R15), the skill subsumptions (as `is_a` facts plus R1),
the ⊔ in MeetsDegree (as R2 plus R3), and the eligibility definitions (R5 to R10).

### 3.4 Limitations analysis

#### Propositional logic versus FOL in this domain

Propositional logic has only true/false symbols with no structure. "Zara has TensorFlow"
must be a symbol such as `Zara_has_TensorFlow`. With *n* candidates the model needs:

- 18*n* symbols for skills, 3*n* for certificates, 4*n* for degrees;
- the hierarchy rule written 6 times per candidate (one per `is_a` pair), so 6*n* rules, and repeated again for every new skill;
- for experience, one symbol per candidate per possible value (`Zara_years_2`), with no way to say "at least 2". Each threshold must be spelled out, e.g. `Zara_years_2 ∨ Zara_years_3 ∨ ... ∨ Zara_years_50 → Zara_meets_exp_Cloud`, about 50 literals per candidate per role;
- one eligibility rule per role per candidate: 6*n* rules.

FOL replaces all of this with a fixed set of formulas (F1 to F15) that use variables,
quantifiers and the comparison n ≥ m. A new candidate needs only new facts.

#### Why FOL is expressive but costly

Entailment in full FOL is **semi-decidable**. If a conclusion follows, a complete prover will
eventually find a proof; if it does not follow, the prover may run forever, and no algorithm
can always answer "no" in finite time. Even when answers exist, general resolution can be very
slow.

#### Why a restricted Horn engine fits this project

Our executable rules are **function-free Horn clauses over a finite set of constants** (a
Datalog-style fragment) plus one built-in comparison, `gte`, applied only to integers that are
already in the facts. `gte` never creates new constants, so the set of possible facts is finite.
Forward chaining therefore always reaches a fixed point after a finite number of passes, and
each step is simple pattern matching a student can trace by hand.

#### Expressivity versus tractability

| Logic | What it can express | Reasoning | Role in this project |
|---|---|---|---|
| Propositional logic | ground true/false statements only | decidable; SAT is NP-complete; Horn-SAT is linear time | used above only to show why it does not scale |
| First-Order Logic | variables, quantifiers, negation, disjunction, nested quantifiers (F5) | semi-decidable (undecidable in general) | formal specification (F1 to F15) |
| Description Logic (ALC with nominals, number restrictions, datatype facets) | classes, subsumption, ⊔ and ¬ in concepts, restrictions, disjointness | decidable but can be expensive (ALC concept satisfiability with a general TBox is EXPTIME-complete) | ontology of the domain (Section 3.3) |
| Horn clauses (function-free, finite constants, + `gte`) | "if all of these then that"; no negation, no disjunction in the head, no nested quantifier | decidable; forward chaining reaches a fixed point | **the executable rules R1 to R15** |

**What we gave up, and how each gap is handled:**

| Lost in Horn | Example in our domain | How the project handles it |
|---|---|---|
| Universal quantifier inside a condition | F5: "for every required skill s, x has s" | compiled into one Horn rule per role (R5 to R10), generated from the frames |
| Disjunction in a condition | MeetsDegree ← degree condition ∨ 5+ years | split into two Horn rules with the same head (R2, R3), since (A ∨ B) → C ≡ (A → C) ∧ (B → C) |
| Negation | PartialMatch, Missing (F10, F11) | computed after chaining with the CWA, outside the rules (Section 4.4) |
| Disjunction in a conclusion | "a candidate is junior or senior" | not needed in this domain |

The design uses FOL and DL to *describe* the domain completely and precisely, including the
parts with negation, disjunction and nested quantifiers, and uses Horn clauses to *execute* the
positive, tractable part with a trace.

---

## 4. Horn Clause Knowledge Base and Chaining Trace Sheets

Notation: Prolog style, `head :- body.` Variables start with an uppercase letter. Constants
are lowercase words or whole numbers. `gte(A, B)` means A ≥ B and is computed by the engine.

### 4.1 Facts

The program builds {{DOMAIN_FACT_COUNT}} domain facts from the frames ({{DOMAIN_FACT_BREAKDOWN}}),
plus each candidate's facts. Selected domain facts:

```prolog
% skill taxonomy (all 6)
is_a(tensorflow, deep_learning).      is_a(pytorch, deep_learning).
is_a(deep_learning, machine_learning). is_a(scikit_learn, machine_learning).
is_a(react, javascript).              is_a(postgresql, sql).
% degree ranks (all 4) and the waiver threshold
degree_rank(none, 0). degree_rank(bachelors, 1). degree_rank(masters, 2). degree_rank(phd, 3).
degree_waiver_years(5).
% role requirements, two roles shown
requires_skill(ml_engineer, python). requires_skill(ml_engineer, machine_learning).
requires_skill(ml_engineer, data_structures).
min_degree_rank(ml_engineer, 1). min_experience(ml_engineer, 1).
requires_skill(cloud_engineer, python). requires_skill(cloud_engineer, linux).
requires_skill(cloud_engineer, cloud_computing).
min_degree_rank(cloud_engineer, 1). min_experience(cloud_engineer, 2).
requires_cert(cloud_engineer, aws_solutions_architect).
```

Candidate facts for Zara (scenario D), exactly as printed by the program:

```prolog
{{FACTS:D}}
```

### 4.2 Rules R1 to R15

{{RULE_TABLE}}

In Python each rule is a dictionary, for example R1:

```python
{"id": "R1",
 "head": ("has_skill", "X", "T"),
 "body": [("is_a", "S", "T"), ("has_skill", "X", "S")]}
```

Rules R5 to R10 are generated by `build_rules()` from `JOB_ROLE_FRAMES`, so a change to a frame
changes its rule automatically.

### 4.3 Why every rule is a Horn clause, and three design points

A Horn clause has at most one positive literal. The rule `H :- B1, ..., Bn.` is the clause
¬B1 ∨ ... ∨ ¬Bn ∨ H: exactly one positive literal (H). All 15 rules have one head and only
positive premises (unit test 36).

**1. Built-in comparison.** `gte(N, M)` is a premise with a fixed meaning (N ≥ M) that the
engine computes instead of looking up. Both arguments must already have values when it is
reached, so it is always placed after the premises that bind them. Unit test 37 checks this for
every rule.

**2. Disjunction split into two rules.** R2 and R3 have the same head `meets_degree(X, R)`.
Together they mean "degree condition OR experience condition", which a single Horn clause cannot
say.

**3. Left recursion in R1.** R1 is recursive: `has_skill` appears in its head and its body.
In backward chaining, the order of the body matters:

- **Bad order:** `has_skill(X, T) :- has_skill(X, S), is_a(S, T).` To prove `has_skill(zara, machine_learning)`, the first sub-goal is `has_skill(zara, S)` with S unknown. That sub-goal matches the head of the same rule, whose first sub-goal is again `has_skill(zara, S')`, and so on forever, before `is_a` is ever checked. This is **left recursion**, the classic way depth-first SLD resolution (as in Prolog) fails to terminate.
- **Our order:** `has_skill(X, T) :- is_a(S, T), has_skill(X, S).` The first sub-goal `is_a(S, machine_learning)` is answered from facts only and binds S to a concrete child skill (deep_learning or scikit_learn). The recursive call is then about a skill that is one level lower in the taxonomy. The taxonomy is finite and has no cycles (unit test 14), so the recursion must stop. Unit test 13 runs goals with unbound skills and confirms they terminate.

Forward chaining does not have this problem with either order, because it works bottom-up from
facts and stops at a fixed point.

### 4.4 Closed World Assumption for "missing" and "partial match"

Horn clauses cannot contain negation, so F10 (partial match) and F11 (missing requirement) are
not rules. After forward chaining reaches its fixed point, `recommend_all_roles()` applies the
**Closed World Assumption**: *a fact that is not in working memory is false.*

- A mandatory skill is **missing** if `has_skill(x, s)` is not in working memory. Inherited skills are already there (R1), so they are never reported as missing.
- The degree / experience requirement is **missing** if `meets_degree(x, r)` / `meets_experience(x, r)` is not there.
- A certificate is **missing** if `has_cert(x, c)` is not there.
- **Partial match** = `relevant_to(x, r)` is there and `eligible(x, r)` is not.

This is the same idea as Prolog's negation as failure (`\+`). It is applied once, outside the
rules, and clearly labelled in the interface.

### 4.5 Queries and answers

All answers below were produced by `backward_chain()`.

| Query | Answer | How |
|--------------------|----------|--------------------|
| `?- eligible(ali, data_analyst).` | PROVED | R5; skills are facts; R2 and R4 succeed |
| `?- eligible(sara, data_analyst).` | NOT PROVED | R5 fails at `has_skill(sara, sql)`; R1 tries postgresql and fails |
| `?- has_skill(zara, machine_learning).` | PROVED | R1 twice: deep_learning, then tensorflow |
| `?- recommended(zara, R).` | R = ml_engineer; R = python_developer | R11, then R6 and R7 succeed |
| `?- meets_degree(hamza, data_scientist).` | NOT PROVED | R2 fails at `gte(1, 2)`; R3 fails at `gte(3, 5)` |
| `?- meets_degree(usman, python_developer).` | PROVED | R2 fails at `gte(0, 1)`; R3 succeeds with `gte(6, 5)` |
| `?- eligible(ayesha, cloud_engineer).` | NOT PROVED | R10 fails at `has_cert(ayesha, aws_solutions_architect)` |
| `?- has_skill(bilal, javascript).` | PROVED | R1 with `is_a(react, javascript)` |
| `?- person(omar).` | PROVED | R15 |
| `?- knows_category(zara, C).` | C = programming; C = data; C = ai | R14, using inherited skills too |

### 4.6 Forward chaining: algorithm and trace sheet

![Forward chaining flowchart](diagrams/forward_chaining.png)

**Algorithm** (`forward_chain()`):

```
working_memory ← domain facts ∪ candidate facts
repeat                                   // one PASS
    added ← false
    for each rule R1 .. R15, in order:
        bindings ← every binding that makes all premises true
                   (facts are matched with unify(); gte is computed)
        for each binding:
            conclusion ← head with variables replaced
            if conclusion ∉ working_memory:
                add it; record (rule, conclusion, premises used); added ← true
until added = false                      // FIXED POINT
for each eligibility rule that never fired: record its missing premises
```

**Trace sheet: scenario D, Zara (skill hierarchy).** Every line below is copied from
`sample_outputs.txt` (the output of `python demo.py`).

Initial candidate facts:
```
{{FACTS:D}}
```

Trace (only rules that produced new facts are listed):
```
{{FORWARD:D}}
```

**Reading the trace.**
- Pass 1, R1 derives `has_skill(zara, deep_learning)` from the stored tensorflow fact.
- In pass 1, R1 cannot also derive machine_learning, because each rule matches against the working memory as it was when that rule started. So `has_skill(zara, machine_learning)` appears in **pass 2**. The ML Engineer rule R6 fires in pass 2, followed by R11.
- Pass 3 adds nothing, so chaining stops at the fixed point.
- The Data Scientist rule stays unsatisfied only because of `meets_degree(zara, data_scientist)` (Masters needed). The Data Analyst rule stays unsatisfied only because of `has_skill(zara, sql)`.

**Shorter trace sheet: scenario F, Usman (experience exception).** Lines selected from the full output:
```
{{FORWARD_SELECT:F}}
```

### 4.7 Backward chaining: algorithm and trace sheets

![Backward chaining flowchart](diagrams/backward_chaining.png)

**Algorithm** (`backward_chain()`):

```
prove(goal):
    if goal is a built-in (gte): compute it, return true/false
    for each fact that unifies with goal: record FACT found, add solution
        (a goal with no variables stops after its first proof)
    for each rule whose head unifies with goal:
        rename the rule's variables (X → X_7) so separate uses do not clash
        record TRY rule
        prove each premise in order, keeping the bindings
        if a premise cannot be proved: record FAIL rule, try the next rule
        if all premises are proved: record SUCCESS rule, add solution
    if no solution: record NOT PROVED
```

It is a small depth-first Horn-clause prover, not a full Prolog: no cut, no negation, no
function symbols. A depth limit of 12 is a safety stop; the only recursive rule (R1) stops on
its own as explained in Section 4.3. Renamed variables such as `D_6` appear in the trace.

**Trace sheet 1: success through the skill hierarchy. Goal `eligible(zara, ml_engineer)`.**
```
{{BACKWARD:D}}
```

**Trace sheet 2: failure because of the degree. Goal `eligible(hamza, data_scientist)`.**
```
{{BACKWARD:E}}
```
Both ways of proving `meets_degree` fail: R2 at `gte(1, 2)` (Bachelors is rank 1, Masters is
rank 2), and R3 at `gte(3, 5)` (3 years is below the waiver).

**Trace sheet 3: success through the exception rule. Goal `eligible(usman, python_developer)`.**
```
{{BACKWARD:F}}
```

**Trace sheet 4: failure because of a missing certificate. Goal `eligible(ayesha, cloud_engineer)`.**
```
{{BACKWARD:G}}
```

**Forward versus backward**

| | Forward chaining | Backward chaining |
|---|---|---|
| Direction | facts → conclusions | goal → sub-goals → facts |
| Answers | "what follows about this candidate?" | "is this specific goal true?" |
| Work for Zara | derives all {{DERIVED:D}} new facts | proves only the sub-goals the goal needs |
| Used in the system for | role labels, full trace | the Backward Chaining tab (proof tree) |

---

## 5. Sample Execution Output and Code Snippets

### 5.1 System architecture

![System architecture](diagrams/architecture.png)

| File | Contents |
|---|---|
| `knowledge_base.py` | frames, facet templates, `create_candidate()`, sample candidates, script, `build_domain_facts()`, `build_candidate_facts()`, `build_rules()` |
| `reasoning_engine.py` | `unify()`, `find_bindings()`, `run_builtin()`, `forward_chain()`, `backward_chain()`, `recommend_all_roles()`, `explain()`, `evaluate_role()` |
| `app.py` | Streamlit interface; calls the engine, does no reasoning itself |
| `ui_helpers.py` | HTML for role cards, proof tree and graph; JSON and PDF export |
| `demo.py` | runs all sample candidates in the terminal; output saved as `sample_outputs.txt` |
| `make_diagrams.py` | writes the semantic network and frame diagrams from the frames |
| `tests/test_reasoning.py` | {{TEST_COUNT}} unit tests |

### 5.2 Results for all sample candidates

"Req. met" is the percentage of requirements met (Section 1.2). "Skills" is matched / mandatory
skills. Copied from `sample_outputs.txt`.

{{ALL_ROLE_TABLES}}

### 5.3 Code snippets

**Unification** (matches one atom with one fact):

```python
{{SNIPPET:unify}}
```

**Finding all bindings for a rule body, with the built-in:**

```python
{{SNIPPET:find_bindings}}
```

**Inner loop of forward chaining** (from `forward_chain()`):

```python
    for pass_number in range(1, max_passes + 1):
        added_this_pass = False
        for rule in rules:
            bindings = find_bindings(rule["body"], sorted(working_memory, key=sort_key))
            new_facts = []
            for binding in bindings:
                conclusion = substitute(rule["head"], binding)
                if conclusion not in working_memory:
                    working_memory.add(conclusion)
                    ...
        if not added_this_pass:
            break
```

### 5.4 Testing

**Method.** Python's built-in `unittest`. Each test states its expected result in a comment.
Test 35 is a consistency check: for 1,500 random candidates (fixed seed 351, random skills,
degree, 0 to 7 years, random certificates) and all 6 roles, the label and missing skills from
forward chaining must equal a plain-Python check that uses no rules (`evaluate_role()`). On every
25th candidate, backward chaining must prove `eligible(...)` exactly when the label is Fully
eligible. In that sample, 231 role results are Fully eligible, 11 of them through the experience
exception.

As a check that the tests can fail, the `gte(Y, W)` premise was deleted from rule R3 in a copy
of the project: 5 tests failed.

Command: `python -m unittest discover -s tests -v`

**Result of the run on {{TEST_DATE}} (Python {{PY_VERSION}}): {{TEST_SUMMARY}}**

{{TEST_TABLE}}

### 5.5 User interface

The Streamlit interface (`app.py`) has a candidate form (name, skills grouped by category,
degree, years of experience, certifications), role cards with an eligibility badge, a
progress bar, green chips for met requirements and red chips for missing ones, and tabs for
Recommendations, Explanation, Forward Chaining, Backward Chaining (proof tree), Knowledge Base,
Semantic Network (interactive graph), Compare Candidates and About. Results can be downloaded as
JSON or PDF.

During development the interface code was executed against a stand-in for the Streamlit
library, because Streamlit could not be installed in the build environment. The group must
run the real interface and complete this checklist:

| Check | Pass / Fail |
|---|---|
| `streamlit run app.py` opens without errors | [ ] |
| Loading each sample candidate updates every tab | [ ] |
| Zara: ML Engineer card is Eligible and mentions TensorFlow | [ ] |
| Backward Chaining tab: Hamza / Data Scientist shows NOT PROVED at gte(1, 2) | [ ] |
| Semantic Network tab shows a draggable graph | [ ] |
| JSON and PDF downloads open correctly | [ ] |
| No skills selected: no error, friendly message shown | [ ] |
| Deployed link opens on a phone | [ ] |

---

## 6. Limitations and Future Work

**Limitations**

1. **Illustrative knowledge.** Role requirements, thresholds and the 5-year waiver are simplified and not validated against hiring data.
2. **Small domain.** 6 roles, 18 skills, 4 degree levels, 3 certificates.
3. **Binary skills.** A skill is held or not; there is no proficiency level.
4. **Experience is one number.** Total years only, not years per skill or per field.
5. **Hierarchy goes one way.** A child skill implies its parent, never the reverse, and there is no partial credit for a sibling skill (PyTorch does not count as TensorFlow).
6. **No negation inside rules.** Missing requirements and partial match use the CWA outside the rules.
7. **FOL and DL are not executed in full.** There is no FOL prover and no DL reasoner; only the Horn-expressible part runs.
8. **Naive forward chaining.** Every pass re-checks every rule. Fine at this size, slow for thousands of rules.

**Future work**

- Skill levels, e.g. `has_skill_level(X, python, L), gte(L, 3)`.
- Use `related_skill` of certificates to suggest what to learn next.
- Move frames to a JSON file so non-programmers can edit them.
- Export the DL axioms to OWL and check them with a standard reasoner such as HermiT.
- Semi-naive evaluation or the Rete algorithm for faster forward chaining.

## 7. Conclusion

The project builds an expert system that matches candidates to job roles from explicit
knowledge. Five kinds of frames with facets, defaults and if-needed slots structure the domain,
a script describes the recommendation process, and four semantic networks show IS-A, HAS-A and
PART-OF links. FOL formulas and DL axioms describe the domain precisely, including the parts
that need negation, disjunction and nested quantifiers. Fifteen Horn clauses, including a
recursive skill-hierarchy rule, numeric comparisons and an exception rule, form the executable
knowledge base. Forward chaining derives every conclusion with a pass-by-pass trace, and
backward chaining proves or refutes a specific goal and shows which premise failed. One
eligibility policy is used in the code, the interface and this report. {{TEST_COUNT}} automated tests,
including a 1,500-candidate comparison against an independent check, confirm the rule-based
results. The main limitation is that the role requirements are illustrative: the reasoning is
correct for the stated knowledge, not a verified model of real hiring.

## 8. References

1. R. J. Brachman and H. J. Levesque, *Knowledge Representation and Reasoning*. Morgan Kaufmann, 2004.
2. S. Russell and P. Norvig, *Artificial Intelligence: A Modern Approach*, 4th ed. Pearson, 2020.
3. F. Baader, D. Calvanese, D. McGuinness, D. Nardi and P. Patel-Schneider (eds.), *The Description Logic Handbook*, 2nd ed. Cambridge University Press, 2007.
4. M. Minsky, "A Framework for Representing Knowledge," MIT AI Laboratory Memo 306, 1974.
5. R. C. Schank and R. P. Abelson, *Scripts, Plans, Goals and Understanding*. Lawrence Erlbaum, 1977.
6. S. Ceri, G. Gottlob and L. Tanca, "What you always wanted to know about Datalog (and never dared to ask)," *IEEE Transactions on Knowledge and Data Engineering*, 1(1), 1989.
7. Streamlit documentation, https://docs.streamlit.io
8. [PLACEHOLDER: CT-351 course lecture notes, NED UET]
