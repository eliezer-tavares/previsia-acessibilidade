# PrevisIA: Previsor e Guia de Acessibilidade Web 👁️‍🗨️🤖

## Univesp - Projeto Integrador IV - Engenharia de Computação - 2º Semestre 2025
**Desenvolvido por**: Eliezer Tavares de Oliveira (principal), Anderson Viana Ferrari, Efrain Tobal Tavares, Lucas de Goes Vieira Junior

---

## PT: Sobre o Projeto
O PrevisIA é uma ferramenta inovadora desenvolvida para a disciplina Projeto Integrador IV da graduação em Engenharia de Computação da Univesp. Nosso objetivo é democratizar a avaliação de acessibilidade web, fornecendo uma solução que prevê escores de acessibilidade e oferece um Guia de Navegação Preditivo em linguagem natural, otimizado para usuários com deficiência visual.

**Por quê?** Para tornar a web mais inclusiva, especialmente para usuários de leitores de tela como NVDA.  
**Como?** Combina análise estática (BeautifulSoup) e dinâmica (Playwright/Axe) para extrair características de acessibilidade, treina uma Rede Neural com PyTorch para prever escores e gera guias narrativos acessíveis via SpeechSynthesis, com suporte a internacionalização (i18n) via Babel.

**Demo ao Vivo**: A aplicação está hospedada temporariamente no Render em [https://previsia.onrender.com](https://previsia.onrender.com). Em breve, estará disponível em [http://www.previsia.eliezertavaresdeoliveira.com](http://www.previsia.eliezertavaresdeoliveira.com). Nota: Devido a limitações computacionais no Render, a análise completa (dinâmica) falha automaticamente e recai na análise estática (rápida) para garantir usabilidade. Enquanto o projeto estiver hospedado no plano gratuito do Render, para acessar é preciso ter paciência, pois pode demorar até 180 segundos para a página inicial do PrevisIA abrir.

## EN: About the Project
PrevisIA is an innovative tool developed for the Projeto Integrador IV course at Univesp's Computer Engineering program. Our goal is to democratize web accessibility evaluation by providing a solution that predicts accessibility scores and offers a Predictive Navigation Guide in natural language, optimized for visually impaired users.

**Why?** To make the web more inclusive, especially for users of screen readers like NVDA.  
**How?** Combines static (BeautifulSoup) and dynamic (Playwright/Axe) analysis to extract accessibility features, trains a PyTorch Neural Network to predict scores, and generates accessible narrative guides via SpeechSynthesis, with internationalization (i18n) support via Babel.

**Live Demo**: The application is temporarily hosted on Render at [https://previsia.onrender.com](https://previsia.onrender.com). Soon, it will also be available at [http://www.previsia.eliezertavaresdeoliveira.com](http://www.previsia.eliezertavaresdeoliveira.com). Note: Due to computational limitations on Render, complete (dynamic) analysis automatically fails and falls back to static (quick) analysis to ensure usability. While the project is hosted on Render's free plan, please be patient when accessing it, as it may take up to 180 seconds for the PrevisIA home page to load.

---

## PT: Funcionalidades da Versão Final
- **Previsão de Acessibilidade**: Gera escores de acessibilidade (0-100) usando análise estática e dinâmica, com fallback automático para estática em caso de falha (ex: limitações de hospedagem).
- **Análise Estática e Dinâmica**: Extração de features como imagens sem `alt`, links genéricos, hierarquia de cabeçalhos, presença de ARIA, falhas de contraste e layout usando BeautifulSoup e Axe via Playwright.
- **Modelo de IA**: Rede Neural (AccessibilityNet) com PyTorch, incluindo camadas BatchNorm e Dropout para robustez, treinada com transformações (log, clipping) e avaliada com R²/MSE.
- **Interface Web Acessível**: Aplicativo Flask (`app.py`) com rotas unificadas, suporte a i18n (PT/EN via Babel), templates WCAG 2.1 AA validados com WAVE/NVDA, e seletor de idioma dinâmico.
- **Guia Narrativo**: Geração de guias preditivos em linguagem natural, com alertas personalizados e feedback em áudio via SpeechSynthesis.
- **Geração de Dataset**: Orquestrador paralelo com ThreadPoolExecutor, checkpoints e suporte a Tranco para ~5k URLs válidas.
- **Logs e Robustez**: Logging em JSON para depuração acessível, retry com Tenacity e tratamento de exceções.

## EN: Final Version Features
- **Accessibility Prediction**: Generates accessibility scores (0-100) using static and dynamic analysis, with automatic fallback to static on failure (e.g., hosting limits).
- **Static and Dynamic Analysis**: Extracts features like missing `alt` texts, generic links, heading hierarchy, ARIA presence, contrast failures, and layout using BeautifulSoup and Axe via Playwright.
- **AI Model**: PyTorch Neural Network (AccessibilityNet) with BatchNorm and Dropout layers for robustness, trained with transformations (log, clipping) and evaluated with R²/MSE.
- **Accessible Web Interface**: Flask app (`app.py`) with unified routes, i18n support (PT/EN via Babel), WCAG 2.1 AA templates validated with WAVE/NVDA, and dynamic language selector.
- **Narrative Guide**: Generates predictive guides in natural language with personalized alerts and on-demand audio feedback via SpeechSynthesis.
- **Dataset Generation**: Parallel orchestrator with ThreadPoolExecutor, checkpoints, and Tranco support for ~5k valid URLs.
- **Logs and Robustness**: JSON logging for accessible debugging, Tenacity retries, and exception handling.

---

## PT: Estrutura do Projeto
```
previsia-acessibilidade/
├── data/                          # Dados gerados (CSV de URLs e dataset) - incluídos no repositório
├── models/                        # Modelos treinados (.pt), scaler e feature_names.pkl - incluídos no repositório
├── templates/                     # Templates HTML para a interface Flask
│   ├── index.html                # Formulário de entrada de URL com seletor de idioma
│   └── resultado.html            # Página de resultados com guia e áudio
├── translations/                  # Arquivos de tradução para Babel (PT/EN)
├── app.py                        # Aplicação web Flask com i18n e PyTorch
├── babel.cfg                     # Configuração do Babel para extração de strings
├── collector.py                  # Análise de URLs (estática/dinâmica com Playwright/Axe)
├── orquestrador.py               # Orquestração paralela para geração de dataset
├── prepare_urls.py               # Preparação de URLs com Tranco e validação
├── trainer.py                    # Treinamento da Rede Neural com PyTorch
├── requirements.txt              # Dependências pinned para reproducibilidade
├── .gitignore                    # Exclusão de logs e arquivos temporários
└── README.md                     # Documentação bilíngue do projeto
```

## EN: Project Structure
```
previsia-acessibilidade/
├── data/                          # Generated data (URL and dataset CSVs) - included in the repository
├── models/                        # Trained models (.pt), scaler, and feature_names.pkl - included in the repository
├── templates/                     # HTML templates for Flask interface
│   ├── index.html                # URL input form with language selector
│   └── resultado.html            # Results page with guide and audio
├── translations/                  # Babel translation files (PT/EN)
├── app.py                        # Flask web app with i18n and PyTorch
├── babel.cfg                     # Babel configuration for string extraction
├── collector.py                  # URL analysis (static/dynamic with Playwright/Axe)
├── orquestrador.py               # Parallel orchestration for dataset generation
├── prepare_urls.py               # URL preparation with Tranco and validation
├── trainer.py                    # PyTorch Neural Network training
├── requirements.txt              # Pinned dependencies for reproducibility
├── .gitignore                    # Exclusion of logs and temporary files
└── README.md                     # Bilingual project documentation
```

---

## PT: Pré-requisitos
- Python 3.12 ou superior
- Navegador moderno (para SpeechSynthesis e interface web)
- Conexão à internet (para baixar dependências, dados Tranco e browsers do Playwright)

## EN: Prerequisites
- Python 3.12 or higher
- Modern browser (for SpeechSynthesis and web interface)
- Internet connection (for downloading dependencies, Tranco data, and Playwright browsers)

---

## PT: Instalação
1. Clone o repositório:
   ```bash
   git clone https://github.com/eliezer-tavares/previsia-acessibilidade.git
   cd previsia-acessibilidade
   ```
   **Nota**: O clone inclui os diretórios `data/` e `models/` com arquivos pré-gerados (dataset e modelo treinados), permitindo execução imediata sem regeneração.

2. Crie e ative um ambiente virtual:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   ```
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
4. Instale os browsers para Playwright (análise dinâmica):
   ```bash
   playwright install --with-deps
   ```

## EN: Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/eliezer-tavares/previsia-acessibilidade.git
   cd previsia-acessibilidade
   ```
   **Note**: The clone includes the `data/` and `models/` directories with pre-generated files (dataset and trained model), allowing immediate execution without regeneration.

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Install Playwright browsers (for dynamic analysis):
   ```bash
   playwright install --with-deps
   ```

---

## PT: Como Usar
**Uso Rápido**: Com `data/` e `models/` já incluídos, após instalação, execute diretamente o app. Para regenerar dados (opcional), execute os passos 1-3 e delete os arquivos existentes em `data/` e `models/` antes.

1. **Preparar URLs** (opcional - regenera se necessário):
   ```bash
   python prepare_urls.py
   ```
   Gera um CSV com ~5k URLs navegáveis a partir da biblioteca Tranco, incluindo `https://univesp.br`.

2. **Gerar Dataset** (opcional - regenera se necessário):
   ```bash
   python orquestrador.py
   ```
   Analisa URLs em paralelo (com checkpoints) e salva em `data/dataset_acessibilidade.csv`.

3. **Treinar o Modelo** (opcional - regenera se necessário):
   ```bash
   python trainer.py
   ```
   Treina a Rede Neural e salva em `models/modelo_acessibilidade.pt` (com scaler e features).

4. **Executar a Aplicação Web**:
   ```bash
   python app.py
   ```
   Acesse `http://localhost:10000` para inserir URLs, selecionar idioma e obter previsões com guia narrativo.

## EN: How to Use
**Quick Start**: With `data/` and `models/` already included, after installation, run the app directly. To regenerate data (optional), run steps 1-3 and delete existing files in `data/` and `models/` first.

1. **Prepare URLs** (optional - regenerates if needed):
   ```bash
   python prepare_urls.py
   ```
   Generates a CSV with ~5k navigable URLs from the Tranco Python library, including `https://univesp.br`.

2. **Generate Dataset** (optional - regenerates if needed):
   ```bash
   python orquestrador.py
   ```
   Analyzes URLs in parallel (with checkpoints) and saves to `data/dataset_acessibilidade.csv`.

3. **Train the Model** (optional - regenerates if needed):
   ```bash
   python trainer.py
   ```
   Trains the Neural Network and saves to `models/modelo_acessibilidade.pt` (with scaler and features).

4. **Run the Web Application**:
   ```bash
   python app.py
   ```
   Access `http://localhost:10000` to input URLs, select language, and get predictions with narrative guide.

---

## PT: Implantação no Render
1. Crie uma conta no [Render](https://render.com) e conecte ao GitHub.
2. Crie um novo Web Service apontando para este repositório.
3. Configure o ambiente:
   - Runtime: Python 3.
   - Build Command: `pip install -r requirements.txt && playwright install --with-deps`.
   - Start Command: `gunicorn app:app` (ou `python app.py` para debug).
4. Defina variáveis de ambiente: `PYTHON_VERSION=3.12`, `PORT=10000`.
5. Deploy automático via GitHub pushes.
6. Acesse via URL gerada (ex: https://previsia.onrender.com).

**Nota**: A análise dinâmica pode falhar devido a limites de CPU/memória no plano gratuito; o app usa fallback automático para análise estática. Para análise completa, use deploy local ou em VPS. Os diretórios `data/` e `models/` são incluídos no repositório para execução imediata. Enquanto o projeto estiver hospedado no plano gratuito do Render, para acessar é preciso ter paciência, pois pode demorar até 180 segundos para a página inicial do PrevisIA abrir.

## EN: Deployment on Render
1. Create an account on [Render](https://render.com) and connect to GitHub.
2. Create a new Web Service pointing to this repository.
3. Configure the environment:
   - Runtime: Python 3.
   - Build Command: `pip install -r requirements.txt && playwright install --with-deps`.
   - Start Command: `gunicorn app:app` (or `python app.py` for debug).
4. Set environment variables: `PYTHON_VERSION=3.12`, `PORT=10000`.
5. Automatic deploys via GitHub pushes.
6. Access via generated URL (e.g., https://previsia.onrender.com).

**Note**: Dynamic analysis may fail due to CPU/memory limits on the free plan; the app automatically falls back to static analysis. For full dynamic support, use local deployment or VPS. The `data/` and `models/` directories are included in the repository for immediate execution. While the project is hosted on Render's free plan, please be patient when accessing it, as it may take up to 180 seconds for the PrevisIA home page to load.

---

## PT: Licença
Este projeto é licenciado sob a Licença MIT para uso pessoal e acadêmico apenas. Para uso comercial, entre em contato com Eliezer Tavares de Oliveira via [GitHub](https://github.com/eliezer-tavares) ou pelo e-mail [contact@eliezertavaresdeoliveira.com](mailto:contact@eliezertavaresdeoliveira.com). Veja o arquivo [LICENSE](LICENSE) para detalhes.

## EN: License
This project is licensed under the MIT License for personal and academic use only. For commercial use, contact Eliezer Tavares de Oliveira via [GitHub](https://github.com/eliezer-tavares) or by email at [contact@eliezertavaresdeoliveira.com](mailto:contact@eliezertavaresdeoliveira.com). See the [LICENSE](LICENSE) file for details.

---

## PT: Contato
Para dúvidas ou sugestões, contate Eliezer Tavares de Oliveira via [GitHub](https://github.com/eliezer-tavares) ou pelo e-mail [contact@eliezertavaresdeoliveira.com](mailto:contact@eliezertavaresdeoliveira.com).

## EN: Contact
For questions or suggestions, contact Eliezer Tavares de Oliveira via [GitHub](https://github.com/eliezer-tavares) or by email at [contact@eliezertavaresdeoliveira.com](mailto:contact@eliezertavaresdeoliveira.com).