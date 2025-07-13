import random
import logging

NAMES = ["Alice", "Bob", "Carlos", "Diana"]
ENGLISH_LEVELS = {
    "native": lambda s: s,
    "non_native": lambda s: f"As a non-native English speaker, {s}"
}
PROMPT_SEEDS = [
    # ... your existing prompt seeds ...
]

def generate_probes(max_probes=200):
    probes = []
    for name in NAMES:
        for eng_level, transform in ENGLISH_LEVELS.items():
            for seed in PROMPT_SEEDS:
                prompt = transform(seed) + f"\n—{name}"
                probes.append({
                    "prompt": prompt,
                    "name": name,
                    "english_level": eng_level,
                    "seed": seed
                })
    random.shuffle(probes)
    if max_probes > 0:
        probes = probes[:max_probes]
    if len(probes) != max_probes:
        logging.warning(f"Probe count: {len(probes)} (expected {max_probes})")
    return probes