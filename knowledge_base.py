"""
knowledge_base.py
-----------------
The KNOWLEDGE BASE of the Intelligent Job Role & Skill Matching Reasoning System.

This file contains ONLY knowledge (no reasoning). It has six parts:

  1. Skill frames          -> 18 skills, their category and their parent skill (is_a)
  2. Qualification frames  -> degree levels with numeric ranks
  3. Certification frames  -> certificates a candidate can hold
  4. Job role frames       -> 6 roles: mandatory skills, minimum degree,
                              minimum experience, required certifications
  5. Candidate frames      -> template (slots, facets, defaults, if-needed) + samples
  6. Script + logic        -> recommendation script, facts and Horn-clause rules

IMPORTANT: all role requirements below are ILLUSTRATIVE, written for an academic
project. They are simplified and are NOT official or universal industry standards.

How frames map to Python:
  - A FRAME is a Python dictionary.
  - A SLOT is a key in that dictionary (e.g. "required_skills").
  - A FACET is information about a slot (type, default, allowed values,
    if_needed), stored in the *_FRAME_TEMPLATE dictionaries.
  - A DEFAULT is the value used when a slot is not filled in.
  - An IF-NEEDED facet names a small function that computes the slot value
    from other slots when it is asked for (e.g. experience_level from years).
"""

# ---------------------------------------------------------------------------
# 1. SKILL FRAMES
# ---------------------------------------------------------------------------
# Slots: name, category, is_a.
# "is_a" is the PARENT skill in the skill taxonomy. Knowing the child skill
# implies knowing the parent skill (rule R1). Example chain:
#     tensorflow -> deep_learning -> machine_learning
# A skill with is_a = None is a top-level skill.

SKILL_FRAMES = {
    "python": {"name": "Python", "category": "programming", "is_a": None},
    "data_structures": {"name": "Data Structures", "category": "programming", "is_a": None},
    "sql": {"name": "SQL", "category": "data", "is_a": None},
    "postgresql": {"name": "PostgreSQL", "category": "data", "is_a": "sql"},
    "pandas": {"name": "Pandas", "category": "data", "is_a": None},
    "data_visualization": {"name": "Data Visualization", "category": "data", "is_a": None},
    "statistics": {"name": "Statistics", "category": "ai", "is_a": None},
    "machine_learning": {"name": "Machine Learning", "category": "ai", "is_a": None},
    "scikit_learn": {"name": "scikit-learn", "category": "ai", "is_a": "machine_learning"},
    "deep_learning": {"name": "Deep Learning", "category": "ai", "is_a": "machine_learning"},
    "tensorflow": {"name": "TensorFlow", "category": "ai", "is_a": "deep_learning"},
    "pytorch": {"name": "PyTorch", "category": "ai", "is_a": "deep_learning"},
    "html": {"name": "HTML", "category": "web", "is_a": None},
    "css": {"name": "CSS", "category": "web", "is_a": None},
    "javascript": {"name": "JavaScript", "category": "web", "is_a": None},
    "react": {"name": "React", "category": "web", "is_a": "javascript"},
    "linux": {"name": "Linux", "category": "cloud", "is_a": None},
    "cloud_computing": {"name": "Cloud Computing", "category": "cloud", "is_a": None},
}

SKILL_CATEGORIES = {
    "programming": "Programming",
    "data": "Data Handling",
    "ai": "AI and Statistics",
    "web": "Web Development",
    "cloud": "Cloud and Systems",
}

SKILL_FRAME_TEMPLATE = {
    "name": {"type": "text", "required": True},
    "category": {"type": "text", "required": True,
                 "allowed_values": list(SKILL_CATEGORIES.keys())},
    "is_a": {"type": "skill ID or None", "required": False, "default": None,
             "allowed_values": list(SKILL_FRAMES.keys())},
}


# ---------------------------------------------------------------------------
# 2. QUALIFICATION FRAMES (degree levels)
# ---------------------------------------------------------------------------
# Each degree has a numeric RANK so that "at least a bachelors" can be checked
# with one number comparison: rank(candidate degree) >= minimum rank of role.

