import json
import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import console_data


def model(name, family, cost_in=0, cost_out=0, context=1000, provider='opencode-go'):
    return {
        'name': name,
        'family': family,
        'release_date': '2026-01-01',
        'status': 'active',
        'context_limit': context,
        'output_limit': 100,
        'input_modalities': ['text'],
        'tool_call': True,
        'cost_input': cost_in,
        'cost_output': cost_out,
        'provider': {'npm': '@ai-sdk/openai-compatible'},
    }


PROVIDERS = {
    'opencode-go': {'models': {
        'minimax-m3.1-flash-free': model('MiniMax M3.1 Flash Free', 'minimax', 0, 0, 1000000),
        'minimax-m3': model('MiniMax M3', 'minimax', 0.3, 1.2, 1000000),
        'beam-free': model('Beam Free', 'beam', 0, 0, 1048576),
    }},
    'console-openrouter': {'models': {
        'minimax/minimax-m3.1-flash:free': model('MiniMax M3.1 Flash (free)', 'minimax', 0, 0, 1000000),
        'nvidia/nemotron-3-ultra-550b-a55b': model('Nemotron 3 Ultra', 'nemotron', 0.6, 2.4),
        'nvidia/nemotron-3-ultra-550b-a55b:free': model('Nemotron 3 Ultra (free)', 'nemotron', 0, 0),
    }},
}


class ConsoleDataTests(unittest.TestCase):
    def setUp(self):
        self.entries = console_data.build_index(PROVIDERS)

    def test_index_is_keyed_by_last_path_segment(self):
        # the Go provider is preferred over OpenRouter for the same model
        hit = console_data.lookup(self.entries, 'minimax-m3.1-flash:free')
        self.assertIsNotNone(hit)
        self.assertEqual(hit['provider'], 'opencode-go')
        openrouter = console_data.lookup(self.entries, 'minimax/minimax-m3.1-flash:free')
        self.assertEqual(openrouter['provider'], 'opencode-go')

    def test_lookup_prefers_exact_then_prefix(self):
        exact = console_data.lookup(self.entries, 'minimax-m3')
        self.assertEqual(exact['id'], 'minimax-m3')
        prefix = console_data.lookup(self.entries, 'nvidia/nemotron-3-ultra-550b-a55b')
        self.assertEqual(prefix['provider'], 'console-openrouter')

    def test_base_model_same_relation(self):
        base = console_data.base_model_for('minimax-m3.1-flash-free', self.entries, None, 'minimax')
        self.assertEqual(base['id'], 'minimax-m3')
        self.assertEqual(base['relation'], 'sibling')
        self.assertEqual(base['input'], 0.3)

    def test_base_model_ignores_free_candidates(self):
        base = console_data.base_model_for('nvidia/nemotron-3-ultra-550b-a55b:free', self.entries,
                                           None, 'nemotron')
        self.assertEqual(base['id'], 'nvidia/nemotron-3-ultra-550b-a55b')
        self.assertEqual(base['relation'], 'same')

    def test_base_model_without_counterpart(self):
        self.assertIsNone(console_data.base_model_for('beam-free', self.entries, None, 'beam'))

    def test_base_model_falls_back_to_go_rows(self):
        rows = [{'go_id': 'beam-free', 'input': 1.0, 'output': 3.0}]
        base = console_data.base_model_for('beam-free', self.entries, rows, 'beam')
        self.assertEqual(base['provider'], 'opencode-go')
        self.assertEqual(base['relation'], 'same')

    def test_load_missing_file_is_empty(self):
        self.assertEqual(console_data.load('/nonexistent/console_models.json'), {})


if __name__ == '__main__':
    unittest.main()
