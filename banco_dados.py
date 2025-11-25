import sqlite3
from datetime import datetime

class BancoDeDados:
    def __init__(self):
        # Cria ou conecta ao arquivo 'sistema_campus.db'
        self.conn = sqlite3.connect('sistema_campus.db')
        self.cursor = self.conn.cursor()
        self.criar_tabelas()

    def criar_tabelas(self):
        # Tabela 1: Veículos e Proprietários
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS veiculos (
                placa TEXT PRIMARY KEY,
                proprietario TEXT,
                tipo TEXT,        -- CARRO ou MOTO
                categoria TEXT,   -- OFICIAL ou PARTICULAR
                status TEXT       -- AUTORIZADO ou BLOQUEADO
            )
        ''')
        # Tabela 2: Registro de Entradas (Logs)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS acessos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                placa TEXT,
                data_hora DATETIME
            )
        ''')
        self.conn.commit()

    def cadastrar_veiculo(self, placa, proprietario, tipo, categoria, status="AUTORIZADO"):
        try:
            self.cursor.execute("""
                INSERT INTO veiculos (placa, proprietario, tipo, categoria, status)
                VALUES (?, ?, ?, ?, ?)
            """, (placa.upper(), proprietario, tipo, categoria, status))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False # Placa já existe

    def buscar_veiculo(self, placa):
        # Busca informações da placa
        self.cursor.execute("SELECT * FROM veiculos WHERE placa = ?", (placa.upper(),))
        resultado = self.cursor.fetchone()
        
        if resultado:
            # Transforma a tupla em um dicionário para ficar fácil de ler
            return {
                "placa": resultado[0],
                "proprietario": resultado[1],
                "tipo": resultado[2],
                "categoria": resultado[3],
                "status": resultado[4]
            }
        return None

    def registrar_acesso(self, placa):
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("INSERT INTO acessos (placa, data_hora) VALUES (?, ?)", (placa.upper(), agora))
        self.conn.commit()

    def fechar(self):
        self.conn.close()