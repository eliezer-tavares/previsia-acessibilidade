  # collector.py
  # -*- coding: utf-8 -*-
  """
  Script para analisar URL: Extrai features de acessibilidade e gera label com Axe.
  Por quê? Automatiza verificação de problemas reais, como hierarquia quebrada que bagunça navegação por voz. Isso é crucial para cegos, pois identifica dores antecipadamente.
  Como? Divide em funções modulares: estática (HTML simples via requests e BeautifulSoup) e dinâmica (com Selenium para JS), com layout semântico no Guia Preditivo, usando dicionário de tags/heurísticas para detecção robusta.
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
      """
      Extrai features do HTML, incluindo layout para Guia Preditivo.
      Por quê? Features quantificam problemas (ex: imagens sem alt perdem contexto para cegos) e agora descrevem estrutura (ex: itens em menu), permitindo guias narrativos.
      Como? Usa soup.find_all (busca múltiplas tags) e soup.select_one (busca CSS selector) para contar/verificar; sum com generator para eficiência.
      Conceitos básicos: Soup é o HTML parseado; find_all retorna lista de tags; get pega atributo ou default.
      """
      features = {}  # Dicionário vazio para armazenar resultados (chave: nome, valor: número ou dict para layout). Por quê? Flexível para expansão.

      # Feature 1: Imagens sem alt.
      # Por quê? Alt descreve imagem; sem ele, leitores de tela dizem "imagem" sem sentido, frustrando cegos.
      # Como? find_all busca todas <img>, sum conta as sem 'alt' (get retorna '' se ausente, strip remove espaços vazios).
      imagens = soup.find_all('img')  # Lista de todas tags <img>.
      features['imagens_sem_alt'] = sum(1 for img in imagens if not img.get('alt', '').strip())  # Generator: eficiente, não cria lista extra.

      # Feature 2: % de links genéricos.
      # Por quê? Links vagos confundem listas de links em leitores de tela, como "clique aqui" sem contexto.
      # Como? Conta links com texto em TEXTOS_GENERICOS (lower para case-insensitive), divide pelo total (if evita divisão por 0).
      links = soup.find_all('a')  # Lista de <a> (links).
      genericos = sum(1 for a in links if a.text.strip().lower() in TEXTOS_GENERICOS)  # Conta matches.
      features['pct_links_genericos'] = (genericos / len(links)) * 100 if links else 0  # Porcentagem.

      # Feature 3: Lang presente.
      # Por quê? Lang define idioma para pronúncia correta (ex: acentos em pt-BR).
      # Como? Verifica atributo em <html> (soup.html é a tag raiz; get retorna None se ausente).
      features['lang_presente'] = 1 if soup.html and soup.html.get('lang') else 0  # 1 sim, 0 não.

      # Feature 4: Erros de hierarquia headers.
      # Por quê? Ordem errada (ex: h1 pulando para h3) quebra outline (navegação por seções em leitores de tela).
      # Como? Extrai níveis (h1=1, int(h.name[1])), conta pulos >1 com loop for e range.
      headers = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])  # Lista de headers.
      niveis = [int(h.name[1]) for h in headers]  # List comprehension: cria lista de níveis.
      features['erros_hierarquia'] = sum(1 for i in range(1, len(niveis)) if niveis[i] > niveis[i-1] + 1)  # Conta pulos.

      # Feature 5: Inputs sem label.
      # Por quê? Labels explicam campos; sem eles, formulários são labirintos para voz.
      # Como? Verifica 'id' e <label for=...> (ignora hidden/submit com not in).
      inputs = soup.find_all(['input', 'select', 'textarea'])  # Campos de entrada.
      sem_label = sum(1 for inp in inputs if inp.get('type') not in ['hidden', 'submit'] and (not inp.get('id') or not soup.find('label', {'for': inp.get('id')})) )  # Condição composta.
      features['inputs_sem_label'] = sem_label

      # Feature 6: ARIA presente.
      # Por quê? ARIA adiciona descrições a elementos dinâmicos (ex: role="button" para anúncio).
      # Como? Busca qualquer tag com 'role' (attrs={'role': True} é filtro booleano).
      features['aria_presente'] = 1 if soup.find(attrs={'role': True}) else 0

      # Feature 7: Vídeos sem captions.
      # Por quê? Captions textuais permitem acesso a áudio em vídeos para surdos ou leitores de tela.
      # Como? Conta <video> sem <track kind='captions'> (find busca filho).
      videos = soup.find_all('video')
      features['videos_sem_captions'] = sum(1 for v in videos if not v.find('track', {'kind': 'captions'}))

      # Features de Layout para Guia Preditivo (dicionário aninhado).
      # Por quê? Detecta estrutura (ex: menu com N itens) para narrativas descritivas, como "guia de viagem".
      # Como? Para cada tipo em LAYOUT_TAGS, busca selectors com select_one (primeiro match), conta elementos chave.
      layout = {}  # Sub-dicionário para layout.
      for key, selectors in LAYOUT_TAGS.items():  # Loop sobre dicionário (items: chave-valor).
          elements = [soup.select_one(selector) for selector in selectors if soup.select_one(selector)]  # List comp: filtra matches não nulos.
          if elements:  # If verifica se achou algo.
              element = elements[0]  # Pega o primeiro match válido.
              if key == 'nav':
                  layout['nav_itens'] = len(element.find_all('a'))  # Conta links no menu.
              elif key == 'form':
                  layout['form_campos'] = len(element.find_all(['input', 'select', 'textarea']))  # Conta campos.
                  layout['form_rotulados'] = features['inputs_sem_label'] == 0  # Booleano se todos rotulados.
              elif key == 'carousel':
                  layout['carousel_imagens'] = len(element.find_all('img'))  # Conta imagens em galeria.
                  layout['carousel_sem_alt'] = sum(1 for img in element.find_all('img') if not img.get('alt', '').strip())
              else:
                  layout[key + '_presente'] = 1  # Presença simples para header, main, footer.
      features['layout'] = layout  # Adiciona sub-dicionário ao features principal.

      return features

  def gerar_label_e_features_dinamicas(url):
      """
      Gera label com Axe.
      Por quê? Axe verifica violações após renderização (mais preciso que HTML estático, capturando JS).
      Como? Configura navegador headless (sem GUI), injeta Axe, roda auditoria, calcula score ponderado (100 - violações*5, clamped 0-100).
      Conceitos básicos: Try/except captura exceções (erros) para retorno graceful (-1).
      """
      try:  # Bloco try: tenta executar, except pega erros.
          options = Options()  # Instancia opções do Chrome.
          options.headless = True  # Headless: sem janela visual, mais rápido e eficiente.
          driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)  # Cria driver, instala se necessário.
          driver.get(url)  # Carrega URL no navegador simulado.
          time.sleep(3)  # Pausa para JS carregar (3 segundos; ajustável).

          axe = Axe(driver)  # Instancia Axe com driver.
          axe.inject()  # Injeta scripts de Axe na página carregada.
          results = axe.run()  # Executa auditoria, retorna dict com violações.
          driver.quit()  # Fecha navegador para liberar recursos (memória/CPU).

          violacoes = len(results.get('violations', []))  # Conta violações (get default [] evita KeyError).
          score = max(0, 100 - (violacoes * 5))  # Score: 100 menos peso por violação (máx 100, min 0 via max).

          # Feature extra: Falhas de contraste (id específico do Axe).
          # Por quê? Contraste afeta legibilidade; sum soma nodes em violações filtradas.
          falhas_contraste = sum(len(v['nodes']) for v in results.get('violations', []) if v['id'] == 'color-contrast')  # Generator sum.

          return score, falhas_contraste  # Retorna tupla (score, falhas).
      except Exception as e:  # Captura qualquer erro, imprime para debug.
          print(f"Erro no Axe para {url}: {e}")
          return -1, -1  # Retorna -1 para indicar falha, permitindo descarte.

  def analisar_url_completa(url):
      """
      Análise completa de URL.
      Por quê? Combina extração rápida (estática) e auditoria precisa (dinâmica) para dataset robusto.
      Como? Baixa HTML, extrai features, chama dinâmica; try/except trata erros como timeout ou offline.
      Conceitos básicos: Response.raise_for_status levanta erro se não 200 OK; None para falha.
      """
      try:
          response = requests.get(url, headers=HEADERS, timeout=10)  # Baixa com timeout (evita espera eterna).
          response.raise_for_status()  # Erro se não sucesso (ex: 404).
          soup = BeautifulSoup(response.content, 'html.parser')  # Parseia bytes do HTML em soup.
          features = extrair_features(soup)  # Chama função modular.

          score, falhas_contraste = gerar_label_e_features_dinamicas(url)  # Chama dinâmica.
          if score == -1:
              return None  # Descarta se falhou.

          features['falhas_contraste'] = falhas_contraste  # Adiciona feature dinâmica.
          features['label_score_acessibilidade'] = score  # Adiciona label.
          return features
      except Exception as e:
          print(f"Erro ao analisar {url}: {e}")
          return None

  def analisar_url_rapida(url):
      """
      Análise rápida (estática) para predição.
      Por quê? Permite respostas instantâneas na app, sem Selenium (lento).
      Como? Similar à completa, mas só estática e falhas_contraste=0 (aproximação).
      """
      try:
          response = requests.get(url, headers=HEADERS, timeout=10)
          response.raise_for_status()
          soup = BeautifulSoup(response.content, 'html.parser')
          features = extrair_features(soup)
          features['falhas_contraste'] = 0  # Simplificação para rapidez.
          return features
      except Exception as e:
          print(f"Erro na análise rápida {url}: {e}")
          return None

  # Teste manual: Rode para verificar uma URL. Por quê? Verificação rápida durante desenvolvimento.
  if __name__ == '__main__':  # If verifica se script roda diretamente (não importado).
      resultado = analisar_url_completa('https://www.univesp.br')
      if resultado:
          print(resultado)  # Imprime dicionário (acessível no terminal).
