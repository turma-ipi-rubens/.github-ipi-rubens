from django.test import TestCase
from unittest.mock import patch
from professor.services.corretor import corrigir_com_ia

class EntregaMock:
    def __init__(self):
        self.resposta = "Resposta acadêmica"
        self.arquivo = None
        self.atividade = AtividadeMock()
        self.nota_ia = 0
        self.feedback_ia = ""
        self.corrigida = False
        self.tentativas_correcao = 0

    def save(self):
        pass

class AtividadeMock:
    def __init__(self):
        self.titulo = "Trabalho de IA"
        self.descricao = "Crie um algoritmo"
        self.criterios = CriteriosManagerMock()

class CriteriosManagerMock:
    def all(self):
        return []

class CorretorIATest(TestCase):
    @patch('professor.services.gemini_services.GeminiService.gerar')
    def test_corrigir_com_ia_sucesso(self, mock_gerar):
        mock_gerar.return_value = '{"nota_final": 8.5, "feedback_geral": "Muito bom trabalho", "criterios": []}'
        
        entrega = EntregaMock()
        resultado = corrigir_com_ia(entrega)
        
        self.assertEqual(resultado.nota_ia, 8.5)
        self.assertEqual(resultado.feedback_ia, "Muito bom trabalho")
        self.assertTrue(resultado.corrigida)
