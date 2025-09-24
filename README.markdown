# PrevisIA: Previsor e Guia de Acessibilidade Web 👁️‍🗨️🤖

## Univesp - Projeto Integrador IV - Engenharia de Computação - 2º Semestre 2025
**Desenvolvido por**: Eliezer Tavares de Oliveira (principal), Anderson Vianna Ferrari, Efrain Tobal Tavares, Lucas de Goes Vieira Junior

---

## PT: Sobre o Projeto
O PrevisIA é uma ferramenta inovadora desenvolvida para a disciplina Projeto Integrador IV da graduação em Engenharia de Computação da Univesp. Nosso objetivo é democratizar a avaliação de acessibilidade web, fornecendo uma solução que prevê escores de acessibilidade e oferece um Guia de Navegação Preditivo em linguagem natural, otimizado para usuários com deficiência visual.

**Por quê?** Para tornar a web mais inclusiva, especialmente para usuários de leitores de tela como NVDA.  
**Como?** Combina análise estática (BeautifulSoup) e dinâmica (Selenium/Axe-core) para extrair características de acessibilidade, treina um modelo RandomForest para prever escores e gera guias narrativos acessíveis via SpeechSynthesis.

## EN: About the Project
PrevisIA is an innovative tool developed for the Projeto Integrador IV course at Univesp's Computer Engineering program. Our goal is to democratize web accessibility evaluation by providing a solution that predicts accessibility scores and offers a Predictive Navigation Guide in natural language, optimized for visually impaired users.

**Why?** To make the web more inclusive, especially for users of screen readers like NVDA.  
**How?** Combines static (BeautifulSoup) and dynamic (Selenium/Axe-core) analysis to extract accessibility features, trains a RandomForest model to predict scores, and generates accessible narrative guides via SpeechSynthesis.

---

## PT: Progresso do Relatório Parcial
### Funcionalidades Implementadas
- **Previsão de Acessibilidade**: Gera escores de acessibilidade (0-100) usando análise estática (completa) e dinâmica (em progresso devido a falhas em testes dinâmicos).
- **Análise Estática**: Extração de features como imagens sem `alt`, links genéricos, hierarquia de cabeçalhos, e presença de ARIA usando BeautifulSoup.
- **Interface Web**: Aplicativo Flask (`app.py`) com rotas `/analisar` (análise estática) e `/analisar_completa` (análise dinâmica, em progresso).
- **Templates Acessíveis**: `index.html` e `resultado.html` com ARIA, contraste WCAG 2.1 (nível AA), e validados com WAVE/NVDA.
- **Testes Unitários**: 100% de sucesso nos testes de acessibilidade estática (`test_acessibilidade.py`) e do aplicativo web (`test_app.py`). Cobertura de ~95% em `collector.py` devido a testes dinâmicos pendentes.
- **Feedback em Áudio**: Integração inicial com SpeechSynthesis para saída de áudio sob demanda.
- **Validação de URLs**: Módulo `validate_url.py` para validação dinâmica de URLs.

### Limitações
- **Teste Dinâmico**: Testes dinâmicos (Selenium/Axe-core) estão incompletos devido a problemas de mocking (`"Object of type Mock is not JSON serializable"`) e serão corrigidos no relatório final.
- **Testes Incompletos**: Testes para `orquestrador.py`, `prepare_urls.py`, `trainer.py`, e testes dinâmicos de acessibilidade não foram incluídos no repositório, pois estão em desenvolvimento.
- **Cobertura**: A cobertura de código é ~95% devido a testes dinâmicos pendentes.

### Planos para o Relatório Final
- Corrigir testes dinâmicos de acessibilidade.
- Finalizar e incluir testes para `orquestrador.py`, `prepare_urls.py`, e `trainer.py`.
- Aumentar a cobertura para 100%.
- Validar a aplicação com mais URLs reais e testes de usabilidade com NVDA.

## EN: Partial Report Progress
### Implemented Features
- **Accessibility Prediction**: Generates accessibility scores (0-100) using static analysis (complete) and dynamic analysis (in progress due to dynamic test failures).
- **Static Analysis**: Extracts features like missing `alt` texts, generic links, heading hierarchy, and ARIA presence using BeautifulSoup.
- **Web Interface**: Flask application (`app.py`) with `/analisar` (static analysis) and `/analisar_completa` (dynamic analysis, in progress) routes.
- **Accessible Templates**: `index.html` and `resultado.html` with ARIA, WCAG 2.1 (Level AA) contrast, and validated with WAVE/NVDA.
- **Unit Tests**: 100% success in static accessibility tests (`test_acessibilidade.py`) and web app tests (`test_app.py`). ~95% code coverage in `collector.py` due to pending dynamic tests.
- **Audio Feedback**: Initial integration with SpeechSynthesis for on-demand audio output.
- **URL Validation**: `validate_url.py` module for dynamic URL validation.

