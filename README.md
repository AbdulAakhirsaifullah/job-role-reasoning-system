# Intelligent Job Role & Skill Matching Reasoning System

CT-351 Knowledge Representation & Reasoning, Complex Computing Problem (CCP), Group 9
NED University of Engineering & Technology

A rule-based KR system that models candidates, skills, qualifications, experience,
certifications and job requirements using Frames and Semantic Networks, formalizes
eligibility and skill-matching constraints through First-Order Logic and Description Logic,
and applies Horn clause reasoning with Forward and Backward Chaining to determine suitable
job roles and give explainable decisions.

It is **not** a machine learning model. Nothing is trained. All knowledge is written by hand
in `knowledge_base.py`.

> Role requirements are simplified, illustrative examples written for this academic project.
> They are not official or universal industry standards.

---

## What it does

You enter a candidate's skills, highest degree, years of experience and certifications. For
each of 6 roles the system decides **Fully eligible**, **Partial match** or **Not matched**,
lists every met and missing requirement, and shows the reasoning:

- a **forward chaining** trace, pass by pass, until no new fact can be derived;
- a **backward chaining** proof tree for any question you pick, e.g. `eligible(zara, ml_engineer)`.

## Eligibility policy (one policy, used everywhere)

A candidate is **Fully eligible** for a role only if all four hold:

1. they have every mandatory skill, directly or through the skill hierarchy (TensorFlow → Deep Learning → Machine Learning);
2. their degree rank is at least the role's minimum (none 0, bachelors 1, masters 2, phd 3), **or** they have 5+ years of experience (the exception rule);
3. their years of experience are at least the role's minimum;
4. they hold every certification the role requires.

**Partial match:** at least one mandatory skill, but not everything. **Not matched:** none of
the mandatory skills. Optional skills and certifications are a bonus only.
"Requirements met %" = met requirements / all requirements of the role.

| Role | Mandatory skills | Min degree | Min years | Required certification |
|---|---|---|---|---|
| Data Analyst | Python, SQL, Pandas | Bachelors | 0 | none |
| Machine Learning Engineer | Python, Machine Learning, Data Structures | Bachelors | 1 | none |
| Python Developer | Python, Data Structures | Bachelors | 0 | none |
| Frontend Developer | HTML, CSS, JavaScript | No degree | 0 | none |
| Data Scientist | Python, Statistics, Machine Learning, Pandas | Masters | 1 | none |
| Cloud Engineer | Python, Linux, Cloud Computing | Bachelors | 2 | AWS Certified Solutions Architect |

## Folder structure

```
job_role_reasoning_system/
├── app.py                  Streamlit interface (no reasoning inside)
├── ui_helpers.py           role cards, proof tree, graph, JSON and PDF export
├── knowledge_base.py       frames, facets, defaults, script, facts, rules R1 to R15
├── reasoning_engine.py     unify, forward_chain, backward_chain, recommend_all_roles
├── demo.py                 terminal demo of all 8 sample candidates
├── sample_outputs.txt      real output of demo.py
├── make_diagrams.py        writes the semantic network and frame diagrams from the frames
├── build_report.py         builds report.md from report_template.md and real outputs
├── run_checks.py           run before pushing: tests + demo + compile check
├── requirements.txt        streamlit, reportlab (pinned)
├── .python-version         Python version for hosts that read it (3.12)
├── .streamlit/config.toml  theme
├── .github/workflows/tests.yml   runs the tests on GitHub
├── report.md / report.docx       CCP report
├── report_template.md
├── viva_questions.md
├── beginner_guide.md       explanation in Roman Urdu
├── tools/build_docx.py     converts report.md to report.docx (needs pandoc)
├── tests/test_reasoning.py 42 unit tests
└── diagrams/               .mmd sources and .png images
```

## Run it on your computer

Open a terminal **inside the `job_role_reasoning_system` folder**. Python 3.11 or newer.

### Windows (Command Prompt or PowerShell)

```bat
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

If PowerShell blocks activation, run once:
`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, then activate again.

### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

The app opens at `http://localhost:8501`. Stop it with `Ctrl + C`.

### Terminal demo and tests (no Streamlit needed)

```bash
python demo.py                                # all 8 sample candidates with traces
python -m unittest discover -s tests -v      # 42 unit tests
python run_checks.py                          # tests + demo + compile check, before pushing
```

