# Run Instructions

From the project directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
python3 validate_project.py
python3 -m pytest -q
python3 run.py
```

Open the URL printed in the terminal.
