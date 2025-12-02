import streamlit as st
import sqlite3
import pandas as pd
import time

# Configuração da página
st.set_page_config(page_title="Sistema de Controle Campus", layout="wide")

st.title("Sistema de Gerenciamento de Acesso - IF MAchado")

# Função para carregar dados do banco
def carregar_dados():
    conn = sqlite3.connect('sistema_campus.db')
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
    
    placeholder = st.empty()
    
    # Atualização em tempo real
    while True:
        df = carregar_dados()
        with placeholder.container():
            st.dataframe(df.head(10), use_container_width=True)
            
            # Métricas
            col1, col2, col3 = st.columns(3)
            col1.metric("Total de Acessos Hoje", len(df))
            col2.metric("Carros", len(df[df['tipo'] == 'CARRO']))
            col3.metric("Motos", len(df[df['tipo'] == 'MOTO']))
            
        time.sleep(2)

elif menu == "Relatórios":
    st.subheader("Histórico Completo para Consultas")
    df = carregar_dados()
    
    # Filtros
    filtro_placa = st.text_input("Filtrar por Placa:")
    if filtro_placa:
        df = df[df['placa'].str.contains(filtro_placa.upper())]
        
    st.dataframe(df, use_container_width=True)
    
    # Botão para baixar relatório
    st.download_button(
        label="Baixar Relatório (CSV)",
        data=df.to_csv().encode('utf-8'),
        file_name='relatorio_acessos.csv',
        mime='text/csv',
    )

elif menu == "Cadastrar Veículo":
    st.subheader("Novo Cadastro")
    # Formulário de cadastro
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