QUALIFICATION_FRAMES = {
    "none": {"name": "No degree", "rank": 0},
    "bachelors": {"name": "Bachelors", "rank": 1},
    "masters": {"name": "Masters", "rank": 2},
    "phd": {"name": "PhD", "rank": 3},
}

QUALIFICATION_FRAME_TEMPLATE = {
    "name": {"type": "text", "required": True},
    "rank": {"type": "integer", "required": True, "allowed_values": [0, 1, 2, 3]},
}

# A candidate with this many years of experience or more is treated as meeting
# the degree requirement of any role (the EXCEPTION rule, R3).
DEGREE_WAIVER_YEARS = 5


# ---------------------------------------------------------------------------
# 3. CERTIFICATION FRAMES
# ---------------------------------------------------------------------------

CERTIFICATION_FRAMES = {
    "aws_solutions_architect": {
        "name": "AWS Certified Solutions Architect", "issuer": "Amazon Web Services",
        "related_skill": "cloud_computing"},
    "google_data_analytics": {
        "name": "Google Data Analytics Certificate", "issuer": "Google",
        "related_skill": "data_visualization"},
    "tensorflow_developer": {
        "name": "TensorFlow Developer Certificate", "issuer": "Google",
        "related_skill": "tensorflow"},
}

CERTIFICATION_FRAME_TEMPLATE = {
    "name": {"type": "text", "required": True},
    "issuer": {"type": "text", "required": False, "default": "Unknown issuer"},
    "related_skill": {"type": "skill ID", "required": False, "default": None,
                      "allowed_values": list(SKILL_FRAMES.keys())},
}


# ---------------------------------------------------------------------------
# 4. JOB ROLE FRAMES
# ---------------------------------------------------------------------------
# ELIGIBILITY POLICY (used everywhere in the project):
#   A candidate is FULLY ELIGIBLE for a role only if ALL of these hold:
#     1. they have every mandatory skill (directly or through the skill hierarchy),
#     2. they meet the degree requirement (or the 5-year experience exception),
#     3. they meet the minimum years of experience,
#     4. they hold every REQUIRED certification of that role (if any).
#   PARTIAL MATCH : not fully eligible, but has at least one mandatory skill.
#   NOT MATCHED   : has none of the mandatory skills.
#   Optional skills and optional certifications are a bonus only.

JOB_ROLE_FRAMES = {
    "data_analyst": {
        "role_id": "data_analyst",
        "name": "Data Analyst",
        "description": "Cleans, queries and summarises data to answer business questions.",
        "required_skills": ["python", "sql", "pandas"],
        "optional_skills": ["data_visualization", "statistics"],
        "min_degree": "bachelors",
        "min_experience": 0,
        "required_certifications": [],
        "optional_certifications": ["google_data_analytics"],
    },
    "ml_engineer": {
        "role_id": "ml_engineer",
        "name": "Machine Learning Engineer",
        "description": "Builds and deploys machine learning models in software.",
        "required_skills": ["python", "machine_learning", "data_structures"],
        "optional_skills": ["deep_learning", "statistics"],
        "min_degree": "bachelors",
        "min_experience": 1,
        "required_certifications": [],
        "optional_certifications": ["tensorflow_developer"],
    },
    "python_developer": {
        "role_id": "python_developer",
        "name": "Python Developer",
        "description": "Writes general-purpose software and scripts in Python.",
        "required_skills": ["python", "data_structures"],
        "optional_skills": ["sql"],
        "min_degree": "bachelors",
        "min_experience": 0,
        "required_certifications": [],
        "optional_certifications": [],
    },
    "frontend_developer": {
        "role_id": "frontend_developer",
        "name": "Frontend Developer",
        "description": "Builds the visible part of websites that users interact with.",
        "required_skills": ["html", "css", "javascript"],
        "optional_skills": ["react"],
        "min_degree": "none",
        "min_experience": 0,
        "required_certifications": [],
        "optional_certifications": [],
    },
    "data_scientist": {
        "role_id": "data_scientist",
        "name": "Data Scientist",
        "description": "Uses statistics and machine learning to find patterns in data.",
        "required_skills": ["python", "statistics", "machine_learning", "pandas"],
        "optional_skills": ["data_visualization", "sql"],
        "min_degree": "masters",
        "min_experience": 1,
        "required_certifications": [],
        "optional_certifications": [],
    },
    "cloud_engineer": {
        "role_id": "cloud_engineer",
        "name": "Cloud Engineer",
        "description": "Designs and runs applications on cloud infrastructure.",
        "required_skills": ["python", "linux", "cloud_computing"],
        "optional_skills": [],
        "min_degree": "bachelors",
        "min_experience": 2,
        "required_certifications": ["aws_solutions_architect"],
        "optional_certifications": [],
    },
}

