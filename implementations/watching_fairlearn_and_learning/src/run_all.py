import os
import subprocess

def run_script(script_name):
    """
    Runs a Python script and prints its output.

    Args:
        script_name (str): The name of the Python script to run.
    """
    try:
        print(f"Running {script_name}...")
        result = subprocess.run(["python", script_name], check=True, text=True, capture_output=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error while running {script_name}: {e.stderr}")

if __name__ == "__main__":
    # Define the scripts to run in sequence
    scripts = [
        "llm_replier.py",
        "fairlearn_processor.py",
        "bias_evaluator.py"
    ]

    for script in scripts:
        if os.path.exists(script):
            run_script(script)
        else:
            print(f"Script {script} not found.")

    print("\nAll scripts executed. Review the outputs for insights.")
