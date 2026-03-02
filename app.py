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

# 1. CONFIGURACIÓN E IDENTIDAD VISUAL (ALTA VISIBILIDAD + ICONO FORZADO V3)
st.set_page_config(page_title="IO SECURITY - Control Maestro", page_icon="logo.png", layout="wide")

# Inyectar metadatos para el icono del celular y estilos de letras grandes
st.markdown("""
    <head>
        <link rel="apple-touch-icon" href="logo.png?v=3">
        <link rel="icon" type="image/png" href="logo.png?v=3">
        <link rel="shortcut icon" href="logo.png?v=3">
    </head>
    <style>
    /* Fondo oscuro y letras blancas grandes */
    .stApp { background-color: #111418; color: #FFFFFF; font-size: 20px; }
    
    /* Títulos Verde Neón Brillante */
    h1, h2, h3 { color: #00FF7F !important; font-family: 'Segoe UI', sans-serif; font-weight: bold !important; }
    
    /* Etiquetas de campos (Labels) GIGANTES y blancas */
    label { font-size: 22px !important; color: #FFFFFF !important; font-weight: bold !important; margin-bottom: 10px !important; }
    
    /* Campos de entrada con borde verde para verlos en el sol */
    .stTextInput>div>div>input, .stNumberInput>div>div>input, .stTextArea>div>textarea {
        background-color: #1F2937 !important; color: #FFFFFF !important; border: 2px solid #00FF7F !important; font-size: 20px !important;
    }
    
    /* Botones de acción reforzados */
    .stButton>button { 
        width: 100%; border-radius: 12px; height: 4.5em; background-color: #1F2937; 
        color: #00FF7F; border: 3px solid #00FF7F; font-weight: bold; font-size: 22px; 
    }
    .stButton>button:hover { background-color: #00FF7F; color: #111418; box-shadow: 0 0 15px #00FF7F; }
    
    /* Botones de descarga y whatsapp */
    .whatsapp-btn { display: inline-block; padding: 20px; border-radius: 12px; color: white !important; background-color: #2E7D32; text-decoration: none; font-weight: bold; text-align: center; width: 100%; font-size: 22px; border: 2px solid #FFFFFF; margin-top: 10px; }
    .download-btn { display: inline-block; padding: 20px; border-radius: 12px; color: white !important; background-color: #0277BD; text-decoration: none; font-weight: bold; text-align: center; width: 100%; margin-top: 10px; font-size: 22px; border: 2px solid #FFFFFF; }
    
    .streamlit-expanderHeader { background-color: #1F2937 !important; color: #00FF7F !important; border: 1px solid #00FF7F; border-radius: 8px; font-size: 20px !important; }
    </style>
    """, unsafe_allow_html=True)

# MOSTRAR LOGO
col_logo, _ = st.columns([1, 2])
with col_logo:
    try: st.image('logo.png', width=250)
    except: st.title("🛡️ IO SECURITY")

# 2. CONEXIÓN AL CATÁLOGO
URL_CATALOGO_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRopR4hg_DfWvNF919M9udZI738JSGiUljkyW02hc3gtcjoN869W3duYOR6VInie_fNvC5kXoByTrCm/pub?gid=596039047&single=true&output=csv"

try:
    df_catalogo = pd.read_csv(URL_CATALOGO_CSV)
    df_catalogo.columns = df_catalogo.columns.str.strip() 
except Exception as e:
    st.error(f"⚠️ Error al conectar con el catálogo: {e}")
    st.stop()

