# Project Structure: `src/` vs `implementations/`

## Overview

This repository uses a two-tiered structure to separate reusable library code from experiment-specific scripts and audit cases.

---

## `src/` — Core Library Code

- **Purpose:**  
  Contains all reusable, production-level modules, classes, and functions.
- **Usage:**  
  Code in `src/` is meant to be imported and reused by multiple experiments, audits, or pipelines.
- **Example Contents:**
  - `src/audits/gemini_linguistic_bias/probe_generator.py`
  - `src/audits/gemini_linguistic_bias/run_audit.py`
  - `src/audits/gemini_linguistic_bias/analyze.py`
  - `src/utils/`, etc.

---

## `implementations/` — Experiments & Audit Scripts

- **Purpose:**  
  Contains scripts, notebooks, and analyses that use (import) the reusable logic from `src/`.
- **Usage:**  
  Each subfolder may correspond to a specific audit case, experiment, or analysis.  
  These may include wrappers, experiment notebooks, and custom scripts.
- **Example Contents:**
  - `implementations/bad_english_bias/run_experiment.py`
  - `implementations/gemini_linguistic_bias/custom_analysis.ipynb`
  - `implementations/gemini_linguistic_bias/README.md`

---

## How to Use

- **Add all reusable code to `src/`.**
- **Add all scripts, notebooks, and experiment-specific code to `implementations/`.**
- **Import from `src/` in your implementation scripts.**  
  For example:
  ```python
from src.audits.gemini_linguistic_bias.probe_generator import generate_grouped_probes
  ```

---

## Why This Structure?

- **Separation of concerns:**  
  Keeps core logic isolated from experiment-specific workflows.
- **Avoids duplication:**  
  Changes to algorithms or utilities only need to be made in `src/`.
- **Scalability:**  
  New audits or experiments can be added in `implementations/` without changing the core library.

---

## Summary Table

| Folder            | Purpose                   | Typical Contents                            |
|-------------------|--------------------------|---------------------------------------------|
| `src/`            | Reusable modules & logic | Functions, classes, utilities, core scripts |
| `implementations/`| Experiments & audits     | Scripts, notebooks, analysis, README        |

---

For further details, see the README files in both folders.