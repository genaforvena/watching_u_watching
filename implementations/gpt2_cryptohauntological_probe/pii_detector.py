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

    def swap_back(self, s):
        # Implement the Y<->Z swap back logic
        # This assumes a simple character swap.
        return s.replace('Y', '#TEMP#').replace('Z', 'Y').replace('#TEMP#', 'Z')

def swap_back(s):
    # Implement the Y<->Z swap back logic
    # This assumes a simple character swap.
    return s.replace('Y', '#TEMP#').replace('Z', 'Y').replace('#TEMP#', 'Z')

if __name__ == "__main__":
    detector = PIIDetector()
    test_text = "My email is test@example.com and my password is StrongP@ssw0rd!"
    found = detector.detect_pii(test_text)
    print(f"Found PII: {found}")

    # Test swap_back
    swapped_text = "ZebraY"
    original_text = swap_back(swapped_text)
    print(f"Swapped '{swapped_text}' back to '{original_text}'")