# 3. FUNCIÓN PDF CON TODAS LAS CLÁUSULAS LEGALES
def generar_pdf_io(cliente, items_finales, total, tipo, subtipo, firma_cli_data, firma_prov_data, fecha_p, notas):
    pdf = FPDF()
    pdf.add_page()
    try: pdf.image('logo.png', 10, 8, 40)
    except: pdf.set_font('Arial', 'B', 16); pdf.cell(0, 10, 'IO SECURITY', ln=True)
    
    gar_ref = "6 meses" if tipo == "Mantenimiento" else "8 meses"
    tit_doc = f"CONTRATO DE SERVICIO: {tipo.upper()} {subtipo.upper() if tipo=='Mantenimiento' else ''}"

    pdf.set_font('Arial', 'B', 12); pdf.cell(0, 10, f'ORDEN DE SERVICIO', ln=True, align='R')
    pdf.set_font('Arial', '', 9); pdf.cell(0, 5, f'Fecha: {datetime.now().strftime("%d/%m/%Y")}', ln=True, align='R'); pdf.ln(18)
    pdf.set_font('Arial', 'B', 11); pdf.cell(0, 7, tit_doc, ln=True, align='C'); pdf.ln(4)
    pdf.set_font('Arial', '', 9); pdf.multi_cell(0, 5, f"Este contrato lo celebran, por una parte, IO SECURITY ('EL PRESTADOR'), y por la otra, {cliente} ('EL CLIENTE')."); pdf.ln(2)

    # Tabla
    pdf.set_fill_color(0, 0, 0); pdf.set_text_color(255, 255, 255); pdf.set_font('Arial', 'B', 9)
    pdf.cell(20, 8, ' Cant.', 1, 0, 'C', True); pdf.cell(120, 8, ' Descripcion del Servicio / Insumos', 1, 0, 'L', True); pdf.cell(50, 8, 'Total Concepto ', 1, 1, 'C', True)
    pdf.set_text_color(0, 0, 0); pdf.set_font('Arial', '', 9)
    for item in items_finales:
        pdf.cell(20, 9, f" {item['Cantidad']}", 1, 0, 'C')
        pdf.cell(120, 9, f" {item['Concepto']}", 1)
        pdf.cell(50, 9, f"$ {round(item['Subtotal_Final'], 2):,.2f} ", 1, 1, 'R')
    pdf.set_font('Arial', 'B', 9); pdf.cell(140, 9, ' TOTAL NETO A PAGAR', 1, 0, 'L'); pdf.cell(50, 9, f"$ {round(total, 2):,.2f} ", 1, 1, 'R'); pdf.ln(5)

    # CLÁUSULAS LEGALES COMPLETAS
    pdf.set_font('Arial', 'B', 9); pdf.cell(0, 5, "CLAUSULA SEGUNDA: GARANTIAS", ln=True)
    pdf.set_font('Arial', '', 9); pdf.multi_cell(0, 4, f"- Refacciones/Equipos: {gar_ref} contra defectos de fabrica.\n- Mano de Obra: 4 meses sobre el trabajo realizado.")
    pdf.ln(2); pdf.set_font('Arial', 'B', 9); pdf.cell(0, 5, "CLAUSULA TERCERA: PROCESO DE GARANTIA", ln=True)
    pdf.set_font('Arial', '', 9); pdf.multi_cell(0, 4, "Reportar al 7711648186. Visita tecnica en un plazo maximo de 72 horas habiles.")
    pdf.ln(2); pdf.set_font('Arial', 'B', 9); pdf.cell(0, 5, "CLAUSULA CUARTA: ANULACION Y COSTOS", ln=True)
    pdf.set_font('Arial', '', 8); pdf.multi_cell(0, 3.5, "La garantia se anula por variaciones de voltaje, daño fisico o vandalismo. Visitas fuera de garantia: $250.00 MXN.")

    hoy = datetime.now(); meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    pdf.ln(4); pdf.set_font('Arial', 'I', 9); pdf.multi_cell(0, 5, f"Firmado en Mineral de la Reforma, a los {hoy.day} dias de {meses[hoy.month-1]} de {hoy.year}.")

    if firma_cli_data is not None:
        y_f = pdf.get_y() + 10
        if y_f > 250: pdf.add_page(); y_f = 25
        def g_tmp(d):
            img = Image.fromarray(d.astype('uint8'), 'RGBA')
            t = tempfile.NamedTemporaryFile(delete=False, suffix=".png"); img.save(t.name); return t.name
        p1 = g_tmp(firma_cli_data); p2 = g_tmp(firma_prov_data)
        pdf.image(p1, 30, y_f, 50, 20); pdf.image(p2, 130, y_f, 50, 20); os.unlink(p1); os.unlink(p2)
        pdf.set_y(y_f + 20); pdf.set_font('Arial', 'B', 9); pdf.cell(95, 7, 'FIRMA CLIENTE', 0, 0, 'C'); pdf.cell(95, 7, 'IVAN ORTIZ (IO SECURITY)', 0, 1, 'C')

    return pdf.output(dest='S').encode('latin-1')

# 4. LÓGICA DE LA APP
st.sidebar.title("🛡️ PANEL IO SECURITY")
tipo_servicio = st.sidebar.radio("Modulo de Trabajo:", ["Nueva Instalación CCTV", "Servicio IO Prevent", "Mantenimiento"])
sub_mant = st.sidebar.selectbox("Tipo de Mantenimiento:", ["Preventivo", "Correctivo"]) if tipo_servicio == "Mantenimiento" else "Instalacion"

st.subheader(f"⚡ GESTIÓN DE {tipo_servicio.upper()}")

