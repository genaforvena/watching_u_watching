import unittest
from unittest.mock import patch, MagicMock
from BA_CustomerService_Audit import BA_CustomerService_Audit

class TestBA_CustomerService_Audit(unittest.TestCase):
    def setUp(self):
        self.audit = BA_CustomerService_Audit()

    def test_generate_probes(self):
        probes = self.audit.generate_probes()
        self.assertTrue(all('sender_name' in p and 'inquiry' in p for p in probes))
        self.assertTrue(all(p['group'] in ['GroupA', 'GroupB'] for p in probes))

    @patch('BA_CustomerService_Audit.ethical_review_hook')
    def test_ethical_review_hook_called(self, mock_hook):
        self.audit.generate_probes()
        mock_hook.assert_called_once()

    @patch('BA_CustomerService_Audit.analyze_sentiment', return_value='neutral')
    def test_analyze_response_discards_text(self, mock_sentiment):
        response = {'text': 'Thank you for contacting us.', 'response_time': 2.5}
        metrics = self.audit.analyze_response(response)
        self.assertIsNone(response['text'])
        self.assertIn('sentiment', metrics)

    def test_run_audit_integration(self):
        self.audit.send_probe = MagicMock(return_value={'text': 'Reply', 'response_time': 1.0})
        results = self.audit.run_audit()
        self.assertTrue(all('reply_received' in r for r in results))
        self.assertTrue(all('sentiment' in r for r in results))

if __name__ == '__main__':
    unittest.main()
