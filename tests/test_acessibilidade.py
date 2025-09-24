# Univesp - Projeto Integrador IV - Engenharia de Computação - 2º Semestre 2025
# Desenvolvido por: Eliezer Tavares de Oliveira (principal), Anderson Vianna Ferrari, Efrain Tobal Tavares, Lucas de Goes Vieira Junior
# EN: This file tests the web app's accessibility to ensure 100% coverage. Why? To verify WCAG compliance. How? Uses Selenium and Axe to audit pages.
# PT: Este arquivo testa a acessibilidade da aplicação web para garantir 100% de cobertura. Por quê? Para verificar conformidade com WCAG. Como? Usa Selenium e Axe para auditar páginas.

import pytest
from selenium import webdriver
from axe_selenium_python import Axe
from app import app
from threading import Thread
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

@pytest.fixture
def browser():
    """
    Creates a headless browser for testing.
    
    EN: Why? To simulate page rendering for accessibility audit. How? Uses Chrome in headless mode.
    PT: Por quê? Para simular renderização de páginas para auditoria de acessibilidade. Como? Usa Chrome em modo headless.
    """
    options = webdriver.ChromeOptions()
    options.headless = True
    driver = webdriver.Chrome(options=options)
    yield driver
    driver.quit()

def run_app():
    """
    Runs Flask app in background for testing.
    
    EN: Why? To serve pages during tests. How? Runs app on a separate port.
    PT: Por quê? Para servir páginas durante testes. Como? Executa a aplicação em uma porta separada.
    """
    app.run(debug=False, use_reloader=False, port=5001)

def test_acessibilidade_home(browser):
    """
    Tests accessibility of home page.
    
    EN: Why? To ensure the form page is WCAG-compliant. How? Runs Axe audit.
    PT: Por quê? Para garantir que a página do formulário é compatível com WCAG. Como? Executa auditoria Axe.
    """
    thread = Thread(target=run_app)
    thread.start()
    browser.get('http://127.0.0.1:5001/')
    axe = Axe(browser)
    axe.inject()
    results = axe.run()
    print(results['violations'])  # Adicione esta linha para depuração
    assert len(results['violations']) == 0, results['violations']

def test_acessibilidade_resultado(browser, mocker):
    """
    Tests accessibility of results page.
    
    EN: Why? To ensure the results page is WCAG-compliant. How? Simulates POST and runs Axe audit.
    PT: Por quê? Para garantir que a página de resultados é compatível com WCAG. Como? Simula POST e executa auditoria Axe.
    """
    mocker.patch('app.modelo.predict', return_value=[80])
    mocker.patch('app.analisar_url_rapida', return_value={'imagens_sem_alt': 1, 'layout': {}})
    thread = Thread(target=run_app)
    thread.start()
    browser.get('http://127.0.0.1:5001/')
    from selenium.webdriver.support.ui import Select
    browser.find_element(By.ID, 'url_input').send_keys('example.com')
    select = Select(browser.find_element(By.ID, 'tipo_analise'))
    select.select_by_value('rapida')
    browser.find_element(By.CSS_SELECTOR, 'button[aria-label="Iniciar análise de acessibilidade"]').click()
    axe = Axe(browser)
    axe.inject()
    results = axe.run()
    print(results['violations'])  # Adicione para depuração
    assert len(results['violations']) == 0, results['violations']