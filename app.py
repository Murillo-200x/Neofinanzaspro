import streamlit as st
import pandas as pd
import sqlite3
from groq import Groq
from datetime import datetime
import plotly.express as px

# --- INICIALIZACIÓN SEGURA ---
try:
    api_key = st.secrets["GROQ_API_KEY"]
except Exception:
    api_key = ""

if not api_key:
    st.error("⚠️ No se encontró la API Key en los secretos de Streamlit Cloud. Configúrala en Settings → Secrets.")
    st.stop()

client = Groq(api_key=api_key.strip())
# Configuración inicial de la página
st.set_page_config(
    page_title="NeoFinanzas Pro", 
    page_icon="💸", 
    layout="centered"
)

# --- CSS PARA ESTILO VISUAL MODERNISTA ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    .stApp {
        background-color: #08080a;
        color: #f1f5f9;
    }
    .neo-card {
        background: #121218;
        padding: 24px;
        border-radius: 20px;
        border: 1px solid #262636;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.4);
    }
    .metric-container {
        background: linear-gradient(135deg, #181824 0%, #121218 100%);
        border: 1px solid #32324a;
        padding: 18px;
        border-radius: 16px;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# --- BASE DE DATOS LOCAL ---
conn = sqlite3.connect('neofinanzas_pro.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS transacciones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    nombre TEXT,
                    tipo TEXT, 
                    monto REAL, 
                    categoria TEXT, 
                    fecha TEXT,
                    mes TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS metas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    nombre TEXT, 
                    objetivo REAL, 
                    actual REAL)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS deudas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    nombre TEXT, 
                    total REAL, 
                    pagado REAL)''')
conn.commit()

# --- GESTIÓN DE SESIÓN (OBLIGA A REGISTRARSE SI SE SALE O RECARGA) ---
if "user_registered" not in st.session_state:
    st.session_state.user_registered = False

if not st.session_state.user_registered:
    st.markdown("<h1 style='text-align: center; color: #a855f7;'>NeoFinanzas Pro 🚀</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #94a3b8;'>Tu asistente financiero inteligente y personal</p>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="neo-card">', unsafe_allow_html=True)
        user_name = st.text_input("👤 ¿Cómo te llamas?")
        
        st.write("Elige tu avatar con emojis:")
        avatar_col = st.columns(6)
        emojis_disponibles = [ "😎", "🚀", "💻", "🦊", "🦁", "⚡", "🎯", "🦉", "💎", "🔥", "🐼", "🤖", "🎨", "🎧", "🎮", "🎸", "📚", "🧠", "💡", "🛠️", "🔮", "👑", "🎩", "🕶️", "💼", "📈", "📉", "⭐", "🌟", "💫", "🎯", "🧩", "🎲", "🛹", "⚽", "🏀", "🏆", "🥇", "🧭", "⚓", "🛸", "🛰️", "📱", "⌚", "📷", "🎙️", "🪄", "🧬", "🧪", "🧰", "🔑", "🛡️", "⚔️", "🔥", "⚡", "🌊", "🌪️", "🌵", "🦄", "🐉", "👻", "👽", "👾", "🤖", "🎃", "🐯", "🐺", "🦅", "🦈", "🦖", "🌺", "🍀", "🍁", "🍄"]
        
        if "selected_emoji" not in st.session_state:
            st.session_state.selected_emoji = "🚀"
            
        for i, emj in enumerate(emojis_disponibles):
            with avatar_col[i % 6]:
                if st.button(emj, key=f"emj_{i}"):
                    st.session_state.selected_emoji = emj
        
        st.info(f"Avatar seleccionado: {st.session_state.selected_emoji}")

        user_reason = st.selectbox(
            "¿Cuál es tu objetivo principal con la aplicación?", 
            [
                "Controlar y registrar gastos diarios detallados", 
                "Ahorrar dinero para metas y objetivos específicos", 
                "Salir de deudas y organizar pagos pendientes", 
                "Analizar mis finanzas mediante Inteligencia Artificial", 
                "Aprender educación financiera y gestión de presupuesto",
                "Optimizar inversiones y flujo de caja personal"
            ]
        )
        
        if st.button("Comenzar Experiencia", use_container_width=True):
            if user_name.strip() != "":
                st.session_state.user_name = user_name
                st.session_state.user_reason = user_reason
                st.session_state.user_registered = True
                st.rerun()
            else:
                st.warning("Por favor ingresa tu nombre para continuar.")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- BARRA LATERAL (VERTICAL) ---
with st.sidebar:
    st.markdown(f"<h2 style='text-align: center;'>{st.session_state.selected_emoji} {st.session_state.user_name}</h2>", unsafe_allow_html=True)
    st.caption(f"🎯 Meta: {st.session_state.user_reason}")
    st.markdown("---")
    
    menu = st.radio("Navegación", [
        "📊 Dashboard & Meses", 
        "⚖️ Presupuesto Pro", 
        "💳 Billetera", 
        "🎯 Metas", 
        "⚠️ Deudas", 
        "🤖 Mentor IA"
    ])
    
    st.markdown("---")
    if st.button("🔄 Cerrar Sesión", use_container_width=True):
        st.session_state.user_registered = False
        st.rerun()
# --- MÓDULO: DASHBOARD & MESES ---
if menu == "📊 Dashboard & Meses":
    st.title("📊 Resumen Financiero y por Meses")
    
    # 1. Obtener los meses que realmente existen en la base de datos sobre la marcha
    df_meses_disponibles = pd.read_sql("SELECT DISTINCT mes FROM transacciones ORDER BY mes DESC", conn)
    
    # Si no hay transacciones todavía, ponemos por defecto el mes actual del sistema
    mes_actual_str = datetime.now().strftime("%Y-%m")
    
    if not df_meses_disponibles.empty:
        lista_meses = df_meses_disponibles['mes'].tolist()
        # Asegurarnos de que el mes actual siempre esté disponible por si quieres registrar algo nuevo hoy
        if mes_actual_str not in lista_meses:
            lista_meses.insert(0, mes_actual_str)
    else:
        lista_meses = [mes_actual_str]
    
    # 2. Selector dinámico de meses
    mes_seleccionado = st.selectbox("📅 Selecciona el Periodo (Mes)", lista_meses)
    
    # 3. Filtrar transacciones del mes elegido
    df_trans = pd.read_sql(f"SELECT * FROM transacciones WHERE mes = '{mes_seleccionado}'", conn)
        
    total_ingresos = df_trans[df_trans['tipo'].str.contains('Ingreso')]['monto'].sum() if not df_trans.empty else 0
    total_gastos = df_trans[df_trans['tipo'].str.contains('Gasto')]['monto'].sum() if not df_trans.empty else 0
    balance = total_ingresos - total_gastos

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="metric-container"><h4>📈 Ingresos</h4><h2>${total_ingresos:,.2f}</h2></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-container"><h4>📉 Gastos</h4><h2>${total_gastos:,.2f}</h2></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-container"><h4>⚖️ Balance</h4><h2>${balance:,.2f}</h2></div>', unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    if not df_trans.empty:
        st.markdown('<div class="neo-card">', unsafe_allow_html=True)
        st.subheader(f"Comportamiento del periodo: {mes_seleccionado}")
        fig = px.bar(df_trans, x='categoria', y='monto', color='tipo', barmode='group', template='plotly_dark')
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info(f"No hay transacciones registradas para el mes de {mes_seleccionado}. ¡Ve a la Billetera para agregar algunas!")
# --- MÓDULO: PRESUPUESTO PRO (3 PARTES + FIJOS/VARIABLES) ---
elif menu == "⚖️ Presupuesto Pro":
    st.title("⚖️ Calculadora de Presupuesto Inteligente")
    st.markdown("<p style='color: #94a3b8;'>Distribuye tus ingresos y controla tus apartados fijos vs variables.</p>", unsafe_allow_html=True)
    
    st.markdown('<div class="neo-card">', unsafe_allow_html=True)
    ingreso_base = st.number_input("Ingreso total mensual estimado ($)", min_value=0.0, step=100.0, value=1500.0)
    
    st.write("### 1. Regla de Partición (Ej. 50/30/20)")
    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        p_necesidades = st.slider("Necesidades (%)", 0, 100, 50)
    with col_p2:
        p_gustos = st.slider("Gustos / Ocio (%)", 0, 100, 30)
    with col_p3:
        p_ahorro = st.slider("Ahorro / Inversión (%)", 0, 100, 20)
        
    suma_porcentajes = p_necesidades + p_gustos + p_ahorro
    if suma_porcentajes != 100:
        st.warning(f"⚠️ La suma actual es {suma_porcentajes}%. Lo ideal es que sume exactamente 100%.")
    else:
        st.success("✅ ¡Distribución perfecta al 100%!")
        
    monto_nec = ingreso_base * (p_necesidades / 100)
    monto_gus = ingreso_base * (p_gustos / 100)
    monto_aho = ingreso_base * (p_ahorro / 100)
    
    res_c1, res_c2, res_c3 = st.columns(3)
    with res_c1:
        st.markdown(f'<div class="metric-container"><h4>🏠 Necesidades</h4><h2>${monto_nec:,.2f}</h2></div>', unsafe_allow_html=True)
    with res_c2:
        st.markdown(f'<div class="metric-container"><h4>🎉 Gustos</h4><h2>${monto_gus:,.2f}</h2></div>', unsafe_allow_html=True)
    with res_c3:
        st.markdown(f'<div class="metric-container"><h4>💰 Ahorro</h4><h2>${monto_aho:,.2f}</h2></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Gastos Fijos vs Variables
    st.markdown('<div class="neo-card">', unsafe_allow_html=True)
    st.subheader("📌 Análisis Rápido: Fijos vs Variables")
    fijos_pro = st.number_input("Tus Gastos Fijos (Renta, Suscripciones, Servicios)", min_value=0.0, step=50.0, value=400.0)
    variables_pro = st.number_input("Tus Gastos Variables (Comida fuera, Antojos)", min_value=0.0, step=50.0, value=200.0)
    total_fv = fijos_pro + variables_pro
    st.write(f"Suma de Gastos Obligatorios y Ocasionales: **${total_fv:,.2f}**")
    st.markdown('</div>', unsafe_allow_html=True)

# --- MÓDULO: BILLETERA (CON NOMBRE Y EMOJIS) ---
elif menu == "💳 Billetera":
    st.title("💳 Gestión de Billetera")
    
    col_f1, col_f2 = st.columns([1, 1])
    with col_f1:
        st.markdown('<div class="neo-card">', unsafe_allow_html=True)
        st.subheader("➕ Nuevo Movimiento")
        with st.form("form_transaccion"):
            nombre_mov = st.text_input("Nombre / Concepto (Ej. Compra Supermercado)")
            tipo = st.selectbox("Tipo de Movimiento", ["Ingreso 💰", "Gasto 💸"])
            monto = st.number_input("Monto ($)", min_value=0.0, step=50.0)
            categoria = st.selectbox("Categoría", [
                "Comida 🍔", "Transporte 🚗", "Servicios ⚡", "Salario 💼", 
                "Entretenimiento 🎮", "Ahorro 🏦", "Salud 💊", "Educación 📚", "Otros 📦"
            ])
            submitted = st.form_submit_button("Registrar Movimiento", use_container_width=True)
            
            if submitted:
                if nombre_mov.strip() != "":
                    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M")
                    mes_actual = datetime.now().strftime("%Y-%m")
                    cursor.execute("INSERT INTO transacciones (nombre, tipo, monto, categoria, fecha, mes) VALUES (?,?,?,?,?,?)", 
                                   (nombre_mov, tipo, monto, categoria, fecha_actual, mes_actual))
                    conn.commit()
                    st.success("¡Movimiento registrado con éxito!")
                    st.rerun()
                else:
                    st.warning("Por favor asigna un nombre al movimiento.")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_f2:
        st.markdown('<div class="neo-card">', unsafe_allow_html=True)
        st.subheader("📜 Historial Reciente")
        df_hist = pd.read_sql("SELECT nombre, tipo, monto, categoria, fecha FROM transacciones ORDER BY id DESC LIMIT 10", conn)
        if not df_hist.empty:
            st.dataframe(df_hist, use_container_width=True)
        else:
            st.write("No hay registros todavía.")
        st.markdown('</div>', unsafe_allow_html=True)

# --- MÓDULO: METAS ---
elif menu == "🎯 Metas":
    st.title("🎯 Metas de Ahorro")
    
    col_m1, col_m2 = st.columns([1, 1])
    with col_m1:
        st.markdown('<div class="neo-card">', unsafe_allow_html=True)
        st.subheader("🎯 Crear Nueva Meta")
        with st.form("form_meta"):
            nombre_meta = st.text_input("Nombre de la meta (Ej. Viaje ✈️, PC Gamer 💻)")
            objetivo_meta = st.number_input("Monto Objetivo ($)", min_value=0.0, step=500.0)
            monto_actual = st.number_input("Ahorro Inicial ($)", min_value=0.0, step=100.0)
            btn_meta = st.form_submit_button("Guardar Meta", use_container_width=True)
            
            if btn_meta and nombre_meta:
                cursor.execute("INSERT INTO metas (nombre, objetivo, actual) VALUES (?,?,?)", (nombre_meta, objetivo_meta, monto_actual))
                conn.commit()
                st.success("¡Meta creada!")
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_m2:
        st.markdown('<div class="neo-card">', unsafe_allow_html=True)
        st.subheader("🏆 Mis Metas Activas")
        df_metas_view = pd.read_sql("SELECT * FROM metas", conn)
        if not df_metas_view.empty:
            for index, row in df_metas_view.iterrows():
                st.write(f"**{row['nombre']}**")
                progreso = min(row['actual'] / row['objetivo'], 1.0) if row['objetivo'] > 0 else 0
                st.progress(progreso)
                st.caption(f"Progreso: ${row['actual']:,.2f} / ${row['objetivo']:,.2f}")
                st.markdown("---")
        else:
            st.write("Aún no tienes metas creadas.")
        st.markdown('</div>', unsafe_allow_html=True)

# --- MÓDULO: DEUDAS ---
elif menu == "⚠️ Deudas":
    st.title("⚠️ Control de Deudas")
    
    col_d1, col_d2 = st.columns([1, 1])
    with col_d1:
        st.markdown('<div class="neo-card">', unsafe_allow_html=True)
        st.subheader("📝 Registrar Deuda")
        with st.form("form_deuda"):
            nombre_deuda = st.text_input("Concepto / Acreedor (Ej. Préstamo Amigo 🤝)")
            total_deuda = st.number_input("Deuda Total ($)", min_value=0.0, step=100.0)
            pagado_deuda = st.number_input("Monto ya pagado ($)", min_value=0.0, step=100.0)
            btn_deuda = st.form_submit_button("Añadir Deuda", use_container_width=True)
            
            if btn_deuda and nombre_deuda:
                cursor.execute("INSERT INTO deudas (nombre, total, pagado) VALUES (?,?,?)", (nombre_deuda, total_deuda, pagado_deuda))
                conn.commit()
                st.success("Deuda registrada")
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_d2:
        st.markdown('<div class="neo-card">', unsafe_allow_html=True)
        st.subheader("📊 Estado de Deudas")
        df_deudas_view = pd.read_sql("SELECT * FROM deudas", conn)
        if not df_deudas_view.empty:
            st.dataframe(df_deudas_view, use_container_width=True)
        else:
            st.write("¡Excelente! No registras deudas pendientes.")
        st.markdown('</div>', unsafe_allow_html=True)

# --- MÓDULO: MENTOR IA (GROQ AUTOMÁTICO) ---
elif menu == "🤖 Mentor IA":
    st.title("🤖 Mentor Financiero IA")
    
    if not client:
        st.error("⚠️ La API Key de Groq no está configurada correctamente en el código. Edita la variable `GROQ_API_KEY` al inicio de tu archivo `app.py`.")
    else:
        st.markdown('<div class="neo-card">', unsafe_allow_html=True)
        st.write(f"Hola **{st.session_state.user_name}** {st.session_state.selected_emoji}. Analizo tus finanzas automáticamente usando la velocidad de Llama 3.")
        
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
            
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                
        user_prompt = st.chat_input("Pídele un consejo a tu mentor financiero...")
        if user_prompt:
            st.session_state.chat_history.append({"role": "user", "content": user_prompt})
            with st.chat_message("user"):
                st.markdown(user_prompt)
                
            ctx_trans = pd.read_sql("SELECT * FROM transacciones", conn).to_string()
            ctx_metas = pd.read_sql("SELECT * FROM metas", conn).to_string()
            ctx_deudas = pd.read_sql("SELECT * FROM deudas", conn).to_string()
            
            prompt_sistema = f"""
            Eres un mentor financiero experto, analítico y cercano. El usuario se llama {st.session_state.user_name} y su objetivo es {st.session_state.user_reason}.
            Aquí tienes sus datos financieros actuales de la base de datos:
            - Transacciones: {ctx_trans}
            - Metas de Ahorro: {ctx_metas}
            - Deudas: {ctx_deudas}
            
            Responde de forma concisa, constructiva, motivadora y basada estrictamente en estos datos reales.
            """
            
            try:
                with st.chat_message("assistant"):
                    with st.spinner("Analizando tus finanzas..."):
                        response = client.chat.completions.create(
                            model="openai/gpt-oss-120b",
                            messages=[
                                {"role": "system", "content": prompt_sistema},
                                {"role": "user", "content": user_prompt}
                            ]
                        )
                        bot_reply = response.choices[0].message.content
                        st.markdown(bot_reply)
                        st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})
            except Exception as e:
                st.error(f"Error al generar respuesta de la IA: {e}")
        st.markdown('</div>', unsafe_allow_html=True)