### Regenerate diagrams and the report after changing the knowledge base

```bash
python make_diagrams.py                        # rewrites diagrams/*.mmd
python demo.py > sample_outputs.txt
python build_report.py                         # rewrites report.md (runs the tests too)
python tools/build_docx.py                     # rewrites report.docx (needs pandoc + python-docx)
```

PNG images are rendered from the `.mmd` files with the Mermaid CLI
(`npx -p @mermaid-js/mermaid-cli mmdc -i diagrams/NAME.mmd -o diagrams/NAME.png -b white -s 2`)
or by pasting the file into https://mermaid.live and exporting.

---

## Deployment (live link)

I cannot deploy for you. These are the steps you do yourself. The app needs no secrets,
no database and no system packages, so the free tier of Streamlit Community Cloud is enough.

### 1. Put the project on GitHub

1. Sign in at https://github.com and click **New repository**. Name it, for example,
   `job-role-reasoning-system`. Choose **Public** (Community Cloud's free tier deploys public
   repos most easily). Do **not** add a README or .gitignore (the project has them).
2. In a terminal inside the project folder:

   ```bash
   python run_checks.py
   git init
   git add .
   git commit -m "CT-351 CCP: job role reasoning system"
   git branch -M main
   git remote add origin https://github.com/YOUR-USERNAME/job-role-reasoning-system.git
   git push -u origin main
   ```

3. On GitHub, open the **Actions** tab. The `tests` workflow should finish with a green tick.

### 2. Deploy on Streamlit Community Cloud

1. Go to https://share.streamlit.io and sign in with GitHub. Allow access to your repositories.
2. Click **Create app**, then **Deploy a public app from GitHub**.
3. Repository: `YOUR-USERNAME/job-role-reasoning-system`. Branch: `main`. Main file path: `app.py`.
4. Optional: choose a custom subdomain in **App URL**.
5. Open **Advanced settings** and select **Python 3.12**.
6. Click **Deploy**. The first build installs `requirements.txt` and takes a few minutes.
7. When it finishes you get a link like `https://YOUR-APP.streamlit.app`. Open it on a phone to
   check it works off your laptop.

### 3. Update the live app

Change the code, then:

```bash
python run_checks.py
git add .
git commit -m "Describe the change"
git push
```

Community Cloud redeploys automatically after each push. If it does not, open the app's
menu on share.streamlit.io and choose **Reboot app**.

Free apps go to sleep after some days without visitors. Open the link a few minutes before
your viva so it is awake.

### Fallback host: Hugging Face Spaces

1. Sign in at https://huggingface.co and click **New Space**. Pick a name, choose the
   **Streamlit** SDK, and the free CPU hardware.
2. Upload all project files (or push with git to the Space's repository).
3. Make sure the Space's own `README.md` starts with this block (Spaces read it for settings):

   ```yaml
   ---
   title: Job Role Reasoning System
   sdk: streamlit
   sdk_version: 1.62.0
   app_file: app.py
   python_version: "3.12"
   ---
   ```

4. The Space builds and gives you a `https://huggingface.co/spaces/USER/NAME` link.

(A second option is Render: create a **Web Service** from the GitHub repo, build command
`pip install -r requirements.txt`, start command
`streamlit run app.py --server.port $PORT --server.address 0.0.0.0`, and set the environment
variable `PYTHON_VERSION` to `3.12.8`.)

### Deployment notes

- `requirements.txt` pins `streamlit==1.62.0` and `reportlab==5.0.1`. Both are pure-pip installs;
  `packages.txt` is not needed because `st.graphviz_chart` draws in the browser.
- The interactive graph loads Cytoscape.js from the jsDelivr CDN in the visitor's browser. The
  "Static graph" view works without it.
- All file paths in the code are built from the project folder with `os.path`, so the app runs
  the same on Windows, macOS and Linux servers.

---

## Known limitations

- Only 6 roles, 18 skills, 4 degree levels and 3 certificates; requirements are illustrative.
- Skills are yes or no; no skill levels or per-skill experience.
- The skill hierarchy only goes upward (TensorFlow implies Machine Learning, not the reverse).
- "Missing" and "Partial match" use the Closed World Assumption (not stated means false).
- FOL and DL describe the domain in the report; the program has no FOL prover or DL reasoner.
- The knowledge base is edited by hand; the system does not learn.
