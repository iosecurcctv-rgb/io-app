import streamlit as st
import pandas as pd
from streamlit_drawable_canvas import st_canvas
from datetime import datetime, timedelta
from fpdf import FPDF
import base64
from PIL import Image
import io
import urllib.parse

# 1. CONFIGURACIÓN E IDENTIDAD VISUAL RELAJADA
st.set_page_config(page_title="IO SECURITY - Control Maestro", page_icon="🛡️", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #111418; color: #D1D5DB; }
    h1, h2, h3 { color: #50C878 !important; font-family: 'Segoe UI', sans-serif; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3.5em; background-color: #1F2937; color: #50C878; border: 1px solid #50C878; font-weight: bold; transition: 0.3s; }
    .stButton>button:hover { background-color: #50C878; color: #111418; box-shadow: 0 0 10px #50C878; }
    .whatsapp-btn { display: inline-block; padding: 14px; border-radius: 8px; color: white !important; background-color: #2E7D32; text-decoration: none; font-weight: bold; text-align: center; width: 100%; margin-top: 10px; }
    .download-btn { display: inline-block; padding: 14px; border-radius: 8px; color: white !important; background-color: #374151; text-decoration: none; font-weight: bold; text-align: center; width: 100%; margin-top: 10px; border: 1px solid #4B5563; }
    </style>
    """, unsafe_allow_html=True)

# MOSTRAR LOGO
col_logo, _ = st.columns([1, 2])
with col_logo:
    try: st.image('logo.png', width=220)
    except: st.title("🛡️ IO SECURITY")

# 2. CONEXIÓN BLINDADA
URL_CATALOGO_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRopR4hg_DfWvNF919M9udZI738JSGiUljkyW02hc3gtcjoN869W3duYOR6VInie_fNvC5kXoByTrCm/pub?gid=596039047&single=true&output=csv"

try:
    df_catalogo = pd.read_csv(URL_CATALOGO_CSV)
    df_catalogo.columns = df_catalogo.columns.str.strip() 
except Exception as e:
    st.error("⚠️ Error al conectar con el catálogo.")
    st.stop()

# 3. FUNCIÓN GENERADORA DE PDF (CON CANTIDADES)
def generar_pdf_io(cliente, items_finales, total, tipo, firma_cli_data, firma_prov_data, fecha_p, notas):
    pdf = FPDF()
    pdf.add_page()
    try: pdf.image('logo.png', 10, 8, 33)
    except: pdf.set_font('Arial', 'B', 16); pdf.cell(0, 10, 'IO SECURITY', ln=True)
    
    pdf.set_font('Arial', 'B', 14); pdf.cell(0, 10, f'CONTRATO DE {tipo.upper()}', ln=True, align='R')
    pdf.set_font('Arial', '', 10); pdf.cell(0, 5, f'Emisión: {datetime.now().strftime("%d/%m/%Y")}', ln=True, align='R')
    pdf.ln(10)

    pdf.set_font('Arial', 'B', 11); pdf.cell(0, 7, f'CLIENTE: {cliente}', ln=True)
    pdf.set_font('Arial', '', 10); pdf.cell(0, 5, f'FECHA DE EJECUCIÓN: {fecha_p.strftime("%d/%m/%Y")}', ln=True)
    pdf.ln(5)

    # Tabla con Cantidad
    pdf.set_fill_color(0, 0, 0); pdf.set_text_color(255, 255, 255)
    pdf.cell(20, 8, ' Cant.', 1, 0, 'C', True)
    pdf.cell(120, 8, ' Descripción del Sistema', 1, 0, 'L', True)
    pdf.cell(50, 8, 'Total Concepto ', 1, 1, 'C', True)
    
    pdf.set_text_color(0, 0, 0); pdf.set_font('Arial', '', 10)
    for item in items_finales:
        pdf.cell(20, 10, f" {item['Cantidad']}", 1, 0, 'C')
        pdf.cell(120, 10, f" {item['Concepto']}", 1)
        pdf.cell(50, 10, f"$ {item['Subtotal_Final']:,}.00 ", 1, 1, 'R')
    
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(140, 12, ' TOTAL NETO A PAGAR', 1, 0, 'L')
    pdf.cell(50, 12, f"$ {total:,.2f} ", 1, 1, 'R')
    
    pdf.ln(10); pdf.set_font('Arial', 'B', 9); pdf.cell(0, 5, 'CLÁUSULAS DE SEGURIDAD:', ln=True)
    pdf.set_font('Arial', '', 8)
    clausulas = ["1. Sistema probado a conformidad.", "2. Exclusión por fallas de Internet/Luz.", "3. Garantía de 1 año (No aplica descargas eléctricas)."]
    for c in clausulas: pdf.cell(0, 4, c, ln=True)

    if firma_cli_data is not None and firma_prov_data is not None:
        y_firma = pdf.get_y() + 15
        img_cli = Image.fromarray(firma_cli_data.astype('uint8'), 'RGBA')
        img_prov = Image.fromarray(firma_prov_data.astype('uint8'), 'RGBA')
        pdf.image(img_cli, 20, y_firma, 50, 25)
        pdf.image(img_prov, 120, y_firma, 50, 25)
        pdf.set_y(y_firma + 25); pdf.set_font('Arial', 'B', 9)
        pdf.cell(95, 7, 'FIRMA CLIENTE', 0, 0, 'C'); pdf.cell(95, 7, 'IVÁN ORTIZ (IO SECURITY)', 0, 1, 'C')

    return pdf.output(dest='S').encode('latin-1')

# 4. INTERFAZ
st.sidebar.title("🛡️ PANEL IO SECURITY")
tipo_servicio = st.sidebar.radio("Módulo:", ["Instalación CCTV", "Servicio Preventivo", "Mantenimiento"])

st.subheader(f"⚡ GESTIÓN: {tipo_servicio}")

with st.container():
    c1, c2 = st.columns(2)
    with c1:
        nom = st.text_input("Nombre Completo")
        tel = st.text_input("WhatsApp (10 dígitos)")
        f_p = st.date_input("Fecha Programada", value=datetime.now() + timedelta(days=1))
        
    with c2:
        mats_seleccionados = st.multiselect("Equipos a Instalar:", df_catalogo['Producto'].tolist())
        mano_obra = st.number_input("Mano de Obra Total ($)", min_value=0, value=1500)

    # MODULO DE CANTIDADES
    items_pdf = []
    total_final = 0.0
    
    if mats_seleccionados:
        st.markdown("### 🔢 Cantidades y Ajustes")
        # Diccionario para guardar cantidades
        cantidades = {}
        # Prorrateo de mano de obra
        extra_unitario = mano_obra / len(mats_seleccionados)
        
        for prod in mats_seleccionados:
            col_a, col_b = st.columns([1, 3])
            with col_a:
                cant = st.number_input(f"Cant.", min_value=1, value=1, key=f"q_{prod}")
            with col_b:
                st.write(f"**{prod}**")
            
            # Obtener precio base
            precio_base = df_catalogo[df_catalogo['Producto'] == prod]['Precio'].values[0]
            # Precio con ganancia oculta
            p_con_ganancia = precio_base + extra_unitario
            subtotal = p_con_ganancia * cant
            
            items_pdf.append({
                "Cantidad": cant,
                "Concepto": prod,
                "Precio_Unit_Final": p_con_ganancia,
                "Subtotal_Final": subtotal
            })
            total_final += subtotal
            
    st.divider()
    st.metric("INVERSIÓN TOTAL", f"${total_final:,.2f}")
    obs = st.text_area("Notas Técnicas")

st.markdown("### ✍️ Panel de Firmas")
f1, f2 = st.columns(2)
with f1: canv_cli = st_canvas(stroke_width=2, stroke_color="#000", background_color="#FFFFFF", height=150, width=300, key="cli")
with f2: canv_prov = st_canvas(stroke_width=2, stroke_color="#000", background_color="#FFFFFF", height=150, width=300, key="prov")

if st.button("🚀 FINALIZAR Y GENERAR CONTRATO"):
    if canv_cli.image_data is not None and nom and tel:
        try:
            pdf_bytes = generar_pdf_io(nom, items_pdf, total_final, tipo_servicio, canv_cli.image_data, canv_prov.image_data, f_p, obs)
            b64 = base64.b64encode(pdf_bytes).decode()
            st.markdown(f'<a href="data:application/octet-stream;base64,{b64}" download="Contrato_{nom}.pdf" class="download-btn">📥 DESCARGAR CONTRATO PDF</a>', unsafe_allow_html=True)
            url_wa = f"https://wa.me/52{tel}?text=Hola {nom}, te envio el contrato de IO SECURITY."
            st.markdown(f'<a href="{url_wa}" target="_blank" class="whatsapp-btn">💬 ENVIAR POR WHATSAPP</a>', unsafe_allow_html=True)
            st.success("✅ ¡Listo!")
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.error("⚠️ Faltan datos o firmas.")
