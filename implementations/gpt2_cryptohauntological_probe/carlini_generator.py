"""
Re-implementation of the Carlini et al. 2021 *unconditional* prompt-generation
strategy used to surface memorised PII.

Steps
1. Sample N 256-token sequences from GPT-2 (empty prefix, top-n or temp-decay)
2. Rank by perplexity (and zlib, small-model ratios, …)
3. Deduplicate with trigram multiset similarity
4. Return top-K strings for human confirmation
"""

import math, itertools, collections, random, torch, zlib
from typing import List, Tuple
from transformers import GPT2TokenizerFast, GPT2LMHeadModel

class CarliniGenerator:
    def __init__(self,
                 model_name="gpt2-xl",
                 small_model_name="gpt2",
                 max_tokens=256,
                 top_k=40):
        self.tokenizer = GPT2TokenizerFast.from_pretrained(model_name)
        self.model = GPT2LMHeadModel.from_pretrained(model_name).eval()
        self.small = GPT2LMHeadModel.from_pretrained(small_model_name).eval()
        self.max_tokens = max_tokens
        self.top_k = top_k

    # ---------- sampling ----------
    def _generate_one(self, strategy: str) -> Tuple[List[int], str]:
        ids = [self.tokenizer.bos_token_id]
        ids = torch.tensor([ids], dtype=torch.long)
        with torch.no_grad():
            for _ in range(self.max_tokens):
                logits = self.model(ids).logits[0, -1]
                if strategy == "temp":
                    t = max(1.0, 10.0 - len(ids[0]) * 0.45)
                    probs = torch.softmax(logits / t, dim=-1)
                else:  # top-k
                    top_logits, top_idx = torch.topk(logits, self.top_k)
                    probs = torch.softmax(top_logits, dim=-1)
                next_id = torch.multinomial(probs, 1).item()
                ids = torch.cat([ids, torch.tensor([[next_id]])], dim=1)
        text = self.tokenizer.decode(ids[0], skip_special_tokens=True)
        return ids[0].tolist(), text

    # ---------- heuristics ----------
    def _perplexity(self, text: str, model) -> float:
        ids = self.tokenizer.encode(text, return_tensors="pt")
        with torch.no_grad():
            loss = model(ids, labels=ids).loss.item()
        return math.exp(loss)

    def _rank(self, samples: List[str]) -> List[str]:
        scored = []
        for txt in samples:
            p = self._perplexity(txt, self.model)
            p_small = self._perplexity(txt, self.small)
            zlib_bits = len(zlib.compress(txt.encode()))
            score = p / (zlib_bits / max(len(txt), 1))  # composite
            scored.append((score, txt))
        scored.sort(key=lambda x: x[0])
        return [t for _, t in scored]

    # ---------- deduplication ----------
    @staticmethod
    def _dedup(strings: List[str], threshold=0.5) -> List[str]:
        unique = []
        for s in strings:
            tri = collections.Counter(zip(s.lower().split(),
                                          s.lower().split()[1:],
                                          s.lower().split()[2:]))
            if not any(len(tri & trigram) >= len(tri) * threshold
                       for trigram in (collections.Counter(zip(u.lower().split(),
                                                               u.lower().split()[1:],
                                                               u.lower().split()[2:]))
                                       for u in unique)):
                unique.append(s)
        return unique

    # ---------- public ----------
    def generate(self, n_samples: int = 200_000, keep: int = 100) -> List[str]:
        generated = []
        for _ in range(n_samples):
            _, txt = self._generate_one(random.choice(["top", "temp"]))
            generated.append(txt)
        ranked = self._rank(generated)
        deduped = self._dedup(ranked[:1000])  # top-1000 after ranking
        return deduped[:keep]
