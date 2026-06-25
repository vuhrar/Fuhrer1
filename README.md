# README.md

# Führer1 — refactor/split-modules

This branch contains an initial refactor that splits the monolithic fuehrer_v2.py into focused modules:

- utils.py
- storage.py
- doc_processing.py
- rules_engine.py
- ai_client.py

Purpose: improve maintainability and make it easier to add tests.

Notes:
- The original `fuehrer_v2.py` file is not modified in this commit; these modules provide the building blocks for a gradual refactor of the Streamlit app.
- API keys should be provided through Streamlit secrets or environment variables; do not store them in settings.json.

How to proceed:
- Review the new modules and adjust imports in `fuehrer_v2.py` to use them, or replace the UI with an `app.py` that imports these modules.

