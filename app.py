# Univesp - Projeto Integrador IV - Engenharia de Computação - 2º Semestre 2025
# Desenvolvido por: Eliezer Tavares de Oliveira (principal), Anderson Vianna Ferrari, Efrain Tobal Tavares, Lucas de Goes Vieira Junior
# EN: This file runs the Flask web app for accessibility analysis. Why? To provide an accessible interface for URL analysis and predictive guides. How? Uses Flask routes and SpeechSynthesis.
# PT: Este arquivo executa a aplicação web Flask para análise de acessibilidade. Por quê? Para fornecer uma interface acessível para análise de URLs e guias preditivos. Como? Usa rotas Flask e SpeechSynthesis.

from flask import Flask, render_template, request
import joblib
import pandas as pd
from collector import extrair_features, gerar_label_e_features_dinamicas, analisar_url_rapida, analisar_url_completa, HEADERS
import requests
from bs4 import BeautifulSoup
import os
from concurrent.futures import ThreadPoolExecutor
import logging
from tenacity import RetryError

# EN: Setup logging for web app. Why? To track requests and errors for debugging.
# PT: Configura o logging para a aplicação web. Por quê? Para rastrear requisições e erros para depuração.
logging.basicConfig(filename='erros_app.log', level=logging.ERROR, format='%(asctime)s - %(message)s')

app = Flask(__name__)

# EN: Load model and feature names. Why? For real-time predictions. How? Uses joblib to deserialize saved objects.
# PT: Carrega o modelo e nomes das features. Por quê? Para previsões em tempo real. Como? Usa joblib para desserializar objetos salvos.
try:
    modelo = joblib.load('models/modelo_acessibilidade.pkl')
    feature_names = joblib.load('models/feature_names.pkl')
except FileNotFoundError:
    modelo, feature_names = None, []
    logging.error("EN: Model not found. PT: Modelo não encontrado.")
    print("Erro: Modelo não encontrado.")

def gerar_guia_preditivo(features, score, url):
    """
    Generates predictive navigation guide in natural language.
    
    :param features: Dictionary of extracted features.
    :param score: Predicted accessibility score.
    :param url: Analyzed URL.
    :return: Narrative guide string.
    
    EN: Why? To describe page structure and issues for screen reader users. How? Uses templates and conditionals based on features.
    PT: Por quê? Para descrever a estrutura da página e problemas para usuários de leitores de tela. Como? Usa templates e condicionais baseados em features.
    """
    guia = f"Análise da página {url.split('/')[-1] or 'principal'} de {url}. Pontuação prevista: {score}. Guia rápido e alertas: "
    layout = features.get('layout', {})
    
    if layout.get('header_presente'):
        guia += "A página começa com um cabeçalho, "
    if layout.get('nav_itens', 0) > 0:
        guia += f"seguido por um menu de navegação com {layout['nav_itens']} itens. "
        if features.get('pct_links_genericos', 0) > 20:
            guia += "Cuidado: muitos links genéricos no menu podem confundir a navegação. "
    if layout.get('carousel_imagens', 0) > 0:
        guia += f"Em seguida, há uma galeria ou carrossel com {layout['carousel_imagens']} imagens. "
        if layout.get('carousel_sem_alt', 0) > 0:
            guia += f"Alerta: {layout['carousel_sem_alt']} imagens sem descrição; seu leitor de tela pode ignorá-las. "
    if layout.get('main_presente'):
        guia += "A área de conteúdo principal segue, "
        if features.get('erros_hierarquia', 0) > 0:
            guia += f"mas com {features['erros_hierarquia']} erros de hierarquia em títulos, o que pode bagunçar a navegação por seções. "
    if layout.get('form_campos', 0) > 0:
        guia += f"há um formulário com {layout['form_campos']} campos no meio ou final da página. "
        if features.get('inputs_sem_label', 0) > 0:
            guia += f"Alerta: {features['inputs_sem_label']} campos sem rótulos adequados; formulários podem ser difíceis. "
        else:
            guia += "Todos os campos parecem rotulados corretamente. "
    if layout.get('footer_presente'):
        guia += "A página termina com um rodapé. "
    
    if features.get('imagens_sem_alt', 0) > 0:
        guia += f"Alerta: {features['imagens_sem_alt']} imagens sem texto alternativo podem dificultar a navegação para leitores de tela. "
    if features.get('videos_sem_captions', 0) > 0:
        guia += f"Alerta: {features['videos_sem_captions']} vídeos sem legendas; áudio pode ser inacessível. "
    if features.get('falhas_contraste', 0) > 0:
        guia += f"Alerta: {features['falhas_contraste']} problemas de contraste detectados, afetando legibilidade para baixa visão. "
    if features.get('aria_presente', 0) == 0:
        guia += "Alerta: Falta de ARIA em elementos dinâmicos; interações podem não ser anunciadas. "
    
    if score > 80:
        guia += "A navegação deve ser direta e acessível."
    elif score > 50:
        guia += "A navegação é razoável, mas evite seções problemáticas."
    else:
        guia += "Sugiro usar ferramentas alternativas como busca do site para evitar frustrações."
    
    return guia

