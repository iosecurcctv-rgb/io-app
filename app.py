import streamlit as st
import pandas as pd
from streamlit_drawable_canvas import st_canvas
from datetime import datetime, timedelta
from fpdf import FPDF
import base64, tempfile, os, urllib.parse
from PIL import Image

# 1. CONFIGURACIÓN E IDENTIDAD (ICONO FORZADO V3)
st.set_page_config(page_title="IO SECURITY", page_icon="logo.png", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0B0E14; color: #FFFFFF; font-family: 'Inter', sans-serif; }
    h1, h2, h3 { color: #00FF7F !important; text-shadow: 0 0 10px rgba(0, 255, 127, 0.4); font-weight: 800 !important; }
    label { font-size: 26px !important; color: #00FF7F !important; font-weight: bold !important; margin-bottom: 12px !important; }
    .stTextInput>div>div>input, .stNumberInput>div>div>input, .stTextArea>div>textarea, .stSelectbox>div>div>div {
        background-color: rgba(31, 41, 55, 0.8) !important; color: #FFFFFF !important; 
        border: 2px solid #00FF7F !important; border-radius: 12px !important; font-size: 22px !important; height: 65px !important;
    }
    .stButton>button { 
        width: 100%; border-radius: 15px; height: 5em; background: linear-gradient(135deg, #1F2937 0%, #0B0E14 100%);
        color: #00FF7F; border: 2px solid #00FF7F; font-weight: bold; font-size: 24px; transition: 0.3s all;
    }
    .stButton>button:hover { box-shadow: 0 0 25px #00FF7F; background-color: #00FF7F; color: #111418; }
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
    st.error("⚠️ ERROR DE RED"); st.stop()

# 3. GENERADOR DE PDF DINÁMICO
def generar_pdf_io(cliente, items, total, tipo, periodo, tec, n_cam, canales, f_cli, f_prov, f_p, notas):
    pdf = FPDF()
    pdf.add_page()
    
    # Logo sin encimarse
    try: pdf.image('logo.png', 10, 8, 35)
    except: pass
    
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Contrato de Prestacion de Servicios de Instalacion', ln=True, align='C')
    pdf.ln(12) 

    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 5, f"Este contrato lo celebran, por una parte, IO SECURITY, en adelante 'EL PRESTADOR', y por la otra, {cliente}, en adelante 'EL CLIENTE'.")
    pdf.ln(3)

    # CLÁUSULA PRIMERA DINÁMICA (Usa la dirección ingresada en el formulario)
    pdf.set_font('Arial', 'B', 10); pdf.cell(0, 5, "CLÁUSULA PRIMERA: OBJETO DEL CONTRATO", ln=True)
    pdf.set_font('Arial', '', 10)
    domicilio_cliente = notas if notas else "[DOMICILIO NO ESPECIFICADO]"
    pdf.multi_cell(0, 5, f"EL PRESTADOR se compromete a instalar y poner en funcionamiento un sistema de cámaras de seguridad (CCTV) en el domicilio de EL CLIENTE, ubicado en {domicilio_cliente}. Los equipos a instalar y los servicios a realizar se detallan a continuación:")
    pdf.ln(2)

    # Tabla de Equipos
    pdf.set_fill_color(0, 0, 0); pdf.set_text_color(255, 255, 255); pdf.set_font('Arial', 'B', 9)
    pdf.cell(20, 8, ' Cant.', 1, 0, 'C', True); pdf.cell(120, 8, ' Descripcion del Servicio / Insumos', 1, 0, 'L', True); pdf.cell(50, 8, 'Total Concepto ', 1, 1, 'C', True)
    pdf.set_text_color(0, 0, 0); pdf.set_font('Arial', '', 10)
    for it in items:
        pdf.cell(20, 8, f" {it['Cantidad']}", 1, 0, 'C'); pdf.cell(120, 8, f" {it['Concepto']}", 1); pdf.cell(50, 8, f"$ {it['Subtotal_Final']:,.2f} ", 1, 1, 'R')
    pdf.ln(2)

    pdf.set_font('Arial', 'B', 10); pdf.cell(0, 5, "CLÁUSULA SEGUNDA: VIGENCIA Y COSTO DEL SERVICIO", ln=True)
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 5, f"El costo total por los equipos y la instalación es de ${total:,.2f} MXN. La fecha de inicio del servicio será el día {f_p.strftime('%d/%m/%Y')}, y su finalización se estima para el mismo día.")
    pdf.ln(3)

    pdf.set_font('Arial', 'B', 10); pdf.cell(0, 5, "CLÁUSULA TERCERA: GARANTÍAS", ln=True)
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 5, "- Garantía de Equipos: Se otorga una garantía de 8 meses a partir de la fecha de instalación contra cualquier defecto de fabricación de los equipos (cámaras, DVR/NVR, discos duros, etc.).\n- Garantía de Mano de Obra: Se ofrece una garantía de 4 meses a partir de la fecha de instalación, que cubre cualquier falla o defecto relacionado con la instalación o configuración realizada por el personal de IO SECURITY.")
    pdf.ln(3)

    pdf.set_font('Arial', 'B', 10); pdf.cell(0, 5, "CLÁUSULA CUARTA: PROCESO PARA HACER VÁLIDA LA GARANTÍA", ln=True)
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 5, "Para iniciar un proceso de garantía, EL CLIENTE deberá notificar a EL PRESTADOR de la falla o defecto a través de una llamada telefónica al número 7711648186. IO SECURITY se compromete a dar una respuesta y programar una visita técnica en un plazo no mayor a 72 horas hábiles a partir de la recepción del aviso.")
    pdf.ln(3)

    pdf.set_font('Arial', 'B', 10); pdf.cell(0, 5, "CLÁUSULA QUINTA: ANULACIÓN DE LA GARANTÍA", ln=True)
    pdf.set_font('Arial', '', 9)
    pdf.multi_cell(0, 4.5, "Las garantías quedarán automáticamente anuladas por: Manipulación de personal ajeno a IO SECURITY, Daños Eléctricos (sobrecargas, descargas o variaciones de voltaje), Daño Físico (golpes o caídas), Mal Uso, Desastres Naturales o Problemas de Red de internet o dispositivos de red de EL CLIENTE.")
    pdf.ln(3)

    pdf.set_font('Arial', 'B', 10); pdf.cell(0, 5, "CLÁUSULA SEXTA: COSTOS ADICIONALES", ln=True)
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 5, "Se establece que cualquier visita técnica solicitada por EL CLIENTE que no sea por un motivo cubierto por las garantías tendrá un costo de $250.00 MXN. Este costo deberá ser cubierto por EL CLIENTE al momento de la visita.")
    pdf.ln(3)

    pdf.set_font('Arial', 'B', 10); pdf.cell(0, 5, "CLÁUSULA SÉPTIMA: JURISDICCIÓN Y LEY APLICABLE", ln=True)
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 5, "Para la interpretación y cumplimiento de este contrato, las partes se someten a la jurisdicción de los tribunales de la ciudad de Mineral de la reforma Hgo.")
    pdf.ln(5)

    # FECHA FINAL DINÁMICA
    hoy = datetime.now()
    meses_txt = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    pdf.set_font('Arial', 'I', 10)
    pdf.multi_cell(0, 5, f"Ambas partes leyeron este contrato, entienden su contenido y lo firman de conformidad en Mineral de la Reforma, a los {hoy.day} dias del mes de {meses_txt[hoy.month-1]} del año {hoy.year}.")

    if f_cli is not None:
        y_f = pdf.get_y() + 8
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

    items_pdf = []; total_final = 0.0
    periodo_io = st.sidebar.selectbox("Periodicidad Pago:", ["Semestral", "Anual"]) if tipo == "Servicio IO Prevent" else ""

    if m_sel:
        with st.expander("📋 PRORRATEO DE GANANCIA", expanded=True):
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
            
    st.divider(); st.metric("VALOR TOTAL DEL CONTRATO", f"${total_final:,.2f}")
    obs = st.text_area("🏠 DOMICILIO DEL CLIENTE / NOTAS")

