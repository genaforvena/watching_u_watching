import re

class PIIDetector:
    def __init__(self):
        # Regex patterns for common PII types
        self.pii_patterns = {
            "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
            "password_like": r"(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\da-zA-Z]).{8,}|(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}|(?=.*[a-z])(?=.*\d)(?=.*[^\da-zA-Z]).{8,}|(?=.*[A-Z])(?=.*\d)(?=.*[^\da-zA-Z]).{8,}"
        }

    def detect_pii(self, text):
        found_pii = []
        for pii_type, pattern in self.pii_patterns.items():
            matches = re.findall(pattern, text)
            for match in matches:
                found_pii.append({pii_type: match})
        return found_pii

if __name__ == "__main__":
    detector = PIIDetector()
    test_text = "My email is test@example.com and my password is StrongP@ssw0rd!"
    found = detector.detect_pii(test_text)
    print(f"Found PII: {found}")