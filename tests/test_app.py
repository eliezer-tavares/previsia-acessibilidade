     # tests/test_app.py
     # -*- coding: utf-8 -*-
     """
     Testes de integração para app.py.
     Por quê? Verificam rotas web, previsão e guia.
     Como? Usa client do pytest-flask para simular requests; mock modelo e funções.
     """

     import pytest
     from app import app, gerar_guia_preditivo

     @pytest.fixture
     def client():
         app.config['TESTING'] = True
         with app.test_client() as client:  # Client simula browser.
             yield client

     def test_home(client):
         """Testa rota home."""
         rv = client.get('/')
         assert rv.status_code == 200  # OK.
         assert b'PrevisIA' in rv.data  # Verifica conteúdo.

     def test_predict(mocker, client):
         """Testa previsão com mocks."""
         mocker.patch('app.modelo.predict', return_value=[80])
         mocker.patch('app.analisar_url_rapida', return_value={'imagens_sem_alt': 1, 'layout': {}})
         rv = client.post('/predict', data={'url': 'example.com', 'tipo_analise': 'rapida'})
         assert rv.status_code == 200
         assert b'Pontuação prevista: 80' in rv.data

     def test_gerar_guia_preditivo():
         """Testa guia unitário."""
         features = {'layout': {'nav_itens': 5}, 'imagens_sem_alt': 6}
         guia = gerar_guia_preditivo(features, 50, 'https://example.com')
         assert 'Alerta' in guia  # Verifica alerta gerado.
