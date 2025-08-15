    # orquestrador.py
    # -*- coding: utf-8 -*-
    """
    Orquestra coleta para dataset.
    Por quê? Automatiza loop sobre URLs para gerar dados em escala, criando CSV para ML. Isso é o "motor" do dataset.
    Como? Lê CSV de URLs, chama análise em paralelo (para velocidade), salva com pandas (trata erros, pausas). Serializa layout como JSON para CSV flat.
    Conceitos básicos: Paralelismo com threads (concorrent) roda tarefas simultâneas; with gerencia recursos automaticamente.
    """
  
    # Importações.
    import pandas as pd  # Para ler/salvar CSV (DataFrame: tabela em memória). Por quê? Eficiente para dados tabulares.
    from collector import analisar_url_completa  # Função de análise (import modular).
    from concurrent.futures import ThreadPoolExecutor, as_completed  # Para processamento paralelo (threads: executa simultâneo). Por quê? Reduz tempo de horas para minutos.
    import time  # Para sleep (pausas). Por quê? Evita bans por requests rápidas.
    import os  # Para makedirs (criar pastas).
    import json  # Para dumps (serializar dict como string JSON). Por quê? CSV não suporta dicts aninhados.
  
    # Configurações: Arquivos fixos. Por quê? Centraliza paths para fácil mudança.
    ARQUIVO_URLS = 'data/tranco_top_1000.csv'  # Entrada: lista de URLs.
    ARQUIVO_DATASET = 'data/dataset_acessibilidade.csv'  # Saída: features + labels.
    MAX_WORKERS = 10  # Número máximo de threads paralelas (ajuste conforme CPU; evita sobrecarga).
  
    def gera_dataset(batch_size=200):
        """
        Gera dataset.
        Por quê? Batch_size permite testes parciais (ex: 200 para rapidez), depois escala para 1000.
        Como? Lê URLs como lista, agenda threads com submit, processa completos com as_completed, append resultados, converte para DF, salva.
        """
        print("Iniciando coleta paralela...")  # Mensagem de progresso.
        try:
            urls = pd.read_csv(ARQUIVO_URLS, header=None)[0].tolist()  # Lê como lista (tolist converte série).
        except FileNotFoundError as e:  # Except específico para arquivo ausente.
            print(f"Erro: {e}. Rode prepare_urls.py.")
            return  # Sai da função.
  
        dados = []  # Lista vazia para armazenar dicionários de resultados.
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:  # With: abre e fecha executor automaticamente.
            futures = {executor.submit(analisar_url_completa, url): url for url in urls[:batch_size]}  # Dict: future -> url; submit agenda tarefa.
            for i, future in enumerate(as_completed(futures)):  # Enumera completos (as_completed yields conforme terminam).
                url = futures[future]  # Pega url da future.
                print(f"Processando {i+1}/{batch_size}: {url}")  # Progresso acessível no terminal.
                try:
                    resultado = future.result()  # Pega output da thread (bloqueia se não pronto).
                    if resultado:
                        # Serializa layout dict como string JSON para CSV (flat).
                        # Por quê? Pandas salva dicts como string; json.dumps converte.
                        if 'layout' in resultado:
                            resultado['layout_json'] = json.dumps(resultado['layout'])  # Dumps: dict para string.
                            del resultado['layout']  # Remove dict original para evitar erro no DataFrame (não serializável direto).
                        resultado['url'] = url  # Adiciona URL para rastreamento.
                        dados.append(resultado)  # Append: adiciona ao final da lista.
                except Exception as e:
                    print(f"Erro em thread para {url}: {e}")
                time.sleep(0.5)  # Pausa curta entre batches (evita ser bloqueado como bot).
  
        if dados:  # If verifica se coletou algo.
            os.makedirs('data', exist_ok=True)  # Cria pasta se necessário.
            df = pd.DataFrame(dados)  # Converte lista para DataFrame (tabela).
            cols = ['url', 'label_score_acessibilidade'] + [c for c in df.columns if c not in ['url', 'label_score_acessibilidade']]  # Reorganiza colunas (list comprehension filtra).
            df = df[cols]
            df.to_csv(ARQUIVO_DATASET, index=False)  # Salva CSV (index=False: sem coluna extra).
            print(f"Dataset salvo: {len(df)} linhas.")
        else:
            print("Nenhum dado coletado.")
  
    if __name__ == '__main__':
        gera_dataset()  # Chama função (altere batch_size para 1000 quando pronto)
