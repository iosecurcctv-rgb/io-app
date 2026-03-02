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
    </style>
    """, unsafe_allow_html=True)

col_logo, _ = st.columns([1, 2])
with col_logo:
    try: st.image('logo.png', width=280)
    except: st.title("🛡️ IO SECURITY")

# 2. CONEXIÓN AL CATÁLOGO
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRopR4hg_DfWvNF919M9udZI738JSGiUljkyW02hc3gtcjoN869W3duYOR6VInie_fNvC5kXoByTrCm/pub?gid=596039047&single=true&output=csv"
try: 
    df_catalogo = pd.read_csv(URL_CSV); df_catalogo.columns = df_catalogo.columns.str.strip() 
except: st.error("⚠️ ERROR DE RED"); st.stop()

# 3. GENERADOR DE PDF
def generar_pdf_io(cliente, items, total, tipo, f_cli, f_prov, f_p, domicilio, notas):
    pdf = FPDF()
    pdf.add_page()
    hoy = datetime.now()
    meses_txt = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    empresa_full = "IO SECURITY CONSULTORIA INTEGRAL EN SISTEMAS DE SEGURIDAD"

    # FECHA SUPERIOR DERECHA
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 5, f"Fecha de Emision: {hoy.day} de {meses_txt[hoy.month-1]} de {hoy.year}", ln=True, align='R')
    pdf.ln(5)

    # Logo sin encimarse
    try: pdf.image('logo.png', 10, 15, 35)
    except: pass
    pdf.ln(25) 
    
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Contrato de Prestacion de Servicios de Instalacion', ln=True, align='C')
    pdf.ln(2)

    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 5, f"Este contrato lo celebran, por una parte, {empresa_full}, en adelante 'EL PRESTADOR', y por la otra, {cliente}, en adelante 'EL CLIENTE'.")
    pdf.ln(3)

    pdf.set_font('Arial', 'B', 10); pdf.cell(0, 5, "CLAUSULA PRIMERA: OBJETO DEL CONTRATO", ln=True)
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 5, f"EL PRESTADOR se compromete a instalar y poner en funcionamiento un sistema de camaras de seguridad (CCTV) en el domicilio de EL CLIENTE, ubicado en {domicilio}. Los equipos se detallan a continuacion:")
    pdf.ln(2)

    # Tabla
    pdf.set_fill_color(0, 0, 0); pdf.set_text_color(255, 255, 255); pdf.set_font('Arial', 'B', 9)
    pdf.cell(20, 8, ' Cant.', 1, 0, 'C', True); pdf.cell(120, 8, ' Descripcion del Servicio / Insumos', 1, 0, 'L', True); pdf.cell(50, 8, 'Total Concepto ', 1, 1, 'C', True)
    pdf.set_text_color(0, 0, 0); pdf.set_font('Arial', '', 10)
    for it in items:
        pdf.cell(20, 8, f" {it['Cantidad']}", 1, 0, 'C'); pdf.cell(120, 8, f" {it['Concepto']}", 1); pdf.cell(50, 8, f"$ {it['Subtotal_Final']:,.2f} ", 1, 1, 'R')
    pdf.ln(2)

    pdf.set_font('Arial', 'B', 10); pdf.cell(0, 5, "CLAUSULA SEGUNDA: VIGENCIA Y COSTO DEL SERVICIO", ln=True)
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 5, f"El costo total por los equipos y la instalacion es de ${total:,.2f} MXN. La fecha de inicio del servicio sera el dia {f_p.strftime('%d/%m/%Y')}.")
    pdf.ln(3)

    pdf.set_font('Arial', 'B', 10); pdf.cell(0, 5, "CLAUSULA TERCERA: GARANTIAS", ln=True)
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 5, "- Garantia de Equipos: 8 meses.\n- Garantia de Mano de Obra: 4 meses.")
    pdf.ln(3)

    pdf.set_font('Arial', 'B', 10); pdf.cell(0, 5, "CLAUSULA QUINTA: ANULACION DE LA GARANTIA", ln=True)
    pdf.set_font('Arial', '', 9)
    pdf.multi_cell(0, 4.5, "Anulacion por: Manipulacion de terceros, Daños Electricos, Daño Fisico, Mal Uso o Problemas de Red.")
    pdf.ln(3)

    pdf.set_font('Arial', 'B', 10); pdf.cell(0, 5, "CLAUSULA SEXTA: COSTOS ADICIONALES", ln=True)
    pdf.set_font('Arial', '', 10); pdf.multi_cell(0, 5, "Visitas tecnicas fuera de garantia: $250.00 MXN.")
    
    if notas:
        pdf.ln(2); pdf.set_font('Arial', 'B', 10); pdf.cell(0, 5, "ANEXO: NOTAS ADICIONALES", ln=True)
        pdf.set_font('Arial', '', 9); pdf.multi_cell(0, 4.5, notas)

    pdf.ln(6)
    pdf.set_font('Arial', 'I', 10); pdf.multi_cell(0, 5, f"Firmado en Mineral de la Reforma, a los {hoy.day} dias de {meses_txt[hoy.month-1]} de {hoy.year}.")

    if f_cli is not None:
        y_f = pdf.get_y() + 8
        def g_t(d):
            img = Image.fromarray(d.astype('uint8'), 'RGBA'); t = tempfile.NamedTemporaryFile(delete=False, suffix=".png"); img.save(t.name); return t.name
        p1 = g_t(f_cli); p2 = g_t(f_prov)
        pdf.image(p1, 30, y_f, 50, 20); pdf.image(p2, 130, y_f, 50, 20); os.unlink(p1); os.unlink(p2)
        pdf.set_y(y_f + 22); pdf.set_font('Arial', 'B', 8); pdf.cell(95, 7, 'FIRMA DEL CONTRATANTE', 0, 0, 'C'); pdf.cell(95, 7, f'IVAN ORTIZ ({empresa_full})', 0, 1, 'C')
    
    return pdf.output(dest='S').encode('latin-1')

# 4. INTERFAZ
st.sidebar.title("🛡️ OPERACIONES IO")
tipo = st.sidebar.radio("Módulo:", ["Nueva Instalación CCTV", "Servicio IO Prevent", "Mantenimiento"])

with st.container():
    c1, c2 = st.columns(2)
    with c1:
        nom = st.text_input("👤 CLIENTE"); tel = st.text_input("📞 WHATSAPP (10 DIG)"); f_p = st.date_input("📅 FECHA INICIO")
    with c2:
        m_sel = st.multiselect("📦 MATERIALES:", df_catalogo['Producto'].tolist()) if tipo != "Servicio IO Prevent" else []
        m_total = st.number_input("💵 GANANCIA / MANO DE OBRA ($)", min_value=0.0)

    domicilio_i = st.text_input("🏠 DOMICILIO DEL CLIENTE")
    notas_i = st.text_area("📝 NOTAS ADICIONALES")

    items_pdf = []; total_final = 0.0
    if m_sel:
        with st.expander("📋 CONFIGURACIÓN DE PRORRATEO", expanded=True):
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
            
    st.divider(); st.metric("VALOR TOTAL", f"${total_final:,.2f}")

st.markdown("### ✍️ FIRMAS DIGITALES")
f1, f2 = st.columns(2)
with f1: canv_cli = st_canvas(stroke_width=3, stroke_color="#000", background_color="#FFFFFF", height=180, width=350, key="cli", display_toolbar=True)
with f2: canv_prov = st_canvas(stroke_width=3, stroke_color="#000", background_color="#FFFFFF", height=180, width=350, key="prov", display_toolbar=True)

if st.button("🚀 FINALIZAR Y GENERAR CONTRATO"):
    if canv_cli.image_data is not None and nom and domicilio_i:
        try:
            pdf_b = generar_pdf_io(nom, items_pdf, total_final, tipo, canv_cli.image_data, canv_prov.image_data, f_p, domicilio_i, notas_i)
            st.markdown(f"""<div class='success-box'>🔒 SISTEMA: CONTRATO GENERADO CON ÉXITO.</div>""", unsafe_allow_html=True)
            st.markdown(f'<a href="data:application/octet-stream;base64,{base64.b64encode(pdf_b).decode()}" download="Contrato_{nom}.pdf" class="download-btn">1. 📥 DESCARGAR CONTRATO</a>', unsafe_allow_html=True)
            msg = urllib.parse.quote(f"Hola {nom}, soy Ivan de IO SECURITY. Confirmamos la generacion de su contrato. Adjunto el PDF.")
            st.markdown(f'<a href="https://wa.me/52{tel}?text={msg}" target="_blank" class="whatsapp-btn">2. 💬 ENVIAR POR WHATSAPP</a>', unsafe_allow_html=True)
        except Exception as e: st.error(f"ERROR: {e}")
    else: st.error("⚠️ REQUERIDO: Nombre, Domicilio y Firmas.")
