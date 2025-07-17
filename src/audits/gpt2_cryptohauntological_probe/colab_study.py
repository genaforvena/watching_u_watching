# -*- coding: utf-8 -*-
"""GPT-2 Cryptohauntological Probe - Google Colab Study

This notebook sets up and runs the GPT-2 Cryptohauntological Probe within a Google Colab environment.
The probe investigates how continuous conversational context with PII injection and consistent perturbation
can influence GPT-2 XL's likelihood of reproducing memorized PII.

To run this study:
1. Ensure you have a GPU runtime enabled (Runtime -> Change runtime type -> GPU).
2. Run all cells in sequence.
"""

# @title 1. Clone Repository and Navigate
# @markdown This cell clones the `watching_u_watching` repository and navigates into the project directory.
!git clone https://github.com/genaforvena/watching_u_watching.git
%cd watching_u_watching

# @title 2. Install Dependencies
# @markdown This cell installs the necessary Python packages for the probe.
%pip install -r src/audits/gpt2_cryptohauntological_probe/requirements.txt

# @title 3. Run the GPT-2 Cryptohauntological Probe
# @markdown This cell executes the main probe script. You can specify the number of rounds to run.
# @markdown If `num_rounds` is left empty, the probe will run endlessly.

num_rounds = 4 # @param {type:"integer"}
perturbation_rule = "swap_chars" # @param {type:"string"}

import src.audits.gpt2_cryptohauntological_probe.probe_runner as probe_runner

probe_runner.run_probe_from_args(num_rounds=num_rounds, perturbation_rule=perturbation_rule)
