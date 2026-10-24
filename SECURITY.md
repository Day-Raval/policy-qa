# Security policy

## Reporting a vulnerability

Email **dayesh.raval@gmail.com** with the subject `policy-qa security`, or open a private security advisory at https://github.com/Day-Raval/policy-qa/security/advisories/new.

Please include what you found, how to reproduce it, and which agent you used. You will get a reply within 7 days, and confirmed issues are fixed in a new release listed in CHANGELOG.md.

**Never include a real company policy in a report.** Reproduce the issue with synthetic policies like those in `evals/corpus/`.

## Scope

The plugin contains markdown instructions, a local install script and Python scripts that use only the standard library. `index.py` and `retrieve.py` read the `.md` and `.txt` files in the folder you point them at; `retrieve.py` writes its results to a JSON file only when given `--out`. `check_citations.py` reads the answer and results files you point it at. None of them make network calls. The skill has no MCP servers.

The skill reports what the supplied documents say. It is not legal or HR advice.