JOB_ROLE_FRAME_TEMPLATE = {
    "role_id": {"type": "text", "required": True},
    "name": {"type": "text", "required": True},
    "description": {"type": "text", "required": False, "default": "No description."},
    "required_skills": {"type": "list of skill IDs", "required": True, "min_items": 1,
                        "allowed_values": list(SKILL_FRAMES.keys())},
    "optional_skills": {"type": "list of skill IDs", "required": False, "default": []},
    "min_degree": {"type": "degree ID", "required": False, "default": "none",
                   "allowed_values": list(QUALIFICATION_FRAMES.keys())},
    "min_experience": {"type": "integer (years)", "required": False, "default": 0},
    "required_certifications": {"type": "list of certification IDs", "required": False,
                                "default": [],
                                "allowed_values": list(CERTIFICATION_FRAMES.keys())},
    "optional_certifications": {"type": "list of certification IDs", "required": False,
                                "default": []},
}


# ---------------------------------------------------------------------------
# 5. CANDIDATE FRAMES
# ---------------------------------------------------------------------------

def experience_level_if_needed(years):
    """IF-NEEDED procedure: compute the experience_level slot from the years slot."""
    if years >= 5:
        return "Senior"
    if years >= 2:
        return "Mid level"
    return "Entry level"


def make_candidate_id(name):
    """IF-NEEDED procedure: turn 'Ali Khan' into the logic constant 'ali_khan'."""
    cleaned = "".join(ch if ch.isalnum() else "_" for ch in str(name).strip().lower())
    cleaned = "_".join(part for part in cleaned.split("_") if part)
    if not cleaned or not cleaned[0].isalpha():
        cleaned = "c_" + cleaned   # a constant must start with a lowercase letter
    return cleaned


CANDIDATE_FRAME_TEMPLATE = {
    "candidate_id": {"type": "text", "required": True, "if_needed": "make_candidate_id(name)"},
    "name": {"type": "text", "required": True, "default": "Candidate"},
    "skills": {"type": "list of skill IDs", "required": False, "default": [],
               "allowed_values": list(SKILL_FRAMES.keys())},
    "degree": {"type": "degree ID", "required": False, "default": "none",
               "allowed_values": list(QUALIFICATION_FRAMES.keys())},
    "total_experience_years": {"type": "integer", "required": False, "default": 0,
                               "range": [0, 50]},
    "experience_level": {"type": "text", "required": False,
                         "if_needed": "experience_level_if_needed(total_experience_years)"},
    "certifications": {"type": "list of certification IDs", "required": False, "default": [],
                       "allowed_values": list(CERTIFICATION_FRAMES.keys())},
    "target_role": {"type": "role ID or None", "required": False, "default": None,
                    "allowed_values": list(JOB_ROLE_FRAMES.keys())},
}


def parse_years(value):
    """Return a whole number of years in the allowed range, 0 for empty, or None if invalid."""
    if value is None or value == "":
        return 0
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    low, high = CANDIDATE_FRAME_TEMPLATE["total_experience_years"]["range"]
    if number != int(number) or not low <= number <= high:
        return None
    return int(number)


