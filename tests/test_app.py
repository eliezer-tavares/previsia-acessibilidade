# Univesp - Projeto Integrador IV - Engenharia de Computação - 2º Semestre 2025
# Desenvolvido por: Eliezer Tavares de Oliveira (principal), Anderson Vianna Ferrari, Efrain Tobal Tavares, Lucas de Goes Vieira Junior
# EN: This file tests the Flask app to ensure 100% coverage. Why? To verify web routes and prediction logic. How? Uses Flask test client and mocks.
# PT: Este arquivo testa a aplicação Flask para garantir 100% de cobertura. Por quê? Para verificar rotas web e lógica de previsão. Como? Usa cliente de teste Flask e mocks.

import pytest
from app import app, gerar_guia_preditivo

@pytest.fixture
def client():
    """
    Creates a test client for Flask app.
    
    EN: Why? To simulate HTTP requests. How? Uses Flask's test_client.
    PT: Por quê? Para simular requisições HTTP. Como? Usa o test_client do Flask.
    """
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home(client):
    """
    Tests home route.
    
    EN: Why? To ensure the form page loads correctly. How? Simulates GET request.
    PT: Por quê? Para garantir que a página do formulário carrega corretamente. Como? Simula requisição GET.
    """
    rv = client.get('/')
    assert rv.status_code == 200
    assert b'PrevisIA' in rv.data

@pytest.mark.parametrize("url, tipo_analise, features, score, expected_text", [
    ('example.com', 'rapida', {'imagens_sem_alt': 1, 'layout': {}}, 80, 'Pontuação prevista: 80'),  # Quick analysis
    ('example.com', 'completa', {'imagens_sem_alt': 1, 'falhas_contraste': 1, 'layout': {}}, 90, 'Pontuação prevista: 90'),  # Complete analysis
    ('invalid.com', 'rapida', None, 0, 'Erro: Falha na análise rápida.'),  # Error case
])
def test_predict(mocker, client, url, tipo_analise, features, score, expected_text):
    """
    Tests prediction route.
    
    :param url: URL to test.
    :param tipo_analise: Type of analysis (rapida or completa).
    :param features: Mock features returned.
    :param score: Mock predicted score.
    :param expected_text: Expected text in response.
    
    EN: Why? To verify prediction and guide generation. How? Mocks analysis and model prediction.
    PT: Por quê? Para verificar previsão e geração de guia. Como? Simula análise e previsão do modelo.
    """
    mocker.patch('app.modelo.predict', return_value=[score])
    mocker.patch('app.analisar_url_rapida', return_value=features)
    if tipo_analise == 'completa':
        mocker.patch('app.analisar_url_completa', return_value=features)
    rv = client.post('/predict', data={'url': url, 'tipo_analise': tipo_analise}, follow_redirects=True)
    print(f"Test predict: URL={url}, Tipo={tipo_analise}, Response={rv.data.decode('utf-8')}")  # Depuração
    assert rv.status_code == 200
    assert expected_text.encode('utf-8') in rv.data

def test_predict_no_model(mocker, client):
    """
    Tests prediction with missing model.
    
    EN: Why? To ensure error handling when model is unavailable. How? Mocks missing model.
    PT: Por quê? Para garantir tratamento de erro quando o modelo está indisponível. Como? Simula modelo ausente.
    """
    mocker.patch('app.modelo', None)
    rv = client.post('/predict', data={'url': 'example.com', 'tipo_analise': 'rapida'}, follow_redirects=True)
    print(f"Test predict_no_model: Response={rv.data.decode('utf-8')}")  # Depuração
    assert rv.status_code == 200
    assert 'Modelo não disponível.' in rv.data.decode('utf-8')

def test_gerar_guia_preditivo():
    """
    Tests predictive guide generation.
    
    EN: Why? To verify narrative guide logic. How? Tests with sample features.
    PT: Por quê? Para verificar a lógica do guia narrativo. Como? Testa com features de exemplo.
    """
    features = {'layout': {'nav_itens': 5}, 'imagens_sem_alt': 6}
    score = 50
    url = 'https://example.com'
    guia = gerar_guia_preditivo(features, score, url)
    print(f"Test gerar_guia_preditivo: Guia={guia}")  # Depuração
    assert 'Pontuação prevista: 50' in guia
    assert 'Alerta: 6 imagens sem texto alternativo' in guia
    assert f'menu de navegação com 5 itens' in guia