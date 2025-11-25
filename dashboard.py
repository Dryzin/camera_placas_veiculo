import streamlit as st
import sqlite3
import pandas as pd
import time

# conf da pagina
st.set_page_config(page_title="Sistema de Controle Campus", layout="wide")

st.title("Sistema de Gerenciamento de Acesso - IF MAchado")

# select query para carregar dados do banco
def carregar_dados():
    conn = sqlite3.connect('sistema_campus.db')
    # Query de acesso com join para pegar dados do veículo
    query = """
    SELECT 
        a.id, 
        a.placa, 
        v.proprietario, 
        v.tipo, 
        v.categoria, 
        a.data_hora as 'Horário Entrada'
    FROM acessos a
    LEFT JOIN veiculos v ON a.placa = v.placa
    ORDER BY a.data_hora DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Sidebar
menu = st.sidebar.selectbox("Menu", ["Monitoramento em Tempo Real", "Relatórios", "Cadastrar Veículo"])

if menu == "Monitoramento em Tempo Real":
    st.subheader("Últimos Acessos Registrados")
    st.info("Esta tabela atualiza automaticamente.")
    
    placeholder = st.empty()
    
    # Simula atualização em tempo real
    while True:
        df = carregar_dados()
        with placeholder.container():
            # Mostra apenas os ultimos 10
            st.dataframe(df.head(10), use_container_width=True)
            
            # Métricas Rápidas
            col1, col2, col3 = st.columns(3)
            col1.metric("Total de Acessos Hoje", len(df))
            col2.metric("Carros", len(df[df['tipo'] == 'CARRO']))
            col3.metric("Motos", len(df[df['tipo'] == 'MOTO']))
            
        time.sleep(2) # Atualiza a cada 2 segundos

elif menu == "Relatórios":
    st.subheader("Histórico Completo para Consultas")
    df = carregar_dados()
    
    # Filtros
    filtro_placa = st.text_input("Filtrar por Placa:")
    if filtro_placa:
        df = df[df['placa'].str.contains(filtro_placa.upper())]
        
    st.dataframe(df, use_container_width=True)
    
    # Botão para baixar Excel/CSV
    st.download_button(
        label="📥 Baixar Relatório (CSV)",
        data=df.to_csv().encode('utf-8'),
        file_name='relatorio_acessos.csv',
        mime='text/csv',
    )

elif menu == "Cadastrar Veículo":
    st.subheader("Novo Cadastro")
    # Insert de usuario no banco
    with st.form("cadastro"):
        placa = st.text_input("Placa")
        nome = st.text_input("Nome do Proprietário")
        tipo = st.selectbox("Tipo", ["CARRO", "MOTO"])
        cat = st.selectbox("Categoria", ["OFICIAL", "PARTICULAR"])
        
        enviou = st.form_submit_button("Salvar")
        
        if enviou:
            conn = sqlite3.connect('sistema_campus.db')
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO veiculos (placa, proprietario, tipo, categoria, status) VALUES (?,?,?,?,?)", 
                               (placa.upper(), nome, tipo, cat, "AUTORIZADO"))
                conn.commit()
                st.success(f"Veículo {placa} cadastrado!")
            except:
                st.error("Erro: Placa já existe.")
            conn.close()