def _clean_ids(values, allowed):
    """Keep known IDs once each; return (known, unknown)."""
    known, unknown = [], []
    for value in values or []:
        item_id = str(value).strip().lower().replace(" ", "_").replace("-", "_")
        if item_id in allowed:
            if item_id not in known:
                known.append(item_id)
        elif str(value).strip():
            unknown.append(str(value).strip())
    return known, unknown


def create_candidate(name, skills, degree=None, experience_years=None,
                     certifications=None, target_role=None):
    """
    Fill a Candidate frame.
      - Empty slots get their DEFAULT value from CANDIDATE_FRAME_TEMPLATE.
      - Unknown skills / certifications are removed (allowed_values facet) and reported.
      - Experience outside 0..50 or not a whole number is replaced by the default 0.
      - candidate_id and experience_level are filled by IF-NEEDED procedures.
    Returns (candidate_frame, list_of_warnings).
    """
    t = CANDIDATE_FRAME_TEMPLATE
    warnings = []

    skill_ids, unknown_skills = _clean_ids(skills, SKILL_FRAMES)
    cert_ids, unknown_certs = _clean_ids(certifications, CERTIFICATION_FRAMES)
    if unknown_skills:
        warnings.append("Unknown skills ignored: " + ", ".join(unknown_skills))
    if unknown_certs:
        warnings.append("Unknown certifications ignored: " + ", ".join(unknown_certs))

    if degree not in QUALIFICATION_FRAMES:
        if degree:
            warnings.append(f"Unknown degree '{degree}', default '{t['degree']['default']}' used")
        degree = t["degree"]["default"]

    years = parse_years(experience_years)
    if years is None:
        low, high = t["total_experience_years"]["range"]
        warnings.append(f"Experience must be a whole number from {low} to {high}; 0 used")
        years = t["total_experience_years"]["default"]

    if target_role not in JOB_ROLE_FRAMES:
        target_role = t["target_role"]["default"]

    clean_name = (str(name).strip() if name else "") or t["name"]["default"]
    candidate = {
        "candidate_id": make_candidate_id(clean_name),
        "name": clean_name,
        "skills": skill_ids,
        "degree": degree,
        "total_experience_years": years,
        "experience_level": experience_level_if_needed(years),
        "certifications": cert_ids,
        "target_role": target_role,
    }
    return candidate, warnings


# Sample candidates used in the demo, the report and the tests.
SAMPLE_CANDIDATES = {
    "A: Ali, data analyst (all requirements met)": {
        "name": "Ali", "skills": ["python", "sql", "pandas"],
        "degree": "bachelors", "experience_years": 1, "certifications": [],
        "target_role": "data_analyst"},
    "B: Sara, missing one skill (SQL)": {
        "name": "Sara", "skills": ["python", "pandas", "data_visualization"],
        "degree": "bachelors", "experience_years": 0, "certifications": [],
        "target_role": "data_analyst"},
    "C: Bilal, frontend without a degree": {
        "name": "Bilal", "skills": ["html", "css", "react"],
        "degree": "none", "experience_years": 1, "certifications": [],
        "target_role": "frontend_developer"},
    "D: Zara, skill hierarchy (TensorFlow gives ML)": {
        "name": "Zara", "skills": ["python", "tensorflow", "data_structures", "statistics", "pandas"],
        "degree": "bachelors", "experience_years": 2, "certifications": [],
        "target_role": "ml_engineer"},
    "E: Hamza, degree failure (needs Masters)": {
        "name": "Hamza", "skills": ["python", "statistics", "machine_learning", "pandas"],
        "degree": "bachelors", "experience_years": 3, "certifications": [],
        "target_role": "data_scientist"},
    "F: Usman, experience exception (6 years, no degree)": {
        "name": "Usman", "skills": ["python", "data_structures", "postgresql", "pandas"],
        "degree": "none", "experience_years": 6, "certifications": [],
        "target_role": "python_developer"},
    "G: Ayesha, missing certification": {
        "name": "Ayesha", "skills": ["python", "linux", "cloud_computing"],
        "degree": "bachelors", "experience_years": 3, "certifications": [],
        "target_role": "cloud_engineer"},
    "H: Omar, no skills selected": {
        "name": "Omar", "skills": [], "degree": None, "experience_years": None,
        "certifications": [], "target_role": None},
}