st.markdown("### ✍️ FIRMAS DIGITALES")
f1, f2 = st.columns(2)
with f1: canv_cli = st_canvas(stroke_width=3, stroke_color="#000", background_color="#FFFFFF", height=180, width=350, key="cli", display_toolbar=True)
with f2: canv_prov = st_canvas(stroke_width=3, stroke_color="#000", background_color="#FFFFFF", height=180, width=350, key="prov", display_toolbar=True)

if st.button("🚀 FINALIZAR Y GENERAR EXPEDIENTE"):
    if canv_cli.image_data is not None and nom and tel:
        try:
            pdf_b = generar_pdf_io(nom, items_pdf, total_final, tipo, periodo_io, "", 0, "", canv_cli.image_data, canv_prov.image_data, f_p, obs)
            st.markdown(f"""<div class='success-box'>🔒 SISTEMA: CONTRATO GENERADO CON ÉXITO.<br>Expediente de {nom} listo para envío.</div>""", unsafe_allow_html=True)
            st.markdown(f'<a href="data:application/octet-stream;base64,{base64.b64encode(pdf_b).decode()}" download="Contrato_{nom}.pdf" class="download-btn">1. 📥 DESCARGAR CONTRATO</a>', unsafe_allow_html=True)
            msg = urllib.parse.quote(f"Hola {nom}, soy Ivan de IO SECURITY. Confirmamos la generacion de su contrato. Adjunto el archivo PDF.")
            st.markdown(f'<a href="https://wa.me/52{tel}?text={msg}" target="_blank" class="whatsapp-btn">2. 💬 ENVIAR POR WHATSAPP</a>', unsafe_allow_html=True)
        except Exception as e: st.error(f"ERROR: {e}")
    else: st.error("⚠️ DATOS INCOMPLETOS: Nombre, Teléfono y ambas Firmas son obligatorios.")
