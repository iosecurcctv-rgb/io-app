import streamlit as st
import pandas as pd
from streamlit_drawable_canvas import st_canvas
from datetime import datetime, timedelta
from fpdf import FPDF
import base64
from PIL import Image
import io
import urllib.parse

# 1. CONFIGURACIÓN E IDENTIDAD
st.set_page_config(page_title="IO SECURITY - Control Maestro", page_icon="🛡️", layout="wide")

# Estilos de botones personalizados para IO SECURITY
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #1E1E1E; color: white; }
    .whatsapp-btn { display: inline-block; padding: 12px; border-radius: 5px; color: white; background-color: #25D366; text-decoration: none; font-weight: bold; text-align: center; width: 100%; margin-top: 10px; }
    .download-btn { display: inline-block; padding: 12px; border-radius: 5px; color: white; background-color: #444; text-decoration: none; font-weight: bold; text-align: center; width: 100%; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# MOSTRAR LOGO EN LA PÁGINA PRINCIPAL
try:
    st.image('logo.png', width=200)
except:
    st.title("🛡️ IO SECURITY")

# 2. CONEXIÓN BLINDADA (Usando tu URL de publicación CSV)
URL_CATALOGO_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRopR4hg_DfWvNF919M9udZI738JSGiUljkyW02hc3gtcjoN869W3duYOR6VInie_fNvC5kXoByTrCm/pub?gid=596039047&single=true&output=csv"

try:
    # Lectura directa del CSV para saltar errores de permisos
    df_catalogo = pd.read_csv(URL_CATALOGO_CSV)
    df_catalogo.columns = df_catalogo.columns.str.strip() 
except Exception as e:
    st.error(f"⚠️ Esperando señal del Catálogo IO SECURITY. Verifica que la hoja esté publicada. Error: {e}")
    st.stop()

# 3. FUNCIÓN GENERADORA DE PDF BLINDADO (ESTRATÉGICO PARA IVÁN ORTIZ)
def generar_pdf_io(cliente, items_finales, total, tipo, firma_cli, firma_prov, fecha_p, notas):
    pdf = FPDF()
    pdf.add_page()
    try: 
        pdf.image('logo.png', 10, 8, 33)
    except: 
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'IO SECURITY', ln=True)
    
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, f'CONTRATO DE {tipo.upper()}', ln=True, align='R')
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 5, f'Fecha de Emision: {datetime.now().strftime("%d/%m/%Y")}', ln=True, align='R')
    
    pdf.set_fill_color(235, 235, 235); pdf.ln(5)
    pdf.cell(0, 10, f' FECHA PROGRAMADA DE INSTALACION: {fecha_p.strftime("%d/%m/%Y")}', 1, 1, 'L', True)
    pdf.ln(5)

    pdf.set_font('Arial', 'B', 11); pdf.cell(0, 7, f'CLIENTE: {cliente}', ln=True)
    pdf.set_font('Arial', '', 10); pdf.cell(0, 5, 'PRESTADOR: Ivan Ortiz Perea | IO SECURITY', ln=True)
    pdf.ln(5)

    # Tabla de Conceptos (Precios prorrateados)
    pdf.set_fill_color(0, 0, 0); pdf.set_text_color(255, 255, 255)
    pdf.cell(140, 8, ' Descripcion del Sistema / Equipo Integrado', 1, 0, 'L', True)
    pdf.cell(50, 8, 'Precio Unitario ', 1, 1, 'C', True)
    
    pdf.set_text_color(0, 0, 0); pdf.set_font('Arial', '', 10)
    for item in items_finales:
        pdf.cell(140, 10, f" {item['Concepto']}", 1)
        pdf.cell(50, 10, f"$ {item['Precio_Final']:,}.00 ", 1, 1, 'R')
    
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(140, 12, ' TOTAL NETO A PAGAR', 1, 0, 'L')
    pdf.cell(50, 12, f"$ {total:,.2f} ", 1, 1, 'R')
    
    pdf.ln(10); pdf.set_font('Arial', 'B', 9); pdf.cell(0, 5, 'CLAUSULAS DE SEGURIDAD Y GARANTIA:', ln=True)
    pdf.set_font('Arial', '', 8)
    clausulas = [
        "1. El sistema se entrega probado. El cliente acepta la recepcion a conformidad tecnica.",
        "2. IO SECURITY no responde por fallas en Internet del cliente o cortes de suministro electrico.",
        "3. La garantia de 1 año se anula por manipulacion de terceros o variaciones de voltaje.",
        "4. Jurisdiccion legal en Pachuca de Soto, Hidalgo."
    ]
    for c in clausulas: pdf.multi_cell(0, 4, c)

    # Firmas Digitales
    if firma_cli is not None and firma_prov is not None:
        img_cli = Image.fromarray(firma_cli.astype('uint8'), 'RGBA')
        img_prov = Image.fromarray(firma_prov.astype('uint8'), 'RGBA')
        b_c, b_p = io.BytesIO(), io.BytesIO()
        img_cli.save(b_c, format='PNG'); img_prov.save(b_p, format='PNG')
        y = pdf.get_y() + 10
        pdf.image(b_c, 20, y, 50, 25); pdf.image(b_p, 120, y, 50, 25)
        pdf.set_y(y + 25); pdf.set_font('Arial', 'B', 9)
        pdf.cell(95, 7, 'FIRMA CLIENTE', 0, 0, 'C'); pdf.cell(95, 7, 'IVAN ORTIZ (IO SECURITY)', 0, 1, 'C')

    return pdf.output(dest='S').encode('latin-1')

