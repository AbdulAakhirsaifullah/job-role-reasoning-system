"""
run_checks.py
-------------
Run this before every push:   python run_checks.py

It runs the same checks as the GitHub Actions workflow:
  1. all unit tests,
  2. the terminal demo (must finish without errors),
  3. a syntax check of the interface files,
  (the diagram files are checked by unit test 39).
"""

import os
import py_compile
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
sys.path.insert(0, HERE)


def main():
    print("1. Unit tests")
    suite = unittest.defaultTestLoader.discover(os.path.join(HERE, "tests"))
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    if not result.wasSuccessful():
        return "Unit tests failed."

    print("\n2. Terminal demo")
    demo = subprocess.run([sys.executable, "demo.py"], capture_output=True, text=True)
    if demo.returncode != 0:
        return "demo.py failed:\n" + demo.stderr
    print("   demo.py finished,", demo.stdout.count("Scenario "), "scenarios")

    print("\n3. Interface files compile")
    for name in ["app.py", "ui_helpers.py"]:
        py_compile.compile(name, doraise=True)
        print("   " + name + " OK")

    print("\nAll checks passed. Safe to push.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
