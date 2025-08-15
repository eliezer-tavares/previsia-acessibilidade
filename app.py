  # app.py
  # -*- coding: utf-8 -*-
  """
  App web com Flask.
  Por quê? Interface acessível para input de URL e exibição de previsão com áudio via SpeechSynthesis. Isso é o "front-end" do projeto.
  Como? Rotas (@app.route) processam requests, preveem com modelo, geram guia, passam variáveis ao template Jinja. Agora com opções de análise, áudio manual e Guia Preditivo.
  Conceitos básicos: Flask é um micro-framework; rotas mapeiam URLs para funções; try/except trata erros de usuário (ex: URL inválida).
  """

  # Importações.
  from flask import Flask, render_template, request  # Flask: app web; render_template: carrega HTML com variáveis; request: dados do form.
  import joblib  # Carrega modelo.
  import pandas as pd  # Para DataFrame na previsão.
  from collector import extrair_features, gerar_label_e_features_dinamicas, analisar_url_rapida, HEADERS  # Reusa funções modulares.
  import requests  # Baixa URL.
  from bs4 import BeautifulSoup  # Parseia.
  import os  # Pastas.
  from concurrent.futures import ThreadPoolExecutor  # Para análise completa em background (não bloqueia app).

  app = Flask(__name__)  # Cria app (name: nome do módulo para templates).

  # Carrega modelo e features. Por quê? Global para reuse em rotas.
  try:
      modelo = joblib.load('models/modelo_acessibilidade.pkl')
      feature_names = joblib.load('models/feature_names.pkl')
  except FileNotFoundError:
      modelo, feature_names = None, []
      print("Erro: Modelo não encontrado.")

  def gerar_guia_preditivo(features, score, url):
      """
      Gera Guia de Navegação Preditivo em linguagem natural.
      Por quê? Descreve estrutura e atritos como 'guia de viagem', mais útil que score sozinho para usuários cegos decidirem navegar.
      Como? Usa templates dinâmicos (strings concatenadas) e condicionais (if) baseados em features/layout; prioriza impactos altos com thresholds (ex: >5 = alerta).
      Conceitos básicos: f-strings formatam texto; .split('/')[-1] pega último segmento da URL para nome amigável.
      """
      guia = f"Análise da página {url.split('/')[-1] or 'principal'} de {url}. Pontuação prevista: {score}. Guia rápido e alertas: "
      
      layout = features.get('layout', {})  # Pega sub-dict de layout (get default {} evita KeyError).
      
      # Descreve estrutura sequencial (header -> nav -> main -> form -> footer). Por quê? Mimica navegação linear de leitores de tela.
      if layout.get('header_presente'):
          guia += "A página começa com um cabeçalho, "
      if layout.get('nav_itens', 0) > 0:  # Get com default 0.
          guia += f"seguido por um menu de navegação com {layout['nav_itens']} itens. "
          if features['pct_links_genericos'] > 20:  # Threshold: >20% genéricos = alerta.
              guia += "Cuidado: muitos links genéricos no menu podem confundir a navegação. "
      if layout.get('carousel_imagens', 0) > 0:
          guia += f"Em seguida, há uma galeria ou carrossel com {layout['carousel_imagens']} imagens. "
          if layout.get('carousel_sem_alt', 0) > 0:
              guia += f"Alerta: {layout['carousel_sem_alt']} imagens sem descrição; seu leitor de tela pode ignorá-las. "
      if layout.get('main_presente'):
          guia += "A área de conteúdo principal segue, "
          if features['erros_hierarquia'] > 0:
              guia += f"mas com {features['erros_hierarquia']} erros de hierarquia em títulos, o que pode bagunçar a navegação por seções. "
      if layout.get('form_campos', 0) > 0:
          guia += f"há um formulário com {layout['form_campos']} campos no meio ou final da página. "
          if features['inputs_sem_label'] > 0:
              guia += f"Alerta: {features['inputs_sem_label']} campos sem rótulos adequados; formulários podem ser difíceis. "
          else:
              guia += "Todos os campos parecem rotulados corretamente. "
      if layout.get('footer_presente'):
          guia += "A página termina com um rodapé. "
      
      # Adiciona alertas gerais baseados em thresholds sênior (ex: >5 = muitos).
      if features['imagens_sem_alt'] > 5:
          guia += "Cuidado geral: Muitas imagens sem descrições alternativas em toda a página. "
      if features['videos_sem_captions'] > 0:
          guia += f"Alerta: {features['videos_sem_captions']} vídeos sem legendas; áudio pode ser inacessível. "
      if features['falhas_contraste'] > 0:
          guia += "Problemas de contraste detectados, o que afeta legibilidade para baixa visão. "
      if features['aria_presente'] == 0:
          guia += "Falta de ARIA em elementos dinâmicos; interações podem não ser anunciadas. "
      
      # Sugestão final baseada em score (buckets para simplicidade).
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
      Rota inicial: Mostra formulário.
      Por quê? Ponto de entrada acessível para usuário digitar URL e escolher tipo de análise.
      Como? Renderiza HTML com render_template (Jinja processa variáveis, mas aqui sem).
      """
      return render_template('index.html')

  @app.route('/predict', methods=['POST'])
  def predict():
      """
      Rota de previsão: Processa form.
      Por quê? Extrai features, prevê, prepara texto para SpeechSynthesis (ativado manualmente) e gera Guia.
      Como? Pega dados com request.form, verifica tipo, processa análise, passa dict ao template.
      """
      if not modelo:  # Verifica se modelo carregou.
          return render_template('resultado.html', erro="Modelo não disponível.", url="", texto_audio="", guia="")

      url = request.form['url']  # Pega do form (string).
      if not url.startswith('http'):  # Adiciona https se faltar.
          url = f'https://{url}'
      tipo_analise = request.form.get('tipo_analise', 'rapida')  # Get com default.

      try:
          if tipo_analise == 'completa':
              # Análise completa: mais precisa, mas lenta (usa thread para não bloquear Flask).
              with ThreadPoolExecutor(max_workers=1) as executor:
                  future = executor.submit(gerar_label_e_features_dinamicas, url)
                  score, falhas_contraste = future.result()
              if score == -1:
                  raise Exception("Falha na análise completa.")  # Raise lança erro custom.
              response = requests.get(url, headers=HEADERS, timeout=10)
              response.raise_for_status()
              soup = BeautifulSoup(response.content, 'html.parser')
              features = extrair_features(soup)
              features['falhas_contraste'] = falhas_contraste
          else:
              # Análise rápida: estática.
              features = analisar_url_rapida(url)
              if not features:
                  raise Exception("Falha na análise rápida.")

          # Previsão: DF com features numéricas (exclui layout).
          features_df = pd.DataFrame([{k: v for k, v in features.items() if k != 'layout'}], columns=feature_names).fillna(0)
          score = modelo.predict(features_df)[0]  # Predict retorna array; [0] pega primeiro.
          score = round(max(0, min(100, score)))  # Round arredonda; max/min clamp 0-100.

          # Gera Guia.
          guia = gerar_guia_preditivo(features, score, url)

          # Texto para SpeechSynthesis (inclui guia).
          texto_audio = guia

          importancias = dict(zip(feature_names, modelo.feature_importances_))  # Dict de importâncias (zip combina listas).
          top_impactos = sorted(importancias.items(), key=lambda x: x[1], reverse=True)[:3]  # Sorted: ordena por valor descendente; [:3] top 3.

          return render_template('resultado.html', url=url, previsao=score, impactos=top_impactos, texto_audio=texto_audio, guia=guia)
      except Exception as e:
          texto_audio = f"Erro: {e}"
          return render_template('resultado.html', url=url, erro=f"Erro: {e}", texto_audio=texto_audio, guia="")

  if __name__ == '__main__':
      app.run(debug=True)  # Debug=True: mostra erros no navegador; para dev.
