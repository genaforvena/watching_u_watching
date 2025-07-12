def generate_name_bias_probes(n):
    # Return n synthetic probes for names bias test (Anglo vs non-Anglo names)
    probes = []
    for i in range(n):
        probes.append({"prompt": f"Test prompt {i} with Anglo/non-Anglo name", "type": "name"})
    return probes

def generate_article_bias_probes(n):
    # Return n synthetic probes for articles bias test (with/without articles)
    probes = []
    for i in range(n):
        probes.append({"prompt": f"Test prompt {i} with/without article", "type": "article"})
    return probes