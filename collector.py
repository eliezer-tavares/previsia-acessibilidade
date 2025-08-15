# collector.py
# -*- coding: utf-8 -*-  
"""
Script para analisar URL: Extrai features de acessibilidade e gera label com Axe.
Por quê? Automatiza verificação de problemas reais, como hierarquia quebrada que bagunça navegação por voz. Isso é crucial para cegos, pois identifica dores antecipadamente.
Como? Divide em funções modulares: estática (HTML simples via requests e BeautifulSoup) e dinâmica (com Selenium para JS). Agora expandido para layout semântico no Guia Preditivo, usando dicionário de tags/heurísticas para detecção robusta.
Conceitos básicos: Funções são blocos reutilizáveis de código; try/except trata erros para evitar crashes; dicionários armazenam pares chave-valor.
"""

# Importações: Cada uma é explicada. Por quê? Importar só o necessário evita conflitos; from importa partes específicas.
import requests  # Para baixar HTML (requisição HTTP como navegador). Por quê? Rápido para análise estática.
from bs4 import BeautifulSoup  # Para parsear HTML (transforma texto em estrutura navegável como árvore). Por quê? Facilita busca por tags.
from selenium import webdriver  # Para simular navegador completo (carrega JavaScript). Por quê? Páginas dinâmicas precisam de renderização.
from selenium.webdriver.chrome.options import Options  # Configura modo headless (invisível, eficiente). Por quê? Economia de recursos.
from webdriver_manager.chrome import ChromeDriverManager  # Instala driver do Chrome automaticamente (sem download manual). Por quê? Facilita setup.
from axe_selenium_python import Axe  # Ferramenta para auditoria (conta violações WCAG). Por quê? Padrão ouro para acessibilidade.
import time  # Para pausas (evita sobrecarga em sites). Por quê? Boas práticas contra bloqueios.

# Constantes: Valores usados repetidamente. Por quê? Evita hardcoding (valores fixos no código), facilita manutenção.
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124'}  # Simula navegador para evitar bloqueios.
TEXTOS_GENERICOS = ['clique aqui', 'saiba mais', 'leia mais', 'aqui', 'click here', 'veja mais']  # Exemplos de links ruins. Por quê? Comuns em sites ruins.
LAYOUT_TAGS = {
    'header': ['header', 'div[id*="header"]', 'div[class*="header"]'],  # Tags e heurísticas para header. Por quê? Cobertura semântica e legacy.
    'nav': ['nav', 'ul[id*="menu"]', 'ul[class*="nav"]', 'div[id*="menu"]', 'div[class*="nav"]'],  # Para menus/navegação.
    'main': ['main', 'article', 'section[id*="content"]', 'div[id*="content"]', 'div[class*="main"]'],  # Conteúdo principal.
    'footer': ['footer', 'div[id*="footer"]', 'div[class*="footer"]'],  # Rodapé.
    'carousel': ['div[class*="carousel"]', 'div[class*="slider"]'],  # Carrosseis/galerias.
    'form': ['form']  # Formulários.
}  # Dicionário para detecção de layout (semântico e heurístico). Por quê? Flexível para sites variados.

def extrair_features(soup):
    ...
# (O restante do código segue conforme fornecido na solicitação do usuário.)