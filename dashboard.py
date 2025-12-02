import streamlit as st
import sqlite3
import pandas as pd
import time
import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Controle de Acesso - IF Machado",
    layout="wide",
    page_icon="🚗",
    initial_sidebar_state="expanded"
)

# --- CSS (VISUAL) ---
st.markdown("""
<style>
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: bold;
        color: #009688;
    }
    div[data-testid="stMetric"] {
        background-color: #f0f2f6;
        border: 1px solid #e0e0e0;
        padding: 10px;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- FUNÇÕES DE BANCO DE DADOS ---

def get_connection():
    return sqlite3.connect('sistema_campus.db')

def init_db():
    """Cria as tabelas se não existirem (Previne erros na 1ª execução)"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS veiculos (
            placa TEXT PRIMARY KEY,
            proprietario TEXT,
            tipo TEXT,
            categoria TEXT,
            status TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS acessos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            placa TEXT,
            data_hora TEXT
        )
    """)
    conn.commit()
    conn.close()

def carregar_acessos():
    conn = get_connection()
    query = """
    SELECT 
        a.id, 
        a.placa, 
        v.proprietario, 
        v.tipo, 
        v.categoria, 
        v.status,
        a.data_hora
    FROM acessos a
    LEFT JOIN veiculos v ON a.placa = v.placa
    ORDER BY a.data_hora DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def carregar_todos_veiculos():
    conn = get_connection()
    query = "SELECT placa, proprietario, tipo, categoria, status FROM veiculos"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def registrar_acesso_simulado(placa):
    """Função auxiliar para criar dados de teste"""
    conn = get_connection()
    cursor = conn.cursor()
    agora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO acessos (placa, data_hora) VALUES (?, ?)", (placa, agora))
    conn.commit()
    conn.close()

def limpar_banco_dados():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM acessos")
    cursor.execute("DELETE FROM veiculos")
    conn.commit()
    conn.close()

# Inicializa o banco ao rodar o script
init_db()

# --- BARRA LATERAL (MENU) ---
with st.sidebar:
    st.image("simulacao_IMG/IFSULDEMINAS_Machado-aplicações-horizontais-01.png", width=200)
    st.title("IF Machado")
    st.markdown("---")
    menu = st.radio(
        "Navegação", 
        ["Monitoramento", "Relatórios", "Base de Veículos", "Cadastrar Novo", "Admin / Testes"]
    )
    st.markdown("---")
    st.caption("Sistema v1.2 - Beta")

# --- 1. MONITORAMENTO ---
if menu == "Monitoramento":
    st.subheader("📡 Monitoramento em Tempo Real")
    
    col_top1, col_top2 = st.columns([3, 1])
    with col_top1:
        st.markdown("Visão geral das entradas recentes no campus.")
    with col_top2:
        # Checkbox para auto-refresh (Evita travar o menu com while True)
        auto_refresh = st.toggle("🔄 Atualização Automática", value=False)

    df = carregar_acessos()

    # Layout de Métricas
    if not df.empty:
        total = len(df)
        carros = len(df[df['tipo'] == 'CARRO'])
        motos = len(df[df['tipo'] == 'MOTO'])
        ultimo_horario = pd.to_datetime(df.iloc[0]['data_hora']).strftime('%H:%M:%S')
    else:
        total, carros, motos, ultimo_horario = 0, 0, 0, "--"

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Acessos", total, delta="Hoje")
    m2.metric("Carros", carros, delta=f"{((carros/total)*100):.0f}%" if total else "0%")
    m3.metric("Motos", motos, delta=f"{((motos/total)*100):.0f}%" if total else "0%")
    m4.metric("Última Entrada", ultimo_horario)

    st.divider()

    col_grid1, col_grid2 = st.columns([2, 1])

    with col_grid1:
        st.caption("📋 Últimas entradas registradas")
        # Dataframe Visual
        st.dataframe(
            df.head(10),
            use_container_width=True,
            column_config={
                "id": None, # Esconde o ID
                "data_hora": st.column_config.DatetimeColumn("Horário", format="DD/MM HH:mm:ss"),
                "tipo": st.column_config.TextColumn("Tipo"),
                "status": st.column_config.TextColumn(
                    "Status",
                    help="Status do veículo",
                    width="small",
                    validate="^(AUTORIZADO|BLOQUEADO)$" # Decoração visual automática se possível ou via pandas styler
                ),
                "placa": st.column_config.TextColumn("Placa", width="medium"),
            },
            hide_index=True
        )

    with col_grid2:
        st.caption("📊 Distribuição")
        if total > 0:
            st.bar_chart(df['tipo'].value_counts())
        else:
            st.info("Sem dados para gráfico.")

    # Lógica de refresh seguro
    if auto_refresh:
        time.sleep(2)
        st.rerun()

