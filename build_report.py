"""
build_report.py
---------------
Builds report.md from report_template.md. Every trace, table and test result in
the report is filled in from REAL program output, so nothing is typed by hand:

  - traces and role tables  <- sample_outputs.txt (written by demo.py)
  - test table              <- a fresh run of the unit tests
  - rule table, snippets    <- the actual rules and source code

Run (from the project folder):
    python demo.py > sample_outputs.txt
    python build_report.py
"""

import collections
import datetime
import inspect
import io
import os
import platform
import re
import unittest

import reasoning_engine
from knowledge_base import RULES, build_domain_facts
from reasoning_engine import rule_to_text

HERE = os.path.dirname(os.path.abspath(__file__))

FOL_REF = {"R1": "F1", "R2": "F2", "R3": "F3", "R4": "F4", "R11": "F7", "R12": "F8",
           "R13": "F9", "R14": "F13", "R15": "F12"}


def read(name):
    with open(os.path.join(HERE, name), encoding="utf-8") as f:
        return f.read()


def scenarios(output):
    """Split sample_outputs.txt into {letter: text of that scenario}."""
    parts = re.split(r"=+\nScenario ([A-H]):[^\n]*\n=+\n", output)
    return {parts[i]: parts[i + 1] for i in range(1, len(parts), 2)}


def block(text, start, end):
    """Lines strictly between a line containing start and the next line containing end."""
    lines = text.splitlines()
    i = next(k for k, line in enumerate(lines) if start in line)
    j = next(k for k in range(i + 1, len(lines)) if end in lines[k])
    return lines[i + 1:j]


def dedent(lines, n=4):
    return "\n".join(line[n:] if line.startswith(" " * n) else line.strip() for line in lines)


def forward(text):
    lines = block(text, "Forward chaining trace", "Backward chaining for")
    return dedent([line for line in lines if line.strip()], 4)


def backward(text):
    lines = block(text, "Backward chaining for", "Explanation (")
    return dedent([line for line in lines if line.strip()], 4)


def facts_line(text):
    line = next(line for line in text.splitlines() if "Initial candidate facts:" in line)
    facts = line.split(":", 1)[1].strip()
    return ".\n".join(re.split(r", (?=[a-z_]+\()", facts)) + "."


def roles_block(text, letter, title):
    lines = block(text, "Role results:", "Forward chaining trace")
    rec = next(line for line in text.splitlines() if "FINAL RECOMMENDATION" in line).strip()
    expl = next(line for line in text.splitlines() if "Explanation (" in line).strip()
    body = dedent([line for line in lines if line.strip()], 4)
    return f"**Scenario {letter}: {title}**\n\n```\n{body}\n```\n\n{expl}  \n{rec}\n"


def rule_table():
    rows = ["| ID | Horn clause | Meaning | FOL |",
            "|-----|" + "-" * 46 + "|" + "-" * 24 + "|------|"]   # dash lengths set column widths
    for rule in RULES:
        fol = FOL_REF.get(rule["id"], "F5 / F6")
        rows.append(f"| {rule['id']} | `{rule_to_text(rule)}` | {rule['meaning']} | {fol} |")
    return "\n".join(rows)


def run_tests():
    suite = unittest.defaultTestLoader.discover(os.path.join(HERE, "tests"))
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    source = read(os.path.join("tests", "test_reasoning.py"))
    expected = {}
    for match in re.finditer(r"def (test_\w+)\(self\):\n((?:\s+#[^\n]*\n)*)", source):
        comment = " ".join(c.strip().lstrip("#").strip() for c in match.group(2).splitlines())
        expected[match.group(1)] = comment.replace("Expected:", "").strip()
    rows = ["| # | Test | Expected | Result |", "|--|------------|----------------------|---|"]
    statuses = re.findall(r"^(test_\w+) \(.*?\) \.\.\. (\w+)", stream.getvalue(), re.M)
    for name, status in sorted(statuses, key=lambda s: int(s[0].split("_")[1])):
        number = int(name.split("_")[1])
        title = name.split("_", 2)[2].replace("_", " ")
        rows.append(f"| {number} | {title} | {expected.get(name, '') or 'see code'} | {status} |")
    passed = result.testsRun - len(result.failures) - len(result.errors)
    summary = f"{result.testsRun} tests ran, {passed} passed, " \
              f"{len(result.failures)} failed, {len(result.errors)} errors."
    return "\n".join(rows), summary, result.wasSuccessful(), result.testsRun


def main():
    output = read("sample_outputs.txt")
    scen = scenarios(output)
    titles = {m.group(1): m.group(2) for m in re.finditer(r"Scenario ([A-H]): ([^\n]*)", output)}
    template = read("report_template.md")

    counts = collections.Counter(f[0] for f in build_domain_facts())
    breakdown = ", ".join(f"{n} {name}" for name, n in counts.most_common())
    test_table, summary, ok, test_count = run_tests()

    values = {
        "DOMAIN_FACT_COUNT": str(sum(counts.values())),
        "DOMAIN_FACT_BREAKDOWN": breakdown,
        "RULE_TABLE": rule_table(),
        "ALL_ROLE_TABLES": "\n".join(roles_block(scen[k], k, titles[k]) for k in sorted(scen)),
        "SNIPPET:unify": inspect.getsource(reasoning_engine.unify).rstrip(),
        "SNIPPET:find_bindings": inspect.getsource(reasoning_engine.find_bindings).rstrip(),
        "TEST_TABLE": test_table,
        "TEST_SUMMARY": summary,
        "TEST_COUNT": str(test_count),
        "TEST_DATE": datetime.date.today().isoformat(),
        "PY_VERSION": platform.python_version(),
    }
    for letter, text in scen.items():
        values[f"FACTS:{letter}"] = facts_line(text)
        values[f"FORWARD:{letter}"] = forward(text)
        values[f"BACKWARD:{letter}"] = backward(text)
        values[f"DERIVED:{letter}"] = re.search(r"Total new facts derived: (\d+)", text).group(1)
        keep = [line for line in forward(text).splitlines()
                if re.search(r"\] R(1|3) ->|-> (eligible|recommended)\(|fixed point reached|^Total", line)]
        values[f"FORWARD_SELECT:{letter}"] = "\n".join(keep)

    report = re.sub(r"\{\{([A-Z_]+(?::[A-Za-z_]+)?)\}\}", lambda m: values[m.group(1)], template)
    with open(os.path.join(HERE, "report.md"), "w", encoding="utf-8") as f:
        f.write(report)
    print("report.md written.", summary)
    if not ok:
        raise SystemExit("Some tests failed: fix them before submitting the report.")


if __name__ == "__main__":
    main()
