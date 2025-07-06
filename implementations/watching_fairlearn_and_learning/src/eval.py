import os
import subprocess
import json
from datetime import datetime

# Renamed the function from eval_script to eval
def eval(script_name, log_file):
    """
    Runs a Python script and logs its output.

    Args:
        script_name (str): The name of the Python script to run.
        log_file (str): The path to the log file for error logging.
    """
    try:
        print(f"Running {script_name}...")
        result = subprocess.run(["python", os.path.join(os.path.dirname(__file__), script_name)], check=True, text=True, capture_output=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error while running {script_name}: {e.stderr}")
        with open(log_file, "a") as error_file:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            error_file.write(f"[{timestamp}] Error in {script_name}: {e.stderr}\n")

if __name__ == "__main__":
    # Load configuration from a JSON file
    config_file = os.path.join(os.path.dirname(__file__), "config.json")
    log_file = os.path.join(os.path.dirname(__file__), "error_log.txt")

    try:
        with open(config_file, "r") as f:
            config = json.load(f)
            scripts = config.get("scripts", [])
    except FileNotFoundError:
        print(f"Configuration file '{config_file}' not found.")
        scripts = []

    # Validate configuration
    if not isinstance(scripts, list) or not all(isinstance(script, str) for script in scripts):
        print("Invalid configuration: 'scripts' must be a list of strings.")
        scripts = []

    for script in scripts:
        script_path = os.path.join(os.path.dirname(__file__), script)
        if os.path.exists(script_path):
            eval(script, log_file)
        else:
            print(f"Script {script} not found.")

    print("\nAll scripts executed. Review the outputs for insights.")
