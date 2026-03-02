import streamlit as st
import pandas as pd
from streamlit_drawable_canvas import st_canvas
from datetime import datetime, timedelta
from fpdf import FPDF
import base64, tempfile, os, urllib.parse
from PIL import Image

# 1. CONFIGURACIÓN E IDENTIDAD TECNOLÓGICA (ICONO FORZADO V3)
st.set_page_config(page_title="IO SECURITY", page_icon="logo.png", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0B0E14; color: #FFFFFF; font-family: 'Inter', sans-serif; }
    h1, h2, h3 { color: #00FF7F !important; text-shadow: 0 0 10px rgba(0, 255, 127, 0.4); font-weight: 800 !important; }
    
    /* Etiquetas Gigantes para lectura en celular */
    label { font-size: 26px !important; color: #00FF7F !important; font-weight: bold !important; margin-bottom: 12px !important; }
    
    .stTextInput>div>div>input, .stNumberInput>div>div>input, .stTextArea>div>textarea, .stSelectbox>div>div>div {
        background-color: rgba(31, 41, 55, 0.8) !important; color: #FFFFFF !important; 
        border: 2px solid #00FF7F !important; border-radius: 12px !important; font-size: 22px !important; height: 65px !important;
    }

    .stButton>button { 
        width: 100%; border-radius: 15px; height: 5em; background: linear-gradient(135deg, #1F2937 0%, #0B0E14 100%);
        color: #00FF7F; border: 2px solid #00FF7F; font-weight: bold; font-size: 24px; transition: 0.3s all;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 0 25px #00FF7F; background-color: #00FF7F; color: #111418; }
    
    .success-box { padding: 25px; border-radius: 15px; background: rgba(0, 255, 127, 0.1); border: 2px solid #00FF7F; color: #FFFFFF; text-align: center; margin: 20px 0; font-size: 22px; font-weight: bold; }
    .whatsapp-btn { display: inline-block; padding: 22px; border-radius: 15px; color: white !important; background-color: #2E7D32; text-decoration: none; font-weight: bold; text-align: center; width: 100%; margin-top: 15px; font-size: 24px; border: 2px solid #FFFFFF; }
    .download-btn { display: inline-block; padding: 22px; border-radius: 15px; color: white !important; background-color: #0277BD; text-decoration: none; font-weight: bold; text-align: center; width: 100%; margin-top: 15px; border: 2px solid #FFFFFF; font-size: 24px; }
    
    .streamlit-expanderHeader { background-color: #1F2937 !important; color: #00FF7F !important; border: 1px solid #00FF7F; border-radius: 10px; font-size: 22px !important; }
    </style>
    """, unsafe_allow_html=True)

col_logo, _ = st.columns([1, 2])
with col_logo:
    try: st.image('logo.png', width=280)
    except: st.title("🛡️ IO SECURITY")

# 2. CONEXIÓN AL CATÁLOGO
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRopR4hg_DfWvNF919M9udZI738JSGiUljkyW02hc3gtcjoN869W3duYOR6VInie_fNvC5kXoByTrCm/pub?gid=596039047&single=true&output=csv"
try: 
    df_catalogo = pd.read_csv(URL_CSV)
    df_catalogo.columns = df_catalogo.columns.str.strip() 
except: 
    st.error("⚠️ ERROR DE CONEXIÓN CON CATÁLOGO"); st.stop()

# 3. GENERADOR DE PDF BLINDADO (REESTRUCTURADO)
def generar_pdf_io(cliente, items, total, tipo, periodo, tec, n_cam, canales, f_cli, f_prov, f_p, notas):
    pdf = FPDF()
    pdf.add_page()
    try: pdf.image('logo.png', 10, 8, 40)
    except: pdf.set_font('Arial', 'B', 16); pdf.cell(0, 10, 'IO SECURITY', ln=True)
    
    hoy = datetime.now()
    meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

    if tipo == "Servicio IO Prevent":
        pdf.set_font('Arial', 'B', 12); pdf.cell(0, 10, 'CONTRATO DE SOPORTE TECNICO REMOTO', ln=True, align='C')
        pdf.set_font('Arial', '', 9); pdf.cell(0, 5, f'FECHA: {hoy.day} de {meses[hoy.month-1]} del {hoy.year} LUGAR: Pachuca de Soto, Hidalgo.', ln=True, align='R'); pdf.ln(5)
        pdf.set_font('Arial', 'B', 10); pdf.cell(0, 7, "REUNIDOS", ln=True); pdf.set_font('Arial', '', 9)
        pdf.multi_cell(0, 5, f"De una parte, IO SECURITY, en adelante 'EL PRESTADOR'. Y de otra parte, {cliente}, en adelante 'EL CLIENTE'. Ambas partes acuerdan celebrar el presente CONTRATO DE SOPORTE TECNICO REMOTO para un sistema de {n_cam} camaras {tec} con grabador de {canales}.")
        
        pdf.ln(2); pdf.set_font('Arial', 'B', 9); pdf.cell(0, 5, "PRIMERA: OBJETO DEL SERVICIO", ln=True); pdf.set_font('Arial', '', 9)
        pdf.multi_cell(0, 4.5, "Prestacion de servicios de asistencia tecnica y monitoreo de salud del sistema de videovigilancia de manera exclusivamente remota.")
        
        pdf.ln(2); pdf.set_font('Arial', 'B', 9); pdf.cell(0, 5, "SEGUNDA: VIGENCIA", ln=True); pdf.set_font('Arial', '', 9)
        meses_v = 6 if periodo == "Semestral" else 12
        f_fin = f_p + timedelta(days=30*meses_v)
        pdf.multi_cell(0, 4.5, f"Modalidad {periodo.upper()}. Inicio: {f_p.strftime('%d/%m/%Y')} - Termino: {f_fin.strftime('%d/%m/%Y')}")

        pdf.ln(2); pdf.set_font('Arial', 'B', 9); pdf.cell(0, 5, "TERCERA: ALCANCE TECNICO LIMITADO", ln=True); pdf.set_font('Arial', '', 8)
        pdf.multi_cell(0, 4, "1) Verificacion de Grabacion y Salud del Disco Duro mensual. 2) Soporte y Configuracion de Aplicacion Movil (Hasta 4 dispositivos).")

        pdf.ln(2); pdf.set_font('Arial', 'B', 9); pdf.cell(0, 5, "CUARTA: EXCLUSIONES", ln=True); pdf.set_font('Arial', '', 8)
        pdf.multi_cell(0, 4, "No incluye visitas fisicas, limpieza, reparacion de cableado o refacciones. Visita de emergencia: $200.00 MXN.")
        
        pdf.ln(2); pdf.set_font('Arial', 'B', 9); pdf.cell(0, 5, "SEPTIMA: HONORARIOS", ln=True); pdf.set_font('Arial', 'B', 10)
        pdf.cell(0, 7, f"COSTO TOTAL: ${total:,.2f} MXN (Pago en una sola exhibicion).", ln=True)
    else:
        pdf.set_font('Arial', 'B', 12); pdf.cell(0, 10, 'CONTRATO DE PRESTACION DE SERVICIOS DE INSTALACION', ln=True, align='C'); pdf.ln(5)
        pdf.set_font('Arial', '', 9); pdf.multi_cell(0, 5, f"Este contrato lo celebran, por una parte, IO SECURITY ('EL PRESTADOR'), y por la otra, {cliente} ('EL CLIENTE').")
        
        pdf.ln(2); pdf.set_font('Arial', 'B', 9); pdf.cell(0, 5, "CLAUSULA PRIMERA: OBJETO DEL CONTRATO", ln=True); pdf.set_font('Arial', '', 9)
        pdf.multi_cell(0, 4.5, "EL PRESTADOR se compromete a instalar un sistema de camaras (CCTV) en el domicilio de EL CLIENTE, ubicado en Julian Villagran #202, Centro Pachuca de Soto Hgo. Equipos detallados a continuacion:")

        pdf.set_fill_color(0, 0, 0); pdf.set_text_color(255, 255, 255); pdf.set_font('Arial', 'B', 9); pdf.ln(2)
        pdf.cell(20, 8, ' Cant.', 1, 0, 'C', True); pdf.cell(120, 8, ' Descripcion del Servicio / Insumos', 1, 0, 'L', True); pdf.cell(50, 8, 'Total Concepto ', 1, 1, 'C', True)
        pdf.set_text_color(0, 0, 0); pdf.set_font('Arial', '', 9)
        for it in items:
            pdf.cell(20, 9, f" {it['Cantidad']}", 1, 0, 'C'); pdf.cell(120, 9, f" {it['Concepto']}", 1); pdf.cell(50, 9, f"$ {it['Subtotal_Final']:,.2f} ", 1, 1, 'R')
        pdf.set_font('Arial', 'B', 10); pdf.cell(140, 9, ' TOTAL NETO A PAGAR', 1, 0, 'L'); pdf.cell(50, 9, f"$ {total:,.2f} ", 1, 1, 'R'); pdf.ln(5)

        gar = "6 meses" if tipo == "Mantenimiento" else "8 meses"
        pdf.set_font('Arial', 'B', 9); pdf.cell(0, 5, "CLAUSULA TERCERA: GARANTIAS", ln=True); pdf.set_font('Arial', '', 9)
        pdf.multi_cell(0, 4.5, f"- Equipos: {gar} contra defectos de fabrica. \n- Mano de Obra: 4 meses sobre instalacion o configuracion.")
        
        pdf.ln(2); pdf.set_font('Arial', 'B', 9); pdf.cell(0, 5, "CLAUSULA QUINTA: ANULACION DE LA GARANTIA", ln=True); pdf.set_font('Arial', '', 8)
        pdf.multi_cell(0, 3.5, "1) Manipulacion ajena a IO SECURITY. 2) Daños Electricos: Sobrecargas o variaciones de voltaje. 3) Daño Fisico: Golpes o vandalismo. 4) Mal Uso. 5) Problemas de Red Internet externos.")

        pdf.ln(2); pdf.set_font('Arial', 'B', 9); pdf.cell(0, 5, "CLAUSULA SEXTA: COSTOS ADICIONALES", ln=True); pdf.set_font('Arial', '', 9)
        pdf.multi_cell(0, 4.5, "Cualquier visita tecnica fuera de garantia tendra un costo de $250.00 MXN cubiertos al momento.")

    pdf.ln(5); pdf.set_font('Arial', 'I', 8); pdf.cell(0, 5, f"Ambas partes firman de conformidad en Mineral de la Reforma, a los {hoy.day} dias de {meses[hoy.month-1]} de {hoy.year}.", ln=True)
    if f_cli is not None:
        y_f = pdf.get_y() + 5
        def g_t(d):
            img = Image.fromarray(d.astype('uint8'), 'RGBA'); t = tempfile.NamedTemporaryFile(delete=False, suffix=".png"); img.save(t.name); return t.name
        p1 = g_t(f_cli); p2 = g_t(f_prov)
        pdf.image(p1, 30, y_f, 50, 20); pdf.image(p2, 130, y_f, 50, 20); os.unlink(p1); os.unlink(p2)
        pdf.set_y(y_f + 22); pdf.set_font('Arial', 'B', 9); pdf.cell(95, 7, 'NOMBRE Y FIRMA DEL CONTRATANTE', 0, 0, 'C'); pdf.cell(95, 7, 'NOMBRE Y FIRMA DEL PRESTADOR', 0, 1, 'C')
    return pdf.output(dest='S').encode('latin-1')

# 4. INTERFAZ OPERATIVA
st.sidebar.title("🛡️ OPERACIONES IO")
tipo = st.sidebar.radio("Módulo:", ["Nueva Instalación CCTV", "Servicio IO Prevent", "Mantenimiento"])

with st.container():
    c1, c2 = st.columns(2)
    with c1:
        nom = st.text_input("👤 CLIENTE"); tel = st.text_input("📞 WHATSAPP (10 DIGITOS)"); f_p = st.date_input("📅 FECHA INICIO")
    with c2:
        m_sel = st.multiselect("📦 MATERIALES:", df_catalogo['Producto'].tolist()) if tipo != "Servicio IO Prevent" else []
        m_total = st.number_input("💵 GANANCIA / MANO DE OBRA ($)", min_value=0.0)

    items_pdf = []; total_final = 0.0; tec_io = ""; n_cam_io = 0; canales_io = ""
    periodo_io = st.sidebar.selectbox("Periodicidad Pago:", ["Semestral", "Anual"]) if tipo == "Servicio IO Prevent" else ""

    if tipo == "Servicio IO Prevent":
        with st.expander("🌐 CONFIGURACION IO PREVENT", expanded=True):
            e1, e2 = st.columns(2)
            with e1: tec_io = st.selectbox("Tecnologia:", ["Analogica", "IP Digital"]); n_cam_io = st.number_input("Num. Camaras:", 1)
            with e2: canales_io = st.selectbox("DVR/NVR:", ["4 Canales", "8 Canales", "16 Canales", "32 Canales"])
            total_final = m_total
    
    elif tipo == "Mantenimiento":
        with st.expander("🛠️ CONFIGURACIÓN MANTENIMIENTO", expanded=True):
            col1, col2 = st.columns(2)
            with col1: c_m = st.number_input("Camaras", 0); p_m = st.number_input("Precio Mant $", 0, 150); c_b = st.number_input("Baluns", 0); p_b = st.number_input("Precio Par $", 0, 120)
            with col2:
                sel_d = st.selectbox("DVR", ["Ninguna", "4 Can", "8 Can", "16 Can", "Placa Madre"])
                costos = {"Ninguna": 0, "4 Can": 250, "8 Can": 350, "16 Can": 450, "Placa Madre": 600}; p_d = st.number_input("Limpieza $", value=costos[sel_d])
            m_opc = ["Cámaras", "Baluns", "DVR"]
            m_prorr = st.multiselect("💰 PRORRATEAR GANANCIA EN:", m_opc)
            act = len(m_prorr); ex = round(m_total / act, 2) if act > 0 else 0
            if c_m > 0: v = round((c_m * p_m) + (ex if "Cámaras" in m_prorr else 0), 2); items_pdf.append({"Cantidad": c_m, "Concepto": "Mantenimiento camara", "Subtotal_Final": v}); total_final += v
            if c_b > 0: v = round((c_b * p_b) + (ex if "Baluns" in m_prorr else 0), 2); items_pdf.append({"Cantidad": c_b, "Concepto": "Reemplazo Baluns", "Subtotal_Final": v}); total_final += v
            if p_d > 0: v = round(p_d + (ex if "DVR" in m_prorr else 0), 2); items_pdf.append({"Cantidad": 1, "Concepto": f"Limpieza {sel_d}", "Subtotal_Final": v}); total_final += v

    elif m_sel:
        with st.expander("📋 PRORRATEO MATERIALES", expanded=True):
            m_gan = st.multiselect("💰 CARGAR GANANCIA EN:", m_sel)
            temp = {}; t_u = 0
            for p in m_sel:
                q = st.number_input(f"Cant. {p}", 1, key=f"q_{p}"); temp[p] = q
                if p in m_gan: t_u += q
            ex_i = round(m_total / t_u, 2) if t_u > 0 else 0
            for p, q in temp.items():
                base = df_catalogo[df_catalogo['Producto'] == p]['Precio'].values[0]
                sub = round((base + (ex_i if p in m_gan else 0)) * q, 2)
                items_pdf.append({"Cantidad": q, "Concepto": p, "Subtotal_Final": sub}); total_final += sub
            
    st.divider(); st.metric("VALOR FINAL", f"${total_final:,.2f}")
    obs = st.text_area("📝 NOTAS ADICIONALES")

st.markdown("### ✍️ FIRMAS DIGITALES")
f1, f2 = st.columns(2)
with f1: canv_cli = st_canvas(stroke_width=3, stroke_color="#000", background_color="#FFFFFF", height=180, width=350, key="cli", display_toolbar=True)
with f2: canv_prov = st_canvas(stroke_width=3, stroke_color="#000", background_color="#FFFFFF", height=180, width=350, key="prov", display_toolbar=True)

if st.button("🚀 FINALIZAR Y GENERAR EXPEDIENTE"):
    if canv_cli.image_data is not None and nom and tel:
        try:
            pdf_b = generar_pdf_io(nom, items_pdf, total_final, tipo, periodo_io, tec_io, n_cam_io, canales_io, canv_cli.image_data, canv_prov.image_data, f_p, obs)
            st.markdown(f"""<div class='success-box'>🔒 SISTEMA: CONTRATO DE {tipo.upper()} GENERADO CON ÉXITO.<br>Expediente de {nom} actualizado.</div>""", unsafe_allow_html=True)
            st.markdown(f'<a href="data:application/octet-stream;base64,{base64.b64encode(pdf_b).decode()}" download="Contrato_{nom}.pdf" class="download-btn">1. 📥 DESCARGAR CONTRATO</a>', unsafe_allow_html=True)
            msg = urllib.parse.quote(f"Hola {nom}, soy Ivan de IO SECURITY. Confirmamos la generacion de su contrato {tipo}. Adjunto el PDF.")
            st.markdown(f'<a href="https://wa.me/52{tel}?text={msg}" target="_blank" class="whatsapp-btn">2. 💬 ENVIAR POR WHATSAPP</a>', unsafe_allow_html=True)
        except Exception as e: st.error(f"ERROR: {e}")
    else: st.error("⚠️ DATOS INCOMPLETOS")
