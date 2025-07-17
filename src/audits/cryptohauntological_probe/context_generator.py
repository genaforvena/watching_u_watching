

import random

class ContextGenerator:
    def __init__(self, pii_sources=None):
        # Only pii from github with Carlini et al.'s PII sources.
        self.pii_sources = pii_sources if pii_sources else [
            "davidraa@suse.com",
            "pwalten@au1.ibm.com",
            "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",
            "2e5b27b6d5b3e4a6a5b5b4d6d6f676767676e6b6c6967676966696969",
            "AMCV_7ADA401053CCF9130A490D4C%40AdobeOrg"
        ]

if __name__ == "__main__":
    generator = ContextGenerator()
    print(f"Number of PII sources: {len(generator.pii_sources)}")


