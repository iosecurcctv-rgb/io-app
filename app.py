import streamlit as st
import pandas as pd
from streamlit_drawable_canvas import st_canvas
from datetime import datetime, timedelta
from fpdf import FPDF
import base64
from PIL import Image
import io
import urllib.parse

# 1. CONFIGURACIÓN E IDENTIDAD VISUAL MEJORADA
st.set_page_config(page_title="IO SECURITY - Control Maestro", page_icon="🛡️", layout="wide")

# Estilos CSS para un diseño tecnológico pero cómodo para la vista
st.markdown("""
    <style>
    /* Fondo oscuro relajado */
    .stApp { background-color: #111418; color: #D1D5DB; }
    
    /* Títulos en Verde Esmeralda Suave (menos lastimoso) */
    h1, h2, h3 { color: #50C878 !important; font-family: 'Segoe UI', sans-serif; letter-spacing: 1px; }
    
    /* Botones con estilo moderno */
    .stButton>button { width: 100%; border-radius: 8px; height: 3.5em; background-color: #1F2937; color: #50C878; border: 1px solid #50C878; font-weight: bold; transition: 0.3s; }
    .stButton>button:hover { background-color: #50C878; color: #111418; box-shadow: 0 0 10px #50C878; }
    
    /* Botones de acción final */
    .whatsapp-btn { display: inline-block; padding: 14px; border-radius: 8px; color: white; background-color: #2E7D32; text-decoration: none; font-weight: bold; text-align: center; width: 100%; margin-top: 10px; transition: 0.3s; }
    .whatsapp-btn:hover { background-color: #1B5E20; }
    
    .download-btn { display: inline-block; padding: 14px; border-radius: 8px; color: white; background-color: #374151; text-decoration: none; font-weight: bold; text-align: center; width: 100%; margin-top: 10px; border: 1px solid #4B5563; transition: 0.3s; }
    .download-btn:hover { border-color: #50C878; background-color: #4B5563; }

    /* Etiquetas de texto */
    .stMarkdown p { color: #ABB2BF; font-size: 1.05rem; }
    </style>
    """, unsafe_allow_html=True)

# MOSTRAR LOGO CENTRADO
col_logo, _ = st.columns([1, 2])
with col_logo:
    try:
        st.image('logo.png', width=220)
    except:
        st.title("🛡️ IO SECURITY")

# 2. CONEXIÓN BLINDADA (Link CSV Directo)
URL_CATALOGO_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRopR4hg_DfWvNF919M9udZI738JSGiUljkyW02hc3gtcjoN869W3duYOR6VInie_fNvC5kXoByTrCm/pub?gid=596039047&single=true&output=csv"

try:
    df_catalogo = pd.read_csv(URL_CATALOGO_CSV)
    df_catalogo.columns = df_catalogo.columns.str.strip() 
except Exception as e:
    st.error(f"⚠️ Error al conectar con el catálogo: {e}")
    st.stop()

# 3. FUNCIÓN GENERADORA DE PDF PROFESIONAL
def generar_pdf_io(cliente, items_finales, total, tipo, firma_cli, firma_prov, fecha_p, notas):
    pdf = FPDF()
    pdf.add_page()
    try: pdf.image('logo.png', 10, 8, 33)
    except: pdf.set_font('Arial', 'B', 16); pdf.cell(0, 10, 'IO SECURITY', ln=True)
    
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, f'CONTRATO DE {tipo.upper()}', ln=True, align='R')
    pdf.set_font('Arial', '', 10); pdf.cell(0, 5, f'Emisión: {datetime.now().strftime("%d/%m/%Y")}', ln=True, align='R')
    
    pdf.set_fill_color(240, 240, 240); pdf.ln(5)
    pdf.cell(0, 10, f' FECHA DE EJECUCIÓN PROGRAMADA: {fecha_p.strftime("%d/%m/%Y")}', 1, 1, 'L', True)
    pdf.ln(5)

    pdf.set_font('Arial', 'B', 11); pdf.cell(0, 7, f'CLIENTE: {cliente}', ln=True)
    pdf.set_font('Arial', '', 10); pdf.cell(0, 5, 'PRESTADOR: Iván Ortiz Perea | IO SECURITY', ln=True)
    pdf.ln(5)

    # Tabla de Conceptos
    pdf.set_fill_color(0, 0, 0); pdf.set_text_color(255, 255, 255)
    pdf.cell(140, 8, ' Descripción Técnica del Sistema', 1, 0, 'L', True)
    pdf.cell(50, 8, 'Inversión Unit. ', 1, 1, 'C', True)
    
    pdf.set_text_color(0, 0, 0); pdf.set_font('Arial', '', 10)
    for item in items_finales:
        pdf.cell(140, 10, f" {item['Concepto']}", 1)
        pdf.cell(50, 10, f"$ {item['Precio_Final']:,}.00 ", 1, 1, 'R')
    
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(140, 12, ' TOTAL NETO A PAGAR', 1, 0, 'L')
    pdf.cell(50, 12, f"$ {total:,.2f} ", 1, 1, 'R')
    
    pdf.ln(10); pdf.set_font('Arial', 'B', 9); pdf.cell(0, 5, 'CLÁUSULAS DE SEGURIDAD Y GARANTÍA:', ln=True)
    pdf.set_font('Arial', '', 8)
    clausulas = [
        "1. El sistema se entrega probado. El cliente acepta la recepción a conformidad técnica.",
        "2. IO SECURITY no responde por fallas en Internet o cortes eléctricos.",
        "3. La garantía de 1 año se anula por manipulación de terceros o variaciones de voltaje.",
        "4. Jurisdicción legal en Pachuca de Soto, Hidalgo."
    ]
    for c in clausulas: pdf.multi_cell(0, 4, c)

    if firma_cli is not None and firma_prov is not None:
        img_cli = Image.fromarray(firma_cli.astype('uint8'), 'RGBA')
        img_prov = Image.fromarray(firma_prov.astype('uint8'), 'RGBA')
        b_c, b_p = io.BytesIO(), io.BytesIO()
        img_cli.save(b_c, format='PNG'); img_prov.save(b_p, format='PNG')
        y = pdf.get_y() + 10
        pdf.image(b_c, 20, y, 50, 25); pdf.image(b_p, 120, y, 50, 25)
        pdf.set_y(y + 25); pdf.set_font('Arial', 'B', 9)
        pdf.cell(95, 7, 'FIRMA CLIENTE', 0, 0, 'C'); pdf.cell(95, 7, 'IVÁN ORTIZ (IO SECURITY)', 0, 1, 'C')

    return pdf.output(dest='S').encode('latin-1')

