import subprocess
import time
import os
import sys

# Definição dos nomes dos arquivos
ARQUIVO_BANCO = "sistema_campus.db"
SCRIPT_POPULAR = "dml.py"     # Seu script de insert inicial
SCRIPT_DASHBOARD = "dashboard.py"
SCRIPT_PRINCIPAL = "main.py"

def verificar_instalacao():
    """
    Verifica se o banco existe. Se não, roda o script de população.
    """
    print("--- VERIFICAÇÃO DE SISTEMA ---")
    if not os.path.exists(ARQUIVO_BANCO):
        print(f"Banco de dados não encontrado. Iniciando configuração inicial...")
        try:
            # Roda o dml.py para criar tabelas e inserir dados
            subprocess.run([sys.executable, SCRIPT_POPULAR], check=True)
            print("Banco de dados criado e populado com sucesso!")
        except Exception as e:
            print(f"Erro ao rodar script de população: {e}")
    else:
        print("Banco de dados encontrado. Sistema pronto.")
    print("-" * 30)

def iniciar_sistema():
    # 1. Verifica se precisa criar o banco
    verificar_instalacao()

    try:
        # 2. Inicia o Dashboard (Streamlit) em processo separado (background)
        print("Iniciando Dashboard (Aguarde abrir no navegador)...")
        # Usamos Popen para não travar o código aqui
        processo_dash = subprocess.Popen(["streamlit", "run", SCRIPT_DASHBOARD])
        
        # Dá um tempinho para o servidor subir
        time.sleep(3)

        # 3. Inicia o Script Principal (Câmera)
        print("Iniciando Sistema de Visão Computacional...")
        # Usamos run para que o Python ESPERE esse processo terminar antes de fechar tudo
        subprocess.run([sys.executable, SCRIPT_PRINCIPAL])

    except KeyboardInterrupt:
        print("\nEncerrando pelo teclado...")
    
    finally:
        # 4. Encerramento Limpo
        print("\nEncerrando Dashboard e limpando processos...")
        if 'processo_dash' in locals():
            processo_dash.terminate() # Mata o processo do streamlit
        print("Sistema finalizado. Até logo!")

if __name__ == "__main__":
    iniciar_sistema()