### Limitations
- **Dynamic Test**: Dynamic tests (Selenium/Axe-core) are incomplete due to mocking issues (`"Object of type Mock is not JSON serializable"`) and will be fixed in the final report.
- **Incomplete Tests**: Tests for `orquestrador.py`, `prepare_urls.py`, `trainer.py`, and dynamic accessibility tests were excluded from the repository as they are still in development.
- **Coverage**: Code coverage is ~95% due to pending dynamic tests.

### Plans for the Final Report
- Fix dynamic accessibility tests.
- Complete and include tests for `orquestrador.py`, `prepare_urls.py`, and `trainer.py`.
- Achieve 100% code coverage.
- Validate the application with more real URLs and NVDA usability tests.

---

## PT: Estrutura do Projeto
```
previsia-acessibilidade/
├── data/                     # Dados gerados (CSV de URLs e dataset)
├── models/                   # Modelos treinados e nomes de features
├── templates/                # Templates HTML para a interface Flask
│   ├── index.html           # Formulário de entrada de URL
│   └── resultado.html       # Página de resultados com guia preditivo
├── tests/                   # Testes unitários e de integração
│   ├── test_acessibilidade.py # Testes de acessibilidade estática
│   └── test_app.py          # Testes do aplicativo web
├── utils/                   # Módulos utilitários
│   └── validate_url.py      # Validação dinâmica de URLs
├── app.py                   # Aplicação web Flask
├── collector.py             # Análise de URLs (estática e dinâmica)
├── orquestrador.py          # Orquestração paralela para geração de dataset
├── prepare_urls.py          # Preparação de URLs com a biblioteca Tranco
├── trainer.py               # Treinamento do modelo RandomForest
├── pytest.ini               # Configuração do pytest
├── requirements.txt         # Dependências do projeto
├── .gitignore               # Exclusão de arquivos não prontos
└── README.md                # Documentação do projeto
```

## EN: Project Structure
```
previsia-acessibilidade/
├── data/                     # Generated data (URL and dataset CSVs)
├── models/                   # Trained models and feature names
├── templates/                # HTML templates for Flask interface
│   ├── index.html           # URL input form
│   └── resultado.html       # Results page with predictive guide
├── tests/                   # Unit and integration tests
│   ├── test_acessibilidade.py # Static accessibility tests
│   └── test_app.py          # Web application tests
├── utils/                   # Utility modules
│   └── validate_url.py      # Dynamic URL validation
├── app.py                   # Flask web application
├── collector.py             # URL analysis (static and dynamic)
├── orquestrador.py          # Parallel orchestration for dataset generation
├── prepare_urls.py          # URL preparation with Tranco Python library
├── trainer.py               # RandomForest model training
├── pytest.ini               # Pytest configuration
├── requirements.txt         # Project dependencies
├── .gitignore               # Exclusion of incomplete files
└── README.md                # Project documentation
```

---

## PT: Pré-requisitos
- Python 3.13 ou superior
- Navegador moderno (para SpeechSynthesis e interface web)
- Conexão à internet (para baixar dependências e dados Tranco)

## EN: Prerequisites
- Python 3.13 or higher
- Modern browser (for SpeechSynthesis and web interface)
- Internet connection (for downloading dependencies and Tranco data)

---

## PT: Instalação
1. Clone o repositório:
   ```bash
   git clone https://github.com/eliezer-tavares/previsia-acessibilidade.git
   cd previsia-acessibilidade
   ```
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

## EN: Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/eliezer-tavares/previsia-acessibilidade.git
   cd previsia-acessibilidade
   ```
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

---

## PT: Como Usar
1. **Preparar URLs**:
   ```bash
   python prepare_urls.py
   ```
   Gera um CSV com URLs navegáveis a partir da biblioteca Tranco, incluindo `https://univesp.br`.

2. **Gerar Dataset**:
   ```bash
   python orquestrador.py
   ```
   Analisa URLs em paralelo e salva os resultados em `data/dataset_acessibilidade.csv`.

