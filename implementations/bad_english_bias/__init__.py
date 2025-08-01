# Import run_audit_loop conditionally to avoid import errors during testing
try:
    from src.audits.gemini_linguistic_bias.run_audit import run_audit_loop as run_audit_main
except ImportError:
    # Define a placeholder function for testing environments
    def run_audit_main(*args, **kwargs):
        raise ImportError("run_audit_loop is not available in this environment. Please ensure src.audits is properly installed.")