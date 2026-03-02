import streamlit as st
import pandas as pd
from streamlit_drawable_canvas import st_canvas
from datetime import datetime, timedelta
from fpdf import FPDF
import base64
from PIL import Image
import io
import urllib.parse
import tempfile
import os

# 1. CONFIGURACIÓN E IDENTIDAD VISUAL (FORZADO TÉCNICO DE ICONO)
st.set_page_config(
    page_title="IO SECURITY - Control Maestro", 
    page_icon="logo.png", # Icono de pestaña
    layout="wide"
)

# Inyectar metadatos para que el celular reconozca el logo.png como icono de app oficial (?v=2)
st.markdown("""
    <head>
        <link rel="apple-touch-icon" href="logo.png?v=2">
        <link rel="icon" type="image/png" href="logo.png?v=2">
        <link rel="shortcut icon" href="logo.png?v=2">
    </head>
    <style>
    .stApp { background-color: #111418; color: #D1D5DB; }
    h1, h2, h3 { color: #50C878 !important; font-family: 'Segoe UI', sans-serif; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3.5em; background-color: #1F2937; color: #50C878; border: 1px solid #50C878; font-weight: bold; transition: 0.3s; }
    .stButton>button:hover { background-color: #50C878; color: #111418; box-shadow: 0 0 10px #50C878; }
    .whatsapp-btn { display: inline-block; padding: 14px; border-radius: 8px; color: white !important; background-color: #2E7D32; text-decoration: none; font-weight: bold; text-align: center; width: 100%; margin-top: 10px; }
    .download-btn { display: inline-block; padding: 14px; border-radius: 8px; color: white !important; background-color: #374151; text-decoration: none; font-weight: bold; text-align: center; width: 100%; margin-top: 10px; border: 1px solid #4B5563; }
    .streamlit-expanderHeader { background-color: #1F2937 !important; color: #50C878 !important; border: 1px solid #50C878; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# MOSTRAR LOGO EN INTERFAZ
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
    st.error(f"⚠️ Error al conectar con el catálogo: {e}")
    st.stop()

# 3. FUNCIÓN GENERADORA DE PDF (CORREGIDA CON REDONDEO Y TÍTULOS)
def generar_pdf_io(cliente, items_finales, total, tipo, subtipo, firma_cli_data, firma_prov_data, fecha_p, notas):
    pdf = FPDF()
    pdf.add_page()
    try: pdf.image('logo.png', 10, 8, 40)
    except: pdf.set_font('Arial', 'B', 16); pdf.cell(0, 10, 'IO SECURITY', ln=True)
    
    if tipo == "Mantenimiento":
        tit_doc = f"CONTRATO DE PRESTACION DE SERVICIOS: MANTENIMIENTO {subtipo.upper()}"
        garantia_ref = "6 meses"
    else:
        tit_doc = f"CONTRATO DE {tipo.upper()}"
        garantia_ref = "8 meses"

    pdf.set_font('Arial', 'B', 12); pdf.cell(0, 10, f'ORDEN DE SERVICIO', ln=True, align='R')
    pdf.set_font('Arial', '', 9); pdf.cell(0, 5, f'Fecha de Emision: {datetime.now().strftime("%d/%m/%Y")}', ln=True, align='R')
    pdf.ln(18)

    pdf.set_font('Arial', 'B', 11); pdf.cell(0, 7, tit_doc, ln=True, align='C')
    pdf.ln(4)
    pdf.set_font('Arial', '', 9)
    pdf.multi_cell(0, 5, f"Este contrato lo celebran, por una parte, IO SECURITY ('EL PRESTADOR'), y por la otra, {cliente} ('EL CLIENTE').")
    pdf.ln(2)

    pdf.set_fill_color(0, 0, 0); pdf.set_text_color(255, 255, 255); pdf.set_font('Arial', 'B', 9)
    pdf.cell(20, 8, ' Cant.', 1, 0, 'C', True)
    pdf.cell(120, 8, ' Descripcion del Servicio / Insumos', 1, 0, 'L', True)
    pdf.cell(50, 8, 'Total Concepto ', 1, 1, 'C', True)
    
    pdf.set_text_color(0, 0, 0); pdf.set_font('Arial', '', 9)
    for item in items_finales:
        pdf.cell(20, 9, f" {item['Cantidad']}", 1, 0, 'C')
        pdf.cell(120, 9, f" {item['Concepto']}", 1)
        pdf.cell(50, 9, f"$ {round(item['Subtotal_Final'], 2):,.2f} ", 1, 1, 'R')
    
    pdf.set_font('Arial', 'B', 9); pdf.cell(140, 9, ' TOTAL NETO A PAGAR', 1, 0, 'L'); pdf.cell(50, 9, f"$ {round(total, 2):,.2f} ", 1, 1, 'R')

    pdf.ln(4); pdf.set_font('Arial', 'B', 9); pdf.cell(0, 5, "CLAUSULA DE GARANTIAS", ln=True)
    pdf.set_font('Arial', '', 9); pdf.multi_cell(0, 4, f"- Refacciones/Equipos: {garantia_ref} contra defectos de fabrica.\n- Mano de Obra: 4 meses sobre el mantenimiento realizado.")
    
    pdf.ln(2); pdf.set_font('Arial', 'B', 9); pdf.cell(0, 5, "ANULACION Y COSTOS", ln=True)
    pdf.set_font('Arial', '', 8); pdf.multi_cell(0, 3.5, "La garantia se anula por manipulacion externa o daños electricos. Visitas tecnicas adicionales fuera de garantia: $250.00 MXN.")

    hoy = datetime.now()
    meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    txt_f = f"Ambas partes firman en Mineral de la Reforma, a los {hoy.day} dias del mes de {meses[hoy.month-1]} del año {hoy.year}."
    pdf.ln(4); pdf.set_font('Arial', 'I', 9); pdf.multi_cell(0, 5, txt_f)

    if firma_cli_data is not None and firma_prov_data is not None:
        y_f = pdf.get_y() + 10
        if y_f > 260: pdf.add_page(); y_f = 25
        def g_tmp(d):
            img = Image.fromarray(d.astype('uint8'), 'RGBA')
            t = tempfile.NamedTemporaryFile(delete=False, suffix=".png"); img.save(t.name); return t.name
        p1 = g_tmp(firma_cli_data); p2 = g_tmp(firma_prov_data)
        pdf.image(p1, 30, y_f, 50, 20); pdf.image(p2, 130, y_f, 50, 20)
        os.unlink(p1); os.unlink(p2)
        pdf.set_y(y_f + 20); pdf.set_font('Arial', 'B', 9)
        pdf.cell(95, 7, 'FIRMA CLIENTE', 0, 0, 'C'); pdf.cell(95, 7, 'IVAN ORTIZ (IO SECURITY)', 0, 1, 'C')

    return pdf.output(dest='S').encode('latin-1')

# 4. LÓGICA DE LA APP
st.sidebar.title("🛡️ PANEL IO SECURITY")
tipo_servicio = st.sidebar.radio("Tipo de Servicio:", ["Nueva Instalación CCTV", "Servicio IO Prevent", "Mantenimiento"])

sub_mant = "Preventivo"
if tipo_servicio == "Mantenimiento":
    sub_mant = st.sidebar.selectbox("Tipo de Mantenimiento:", ["Preventivo", "Correctivo"])

st.subheader(f"⚡ GESTIÓN: {tipo_servicio} {sub_mant if tipo_servicio == 'Mantenimiento' else ''}")

with st.container():
    c1, c2 = st.columns(2)
    with c1:
        nom = st.text_input("Nombre del Cliente")
        tel = st.text_input("WhatsApp (10 dígitos)")
        f_p = st.date_input("Fecha Programada", value=datetime.now() + timedelta(days=1))
    with c2:
        mats_seleccionados = st.multiselect("Materiales extra del catálogo:", df_catalogo['Producto'].tolist())
        mano_obra_manual = st.number_input("Mano de Obra Total a Prorratear ($)", min_value=0, value=0)

    items_pdf = []; total_final = 0.0

    if tipo_servicio == "Mantenimiento":
        with st.expander("🛠️ CONFIGURACIÓN TÉCNICA MANTENIMIENTO", expanded=True):
            m1, m2 = st.columns(2)
            with m1:
                c_mant = st.number_input("Cámaras a mantener", min_value=0, value=0)
                p_mant_base = st.number_input("Costo Mantenimiento unitario $", min_value=0, value=150)
                c_bal = st.number_input("Baluns a reemplazar", min_value=0, value=0)
                p_bal_base = st.number_input("Costo por par $", min_value=0, value=120)
            with m2:
                sel_dvr = st.selectbox("Limpieza DVR", ["Ninguna", "DVR 4 Canales", "DVR 8 Canales", "DVR 16 Canales", "Placa Madre"])
                costos_dvr = {"Ninguna": 0, "DVR 4 Canales": 250, "DVR 8 Canales": 350, "DVR 16 Canales": 450, "Placa Madre": 600}
                p_dvr_base = st.number_input("Costo Limpieza DVR $", value=costos_dvr[sel_dvr])

            serv_activos = (1 if c_mant > 0 else 0) + (1 if c_bal > 0 else 0) + (1 if p_dvr_base > 0 else 0)
            extra_por_concepto = round(mano_obra_total / serv_activos, 2) if serv_activos > 0 else 0

            if c_mant > 0:
                p_final = round((c_mant * p_mant_base) + extra_por_concepto, 2)
                items_pdf.append({"Cantidad": c_mant, "Concepto": "Mantenimiento preventivo a camara", "Subtotal_Final": p_final})
                total_final += p_final
            if c_bal > 0:
                p_final = round((c_bal * p_bal_base) + extra_por_concepto, 2)
                items_pdf.append({"Cantidad": c_bal, "Concepto": "Remplazo de transceptores (Baluns)", "Subtotal_Final": p_final})
                total_final += p_final
            if p_dvr_base > 0:
                p_final = round(p_dvr_base + extra_por_concepto, 2)
                items_pdf.append({"Cantidad": 1, "Concepto": f"Limpieza tecnica: {sel_dvr}", "Subtotal_Final": p_final})
                total_final += p_final

    if mats_seleccionados:
        with st.expander("📦 CANTIDADES DE MATERIALES", expanded=True):
            temp_data = {}; total_unidades_ganancia = 0
            for prod in mats_seleccionados:
                col_q, col_p = st.columns([1, 4])
                with col_q: q = st.number_input(f"Cant.", min_value=1, value=1, key=f"q_{prod}")
                with col_p: st.write(f"📦 **{prod}**")
                temp_data[prod] = q
                total_unidades_ganancia += q
            
            extra_unit_ins = round(mano_obra_total / total_unidades_ganancia, 2) if tipo_servicio != "Mantenimiento" and total_unidades_ganancia > 0 else 0
            
            for prod, q in temp_data.items():
                p_base = df_catalogo[df_catalogo['Producto'] == prod]['Precio'].values[0]
                sub = round((p_base + extra_unit_ins) * q, 2)
                items_pdf.append({"Cantidad": q, "Concepto": prod, "Subtotal_Final": sub})
                total_final += sub
            
    st.divider()
    total_final = round(total_final, 2)
    st.metric("TOTAL PARA EL CLIENTE", f"${total_final:,.2f}")
    obs = st.text_area("Notas Técnicas / Dirección")

st.markdown("### ✍️ Panel de Firmas (Usa la Papelera para borrar)")
f1, f2 = st.columns(2)
with f1: 
    canv_cli = st_canvas(stroke_width=2, stroke_color="#000", background_color="#FFFFFF", height=150, width=300, key="cli", drawing_mode="freedraw", display_toolbar=True)
    st.caption("Firma del Cliente")
with f2: 
    canv_prov = st_canvas(stroke_width=2, stroke_color="#000", background_color="#FFFFFF", height=150, width=300, key="prov", drawing_mode="freedraw", display_toolbar=True)
    st.caption("Firma de Iván Ortiz")

if st.button("🚀 GENERAR CONTRATO"):
    if canv_cli.image_data is not None and nom and tel:
        try:
            pdf_bytes = generar_pdf_io(nom, items_pdf, total_final, tipo_servicio, sub_mant, canv_cli.image_data, canv_prov.image_data, f_p, obs)
            b64 = base64.b64encode(pdf_bytes).decode()
            st.markdown(f'<a href="data:application/octet-stream;base64,{b64}" download="Contrato_{nom}.pdf" class="download-btn">📥 Descargar Contrato PDF</a>', unsafe_allow_html=True)
            
            msg = f"Hola {nom}, soy Ivan de IO SECURITY. Te envio tu contrato por el servicio de {tipo_servicio} ({sub_mant if tipo_servicio=='Mantenimiento' else ''}). Saludos."
            url_wa = f"https://wa.me/52{tel}?text={urllib.parse.quote(msg)}"
            st.markdown(f'<a href="{url_wa}" target="_blank" class="whatsapp-btn">💬 Compartir por WhatsApp</a>', unsafe_allow_html=True)
            st.success("✅ Documento generado.")
        except Exception as e: st.error(f"Error: {e}")
    else: st.error("⚠️ Completa datos y firmas.")
