# Beginner Guide (Roman Urdu)

Yeh guide poore project ko simple Roman Urdu mein samjhati hai. Technical terms English mein
hain, kyun ke viva mein teacher yahi words use karenge. Har number aur trace asli program
output (`sample_outputs.txt`) se liya gaya hai.

---

## 1. Project kya karta hai?

Candidate apni skills, degree, experience (saal) aur certificates batata hai. System 6 job
roles ke saath compare karke har role ko label deta hai:

- **Fully eligible**: saari requirements poori
- **Partial match**: kam az kam ek mandatory skill hai, magar sab kuch nahi
- **Not matched**: ek bhi mandatory skill nahi

Saath mein batata hai ke kya missing hai aur **kyun**. Yeh **rule-based expert system** hai,
machine learning nahi. Saari knowledge `knowledge_base.py` mein haath se likhi hai.

> Requirements sirf academic examples hain, official industry standards nahi.

## 2. Knowledge base mein kya hai?

| Cheez | Kitni |
|---|---|
| Skills | 18 (jaise python, tensorflow, react) |
| Skill categories | 5 |
| Degree levels | 4: none=0, bachelors=1, masters=2, phd=3 |
| Certificates | 3 |
| Job roles | 6 |
| Rules | 15 (R1 se R15) |
| Domain facts | 87 |
| Sample candidates | 8 (A se H) |

## 3. Eligibility ki 4 shartein (policy)

Role ke liye **Fully eligible** tab, jab:
1. saari mandatory skills hon (seedhi ya **skill hierarchy** se),
2. degree rank kam az kam role ka minimum ho, **ya** experience 5+ saal ho (exception),
3. experience kam az kam role ka minimum ho,
4. role ka har required certificate ho.

| Role | Mandatory skills | Min degree | Min saal | Certificate |
|---|---|---|---|---|
| Data Analyst | python, sql, pandas | Bachelors | 0 | nahi |
| ML Engineer | python, machine_learning, data_structures | Bachelors | 1 | nahi |
| Python Developer | python, data_structures | Bachelors | 0 | nahi |
| Frontend Developer | html, css, javascript | koi degree nahi | 0 | nahi |
| Data Scientist | python, statistics, machine_learning, pandas | Masters | 1 | nahi |
| Cloud Engineer | python, linux, cloud_computing | Bachelors | 2 | AWS Solutions Architect |

## 4. Candidate input kaise deta hai?

App ke sidebar mein: naam, skills (category ke hisaab se), degree, saal, certificates. Ya
"Load a sample candidate" se A se H mein se koi load karo.

`create_candidate()` Candidate frame bharta hai:
- ghalat skill/certificate/degree hata kar warning deta hai,
- experience 0 se 50 ka whole number na ho to 0 kar deta hai,
- khali slots mein default daalta hai,
- `candidate_id` naam se aur `experience_level` saalon se **if-needed** procedure se banata hai.

## 5. Rules kaise kaam karte hain?

Fact ek tuple hai: `("has_skill", "zara", "tensorflow")` matlab `has_skill(zara, tensorflow)`.
Bara letter (X, R, S) variable hai, chhota (zara, python, 5) constant hai.

| Rule | Kya kehta hai |
|---|---|
| R1 | `has_skill(X, T) :- is_a(S, T), has_skill(X, S).` child skill hai to parent skill bhi hai |
| R2 | degree rank ≥ role ka minimum → meets_degree |
| R3 | **exception**: 5+ saal experience → meets_degree (har role ke liye) |
| R4 | saal ≥ role ka minimum → meets_experience |
| R5 se R10 | har role ka eligibility rule: skills + meets_degree + meets_experience (+ certificate) |
| R11 | eligible → recommended |
| R12 | matched_skill (role ko chahiye aur candidate ke paas hai) |
| R13 | relevant_to (kam az kam ek skill match) |
| R14 | knows_category |
| R15 | candidate → person |

`gte(A, B)` ka matlab A ≥ B. Yeh fact nahi, engine isay calculate karta hai. Is liye yeh
hamesha un premises ke **baad** aata hai jo A aur B ko value dete hain.

