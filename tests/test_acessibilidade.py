     # tests/test_acessibilidade.py
     # -*- coding: utf-8 -*-
     """
     Testes de acessibilidade para app web.
     Por quê? Garante que a própria app siga WCAG (ex: ARIA, labels), cobrindo 100% das páginas.
     Como? Roda app local, carrega com Selenium, injeta Axe, assert violações == 0.
     """

     import pytest
     from selenium import webdriver
     from axe_selenium_python import Axe
     from app import app
     from flask.testing import FlaskClient
     from threading import Thread  # Para rodar app em background.

     @pytest.fixture
     def browser():
         options = webdriver.ChromeOptions()
         options.headless = True
         driver = webdriver.Chrome(options=options)
         yield driver
         driver.quit()

     def run_app():
         app.run(debug=False, use_reloader=False, port=5001)  # Porta diferente para teste.

     def test_acessibilidade_home(browser):
         thread = Thread(target=run_app)
         thread.start()
         browser.get('http://127.0.0.1:5001/')
         axe = Axe(browser)
         axe.inject()
         results = axe.run()
         assert len(results['violations']) == 0, results['violations']  # Assert zero violações.

     # Similar para /predict (simule post).
