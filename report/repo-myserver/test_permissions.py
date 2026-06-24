from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from app.models import Servidor, Plano, Jogo, CategoriaServidor, Usuario, ConfiguracaoServidor

class ServidorPermissionsTest(APITestCase):
    def setUp(self):
        # Configurar dados fictícios
        self.dono = Usuario.objects.create(nome="Admin", email="admin@myserver.com", senha="123")
        self.plano = Plano.objects.create(nome="Plano 1", uso_ram=2, uso_armazenamento=10, uso_cpu=1, limite_jogadores=5, preco=10.0)
        self.jogo = Jogo.objects.create(nome="Minecraft")
        self.cat = CategoriaServidor.objects.create(nome="Survival")
        
        self.servidor = Servidor.objects.create(
            dono=self.dono, plano=self.plano, jogo=self.jogo, categoria_servidor=self.cat,
            nome="Servidor Teste", ip="127.0.0.1", porta=25565
        )
        # Cria a configuração do servidor associada
        ConfiguracaoServidor.objects.create(
            servidor=self.servidor, privacidade="publico", exibir_na_pagina_inicial=True
        )

    def test_list_public_servers(self):
        response = self.client.get('/api/servidores/')
        self.assertEqual(response.status_code, 200)
        # Verifica se o IP não é retornado (ocultação de dados sensíveis)
        self.assertNotIn('ip', response.data[0])