Saare 15 rules **Horn clauses** hain: ek natija, shartein sirf AND se, koi NOT ya OR nahi.

## 6. Skill hierarchy aur left recursion (bohot important)

`tensorflow is_a deep_learning`, `deep_learning is_a machine_learning`. Zara ne sirf TensorFlow
likha, phir bhi system usay Machine Learning wala maanta hai.

R1 mein **pehle `is_a`, phir `has_skill`** kyun?
- Agar `has_skill(X, S)` pehle hota, backward chaining S ke baghair dobara `has_skill` bulata, jo phir R1 se match hota, aur yeh **hamesha** chalta rehta. Isay **left recursion** kehte hain.
- `is_a(S, T)` pehle hone se S ko facts se asli value mil jati hai (jaise deep_learning). Har recursive call taxonomy mein ek level neeche jati hai. Taxonomy chhoti hai aur us mein cycle nahi (test 14), is liye ruk jati hai.

## 7. Forward Chaining (asli example: Zara)

Algorithm (`forward_chain()`): facts se shuru karo, har pass mein har rule check karo, naye
facts jodo, jab poore pass mein kuch naya na banay to ruk jao (**fixed point**).

Zara ke facts: python, tensorflow, data_structures, statistics, pandas, bachelors, 2 saal.

| Pass | Kya hua |
|---|---|
| 1 | R1: `has_skill(zara, deep_learning)` (tensorflow se). R2, R4: degree aur experience facts. Data Scientist ke liye meets_degree nahi bana (Masters chahiye). |
| 2 | R1: `has_skill(zara, machine_learning)` (deep_learning se). R6: `eligible(zara, ml_engineer)`. R11: recommended. |
| 3 | kuch naya nahi: fixed point |

Kul **38 naye facts, 3 passes**. Machine Learning pass 2 mein kyun? Kyun ke pass 1 mein R1
ne us waqt ki memory dekhi thi jab deep_learning abhi bana nahi tha.

## 8. Backward Chaining (asli examples)

Algorithm (`backward_chain()`): goal se shuru karo; pehle facts dekho; phir woh rules jin ka
natija goal hai; har shart ko naya goal bana kar sabit karo.

**Hamza (degree failure)**: `eligible(hamza, data_scientist)`?
- R9: chaaron skills facts hain ✔
- `meets_degree(hamza, data_scientist)`:
  - R2: `gte(1, 2)` false ✘ (Bachelors rank 1, Masters chahiye rank 2)
  - R3: `gte(3, 5)` false ✘ (3 saal, 5 chahiye)
- **NOT PROVED**

**Usman (exception)**: degree nahi, 6 saal. `meets_degree(usman, python_developer)`:
R2 fail `gte(0, 1)`, magar R3 pass `gte(6, 5)`. **PROVED**.

**Ayesha (certificate)**: sab theek, magar `has_cert(ayesha, aws_solutions_architect)` fact
nahi aur koi rule nahi. **NOT PROVED**.

Trace mein `D_6`, `X_3` jaise naam **renamed variables** hain, taake ek rule do dafa use ho
to variables mix na hon.

## 9. Missing aur Partial match: Closed World Assumption

Horn rules mein NOT nahi ho sakta. Is liye chaining ke **baad** `recommend_all_roles()` yeh
maanta hai: **jo fact memory mein nahi, woh false hai** (CWA).
- `has_cert(ayesha, aws_...)` nahi → certificate missing.
- `relevant_to` hai magar `eligible` nahi → Partial match.

DL **Open World** hai: wahan "nahi likha" ka matlab "pata nahi", is liye DL akela missing nahi bata sakta.

## 10. Frames Python mein

| Frame concept | Python |
|---|---|
| Frame | dictionary |
| Slot | key (jaise `"min_degree"`) |
| Facet | `*_FRAME_TEMPLATE` mein: type, default, allowed_values, range, if_needed |
| Default | `create_candidate()` khali slot bharta hai |
| If-needed | `experience_level_if_needed(years)`: 6 saal → "Senior" |

## 11. Semantic Network aur code

