# Sistema de Controle de Acesso - Campus

  * **Reconhecimento de Placas (OCR):** Utiliza EasyOCR para ler placas Mercosul e Antigas.
  * **Detecção de Veículos (IA):** Utiliza YOLOv8 para identificar visualmente se é Carro ou Moto.
  * **Gestão de Acesso:** Verifica permissões no banco de dados SQLite.
  * **Dashboard Web:** Interface para relatórios e cadastros via Streamlit.
  * **Alertas:** Identifica veículos não autorizados ou divergências de categoria.

## Ambiente

Antes de começar, certifique-se de ter instalado:

  * **Python 3.8+**
  * **Webcam** conectada

### 1\. Instalação das Dependências

Abra o terminal na pasta do projeto e execute o comando abaixo para instalar todas as bibliotecas necessárias.

> **Nota:** O comando abaixo já previne conflitos de versão do OpenCV.

```bash
pip uninstall opencv-python-headless -y
pip install opencv-python easyocr ultralytics streamlit pandas
```

  * `opencv-python`: Manipulação de imagem e câmera.
  * `easyocr`: Leitura de texto (Placas).
  * `ultralytics`: Detecção de objetos (YOLOv8).
  * `streamlit` & `pandas`: Dashboard e manipulação de dados.

### 2\. Banco de Dados

O sistema utiliza **SQLite** (arquivo local). Não é necessário instalar nenhum servidor.

  * O arquivo `sistema_campus.db` será criado automaticamente na primeira execução.
  * **Dica para VS Code:** Instale a extensão **SQLite Viewer** ou **SQLite** para visualizar as tabelas dentro do editor.

-----

## Executar

O projeto roda em duas partes simultâneas: a **Câmera** (Visão) e o **Dashboard** (Gestão).

### Iniciar o Sistema de Visão

Este script abre a câmera, detecta os veículos e registra os acessos.

```bash
python main.py
```

*(Pressione `Q` na janela da câmera para encerrar)*

### Iniciar o Dashboard (Relatórios)

Abra um **novo terminal** e execute:

```bash
streamlit run dashboard.py
```

O painel administrativo abrirá automaticamente no seu navegador.

-----

## Estrutura do Projeto

  * `main.py`: Código principal (Câmera, OCR e YOLO).
  * `banco_dados.py`: Classe responsável pela conexão e queries no SQLite.
  * `dml.py`: Insert iniciais no banco de dados.
  * `dashboard.py`: Interface web para relatórios e cadastros.
  * `sistema_campus.db`: Arquivo do banco de dados (gerado automaticamente).