# Univesp - Projeto Integrador IV - Engenharia de Computação - 2º Semestre 2025
# Desenvolvido por: Eliezer Tavares de Oliveira (principal), Anderson Vianna Ferrari, Efrain Tobal Tavares, Lucas de Goes Vieira Junior
# EN: This file analyzes URLs to extract accessibility features and generate labels. Why? To quantify accessibility issues for ML and predictive guides. How? Combines static (BeautifulSoup) and dynamic (Selenium/Axe) analysis.
# PT: Este arquivo analisa URLs para extrair features de acessibilidade e gerar labels. Por quê? Para quantificar problemas de acessibilidade para ML e guias preditivos. Como? Combina análise estática (BeautifulSoup) e dinâmica (Selenium/Axe).

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from axe_selenium_python import Axe
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import logging
import json
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

# EN: Setup logging to track analysis errors. Why? Facilitates debugging with NVDA, saving errors to file.
# PT: Configura o logging para rastrear erros de análise. Por quê? Facilita depuração com NVDA, salvando erros em arquivo.
logging.basicConfig(
    filename='erros_collector.log',
    level=logging.ERROR,
    format='{"time": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}'
)

# EN: Constants for HTTP headers and accessibility checks. Why? Avoids hardcoding and improves maintainability.
# PT: Constantes para cabeçalhos HTTP e verificações de acessibilidade. Por quê? Evita hardcoding e melhora a manutenção.
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
}
TEXTOS_GENERICOS = ['clique aqui', 'saiba mais', 'leia mais', 'aqui', 'click here', 'veja mais']
LAYOUT_TAGS = {
    'header': ['header', 'div[id*="header"]', 'div[class*="header"]'],
    'nav': ['nav', 'ul[id*="menu"]', 'ul[class*="nav"]', 'div[id*="menu"]', 'div[class*="nav"]'],
    'main': ['main', 'article', 'section[id*="content"]', 'div[id*="content"]', 'div[class*="main"]'],
    'footer': ['footer', 'div[id*="footer"]', 'div[class*="footer"]'],
    'carousel': ['div[class*="carousel"]', 'div[class*="slider"]'],
    'form': ['form']
}

def extrair_features(soup: BeautifulSoup) -> dict:
    """
    Extracts accessibility features from HTML, including layout for predictive guide.
    
    :param soup: Parsed HTML (BeautifulSoup object).
    :return: Dictionary with accessibility features.
    
    EN: Why? To quantify issues like missing alt texts and describe page structure. How? Uses soup.find_all/select_one to count/check elements.
    PT: Por quê? Para quantificar problemas como textos alternativos ausentes e descrever a estrutura da página. Como? Usa soup.find_all/select_one para contar/verificar elementos.
    """
    features = {
        'imagens_sem_alt': 0,
        'pct_links_genericos': 0,
        'lang_presente': 0,
        'erros_hierarquia': 0,
        'inputs_sem_label': 0,
        'aria_presente': 0,
        'videos_sem_captions': 0,
        'falhas_contraste': 0,
        'layout': {}
    }
    
    imagens = soup.find_all('img')
    features['imagens_sem_alt'] = sum(1 for img in imagens if not img.get('alt', '').strip())
    
    links = soup.find_all('a')
    genericos = sum(1 for a in links if a.text.strip().lower() in TEXTOS_GENERICOS)
    features['pct_links_genericos'] = (genericos / len(links)) * 100 if links else 0
    
    features['lang_presente'] = 1 if soup.html and soup.html.get('lang') else 0
    
    headers = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    niveis = [int(h.name[1]) for h in headers]
    features['erros_hierarquia'] = sum(1 for i in range(1, len(niveis)) if niveis[i] > niveis[i-1] + 1)
    
    inputs = soup.find_all(['input', 'select', 'textarea'])
    sem_label = sum(1 for inp in inputs if inp.get('type') not in ['hidden', 'submit'] and (not inp.get('id') or not soup.find('label', {'for': inp.get('id')})))
    features['inputs_sem_label'] = sem_label
    
    features['aria_presente'] = 1 if soup.find(attrs={'role': True}) else 0
    
    videos = soup.find_all('video')
    features['videos_sem_captions'] = sum(1 for v in videos if not v.find('track', {'kind': 'captions'}))
    
    layout = {}
    for key, selectors in LAYOUT_TAGS.items():
        elements = [soup.select_one(selector) for selector in selectors if soup.select_one(selector)]
        if elements:
            element = elements[0]
            if key == 'nav':
                layout['nav_itens'] = len(element.find_all('a'))
            elif key == 'form':
                layout['form_campos'] = len(element.find_all(['input', 'select', 'textarea']))
            elif key == 'carousel':
                layout['carousel_imagens'] = len(element.find_all('img'))
                layout['carousel_sem_alt'] = len([img for img in element.find_all('img') if not img.get('alt', '').strip()])
            else:
                layout[f'{key}_presente'] = 1
    features['layout'] = layout
    return features