3. **Treinar o Modelo**:
   ```bash
   python trainer.py
   ```
   Treina um modelo RandomForest e salva em `models/modelo_acessibilidade.pkl`.

4. **Executar a Aplicação Web**:
   ```bash
   python app.py
   ```
   Acesse `http://127.0.0.1:5000` para usar a interface, inserir URLs e obter previsões.

5. **Executar Testes**:
   ```bash
   pytest --cov=. --cov-report=html
   ```
   Gera um relatório de cobertura (~95% no relatório parcial devido a testes dinâmicos pendentes).

## EN: How to Use
1. **Prepare URLs**:
   ```bash
   python prepare_urls.py
   ```
   Generates a CSV with navigable URLs from the Tranco Python library, including `https://univesp.br`.

2. **Generate Dataset**:
   ```bash
   python orquestrador.py
   ```
   Analyzes URLs in parallel and saves results to `data/dataset_acessibilidade.csv`.

3. **Train the Model**:
   ```bash
   python trainer.py
   ```
   Trains a RandomForest model and saves it to `models/modelo_acessibilidade.pkl`.

4. **Run the Web Application**:
   ```bash
   python app.py
   ```
   Access `http://127.0.0.1:5000` to use the interface, input URLs, and get predictions.

5. **Run Tests**:
   ```bash
   pytest --cov=. --cov-report=html
   ```
   Generates a coverage report (~95% in the partial report due to pending dynamic tests).

---

## PT: Implantação no PythonAnywhere
1. Crie uma conta no [PythonAnywhere](https://www.pythonanywhere.com).
2. Faça upload do projeto usando a aba "Files", mantendo a estrutura de pastas.
3. Configure o ambiente:
   - Na aba "Consoles", crie um Bash console com Python 3.10.
   - Instale as dependências:
     ```bash
     pip3.10 install --user -r requirements.txt
     ```
4. Configure o WSGI:
   - Na aba "Web", crie uma nova aplicação web com Python 3.10.
   - Edite `/var/www/<seu_usuario>_pythonanywhere_com_wsgi.py`:
     ```python
     import sys
     path = '/home/<seu_usuario>/previsia-acessibilidade'
     if path not in sys.path:
         sys.path.append(path)
     from app import app as application
     ```
5. Ajuste permissões:
   - Certifique-se de que `data/` e `models/` têm permissões de escrita:
     ```bash
     chmod -R 777 data models
     ```
6. Recarregue a aplicação na aba "Web".
7. Acesse `http://<seu_usuario>.pythonanywhere.com`.

**Nota**: A análise dinâmica (Selenium/Axe-core) pode ter limitações no PythonAnywhere devido a restrições de recursos. Use a análise rápida para melhor desempenho.

## EN: Deployment on PythonAnywhere
1. Create an account on [PythonAnywhere](https://www.pythonanywhere.com).
2. Upload the project using the "Files" tab, keeping the folder structure intact.
3. Set up the environment:
   - In the "Consoles" tab, create a Bash console with Python 3.10.
   - Install dependencies:
     ```bash
     pip3.10 install --user -r requirements.txt
     ```
4. Configure WSGI:
   - In the "Web" tab, create a new web app with Python 3.10.
   - Edit `/var/www/<your_username>_pythonanywhere_com_wsgi.py`:
     ```python
     import sys
     path = '/home/<your_username>/previsia-acessibilidade'
     if path not in sys.path:
         sys.path.append(path)
     from app import app as application
     ```
5. Adjust permissions:
   - Ensure `data/` and `models/` have write permissions:
     ```bash
     chmod -R 777 data models
     ```
6. Reload the application in the "Web" tab.
7. Access `http://<your_username>.pythonanywhere.com`.

**Note**: Complete analysis (Selenium/Axe-core) may face limitations on PythonAnywhere due to resource constraints. Use quick analysis for better performance.

---

## PT: Licença
Este projeto é licenciado sob a [Licença MIT](LICENSE).

## EN: License
This project is licensed under the [MIT License](LICENSE).

---

## PT: Contato
Para dúvidas ou sugestões, contate Eliezer Tavares de Oliveira via [GitHub](https://github.com/eliezer-tavares) ou pelo e-mail [contact@eliezertavaresdeoliveira.com](mailto:contact@eliezertavaresdeoliveira.com).

## EN: Contact
For questions or suggestions, contact Eliezer Tavares de Oliveira via [GitHub](https://github.com/eliezer-tavares) or by email at [contact@eliezertavaresdeoliveira.com](mailto:contact@eliezertavaresdeoliveira.com).