@app.route('/', methods=['GET'])
def home():
    """
    Renders the initial form page.
    
    EN: Why? To provide an accessible entry point for URL input. How? Renders HTML template with Jinja.
    PT: Por quê? Para fornecer um ponto de entrada acessível para entrada de URL. Como? Renderiza template HTML com Jinja.
    """
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    """
    Processes form submission and generates prediction.
    
    EN: Why? To analyze URLs and provide accessibility insights. How? Extracts features, predicts score, and generates guide.
    PT: Por quê? Para analisar URLs e fornecer insights de acessibilidade. Como? Extrai features, prevê escore e gera guia.
    """
    if not modelo:
        logging.error("EN: Model not available. PT: Modelo não disponível.")
        return render_template('resultado.html', error="Modelo não disponível. Por favor, verifique a configuração do servidor.", url="", features={})
    
    url = request.form['url']
    if not url.startswith('http'):
        url = f'https://{url}'
    tipo_analise = request.form.get('tipo_analise', 'rapida')
    
    try:
        if tipo_analise == 'completa':
            features = analisar_url_completa(url)
            if features is None:
                print(f"Fallback para análise rápida para {url}")  # Depuração
                features = analisar_url_rapida(url)
                if not features:
                    logging.error(f"EN: Failed to analyze URL {url} in quick mode. PT: Falha ao analisar URL {url} no modo rápido.")
                    return render_template('resultado.html', error="Falha na análise rápida.", url=url, features={})
                aviso = f"A análise completa falhou; usamos a análise rápida como fallback para {url}."
            else:
                aviso = None
        else:
            features = analisar_url_rapida(url)
            if not features:
                logging.error(f"EN: Failed to analyze URL {url} in quick mode. PT: Falha ao analisar URL {url} no modo rápido.")
                return render_template('resultado.html', error="Falha na análise rápida.", url=url, features={})
            aviso = None
        
        # Garantir que todas as feature_names estejam presentes
        features_df = pd.DataFrame([{k: features.get(k, 0) for k in feature_names}], columns=feature_names).fillna(0)
        score = modelo.predict(features_df)[0]
        score = round(max(0, min(100, score)))
        print(f"Score: {score}, Features: {features}, URL: {url}")  # Depuração
        
        guia = gerar_guia_preditivo(features, score, url)
        print(f"Guia: {guia}")  # Depuração
        
        logging.info(f"EN: Analysis completed for {url}: {score}. PT: Análise concluída para {url}: {score}.")
        return render_template('resultado.html', url=url, score=score, guia=guia, features=features, aviso=aviso)
    
    except RetryError as e:
        logging.error(f"EN: Retry error in prediction for {url}: {str(e)}. PT: Erro de retry na previsão para {url}: {str(e)}.")
        print(f"Erro de retry na previsão: {str(e)}")  # Depuração
        features = analisar_url_rapida(url)
        if not features:
            return render_template('resultado.html', error="Falha na análise rápida.", url=url, features={})
        features_df = pd.DataFrame([{k: features.get(k, 0) for k in feature_names}], columns=feature_names).fillna(0)
        score = modelo.predict(features_df)[0]
        score = round(max(0, min(100, score)))
        print(f"Score (rápida): {score}, Features: {features}, URL: {url}")  # Depuração
        guia = gerar_guia_preditivo(features, score, url)
        print(f"Guia (rápida): {guia}")  # Depuração
        logging.info(f"EN: Fallback analysis completed for {url}: {score}. PT: Análise de fallback concluída para {url}: {score}.")
        return render_template('resultado.html', url=url, score=score, guia=guia, features=features, aviso=f"A análise completa falhou; usamos a análise rápida como fallback para {url}.")
    
    except Exception as e:
        logging.error(f"EN: Error in prediction for {url}: {str(e)}. PT: Erro na previsão para {url}: {str(e)}.")
        print(f"Erro na previsão: {str(e)}")  # Depuração
        return render_template('resultado.html', error="Falha na análise rápida.", url=url, features={})

if __name__ == '__main__':
    app.run(debug=True)