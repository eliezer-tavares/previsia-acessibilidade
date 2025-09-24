# Univesp - Projeto Integrador IV - Engenharia de Computação - 2º Semestre 2025
# Desenvolvido por: Eliezer Tavares de Oliveira (principal), Anderson Vianna Ferrari, Efrain Tobal Tavares, Lucas de Goes Vieira Junior
# EN: This file prepares URLs from the Tranco dataset for accessibility analysis. Why? To obtain a curated list of navigable URLs. How? Uses the Tranco Python library and dynamic validation.
# PT: Este arquivo prepara URLs do dataset Tranco para análise de acessibilidade. Por quê? Para obter uma lista curada de URLs navegáveis. Como? Usa a biblioteca Python Tranco e validação dinâmica.

from tranco import Tranco
import pandas as pd
import os
from utils.validate_url import is_navigable_url
import logging

# EN: Setup logging to track URL preparation. Why? To debug and ensure accessibility for screen readers like NVDA.
# PT: Configura o logging para rastrear a preparação de URLs. Por quê? Para depurar e garantir acessibilidade para leitores de tela como NVDA.
logging.basicConfig(filename='erros_prepare_urls.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_urls(max_urls: int = 1000) -> None:
    """
    Loads and validates URLs from Tranco, saving to CSV.
    
    :param max_urls: Maximum number of URLs to load (default: 1000).
    
    EN: Why? To ensure only navigable URLs are saved for analysis. How? Fetches Tranco list using the Tranco Python library, validates URLs dynamically, and saves to CSV.
    PT: Por quê? Para garantir que apenas URLs navegáveis sejam salvas para análise. Como? Obtém a lista Tranco usando a biblioteca Python Tranco, valida URLs dinamicamente e salva em CSV.
    """
    try:
        # EN: Create data directory if it doesn't exist. Why? Avoids FileNotFoundError.
        # PT: Cria diretório data se não existir. Por quê? Evita FileNotFoundError.
        os.makedirs('data', exist_ok=True)
        
        # EN: Fetch top domains from Tranco. Why? Provides a ranked list for representative sampling.
        # PT: Obtém principais domínios do Tranco. Por quê? Fornece uma lista classificada para amostragem representativa.
        t = Tranco(cache=True, cache_dir='.tranco')
        latest_list = t.list()
        domains = latest_list.top(max_urls)
        
        # EN: Add https:// and validate URLs dynamically. Why? Ensures proper URL format and navigability.
        # PT: Adiciona https:// e valida URLs dinamicamente. Por quê? Garante formato correto e navegabilidade.
        urls = [f"https://{domain}" for domain in domains]
        valid_urls = [url for url in urls if is_navigable_url(url)]
        valid_urls.append("https://univesp.br")  # EN: Add Univesp URL. Why? Ensures inclusion for testing.
                                                # PT: Adiciona URL da Univesp. Por quê? Garante inclusão para testes.
        
        # EN: Save to CSV. Why? Format expected by orchestrator. How? Uses pandas without index or header.
        # PT: Salva em CSV. Por quê? Formato esperado pelo orquestrador. Como? Usa pandas sem índice ou cabeçalho.
        df = pd.DataFrame(valid_urls)
        df.to_csv('data/tranco_top_1000.csv', index=False, header=False)
        logging.info(f"EN: CSV generated with {len(valid_urls)} URLs: data/tranco_top_1000.csv. PT: CSV gerado com {len(valid_urls)} URLs: data/tranco_top_1000.csv")
        print(f"CSV gerado com sucesso: data/tranco_top_1000.csv")
    
    except Exception as e:
        logging.error(f"EN: Error generating CSV: {str(e)}. PT: Erro ao gerar CSV: {str(e)}.")
        print(f"Erro ao gerar CSV: {e}")

if __name__ == "__main__":
    load_urls()