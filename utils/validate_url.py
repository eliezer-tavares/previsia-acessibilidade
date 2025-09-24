# Univesp - Projeto Integrador IV - Engenharia de Computação - 2º Semestre 2025
# Desenvolvido por: Eliezer Tavares de Oliveira (principal), Anderson Vianna Ferrari, Efrain Tobal Tavares, Lucas de Goes Vieira Junior
# EN: This file validates URLs dynamically to ensure they are navigable. Why? To replace hardcoded ignore lists and improve maintainability.
# PT: Este arquivo valida URLs dinamicamente para garantir que são navegáveis. Por quê? Para substituir listas fixas de ignorados e melhorar a manutenção.

import urllib.request
import urllib.parse
import re
import logging

# EN: Setup logging for URL validation. Why? To track which URLs are filtered and why, aiding debugging.
# PT: Configura o logging para validação de URLs. Por quê? Para rastrear quais URLs são filtradas e por quê, auxiliando na depuração.
logging.basicConfig(filename='erros_validate_url.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def is_navigable_url(url: str) -> bool:
    """
    Validates if a URL is navigable (returns HTML content, not CDN/redirects).
    
    :param url: URL to validate.
    :return: True if navigable, False otherwise.
    
    EN: Why? To filter out non-navigable URLs (e.g., CDNs, images) dynamically. How? Uses urllib to check status and content-type.
    PT: Por quê? Para filtrar URLs não navegáveis (ex.: CDNs, imagens) dinamicamente. Como? Usa urllib para verificar status e content-type.
    """
    try:
        # EN: Parse URL to extract scheme and domain. Why? To validate format and avoid malformed URLs.
        # PT: Analisa a URL para extrair esquema e domínio. Por quê? Para validar o formato e evitar URLs malformadas.
        parsed = urllib.parse.urlparse(url)
        if not parsed.scheme in ('http', 'https'):
            logging.warning(f"EN: Invalid scheme for {url}. PT: Esquema inválido para {url}.")
            return False
        
        # EN: Check domain patterns to exclude common non-navigable ones. Why? Avoids CDNs without hardcoded lists.
        # PT: Verifica padrões de domínio para excluir os não navegáveis comuns. Por quê? Evita CDNs sem listas fixas.
        cdn_patterns = r'\.(cdn|cloudfront|akamai|edgekey|edgesuite|msedge|akamaiedge|fastly|fbcdn|azurefd|aws)\.'
        if re.search(cdn_patterns, parsed.netloc):
            logging.info(f"EN: Excluded CDN-like domain {parsed.netloc}. PT: Excluído domínio tipo CDN {parsed.netloc}.")
            return False
        
        # EN: Make a HEAD request to check if URL returns HTML. Why? Ensures URL is a webpage, not an image or file.
        # PT: Faz uma requisição HEAD para verificar se a URL retorna HTML. Por quê? Garante que a URL é uma página, não uma imagem ou arquivo.
        req = urllib.request.Request(url, method='HEAD', headers={'User-Agent': 'PrevisIA/1.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status != 200:
                logging.warning(f"EN: Non-200 status for {url}: {response.status}. PT: Status não-200 para {url}: {response.status}.")
                return False
            content_type = response.headers.get('Content-Type', '')
            if 'text/html' not in content_type.lower():
                logging.info(f"EN: Non-HTML content for {url}: {content_type}. PT: Conteúdo não-HTML para {url}: {content_type}.")
                return False
        
        return True
    
    except Exception as e:
        logging.error(f"EN: Error validating {url}: {str(e)}. PT: Erro ao validar {url}: {str(e)}.")
        return False