def create_sample_candidate(key):
    data = SAMPLE_CANDIDATES[key]
    return create_candidate(data["name"], data["skills"], data["degree"],
                            data["experience_years"], data["certifications"],
                            data["target_role"])


# ---------------------------------------------------------------------------
# 6a. SCRIPT: the stereotyped sequence of events for one recommendation
# ---------------------------------------------------------------------------

RECOMMENDATION_SCRIPT = {
    "script_name": "Get a job role recommendation",
    "entry_conditions": ["A candidate wants to know which roles suit their profile"],
    "roles_in_script": ["Candidate", "Reasoning System"],
    "props": ["Skill list", "Degree", "Experience", "Certifications",
              "Job role frames", "Rules"],
    "scenes": [
        "1. Candidate enters a name, skills, degree, years of experience and certifications.",
        "2. System fills the Candidate frame (defaults, if-needed slots, invalid values removed).",
        "3. System turns the frame into facts: candidate, has_skill, has_degree, "
        "total_experience_years, has_cert.",
        "4. Forward chaining derives inherited skills, meets_degree, meets_experience, "
        "eligible and recommended facts.",
        "5. System labels each role: Fully eligible, Partial match or Not matched.",
        "6. System lists what is met and what is missing (Closed World Assumption) and explains it.",
        "7. Candidate may ask a specific question; backward chaining tries to prove it.",
    ],
    "results": ["Candidate sees recommended roles, missing requirements and the reasoning trace"],
}


# ---------------------------------------------------------------------------
# 6b. LOGIC: facts and Horn-clause rules
# ---------------------------------------------------------------------------
# ATOM: a tuple (predicate, arg1, arg2, ...), e.g. ("has_skill", "ali", "python").
# VARIABLE: a string starting with an UPPERCASE letter ("X", "R", "S").
# CONSTANT: a lowercase string ("ali", "python") or a whole number (3).
# BUILT-IN: gte(A, B) means A >= B. It is not stored as a fact; the engine
#           computes it. Its arguments must already have values when it is reached,
#           so it is always placed AFTER the premises that give those values.
# RULE: {"id", "head": one atom, "body": list of atoms}. One head and only
#       positive premises -> every rule is a HORN CLAUSE.


def build_domain_facts():
    """Facts that are the same for every candidate (taken from the frames)."""
    facts = set()
    for skill_id, skill in SKILL_FRAMES.items():
        facts.add(("skill", skill_id))
        facts.add(("belongs_to", skill_id, skill["category"]))
        if skill["is_a"]:
            facts.add(("is_a", skill_id, skill["is_a"]))
    for degree_id, degree in QUALIFICATION_FRAMES.items():
        facts.add(("degree_rank", degree_id, degree["rank"]))
    for cert_id in CERTIFICATION_FRAMES:
        facts.add(("certification", cert_id))
    facts.add(("degree_waiver_years", DEGREE_WAIVER_YEARS))
    for role_id, role in JOB_ROLE_FRAMES.items():
        facts.add(("job_role", role_id))
        for skill in role["required_skills"]:
            facts.add(("requires_skill", role_id, skill))
        facts.add(("min_degree_rank", role_id, QUALIFICATION_FRAMES[role["min_degree"]]["rank"]))
        facts.add(("min_experience", role_id, role["min_experience"]))
        for cert in role["required_certifications"]:
            facts.add(("requires_cert", role_id, cert))
    return facts


