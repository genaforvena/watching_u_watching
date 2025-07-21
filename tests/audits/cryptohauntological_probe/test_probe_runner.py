import unittest
from unittest.mock import patch, MagicMock
from src.audits.cryptohauntological_probe import probe_runner

class TestProbeRunner(unittest.TestCase):
    @patch('src.audits.cryptohauntological_probe.probe_runner.SpectreProbe')
    @patch('src.audits.cryptohauntological_probe.probe_runner.argparse.ArgumentParser')
    def test_run_probe(self, mock_argparse, mock_spectre_probe):
        # Arrange
        mock_args = MagicMock()
        mock_args.num_rounds = 1
        mock_args.model = 'mock_model'
        mock_args.model_name = 'mock_model_name'
        mock_args.swap_type = 'zy'
        mock_args.initial_word = 'lazy'
        mock_argparse.return_value.parse_args.return_value = mock_args

        mock_probe_instance = MagicMock()
        mock_spectre_probe.return_value = mock_probe_instance

        # Act
        with patch('src.audits.cryptohauntological_probe.probe_runner.os.environ.get', return_value='test_key'):
            probe_runner.run_probe(
                num_rounds=mock_args.num_rounds,
                model=mock_args.model,
                model_name=mock_args.model_name,
                api_key='test_key',
                swap_type=mock_args.swap_type,
                initial_word=mock_args.initial_word
            )

        # Assert
        mock_spectre_probe.assert_called_once_with(
            worker_type='mock_model',
            worker_options={'model_name': 'mock_model_name', 'api_key': 'test_key'},
            initial_word='lazy',
            max_conversation_turns=1,
            thinking_mode=True
        )
        mock_probe_instance.run_probe.assert_called_once_with(swap_type='zy')
        mock_probe_instance.save_logs.assert_called_once_with('mock_model_name_zy_lazy_1_rounds.json')

if __name__ == '__main__':
    unittest.main()
