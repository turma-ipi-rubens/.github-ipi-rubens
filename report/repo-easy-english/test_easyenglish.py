from django.test import TestCase
from django.contrib.auth.models import User
from extensao.models import Flashcard
from easyenglish.models import EstudoSessao

class FlashcardTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='aluno', password='password123')

    def test_create_flashcard(self):
        card = Flashcard.objects.create(
            user=self.user,
            phrase="Hello, world!",
            translation="Olá, mundo!",
            deck="geral"
        )
        self.assertEqual(card.status, 'new')
        self.assertEqual(card.progress, 0)
        self.assertEqual(str(card), "Hello, world!")

    def test_estudo_sessao_taxa_acerto(self):
        sessao = EstudoSessao.objects.create(
            user=self.user,
            cards_estudados=10,
            acertos=7,
            erros=3
        )
        self.assertEqual(sessao.taxa_acerto, 70)
