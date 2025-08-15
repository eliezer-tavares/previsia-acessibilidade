     # tests/test_collector.py
     # -*- coding: utf-8 -*-
     """
     Testes unitários para collector.py.
     Por quê? Verificam funções isoladas com dados mock (falsos), garantindo lógica correta sem dependências externas.
     Como? Usa pytest (framework), mock (de pytest-mock) para simular soup/responses. Rode com 'pytest tests/test_collector.py'.
     Conceitos básicos: @pytest.fixture cria setup reutilizável; assert verifica esperado vs real.
     """

     import pytest  # Framework de testes.
     from bs4 import BeautifulSoup  # Para mock soup.
     from collector import extrair_features, gerar_label_e_features_dinamicas, analisar_url_completa, analisar_url_rapida  # Funções a testar.

     @pytest.fixture
     def mock_soup():  # Fixture: cria soup mock para testes.
         """Cria HTML mock simples para testes."""
         html = """
         <html lang="pt">
             <header>Header</header>
             <nav><a href="#">Link1</a><a href="#">clique aqui</a></nav>
             <main>
                 <img alt="desc" />
                 <img />
                 <h1>Título</h1><h3>Sub</h3>
                 <input id="field" type="text" />
                 <label for="field">Label</label>
                 <video><track kind="captions" /></video>
                 <div role="button">ARIA</div>
             </main>
             <footer>Footer</footer>
             <form><input type="text" /></form>
             <div class="carousel"><img /><img /></div>
         </html>
         """
         return BeautifulSoup(html, 'html.parser')  # Retorna soup parseado.

     def test_extrair_features(mock_soup):
         """Testa extração de features."""
         features = extrair_features(mock_soup)
         assert features['imagens_sem_alt'] == 3  # 3 imgs sem alt (2 em carousel + 1 geral).
         assert features['pct_links_genericos'] == 50.0  # 1 de 2 links genérico.
         assert features['lang_presente'] == 1
         assert features['erros_hierarquia'] == 1  # h1 para h3 pula.
         assert features['inputs_sem_label'] == 1  # Um input sem label.
         assert features['aria_presente'] == 1
         assert features['videos_sem_captions'] == 0
         layout = features['layout']
         assert layout['header_presente'] == 1
         assert layout['nav_itens'] == 2
         assert layout['form_campos'] == 1
         assert layout['carousel_imagens'] == 2

     def test_gerar_label_e_features_dinamicas(mocker):  # Mocker de pytest-mock.
         """Testa dinâmica com mock (não roda Selenium real)."""
         mocker.patch('collector.webdriver.Chrome')  # Mock driver.
         mocker.patch('collector.Axe')  # Mock Axe.
         score, falhas = gerar_label_e_features_dinamicas('https://example.com')
         assert score == -1  # Espera falha em mock.

     def test_analisar_url_completa(mocker):
         """Testa análise completa com mocks."""
         mocker.patch('requests.get', side_effect=Exception("Mock error"))  # Simula erro.
         assert analisar_url_completa('https://example.com') is None

     def test_analisar_url_rapida(mocker):
         """Testa análise rápida."""
         mock_response = mocker.Mock()
         mock_response.content = b'<html></html>'
         mock_response.raise_for_status = mocker.Mock()
         mocker.patch('requests.get', return_value=mock_response)
         features = analisar_url_rapida('https://example.com')
         assert features['falhas_contraste'] == 0