# --- 2. RELATÓRIOS ---
elif menu == "Relatórios":
    st.subheader("📑 Histórico Completo")
    df = carregar_acessos()
    
    # Filtros em Expander para limpar visual
    with st.expander("🔍 Filtros de Pesquisa", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            filtro_placa = st.text_input("Buscar Placa:")
        with c2:
            filtro_tipo = st.multiselect("Tipo de Veículo", ["CARRO", "MOTO"], default=["CARRO", "MOTO"])

    if filtro_placa:
        df = df[df['placa'].str.contains(filtro_placa.upper())]
    if filtro_tipo:
        df = df[df['tipo'].isin(filtro_tipo)]

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "tipo": st.column_config.SelectboxColumn("Tipo", options=["CARRO", "MOTO"]),
            "data_hora": st.column_config.DatetimeColumn("Data/Hora", format="DD/MM/YYYY HH:mm")
        }
    )

# --- 3. BASE DE VEÍCULOS ---
elif menu == "Base de Veículos":
    st.subheader("🚗 Frota Cadastrada")
    df_veiculos = carregar_todos_veiculos()
    
    if not df_veiculos.empty:
        tabs = st.tabs(["Todos", "Autorizados", "Bloqueados"])
        
        with tabs[0]:
            st.dataframe(
                df_veiculos, 
                use_container_width=True,
                column_config={
                    "status": st.column_config.SelectboxColumn(
                        "Status",
                        options=["AUTORIZADO", "BLOQUEADO"],
                        required=True,
                    ),
                    "tipo": st.column_config.ImageColumn("Ícone", help="Visualização") # Exemplo se tivesse url de imagem
                }
            )
        
        # Exemplo de uso simples de métrica visual com Pandas Styler
        def color_status(val):
            color = '#d4edda' if val == 'AUTORIZADO' else '#f8d7da'
            return f'background-color: {color}; color: black; border-radius: 5px'

        with tabs[1]:
            st.write("Veículos liberados para acesso:")
            df_auth = df_veiculos[df_veiculos['status'] == 'AUTORIZADO']
            st.dataframe(df_auth.style.map(color_status, subset=['status']), use_container_width=True)

    else:
        st.warning("Nenhum veículo cadastrado.")

# --- 4. CADASTRO ---
elif menu == "Cadastrar Novo":
    st.subheader("📝 Novo Cadastro")
    
    with st.container(border=True):
        with st.form("cadastro_form", clear_on_submit=True):
            col_a, col_b = st.columns(2)
            with col_a:
                placa = st.text_input("Placa do Veículo", placeholder="ABC1234", max_chars=7)
                nome = st.text_input("Nome do Proprietário", placeholder="Ex: João Silva")
            with col_b:
                tipo = st.selectbox("Tipo", ["CARRO", "MOTO"])
                cat = st.selectbox("Categoria", ["OFICIAL", "PARTICULAR", "TERCEIRIZADO"])
            
            obs = st.text_area("Observações")
            
            col_btn1, col_btn2 = st.columns([1, 4])
            submitted = col_btn1.form_submit_button("💾 Salvar", type="primary")
            
            if submitted:
                if placa and nome:
                    conn = get_connection()
                    cursor = conn.cursor()
                    try:
                        cursor.execute("""
                            INSERT INTO veiculos (placa, proprietario, tipo, categoria, status) 
                            VALUES (?, ?, ?, ?, ?)
                        """, (placa.upper().strip(), nome, tipo, cat, "AUTORIZADO"))
                        conn.commit()
                        st.success(f"✅ Veículo {placa.upper()} cadastrado com sucesso!")
                        st.balloons()
                    except sqlite3.IntegrityError:
                        st.error(f"⚠️ A placa {placa.upper()} já existe no sistema.")
                    finally:
                        conn.close()
                else:
                    st.warning("Preencha Placa e Nome.")

# --- 5. ADMIN / TESTES ---
elif menu == "Admin / Testes":
    st.subheader("🛠️ Ferramentas Administrativas")
    
    c1, c2 = st.columns(2)
    
    with c1:
        st.error("Zona de Perigo")
        if st.button("🗑️ LIMPAR TODO O BANCO", type="primary"):
            limpar_banco_dados()
            st.toast("Banco resetado!", icon="🔥")
            time.sleep(1)
            st.rerun()

    with c2:
        st.info("Simulação de Dados")
        st.write("Gera uma entrada fake de um veículo já cadastrado.")
        
        # Pega veículos existentes para o selectbox
        df_v = carregar_todos_veiculos()
        if not df_v.empty:
            veiculo_teste = st.selectbox("Escolha um veículo para simular entrada:", df_v['placa'].tolist())
            if st.button("Simular Entrada Agora"):
                registrar_acesso_simulado(veiculo_teste)
                st.success(f"Entrada registrada para {veiculo_teste}")
                time.sleep(1)
                st.rerun()
        else:
            st.warning("Cadastre um veículo primeiro para testar.")

    st.markdown("---")
    st.json({"Status DB": "OK", "Local": "Minas Gerais", "Sistema": "Ativo"})