with st.container():
    c1, c2 = st.columns(2)
    with c1:
        nom = st.text_input("👤 NOMBRE DEL CLIENTE")
        tel = st.text_input("📞 WHATSAPP (10 DÍGITOS)")
        f_p = st.date_input("📅 FECHA PROGRAMADA", value=datetime.now() + timedelta(days=1))
    with c2:
        mats_sel = st.multiselect("📦 1. SELECCIONAR MATERIALES:", df_catalogo['Producto'].tolist())
        # RESTAURADO: Prorrateo selectivo
        mats_para_ganancia = st.multiselect("💰 2. OCULTAR GANANCIA EN:", mats_sel)
        mano_obra_total = st.number_input("💵 MANO DE OBRA TOTAL ($)", min_value=0, value=0)

    items_pdf = []; total_final = 0.0

    # LÓGICA MANTENIMIENTO TÉCNICO
    if tipo_servicio == "Mantenimiento":
        with st.expander("🛠️ CONFIGURACIÓN TÉCNICA MANTENIMIENTO", expanded=True):
            m1, m2 = st.columns(2)
            with m1:
                c_mant = st.number_input("Cámaras", 0); p_mant_base = st.number_input("Precio Mant unitario $", 0, 150)
                c_bal = st.number_input("Baluns", 0); p_bal_base = st.number_input("Precio par Balun $", 0, 120)
            with m2:
                sel_dvr = st.selectbox("DVR", ["Ninguna", "DVR 4 Canales", "DVR 8 Canales", "DVR 16 Canales", "Placa Madre"])
                costos_dvr = {"Ninguna": 0, "DVR 4 Canales": 250, "DVR 8 Canales": 350, "DVR 16 Canales": 450, "Placa Madre": 600}
                p_dvr_base = st.number_input("Costo Limpieza DVR $", value=costos_dvr[sel_dvr])

            serv_activos = (1 if c_mant > 0 else 0) + (1 if c_bal > 0 else 0) + (1 if p_dvr_base > 0 else 0)
            extra_oculto = round(mano_obra_total / serv_activos, 2) if serv_activos > 0 else 0

            if c_mant > 0:
                v = round((c_mant * p_mant_base) + extra_oculto, 2)
                items_pdf.append({"Cantidad": c_mant, "Concepto": f"Mantenimiento {sub_mant} a camara", "Subtotal_Final": v}); total_final += v
            if c_bal > 0:
                v = round((c_bal * p_bal_base) + extra_oculto, 2)
                items_pdf.append({"Cantidad": c_bal, "Concepto": "Remplazo de Baluns", "Subtotal_Final": v}); total_final += v
            if p_dvr_base > 0:
                v = round(p_dvr_base + extra_oculto, 2)
                items_pdf.append({"Cantidad": 1, "Concepto": f"Limpieza tecnica: {sel_dvr}", "Subtotal_Final": v}); total_final += v

    # LÓGICA INSTALACIÓN Y PRORRATEO SELECTIVO
    if mats_sel:
        with st.expander("📋 CANTIDADES Y COSTOS MATERIALES", expanded=True):
            temp = {}; total_u_gan = 0
            for p in mats_sel:
                q = st.number_input(f"Cant. {p}", min_value=1, value=1, key=f"q_{p}"); temp[p] = q
                if p in mats_para_ganancia: total_u_gan += q
            
            ex_ins = round(mano_obra_total / total_u_gan, 2) if (total_u_gan > 0 and tipo_servicio != "Mantenimiento") else 0
            for p, q in temp.items():
                base = df_catalogo[df_catalogo['Producto'] == p]['Precio'].values[0]
                sub = round((base + (ex_ins if p in mats_para_ganancia else 0)) * q, 2)
                items_pdf.append({"Cantidad": q, "Concepto": p, "Subtotal_Final": sub}); total_final += sub
            
    st.divider(); st.metric("TOTAL A COBRAR", f"${total_final:,.2f}")
    obs = st.text_area("📝 NOTAS TÉCNICAS / DIRECCIÓN")

st.markdown("### ✍️ Panel de Firmas (Usa la Papelera para borrar)")
f1, f2 = st.columns(2)
with f1: canv_cli = st_canvas(stroke_width=2, stroke_color="#000", background_color="#FFFFFF", height=150, width=300, key="cli", display_toolbar=True)
with f2: canv_prov = st_canvas(stroke_width=2, stroke_color="#000", background_color="#FFFFFF", height=150, width=300, key="prov", display_toolbar=True)

if st.button("🚀 GENERAR CONTRATO"):
    if canv_cli.image_data is not None and nom and tel:
        try:
            pdf_b = generar_pdf_io(nom, items_pdf, total_final, tipo_servicio, sub_mant, canv_cli.image_data, canv_prov.image_data, f_p, obs)
            st.markdown(f'<a href="data:application/octet-stream;base64,{base64.b64encode(pdf_b).decode()}" download="Contrato_{nom}.pdf" class="download-btn">1. 📥 DESCARGAR PDF</a>', unsafe_allow_html=True)
            msg = urllib.parse.quote(f"Hola {nom}, soy Ivan de IO SECURITY. Te envio tu contrato por el servicio. Por favor adjunta el PDF que te acabo de enviar.")
            st.markdown(f'<a href="https://wa.me/52{tel}?text={msg}" target="_blank" class="whatsapp-btn">2. 💬 COMPARTIR POR WHATSAPP</a>', unsafe_allow_html=True)
        except Exception as e: st.error(f"Error: {e}")
    else: st.error("⚠️ Completa Nombre, WhatsApp y Firmas.")
