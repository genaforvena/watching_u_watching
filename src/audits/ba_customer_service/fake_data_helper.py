import random
import string

def generate_synthetic_name(origin: str = None) -> str:
    """
    Generate a synthetic name based on origin (e.g., for demographic simulation).
    """
    # Example: Use origin to select name pool (expand as needed)
    name_pools = {
        'british': ['John Smith', 'Emily Clark', 'Oliver Brown'],
        'minority': ['Aisha Khan', 'Raj Patel', 'Chen Wang'],
        'default': ['Alex Taylor', 'Sam Lee', 'Jordan Kim']
    }
    pool = name_pools.get(origin, name_pools['default'])
    return random.choice(pool)

def generate_fake_email(name: str) -> str:
    """
    Generate a fake email address from a name.
    """
    username = ''.join(c for c in name.lower() if c.isalnum())
    domain = random.choice(['example.com', 'testmail.com', 'fakemail.org'])
    return f"{username}@{domain}"
