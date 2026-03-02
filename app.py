import streamlit as st
import pandas as pd
from streamlit_drawable_canvas import st_canvas
from datetime import datetime, timedelta
from fpdf import FPDF
import base64, tempfile, os, urllib.parse
from PIL import Image

# 1. CONFIGURACIÓN ÉLITE E IDENTIDAD (ICONO V3)
st.set_page_config(page_title="IO SECURITY", page_icon="logo.png", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0B0E14; color: #FFFFFF; font-family: 'Inter', sans-serif; }
    h1, h2, h3 { color: #00FF7F !important; text-shadow: 0 0 15px rgba(0, 255, 127, 0.4); font-weight: 800 !important; }
    label { font-size: 26px !important; color: #00FF7F !important; font-weight: bold !important; margin-bottom: 12px !important; }
    .stTextInput>div>div>input, .stNumberInput>div>div>input, .stTextArea>div>textarea, .stSelectbox>div>div>div {
        background-color: rgba(31, 41, 55, 0.8) !important; color: #FFFFFF !important; 
        border: 2px solid #00FF7F !important; border-radius: 12px !important; font-size: 22px !important; height: 65px !important;
    }
    .stButton>button { 
        width: 100%; border-radius: 15px; height: 5em; background: linear-gradient(135deg, #1F2937 0%, #0B0E14 100%);
        color: #00FF7F; border: 2px solid #00FF7F; font-weight: bold; font-size: 24px; transition: 0.3s all;
    }
    .success-box { padding: 30px; border-radius: 15px; background: rgba(0, 255, 127, 0.1); border: 2px solid #00FF7F; color: #FFFFFF; text-align: center; margin: 25px 0; font-size: 24px; font-weight: bold; }
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
try: df_cat = pd.read_csv(URL_CSV); df_cat.columns = df_cat.columns.str.strip()
except: st.error("⚠️ ERROR DE RED"); st.stop()

# 3. GENERADOR DE PDF (TEXTO LITERAL Y BLINDADO)
def generar_pdf_io(cli, items, total, tipo, f_ini, dom, notas, f_c_img, f_p_img, periodicidad=""):
    pdf = FPDF()
    pdf.add_page()
    hoy = datetime.now()
    meses_txt = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    empresa_full = "IO SECURITY CONSULTORIA INTEGRAL EN SISTEMAS DE SEGURIDAD"

    # FECHA DE EMISIÓN SUPERIOR
    pdf.set_font('Arial', '', 10); pdf.cell(0, 5, f"Fecha de Emision: {hoy.day} de {meses_txt[hoy.month-1]} de {hoy.year}", ln=True, align='R'); pdf.ln(10)
    try: pdf.image('logo.png', 10, 15, 35)
    except: pass
    pdf.ln(30) 
    
    if tipo == "Servicio IO Prevent":
        pdf.set_font('Arial', 'B', 12); pdf.cell(0, 10, 'CONTRATO DE SOPORTE TECNICO REMOTO', ln=True, align='C'); pdf.ln(5)
        pdf.set_font('Arial', '', 10); pdf.multi_cell(0, 5, f"De una parte, {empresa_full}, en adelante 'EL PRESTADOR'. Y de otra parte, {cli}, en adelante 'EL CLIENTE'.")
        pdf.ln(3); pdf.set_font('Arial', 'B', 10); pdf.cell(0, 5, "PRIMERA: OBJETO DEL SERVICIO", ln=True)
        pdf.set_font('Arial', '', 10); pdf.multi_cell(0, 5, "Monitoreo de salud del sistema de videovigilancia de manera exclusivamente remota."); pdf.ln(2)
        pdf.set_font('Arial', 'B', 10); pdf.cell(0, 5, "SEGUNDA: VIGENCIA", ln=True)
        m_v = 6 if periodicidad == "Semestral" else 12; f_fin = f_ini + timedelta(days=30*m_v)
        pdf.set_font('Arial', '', 10); pdf.multi_cell(0, 5, f"Vigencia {periodicidad.upper()}. Inicio: {f_ini.strftime('%d/%m/%Y')} - Termino: {f_fin.strftime('%d/%m/%Y')}."); pdf.ln(2)
        pdf.set_font('Arial', 'B', 10); pdf.cell(0, 5, "TERCERA: ALCANCE TECNICO LIMITADO", ln=True)
        pdf.set_font('Arial', '', 9); pdf.multi_cell(0, 4.5, "1) Verificacion de Grabacion mensual. 2) Soporte de Aplicacion Movil (Hasta 4 dispositivos)."); pdf.ln(2)
        pdf.set_font('Arial', 'B', 10); pdf.cell(0, 5, "CUARTA: EXCLUSIONES", ln=True)
        pdf.set_font('Arial', '', 9); pdf.multi_cell(0, 4.5, "No incluye visitas fisicas. Visita de emergencia: $200.00 MXN."); pdf.ln(2)
        pdf.set_font('Arial', 'B', 10); pdf.cell(0, 5, "SEPTIMA: HONORARIOS", ln=True)
        pdf.set_font('Arial', 'B', 10); pdf.cell(0, 7, f"COSTO TOTAL: ${total:,.2f} MXN (Pago en una exhibicion).", ln=True)
    else:
        pdf.set_font('Arial', 'B', 12); pdf.cell(0, 10, 'Contrato de Prestacion de Servicios de Instalacion', ln=True, align='C'); pdf.ln(5)
        pdf.set_font('Arial', '', 10); pdf.multi_cell(0, 5, f"Este contrato lo celebran, por una parte, {empresa_full}, en adelante 'EL PRESTADOR', y por la otra, {cli}, en adelante 'EL CLIENTE'.")
        pdf.ln(3); pdf.set_font('Arial', 'B', 10); pdf.cell(0, 5, "CLAUSULA PRIMERA: OBJETO DEL CONTRATO", ln=True)
        pdf.set_font('Arial', '', 10); pdf.multi_cell(0, 5, f"EL PRESTADOR se compromete a instalar y poner en funcionamiento un sistema de CCTV en el domicilio de EL CLIENTE, ubicado en {dom}. Detalle:")
        pdf.ln(2); pdf.set_fill_color(0, 0, 0); pdf.set_text_color(255, 255, 255); pdf.set_font('Arial', 'B', 9)
        pdf.cell(20, 8, ' Cant.', 1, 0, 'C', True); pdf.cell(120, 8, ' Descripcion del Servicio', 1, 0, 'L', True); pdf.cell(50, 8, 'Total Concepto', 1, 1, 'C', True)
        pdf.set_text_color(0, 0, 0); pdf.set_font('Arial', '', 10)
        for it in items:
            pdf.cell(20, 8, f" {it['Cantidad']}", 1, 0, 'C'); pdf.cell(120, 8, f" {it['Concepto']}", 1); pdf.cell(50, 8, f"$ {it['Subtotal_Final']:,.2f} ", 1, 1, 'R')
        pdf.ln(2); pdf.set_font('Arial', 'B', 10); pdf.cell(140, 8, ' TOTAL NETO A PAGAR', 1, 0, 'L'); pdf.cell(50, 8, f"$ {total:,.2f} ", 1, 1, 'R'); pdf.ln(4)
        
        pdf.set_font('Arial', 'B', 10); pdf.cell(0, 5, "CLAUSULA TERCERA: GARANTIAS", ln=True); pdf.set_font('Arial', '', 10)
        gar_v = "8 meses" if tipo == "Nueva Instalación CCTV" else "6 meses"
        pdf.multi_cell(0, 5, f"- Garantia de Equipos: {gar_v} contra defectos de fabrica.\n- Garantia de Mano de Obra: 4 meses sobre la instalacion."); pdf.ln(2)
        pdf.set_font('Arial', 'B', 10); pdf.cell(0, 5, "CLAUSULA QUINTA: ANULACION DE LA GARANTIA", ln=True); pdf.set_font('Arial', '', 9)
        pdf.multi_cell(0, 4.2, "Quedara anulada por: Manipulacion de terceros, Daños Electricos (voltaje), Daño Fisico (golpes), Mal Uso, Desastres Naturales o Problemas de Red externos."); pdf.ln(2)
        pdf.set_font('Arial', 'B', 10); pdf.cell(0, 5, "CLAUSULA SEXTA: COSTOS ADICIONALES", ln=True); pdf.set_font('Arial', '', 10)
        pdf.multi_cell(0, 5, "Visitas fuera de garantia tendran un costo de $250.00 MXN cubiertos al momento."); pdf.ln(2)
        pdf.set_font('Arial', 'B', 10); pdf.cell(0, 5, "CLAUSULA SEPTIMA: JURISDICCION", ln=True); pdf.set_font('Arial', '', 10)
        pdf.multi_cell(0, 5, "Las partes se someten a los tribunales de Mineral de la Reforma, Hgo.")

    pdf.ln(6); pdf.set_font('Arial', 'I', 10)
    pdf.multi_cell(0, 5, f"Firmado de conformidad en Mineral de la Reforma, a los {hoy.day} dias del mes de {meses_txt[hoy.month-1]} de {hoy.year}.")
    if f_c_img is not None:
        y_f = pdf.get_y() + 8
        def g_t(d):
            img = Image.fromarray(d.astype('uint8'), 'RGBA'); t = tempfile.NamedTemporaryFile(delete=False, suffix=".png"); img.save(t.name); return t.name
        p1 = g_t(f_c_img); p2 = g_t(f_p_img)
        pdf.image(p1, 30, y_f, 50, 20); pdf.image(p2, 130, y_f, 50, 20); os.unlink(p1); os.unlink(p2)
        pdf.set_y(y_f + 22); pdf.set_font('Arial', 'B', 8); pdf.cell(95, 7, 'EL CLIENTE', 0, 0, 'C'); pdf.cell(95, 7, 'IVAN ORTIZ (IO SECURITY)', 0, 1, 'C')
    return pdf.output(dest='S').encode('latin-1')

# 4. INTERFAZ OPERATIVA
st.sidebar.title("🛡️ OPERACIONES IO")
tipo = st.sidebar.radio("Módulo:", ["Nueva Instalación CCTV", "Servicio IO Prevent", "Mantenimiento"])
sub_m = st.sidebar.selectbox("Subtipo Mant.:", ["Preventivo", "Correctivo"]) if tipo == "Mantenimiento" else ""

with st.container():
    c1, c2 = st.columns(2)
    with c1:
        nom = st.text_input("👤 CLIENTE"); tel = st.text_input("📞 WHATSAPP (10 DIG)"); f_p = st.date_input("📅 FECHA INICIO")
    with c2:
        m_sel = st.multiselect("📦 MATERIALES CATÁLOGO:", df_cat['Producto'].tolist()) if tipo != "Servicio IO Prevent" else []
        m_total = st.number_input("💵 MANO DE OBRA / GANANCIA ($)", min_value=0.0)

    dom_input = st.text_input("🏠 DOMICILIO DEL CLIENTE")
    notas_input = st.text_area("📝 NOTAS ADICIONALES")

    items_pdf = []; total_final = 0.0; periodo_io = ""
    
    if tipo == "Servicio IO Prevent":
        periodo_io = st.sidebar.selectbox("Periodicidad:", ["Semestral", "Anual"])
        total_final = m_total
    
    elif tipo == "Mantenimiento":
        with st.expander("🛠️ CONFIGURACIÓN MANTENIMIENTO", expanded=True):
            col1, col2 = st.columns(2)
            c_m = col1.number_input("Cámaras", 0); p_m = col1.number_input("Precio Mant. $", 150)
            c_b = col1.number_input("Pares Baluns", 0); p_b = col1.number_input("Precio Par $", 120)
            sel_d = col2.selectbox("DVR", ["4 Can", "8 Can", "16 Can", "Placa Madre"])
            p_d_mnt = col2.number_input(f"Limpieza {sel_d} $", value={"4 Can": 250, "8 Can": 350, "16 Can": 450, "Placa Madre": 600}[sel_d])
            
            # LÓGICA DE PRORRATEO SELECTIVO PARA MANTENIMIENTO
            opc_mnt = []
            if c_m > 0: opc_mnt.append(f"Mantenimiento {c_m} Cam")
            if c_b > 0: opc_mnt.append(f"Baluns {c_b} Par")
            opc_mnt.append(f"Limpieza {sel_d}")
            
            m_prorr = st.multiselect("💰 PRORRATEAR GANANCIA EN:", opc_mnt)
            act = len(m_prorr); ex = round(m_total / act, 2) if act > 0 else 0
            
            if c_m > 0:
                v = round((c_m*p_m)+(ex if f"Mantenimiento {c_m} Cam" in m_prorr else 0), 2)
                items_pdf.append({"Cantidad": c_m, "Concepto": f"Mantenimiento {sub_m} Camara", "Subtotal_Final": v}); total_final += v
            if c_b > 0:
                v = round((c_b*p_b)+(ex if f"Baluns {c_b} Par" in m_prorr else 0), 2)
                items_pdf.append({"Cantidad": c_b, "Concepto": "Reemplazo de Baluns", "Subtotal_Final": v}); total_final += v
            
            v_d = round(p_d_mnt+(ex if f"Limpieza {sel_d}" in m_prorr else 0), 2)
            items_pdf.append({"Cantidad": 1, "Concepto": f"Limpieza tecnica {sel_d}", "Subtotal_Final": v_d}); total_final += v_d

    elif m_sel:
        with st.expander("📋 PRORRATEO INSTALACIÓN", expanded=True):
            m_gan = st.multiselect("💰 CARGAR GANANCIA EN:", m_sel)
            temp = {}; t_u = 0
            for p in m_sel:
                q = st.number_input(f"Cant. {p}", 1, key=f"q_{p}"); temp[p] = q
                if p in m_gan: t_u += q
            ex_i = round(m_total / t_u, 2) if t_u > 0 else 0
            for p, q in temp.items():
                base = df_cat[df_cat['Producto'] == p]['Precio'].values[0]
                sub = round((base + (ex_i if p in m_gan else 0)) * q, 2)
                items_pdf.append({"Cantidad": q, "Concepto": p, "Subtotal_Final": sub}); total_final += sub

    st.divider(); st.metric("VALOR TOTAL", f"${total_final:,.2f}")

st.markdown("### ✍️ FIRMAS DIGITALES")
f1, f2 = st.columns(2)
with f1: c_cli = st_canvas(stroke_width=3, stroke_color="#000", background_color="#FFFFFF", height=180, width=350, key="cli", display_toolbar=True)
with f2: c_prov = st_canvas(stroke_width=3, stroke_color="#000", background_color="#FFFFFF", height=180, width=350, key="prov", display_toolbar=True)

if st.button("🚀 FINALIZAR Y GENERAR EXPEDIENTE"):
    if c_cli.image_data is not None and nom and dom_input:
        try:
            pdf_b = generar_pdf_io(nom, items_pdf, total_final, tipo, f_p, dom_input, notas_input, c_cli.image_data, c_prov.image_data, periodo_io)
            st.markdown(f"<div class='success-box'>🔒 SISTEMA: CONTRATO DE {tipo.upper()} GENERADO CON ÉXITO.</div>", unsafe_allow_html=True)
            st.markdown(f'<a href="data:application/octet-stream;base64,{base64.b64encode(pdf_b).decode()}" download="Contrato_{nom}.pdf" class="download-btn">1. 📥 DESCARGAR CONTRATO</a>', unsafe_allow_html=True)
            msg = urllib.parse.quote(f"Hola {nom}, soy Ivan de IO SECURITY. Confirmo la generacion de su contrato {tipo}. Adjunto PDF.")
            st.markdown(f'<a href="https://wa.me/52{tel}?text={msg}" target="_blank" class="whatsapp-btn">2. 💬 ENVIAR POR WHATSAPP</a>', unsafe_allow_html=True)
        except Exception as e: st.error(f"ERROR: {e}")
    else: st.error("⚠️ REQUERIDO: Nombre, Domicilio y Firmas.")
