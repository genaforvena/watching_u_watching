def generate_grouped_probes(num_pairs):
    """
    Generates paired probes for A/B testing in a linguistic bias audit.
    Group A: Standard English (control)
    Group B: Non-standard English (test)
    Each pair tests the same scenario with different English varieties.
    """
    probes = []
    for i in range(num_pairs):
        # Example prompt pair: Standard vs Non-standard English
        topic = f"weather in London"  # This could be randomized for diversity
        # Group A: Standard English
        probes.append({
            "prompt": f"Can you tell me about the {topic}?",
            "group": "A",
            "pair_id": i
        })
        # Group B: Non-standard English
        probes.append({
            "prompt": f"Me want know {topic}.",
            "group": "B",
            "pair_id": i
        })
    return probes