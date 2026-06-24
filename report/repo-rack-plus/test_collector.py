from django.test import TestCase
from unittest.mock import patch
from agente.collector import Collector

class MockConfig:
    def get(self, section, option, default=None):
        return default

class TelemetryCollectorTest(TestCase):
    @patch('agente.collector.get_cpu_name')
    def test_collect_cpu_metrics(self, mock_cpu):
        mock_cpu.return_value = "Intel Core i7"
        config = MockConfig()
        collector = Collector(config)
        # Verifica se o coletor lê corretamente os dados fictícios mockados
        self.assertEqual(collector.get_system_info()['cpu_name'], "Intel Core i7")