def gerar_label_e_features_dinamicas(url: str) -> tuple[int, int]:
    """
    Generates accessibility score and contrast failures using Axe audit.
    
    :param url: URL to analyze.
    :return: Tuple of (score, contrast_failures).
    
    EN: Why? To quantify accessibility in runtime with precision. How? Uses headless Chrome and Axe to audit rendered pages.
    PT: Por quê? Para quantificar acessibilidade em tempo de execução com precisão. Como? Usa Chrome headless e Axe para auditar páginas renderizadas.
    """
    driver = None
    try:
        options = Options()
        options.headless = True
        options.add_argument('--log-level=3')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-application-cache')
        options.add_argument('--window-size=1280,720')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--disable-web-security')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36')
        options.add_argument('--enable-webgl')
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(120)
        print(f"Iniciando análise dinâmica para {url}")
        driver.get(url)
        logging.info(f'{{"url": "{url}", "step": "Navigated to URL"}}')
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        logging.info(f'{{"url": "{url}", "step": "Body loaded"}}')
        axe = Axe(driver)
        axe.inject()
        logging.info(f'{{"url": "{url}", "step": "Axe injected"}}')
        results = axe.run()
        logging.info(f'{{"url": "{url}", "step": "Axe run completed", "results": "{json.dumps(results)}"}}')
        
        violations = results.get('violations', [])
        score = max(0, 100 - (len(violations) * 5))
        contrast_failures = sum(len(v['nodes']) for v in violations if v['id'] == 'color-contrast')
        
        print(f"Análise dinâmica - URL: {url}, Score: {score}, Violações: {len(violations)}, Falhas de contraste: {contrast_failures}")
        return score, contrast_failures
    except TimeoutException as e:
        logging.error(f'{{"url": "{url}", "error": "Timeout in Axe", "details": "{str(e)}"}}')
        print(f"Timeout no Axe para {url}: {str(e)}")
        return -1, -1
    except Exception as e:
        logging.error(f'{{"url": "{url}", "error": "Error in Axe", "details": "{str(e)}"}}')
        print(f"Erro no Axe para {url}: {str(e)}")
        return -1, -1
    finally:
        if driver:
            try:
                driver.quit()
                logging.info(f'{{"url": "{url}", "step": "Driver closed"}}')
            except Exception as e:
                logging.error(f'{{"url": "{url}", "error": "Error closing driver", "details": "{str(e)}"}}')
                print(f"Erro ao fechar driver para {url}: {str(e)}")

def analisar_url_completa(url: str) -> dict | None:
    """
    Performs complete URL analysis.
    
    :param url: URL to analyze.
    :return: Dictionary of features or None if failed.
    
    EN: Why? Combines static and dynamic analysis for robust dataset. How? Downloads HTML, extracts features, and runs Axe audit.
    PT: Por quê? Combina análise estática e dinâmica para dataset robusto. Como? Baixa HTML, extrai features e executa auditoria Axe.
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        features = extrair_features(soup)
        
        score, falhas_contraste = gerar_label_e_features_dinamicas(url)
        if score == -1:
            return None
        
        features['falhas_contraste'] = falhas_contraste
        features['label_score_acessibilidade'] = score
        print(f"Análise completa - Features: {features}")
        return features
    except Exception as e:
        logging.error(f'{{"url": "{url}", "error": "Error analyzing", "details": "{str(e)}"}}')
        print(f"Erro ao analisar {url}: {str(e)}")
        return None

def analisar_url_rapida(url: str) -> dict | None:
    """
    Performs quick static analysis for prediction.
    
    :param url: URL to analyze.
    :return: Dictionary of features or None if failed.
    
    EN: Why? Enables fast responses in the web app. How? Uses only static HTML analysis.
    PT: Por quê? Permite respostas rápidas na aplicação web. Como? Usa apenas análise estática de HTML.
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        features = extrair_features(soup)
        features['falhas_contraste'] = 0
        print(f"Análise rápida - Features: {features}")
        return features
    except Exception as e:
        logging.error(f'{{"url": "{url}", "error": "Error in quick analysis", "details": "{str(e)}"}}')
        print(f"Erro na análise rápida {url}: {str(e)}")
        return None