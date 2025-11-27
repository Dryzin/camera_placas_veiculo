import streamlit as st
import sqlite3
import pandas as pd
import time

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Sistema de Controle Campus", layout="wide", page_icon="🚗")

st.title("Sistema de Gerenciamento de Acesso - IF Machado")

# --- FUNÇÕES DE BANCO DE DADOS ---

def get_connection():
    return sqlite3.connect('sistema_campus.db')

def carregar_acessos():
    conn = get_connection()
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

def carregar_todos_veiculos():
    conn = get_connection()
    # Pega apenas o cadastro fixo
    query = "SELECT placa, proprietario, tipo, categoria, status FROM veiculos"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def limpar_banco_dados():
    conn = get_connection()
    cursor = conn.cursor()
    # Apaga os dados mas mantem as tabelas vivas
    cursor.execute("DELETE FROM acessos")
    cursor.execute("DELETE FROM veiculos")
    conn.commit()
    conn.close()

# --- BARRA LATERAL (MENU) ---
menu = st.sidebar.radio(
    "Navegação", 
    ["Monitoramento", "Relatórios de Acesso", "Base de Veículos", "Cadastrar Novo", "Área Admin"]
)

# --- 1. MONITORAMENTO ---
if menu == "Monitoramento":
    st.subheader("Monitoramento de Entradas")
    st.info("Aguardando novos acessos... (Atualização automática)")
    
    placeholder = st.empty()
    
    # Loop de atualização (simulação de real-time)
    while True:
        df = carregar_acessos()
        with placeholder.container():
            # Métricas no topo
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Acessos", len(df))
            col2.metric("Carros", len(df[df['tipo'] == 'CARRO']))
            col3.metric("Motos", len(df[df['tipo'] == 'MOTO']))
            
            # Pega o último acesso para destaque
            ultimo = df.iloc[0]['Horário Entrada'] if not df.empty else "--"
            col4.metric("Última Entrada", ultimo.split(' ')[-1] if len(ultimo) > 5 else "--")

            # Tabela
            st.dataframe(df.head(15), use_container_width=True)
            
        time.sleep(2) # Atualiza a cada 2 segundos

# --- 2. RELATÓRIOS ---
elif menu == "Relatórios de Acesso":
    st.subheader("Histórico de Acessos")
    df = carregar_acessos()
    
    col1, col2 = st.columns(2)
    with col1:
        filtro_placa = st.text_input("Buscar por Placa:")
    with col2:
        filtro_tipo = st.multiselect("Filtrar Tipo", ["CARRO", "MOTO"], default=["CARRO", "MOTO"])

    # Aplica filtros
    if filtro_placa:
        df = df[df['placa'].str.contains(filtro_placa.upper())]
    
    if filtro_tipo:
        df = df[df['tipo'].isin(filtro_tipo)]
        
    st.dataframe(df, use_container_width=True)
    
    st.download_button(
        label="Baixar Relatório (CSV)",
        data=df.to_csv(index=False).encode('utf-8'),
        file_name='relatorio_acessos.csv',
        mime='text/csv',
    )

# --- 3. BASE DE VEÍCULOS (NOVA SOLICITAÇÃO) ---
elif menu == "Base de Veículos":
    st.subheader("Base de ceículos")
    st.markdown("Aqui você visualiza todos os veículos autorizados ou bloqueados no sistema.")
    
    df_veiculos = carregar_todos_veiculos()
    
    if not df_veiculos.empty:
        col1, col2 = st.columns(2)
        col1.info(f"Total de Veículos Cadastrados: {len(df_veiculos)}")
        
        # Filtro rápido
        status_filter = col2.selectbox("Filtrar por Status", ["Todos", "AUTORIZADO", "BLOQUEADO"])
        if status_filter != "Todos":
            df_veiculos = df_veiculos[df_veiculos['status'] == status_filter]

        st.dataframe(df_veiculos, use_container_width=True)
    else:
        st.warning("Nenhum veículo cadastrado na base.")

# --- 4. CADASTRO ---
elif menu == "Cadastrar Novo":
    st.subheader("Novo Cadastro")
    
    with st.form("cadastro_form", clear_on_submit=True):
        col_a, col_b = st.columns(2)
        with col_a:
            placa = st.text_input("Placa (Sem traços)")
            nome = st.text_input("Nome do Proprietário")
        with col_b:
            tipo = st.selectbox("Tipo", ["CARRO", "MOTO"])
            cat = st.selectbox("Categoria", ["OFICIAL", "PARTICULAR"])
        
        obs = st.text_area("Observação (Opcional)")
        
        # Botão de envio
        submitted = st.form_submit_button("Salvar no Banco")
        
        if submitted and placa and nome:
            conn = get_connection()
            cursor = conn.cursor()
            try:
                # Inserindo com status padrão AUTORIZADO
                cursor.execute("""
                    INSERT INTO veiculos (placa, proprietario, tipo, categoria, status) 
                    VALUES (?, ?, ?, ?, ?)
                """, (placa.upper().strip(), nome, tipo, cat, "AUTORIZADO"))
                conn.commit()
                st.success(f"Veículo {placa.upper()} cadastrado com sucesso!")
            except sqlite3.IntegrityError:
                st.error(f"Erro: A placa {placa.upper()} já está cadastrada.")
            except Exception as e:
                st.error(f"Erro desconhecido: {e}")
            finally:
                conn.close()
        elif submitted:
            st.warning("Preencha Placa e Nome.")

# --- 5. ÁREA ADMIN (NOVA SOLICITAÇÃO) ---
elif menu == "Área Admin":
    st.subheader("Testes")
    
    st.markdown("""
    Use esta área para limpar o banco de dados durante os testes.
    **Isso apagará todos os registros de acessos e cadastros de veículos.**
    """)
    
    # Checkbox de segurança para habilitar o botão
    confirmacao = st.checkbox("Eu entendo que essa ação é irreversível.")
    
    if st.button("LIMPAR TODO O BANCO DE DADOS", type="primary", disabled=not confirmacao):
        try:
            limpar_banco_dados()
            st.toast("Banco de dados resetado com sucesso!", icon="🧹")
            st.success("Tabelas limpas! Você pode iniciar novos testes.")
            time.sleep(2)
            st.rerun() # Recarrega a página
        except Exception as e:
            st.error(f"Erro ao limpar banco: {e}")

    st.divider()
    st.markdown("### Status do Sistema")
    st.json({
        "Banco de Dados": "Conectado (Local)",
        "Arquivo": "sistema_campus.db",
        "Status": "Operante"
    })