# 4. INTERFAZ EN ESPAÑOL
st.sidebar.title("🛡️ PANEL IO SECURITY")
tipo_servicio = st.sidebar.radio("Módulo de Servicio:", ["Instalación CCTV", "Servicio Preventivo", "Mantenimiento"])

st.subheader(f"⚡ SISTEMA DE GESTIÓN: {tipo_servicio}")

with st.container():
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### 👤 Datos del Cliente")
        nom = st.text_input("Nombre Completo")
        tel = st.text_input("WhatsApp (10 dígitos)")
        f_p = st.date_input("Fecha Programada", value=datetime.now() + timedelta(days=1))
        
    with c2:
        st.markdown("### 📦 Configuración de Equipos")
        mats_totales = st.multiselect("Seleccionar materiales del catálogo:", df_catalogo['Producto'].tolist())
        mats_para_ganancia = st.multiselect("Ocultar Mano de Obra en:", mats_totales)
        mano_obra_interna = st.number_input("Mano de Obra Oculta ($)", min_value=0, value=1500)

    # Lógica de cálculo de prorrateo
    df_base = df_catalogo[df_catalogo['Producto'].isin(mats_totales)].copy()
    items_pdf = []
    total_final = 0.0
    num_mats_ganancia = len(mats_para_ganancia)
    extra = mano_obra_interna / num_mats_ganancia if num_mats_ganancia > 0 else 0
    
    for _, row in df_base.iterrows():
        p_final = row['Precio']
        if row['Producto'] in mats_para_ganancia: p_final += extra
        items_pdf.append({"Concepto": row['Producto'], "Precio_Final": p_final})
        total_final += p_final
            
    st.markdown("---")
    st.metric("INVERSIÓN TOTAL DEL CLIENTE", f"${total_final:,.2f}", delta="Prorrateo Activo")
    obs = st.text_area("Observaciones y Notas Técnicas")

st.markdown("---")
st.markdown("### ✍️ Panel de Validación (Firmas)")
f1, f2 = st.columns(2)
with f1:
    st.write("Firma del Cliente")
    canv_cli = st_canvas(stroke_width=2, stroke_color="#000", background_color="#FFFFFF", height=150, width=300, key="cli")
with f2:
    st.write("Autorización IO SECURITY")
    canv_prov = st_canvas(stroke_width=2, stroke_color="#000", background_color="#FFFFFF", height=150, width=300, key="prov")

if st.button("🚀 FINALIZAR Y GENERAR CONTRATO"):
    if canv_cli.image_data is not None and nom and tel:
        pdf_data = generar_pdf_io(nom, items_pdf, total_final, tipo_servicio, canv_cli.image_data, canv_prov.image_data, f_p, obs)
        b64 = base64.b64encode(pdf_data).decode()
        st.markdown(f'<a href="data:application/octet-stream;base64,{b64}" download="Contrato_{nom}.pdf" class="download-btn">📥 DESCARGAR CONTRATO PDF</a>', unsafe_allow_html=True)
        msg = f"Hola {nom}, soy Iván de IO SECURITY. Te envío el contrato firmado de tu servicio."
        url_wa = f"https://wa.me/52{tel}?text={urllib.parse.quote(msg)}"
        st.markdown(f'<a href="{url_wa}" target="_blank" class="whatsapp-btn">💬 ENVIAR POR WHATSAPP</a>', unsafe_allow_html=True)
        st.success("✅ Documentación generada con éxito.")
    else:
        st.error("⚠️ Faltan datos críticos o firmas.")