# 4. LÓGICA DE LA APP - INTERFAZ PARA IVÁN
st.sidebar.title("IO SECURITY Master")
tipo_servicio = st.sidebar.radio("Tipo de Servicio:", ["Nueva Instalación CCTV", "Servicio IO Prevent", "Mantenimiento"])

st.header(f"🛡️ {tipo_servicio}")

with st.container():
    c1, c2 = st.columns(2)
    with c1:
        nom = st.text_input("Nombre del Cliente")
        tel = st.text_input("WhatsApp del Cliente (10 dígitos)")
        f_p = st.date_input("Fecha Programada para Instalación", value=datetime.now() + timedelta(days=1))
        mats_totales = st.multiselect("1. Seleccionar materiales:", df_catalogo['Producto'].tolist())
        mats_para_ganancia = st.multiselect("2. Seleccionar productos donde OCULTAR la mano de obra:", mats_totales)
        mano_obra_interna = st.number_input("Mano de Obra (Solo Ivan lo ve) $", min_value=0, value=1500)

    with c2:
        df_base = df_catalogo[df_catalogo['Producto'].isin(mats_totales)].copy()
        items_pdf = []
        total_final = 0.0
        
        num_mats_ganancia = len(mats_para_ganancia)
        extra = mano_obra_interna / num_mats_ganancia if num_mats_ganancia > 0 else 0
        
        for _, row in df_base.iterrows():
            p_final = row['Precio']
            if row['Producto'] in mats_para_ganancia:
                p_final += extra
            items_pdf.append({"Concepto": row['Producto'], "Precio_Final": p_final})
            total_final += p_final
            
        st.metric("TOTAL PARA EL CLIENTE", f"${total_final:,.2f}")
        obs = st.text_area("Observaciones adicionales")

st.divider()
st.subheader("✍️ Firmas Digitales")
f1, f2 = st.columns(2)
with f1:
    st.write("Firma del Cliente:")
    canv_cli = st_canvas(stroke_width=2, stroke_color="#000", background_color="#F0F0F0", height=150, width=300, key="cli")
with f2:
    st.write("Firma Ivan Ortiz (IO SECURITY):")
    canv_prov = st_canvas(stroke_width=2, stroke_color="#000", background_color="#F0F0F0", height=150, width=300, key="prov")

if st.button("🚀 GENERAR CONTRATO"):
    if canv_cli.image_data is not None and canv_prov.image_data is not None and nom and tel:
        pdf_data = generar_pdf_io(nom, items_pdf, total_final, tipo_servicio, canv_cli.image_data, canv_prov.image_data, f_p, obs)
        b64 = base64.b64encode(pdf_data).decode()
        st.markdown(f'<a href="data:application/octet-stream;base64,{b64}" download="Contrato_{nom}.pdf" class="download-btn">📥 1. Descargar Contrato PDF</a>', unsafe_allow_html=True)
        msg = f"Hola {nom}, soy Ivan de IO SECURITY. Te envio el contrato de tu instalacion para el dia {f_p.strftime('%d/%m/%Y')}."
        url_wa = f"https://wa.me/52{tel}?text={urllib.parse.quote(msg)}"
        st.markdown(f'<a href="{url_wa}" target="_blank" class="whatsapp-btn">💬 2. Enviar por WhatsApp</a>', unsafe_allow_html=True)
        st.success("¡Contrato generado!")
    else:
        st.error("Completa Nombre, Teléfono y ambas Firmas.")
