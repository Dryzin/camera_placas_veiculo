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

O sistema possui um **Orquestrador de Inicialização (`start.py`)** que automatiza todo o processo. Ele verifica o banco de dados, inicia o servidor web em segundo plano e abre a interface de visão computacional simultaneamente.

Basta abrir o terminal na pasta do projeto e executar um único comando:

```bash
python start.py
```

**O que vai acontecer:**

1.  **Verificação:** Se for a primeira vez, o sistema criará o banco de dados e cadastrará os usuários padrão automaticamente.
2.  **Dashboard:** O navegador abrirá automaticamente com o Painel Administrativo.
3.  **Câmera:** A janela do sistema de detecção (Carro/Moto) será aberta.

**Para encerrar:**

  * Pressione a tecla **`Q`** na janela da câmera. O script encerrará automaticamente a câmera e o servidor do dashboard.

-----

## Estrutura do Projeto

  * `main.py`: Código principal (Câmera, OCR e YOLO).
  * `banco_dados.py`: Classe responsável pela conexão e queries no SQLite.
  * `dml.py`: Insert iniciais no banco de dados.
  * `dashboard.py`: Interface web para relatórios e cadastros.
  * `sistema_campus.db`: Arquivo do banco de dados (gerado automaticamente).

<img width="1593" height="4975" alt="diagrama" src="https://github.com/user-attachments/assets/c9d3ec2f-2cb9-430d-9ba7-33ed699eb54b" />