- **IS-A**: Candidate IS-A Person (R15), TensorFlow IS-A Deep Learning (`is_a` facts + R1)
- **HAS-A**: Candidate HAS-A Skill / Qualification / Experience / Certification (candidate facts)
- **PART-OF**: har requirement RequirementProfile ka PART-OF; skill category ka PART-OF
- Dotted teer = **infer** hua, store nahi hua

`make_diagrams.py` diagrams frames se banata hai, aur test 39 check karta hai ke files code se match karti hain.

## 12. FOL aur DL ka rules se rishta

| FOL / DL | Rule |
|---|---|
| ∀x∀s∀t (IsA(s,t) ∧ HasSkill(x,s) → HasSkill(x,t)) | R1 |
| MeetsDegree ← (degree ∨ 5+ saal) | R2 + R3 (OR ko do rules mein toda) |
| ∀s (RequiresSkill(r,s) → HasSkill(x,s)) wala general formula | R5 se R10 (har role ka alag rule) |
| Candidate ⊑ Person | R15 |
| TensorFlowSkill ⊑ DeepLearningSkill ⊑ MachineLearningSkill | is_a facts + R1 |

Shart ke andar ∀ Horn nahi hota, is liye har role ka alag Horn rule frames se banaya.
**Program mein DL reasoner nahi hai**; DL sirf report mein domain describe karta hai.

## 13. Har file kya karti hai?

| File | Kaam |
|---|---|
| `knowledge_base.py` | frames, facets, defaults, script, facts, rules |
| `reasoning_engine.py` | `unify`, `find_bindings`, `run_builtin`, `forward_chain`, `backward_chain`, `recommend_all_roles`, `evaluate_role` |
| `app.py` | sirf interface; engine ko call karta hai |
| `ui_helpers.py` | cards, proof tree, graph, JSON aur PDF |
| `demo.py` | terminal mein 8 scenarios |
| `make_diagrams.py` | diagrams frames se |
| `build_report.py` | report asli output se banata hai |
| `tests/test_reasoning.py` | 42 tests |

## 14. Viva demo (step by step)

1. `streamlit run app.py` (ya live link). Backup: `python demo.py`.
2. Sample **D Zara** → ML Engineer card par note: "Inferred through the skill hierarchy".
3. **Forward chaining** tab: Pass 1 mein deep_learning, Pass 2 mein machine_learning dikhao.
4. **Backward chaining** tab: question "has_skill", skill Machine Learning → proof tree mein R1 do dafa.
5. Sample **E Hamza** → Backward: eligible + Data Scientist → `gte(1, 2)` aur `gte(3, 5)` fail.
6. Sidebar mein Hamza ke saal 5 karo → Data Scientist Eligible ban jata hai (R3 exception, live).
7. Sample **G Ayesha** → red chip "Certification", phir certificate add karo → Eligible.
8. **Semantic network** tab: graph drag karke dikhao; dotted = inferred.
9. **Knowledge base** tab: frames, facets, 15 rules.
10. Agar poocha jaye: `python run_checks.py` chala kar 42 tests pass dikhao.

## 15. Koi skill na ho to?

Omar (H): sab roles Not matched, friendly message. Program crash nahi hota. Phir bhi 5 facts
bante hain, jaise `meets_degree(omar, frontend_developer)` aur `person(omar)`.

## 16. Kai roles match hon to?

Zara: ML Engineer aur Python Developer. Usman: Data Analyst aur Python Developer (degree
exception se). Eligible roles cards mein upar aate hain.

## 17. Limitations aur imaandar jawab

| Sawal | Jawab |
|---|---|
| Requirements real hain? | Nahi, illustrative. Claim sirf yeh: in rules ke hisaab se reasoning sahi hai. |
| Skill level? | Nahi, skill haan ya na. |
| PyTorch se TensorFlow milta hai? | Nahi. Hierarchy sirf upar jati hai. |
| FOL/DL program mein chalta hai? | Sirf Horn wala hissa (R1 se R15). |
| Graph internet ke baghair? | Interactive graph CDN se aata hai; "Static graph" offline chalta hai. |
| System seekhta hai? | Nahi, knowledge haath se update hoti hai. |