def build_candidate_facts(candidate):
    """Facts about one candidate, taken from the Candidate frame."""
    cid = candidate["candidate_id"]
    facts = {("candidate", cid),
             ("has_degree", cid, candidate["degree"]),
             ("total_experience_years", cid, candidate["total_experience_years"])}
    for skill in candidate["skills"]:
        facts.add(("has_skill", cid, skill))
    for cert in candidate["certifications"]:
        facts.add(("has_cert", cid, cert))
    return facts


def build_rules():
    """
    Build the rule base. Support rules come first (R1 to R4), then one
    eligibility rule per role (generated from the Job Role frames, so rules
    and frames can never disagree), then the remaining rules.
    """
    rules = [
        {   # Skill hierarchy. is_a comes FIRST: in backward chaining it binds S
            # to a known child skill before has_skill is called again, so the
            # recursion always moves DOWN the finite taxonomy and stops.
            "id": "R1",
            "head": ("has_skill", "X", "T"),
            "body": [("is_a", "S", "T"), ("has_skill", "X", "S")],
            "meaning": "If S is a kind of T and X has S, then X also has T.",
        },
        {
            "id": "R2",
            "head": ("meets_degree", "X", "R"),
            "body": [("has_degree", "X", "D"), ("degree_rank", "D", "N"),
                     ("min_degree_rank", "R", "M"), ("gte", "N", "M")],
            "meaning": "X meets the degree requirement of R if the rank of X's degree "
                       "is at least R's minimum rank.",
        },
        {
            "id": "R3",
            "head": ("meets_degree", "X", "R"),
            "body": [("total_experience_years", "X", "Y"), ("degree_waiver_years", "W"),
                     ("gte", "Y", "W"), ("job_role", "R")],
            "meaning": f"EXCEPTION: {DEGREE_WAIVER_YEARS} or more years of experience "
                       "counts as meeting the degree requirement of every role.",
        },
        {
            "id": "R4",
            "head": ("meets_experience", "X", "R"),
            "body": [("total_experience_years", "X", "Y"), ("min_experience", "R", "M"),
                     ("gte", "Y", "M")],
            "meaning": "X meets the experience requirement of R if X's years are at "
                       "least R's minimum.",
        },
    ]

    number = len(rules) + 1
    for role_id, role in JOB_ROLE_FRAMES.items():
        body = [("has_skill", "X", skill) for skill in role["required_skills"]]
        body.append(("meets_degree", "X", role_id))
        body.append(("meets_experience", "X", role_id))
        body += [("has_cert", "X", cert) for cert in role["required_certifications"]]
        extra = " and every required certification" if role["required_certifications"] else ""
        rules.append({
            "id": f"R{number}",
            "head": ("eligible", "X", role_id),
            "body": body,
            "meaning": f"X is eligible for {role['name']} if X has every mandatory skill, "
                       f"meets the degree and experience requirements{extra}.",
        })
        number += 1

    rules += [
        {"head": ("recommended", "X", "R"), "body": [("eligible", "X", "R")],
         "meaning": "If X is eligible for role R, then R is recommended to X."},
        {"head": ("matched_skill", "X", "R", "S"),
         "body": [("requires_skill", "R", "S"), ("has_skill", "X", "S")],
         "meaning": "S is a matched skill of X for R if R requires S and X has S."},
        {"head": ("relevant_to", "X", "R"), "body": [("matched_skill", "X", "R", "S")],
         "meaning": "X is relevant to R if X has at least one skill that R requires."},
        {"head": ("knows_category", "X", "C"),
         "body": [("has_skill", "X", "S"), ("belongs_to", "S", "C")],
         "meaning": "X knows category C if X has some skill S that belongs to C."},
        {"head": ("person", "X"), "body": [("candidate", "X")],
         "meaning": "Every candidate is a person."},
    ]
    for rule in rules[number - 1:]:
        rule["id"] = f"R{number}"
        number += 1
    return rules


RULES = build_rules()
BUILTINS = {"gte": lambda a, b: a >= b}
