from framework.rate_limiter import rate_limiter
from utils.fake_data_helper import generate_synthetic_names
from utils.ethical_review_hook import ethical_review_hook
from correspondence_audit import CorrespondenceAudit
import time

class BA_CustomerService_Audit(CorrespondenceAudit):
    """
    Audit for British Airways customer service responsiveness bias.
    Implements Issue #25 requirements.
    """
    def __init__(self, num_probes=100):
        super().__init__()
        self.num_probes = num_probes
        self.probes = []
        self.results = []

    @rate_limiter(requests=5, period=60)
    def generate_probes(self):
        # Generate synthetic names by demographic group
        name_groups = generate_synthetic_names(groups=['white', 'black', 'asian', 'arabic', 'hispanic'], n=self.num_probes)
        ethical_review_hook(name_groups)
        # Create identical inquiries, varying only sender name
        for group, names in name_groups.items():
            for name in names:
                self.probes.append({
                    'sender_name': name,
                    'group': group,
                    'content': "Hello, I have a question about my upcoming flight. Could you please assist?"
                })
        return self.probes

    @rate_limiter(requests=5, period=60)
    def submit_probes(self):
        # Simulate sending emails/web forms
        for probe in self.probes:
            # Here, integrate with actual email/web form submission logic
            send_time = time.time()
            # Simulate BA response (replace with real integration)
            response = self._simulate_ba_response(probe)
            response_time = time.time() - send_time
            sentiment = self._analyze_sentiment(response['reply_text'])
            # Immediately discard raw reply text after analysis
            self.results.append({
                'sender_name': probe['sender_name'],
                'group': probe['group'],
                'response_received': response['received'],
                'response_time': response_time,
                'sentiment': sentiment
            })
        return self.results

    def _simulate_ba_response(self, probe):
        # Placeholder for integration with BA system
        # Simulate random response
        import random
        received = random.choice([True, False])
        reply_text = "Thank you for contacting British Airways. We will get back to you soon." if received else ""
        return {'received': received, 'reply_text': reply_text}

    def _analyze_sentiment(self, text):
        # Placeholder for sentiment analysis
        if not text:
            return None
        # Simple rule-based sentiment
        if "thank you" in text.lower():
            return "positive"
        return "neutral"

    def analyze_results(self):
        # Aggregate results for bias detection
        from collections import defaultdict
        stats = defaultdict(lambda: {'responses': 0, 'total': 0, 'avg_time': 0, 'sentiments': []})
        for r in self.results:
            stats[r['group']]['total'] += 1
            if r['response_received']:
                stats[r['group']]['responses'] += 1
                stats[r['group']]['avg_time'] += r['response_time']
                stats[r['group']]['sentiments'].append(r['sentiment'])
        for group in stats:
            if stats[group]['responses'] > 0:
                stats[group]['avg_time'] /= stats[group]['responses']
        return stats
