import streamlit as st
import pandas as pd
from streamlit_drawable_canvas import st_canvas
from datetime import datetime, timedelta, time
from fpdf import FPDF
import base64, tempfile, os, urllib.parse, random
from PIL import Image

# --- NUEVO: IMPORTACIONES PARA EL CALENDARIO ---
import requests
import json
# -----------------------------------------------

# 1. IDENTIDAD Y ESTILO (INTACTO)
st.set_page_config(page_title="IO SECURITY", page_icon="logo.png", layout="wide")

st.markdown("""
    <head>
        <link rel="apple-touch-icon" href="logo.png?v=3">
        <link rel="shortcut icon" href="logo.png?v=3">
    </head>
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
    .stButton>button:hover { box-shadow: 0 0 25px #00FF7F; background-color: #00FF7F; color: #111418; }
    .success-box { padding: 30px; border-radius: 15px; background: rgba(0, 255, 127, 0.1); border: 2px solid #00FF7F; color: #FFFFFF; text-align: center; margin: 25px 0; font-size: 24px; font-weight: bold; }
    .whatsapp-btn { display: inline-block; padding: 22px; border-radius: 15px; color: white !important; background-color: #2E7D32; text-decoration: none; font-weight: bold; text-align: center; width: 100%; margin-top: 15px; font-size: 24px; border: 2px solid #FFFFFF; }
    .download-btn { display: inline-block; padding: 22px; border-radius: 15px; color: white !important; background-color: #0277BD; text-decoration: none; font-weight: bold; text-align: center; width: 100%; margin-top: 15px; border: 2px solid #FFFFFF; font-size: 24px; }
    .streamlit-expanderHeader { background-color: #1F2937 !important; color: #00FF7F !important; border: 1px solid #00FF7F; border-radius: 10px; font-size: 22px !important; }
    </style>
    """, unsafe_allow_html=True)

col_logo, _ = st.columns([1, 2])
with col_logo:
    try: 
        st.image('logo.png', width=280)
    except: 
        st.title("🛡️ IO SECURITY")

# 2. CONEXIÓN AL CATÁLOGO (INTACTA)
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRopR4hg_DfWvNF919M9udZI738JSGiUljkyW02hc3gtcjoN869W3duYOR6VInie_fNvC5kXoByTrCm/pub?gid=596039047&single=true&output=csv"
try: 
    df_cat = pd.read_csv(URL_CSV)
    df_cat.columns = df_cat.columns.str.strip()
except: 
    st.error("⚠️ ERROR DE RED")
    st.stop()

# FUNCIÓN PARA CONVERTIR NÚMEROS A LETRAS
def numero_a_letras(numero):
    unidades = ["", "UN", "DOS", "TRES", "CUATRO", "CINCO", "SEIS", "SIETE", "OCHO", "NUEVE", "DIEZ", "ONCE", "DOCE", "TRECE", "CATORCE", "QUINCE", "DIECISEIS", "DIECISIETE", "DIECIOCHO", "DIECINUEVE", "VEINTE", "VEINTIUN", "VEINTIDOS", "VEINTITRES", "VEINTICUATRO", "VEINTICINCO", "VEINTISEIS", "VEINTISIETE", "VEINTIOCHO", "VEINTINUEVE"]
    decenas = ["", "DIEZ", "VEINTE", "TREINTA", "CUARENTA", "CINCUENTA", "SESENTA", "SETENTA", "OCHENTA", "NOVENTA"]
    centenas = ["", "CIENTO", "DOSCIENTOS", "TRESCIENTOS", "CUATROCIENTOS", "QUINIENTOS", "SEISCIENTOS", "SETECIENTOS", "OCHOCIENTOS", "NOVECIENTOS"]

    def convertir_999(n):
        if n == 100: return "CIEN"
        if n == 0: return ""
        c = n // 100
        r = n % 100
        res = centenas[c] + " " if c > 0 else ""
        if r <= 29:
            res += unidades[r]
        else:
            d = r // 10
            u = r % 10
            res += decenas[d]
            if u > 0: res += " Y " + unidades[u]
        return res.strip()

    entero = int(numero)
    decimal = int(round((numero - entero) * 100))
    if entero == 0: return f"CERO PESOS {decimal:02d}/100 M.N."
    letras = ""
    miles = entero // 1000
    resto = entero % 1000
    if miles == 1: letras += "MIL "
    elif miles > 1: letras += convertir_999(miles) + " MIL "
    letras += convertir_999(resto)
    return f"{letras.strip()} PESOS {decimal:02d}/100 M.N."


# ---------------- MÓDULO: GENERADOR DE PDF PARA ANTICIPO (CON FIRMA DIGITAL) ----------------
def generar_pdf_anticipo(cli_nom, cli_email, cli_tel, cli_id, proy_nom, proy_desc, proy_ini, proy_plazo, proy_link, ant_fecha, ant_monto, ant_metodo, ant_ref, ant_total, ant_saldo, f_p_img):
    pdf = FPDF()
    pdf.add_page()
    
    # Encabezado
    try: 
        pdf.image('logo.png', 10, 10, 35)
    except: 
        pass
    
    pdf.set_font('Arial', 'B', 18)
    pdf.set_xy(50, 15)
    pdf.cell(0, 10, 'Confirmacion de Anticipo', 0, 1, 'R')
    
    pdf.set_y(50) 
    
    def dibujar_tabla(titulo, texto_previo, datos):
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 8, titulo, 0, 1, 'L')
        if texto_previo:
            pdf.set_font('Arial', '', 10)
            pdf.multi_cell(0, 5, texto_previo)
            pdf.ln(2)
            
        pdf.set_fill_color(164, 25, 25)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font('Arial', 'B', 10)
        
        pdf.cell(65, 7, 'Concepto', 1, 0, 'C', True)
        pdf.cell(125, 7, 'Detalle', 1, 1, 'C', True)
        
        pdf.set_text_color(0, 0, 0)
        for concepto, detalle in datos:
            pdf.set_font('Arial', 'B', 9) 
            pdf.cell(65, 7, f" {concepto}", 1, 0, 'L')
            pdf.set_font('Arial', '', 9)  
            pdf.cell(125, 7, f" {detalle}", 1, 1, 'L')
        pdf.ln(6)

    # 1. Detalles de la Empresa
    empresa_datos = [
        ("Nombre de la Empresa", "IO SECURITY CONSULTORIA INTEGRAL EN SISTEMAS DE SEGURIDAD"),
        ("Direccion", "Calle Alcatraz #206"),
        ("Correo Electronico", "info@iosecurity.com"),
        ("Telefono", "7711648186")
    ]
    dibujar_tabla("Detalles de la Empresa", "", empresa_datos)
    
    # 2. Información del Cliente
    cliente_datos = [
        ("Nombre del Cliente", cli_nom),
        ("Correo Electronico", cli_email),
        ("Telefono", cli_tel),
        ("Documento de Identidad/ID Fiscal", cli_id)
    ]
    dibujar_tabla("Informacion del Cliente", "Este documento sirve como confirmacion de la recepcion de un pago de anticipo por parte de nuestro cliente:", cliente_datos)
    
    # 3. Detalles del Proyecto
    proy_datos = [
        ("Nombre del Proyecto/Servicio", proy_nom),
        ("Descripcion Breve", proy_desc),
        ("Fecha de Inicio Estimada", proy_ini),
        ("Plazo de Entrega Estimado", proy_plazo),
        ("Enlace al Contrato/Propuesta", proy_link)
    ]
    dibujar_tabla("Detalles del Proyecto/Servicio", "El anticipo se aplica al siguiente proyecto o servicio acordado:", proy_datos)
    
    # Prevención de corte de página
    if pdf.get_y() > 220:
        pdf.add_page()
        
    # 4. Detalles del Anticipo
    ant_datos = [
        ("Fecha de Recepcion", ant_fecha),
        ("Monto del Anticipo", f"${ant_monto:,.2f} MXN"),
        ("Metodo de Pago", ant_metodo),
        ("Referencia de la Transaccion", ant_ref),
        ("Monto Total del Proyecto", f"${ant_total:,.2f} MXN"),
        ("Saldo Pendiente", f"${ant_saldo:,.2f} MXN")
    ]
    dibujar_tabla("Detalles del Anticipo Recibido", "A continuacion, se detallan los datos del anticipo recibido:", ant_datos)
    
    # 5. Declaración y Próximos Pasos 
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 8, "Declaracion y Proximos Pasos", 0, 1, 'L')
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 5, f"Confirmamos que el anticipo de ${ant_monto:,.2f} MXN ha sido recibido con exito, lo que nos permite proceder con la fase de {proy_nom}.")
    pdf.ln(2)
    pdf.multi_cell(0, 5, "Agradecemos su confianza en nuestra empresa. Si tiene alguna pregunta, no dude en contactarnos.")
    
    # FIRMA PROFESIONAL CON RECUADRO DIGITAL APLICADO
    pdf.ln(12)
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 5, "Atentamente,", 0, 1, 'C')
    
    y_firma = pdf.get_y() + 2
    if f_p_img is not None:
        def g_t(d):
            img = Image.fromarray(d.astype('uint8'), 'RGBA')
            t = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            img.save(t.name)
            return t.name
        p_img = g_t(f_p_img)
        # Centrar firma (Ancho hoja 210, Ancho firma 40 -> X = 85)
        pdf.image(p_img, 85, y_firma, 40, 15)
        os.unlink(p_img)
        
    pdf.ln(18)
    pdf.set_x(65)
    pdf.cell(80, 0, "", "T", 1, 'C') # Línea para firmar
    pdf.ln(2)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(0, 5, "Ing. Ivan Ortiz Perea", 0, 1, 'C')
    pdf.set_font('Arial', '', 9)
    pdf.cell(0, 4, "CEO", 0, 1, 'C')
    pdf.set_font('Arial', 'B', 8)
    pdf.cell(0, 4, "IO SECURITY CONSULTORIA INTEGRAL EN SISTEMAS DE SEGURIDAD", 0, 1, 'C')

    return pdf.output(dest='S').encode('latin-1')
# --------------------------------------------------------------------------------


# 3. GENERADOR DE PDF COTIZACIÓN (INTACTO)
def generar_pdf_cotizacion(cli, items, total_base, tel, email, iva_pct, anticipo_pct, folio):
    pdf = FPDF()
    pdf.add_page()
    hoy = datetime.now()
    
    pdf.set_fill_color(164, 25, 25) 
    pdf.rect(10, 10, 50, 25, 'FD')
    try: 
        pdf.image('logo.png', 12, 12, 46, 21)
    except: 
        pass
    
    pdf.rect(60, 10, 80, 25, 'D')
    pdf.set_xy(60, 12)
    pdf.set_font('Arial', 'B', 22)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(80, 8, 'COTIZACION', 0, 1, 'C')
    pdf.set_font('Arial', '', 8)
    pdf.set_x(60)
    pdf.cell(80, 4, 'Calle Alcatraz #206 Col. Tuzos', 0, 1, 'C')
    pdf.set_x(60)
    pdf.cell(80, 4, 'Email: iosecur.cctv@gmail.com   Tel: 7711648186', 0, 1, 'C')
    
    pdf.rect(140, 10, 60, 25, 'D')
    pdf.set_xy(140, 12)
    pdf.set_font('Arial', 'B', 9)
    pdf.cell(30, 10, 'FOLIO', 1, 0, 'C')
    pdf.set_text_color(255, 0, 0)
    pdf.cell(30, 10, str(folio), 1, 1, 'C')
    pdf.set_text_color(0, 0, 0)
    pdf.set_xy(140, 22)
    pdf.cell(30, 10, 'FECHA:', 1, 0, 'C')
    pdf.cell(30, 10, f"{hoy.day}/{hoy.month}/{hoy.year}", 1, 1, 'C')
    
    pdf.set_y(38)
    
    pdf.set_fill_color(164, 25, 25)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Arial', 'B', 9)
    pdf.cell(190, 6, 'COTIZACION', 1, 1, 'C', True)
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', 'B', 8)
    pdf.cell(15, 6, 'NOMBRE:', 1, 0, 'L')
    pdf.set_font('Arial', '', 8)
    pdf.cell(75, 6, cli, 1, 0, 'L')
    pdf.set_font('Arial', 'B', 8)
    pdf.cell(10, 6, 'TEL:', 1, 0, 'L')
    pdf.set_font('Arial', '', 8)
    pdf.cell(30, 6, tel, 1, 0, 'L')
    pdf.set_font('Arial', 'B', 8)
    pdf.cell(15, 6, 'EMAIL:', 1, 0, 'L')
    pdf.set_font('Arial', '', 8)
    pdf.cell(45, 6, email, 1, 1, 'L')
    
    pdf.ln(2)
    
    pdf.set_fill_color(164, 25, 25)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Arial', 'B', 8)
    pdf.cell(15, 6, 'CANT', 1, 0, 'C', True)
    pdf.cell(115, 6, 'DESCRIPCION', 1, 0, 'C', True)
    pdf.cell(30, 6, 'COSTO UNIT', 1, 0, 'C', True)
    pdf.cell(30, 6, 'SUBTOTAL', 1, 1, 'C', True)
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', '', 8)
    min_rows = 18
    for i in range(max(min_rows, len(items))):
        if i < len(items):
            it = items[i]
            pdf.cell(15, 6, str(it['Cantidad']), 1, 0, 'C')
            pdf.cell(115, 6, it['Concepto'], 1, 0, 'L')
            unit = it['Subtotal_Final'] / it['Cantidad'] if it['Cantidad'] > 0 else 0
            pdf.cell(30, 6, f"$ {unit:,.2f}", 1, 0, 'R')
            pdf.cell(30, 6, f"$ {it['Subtotal_Final']:,.2f}", 1, 1, 'R')
        else:
            pdf.cell(15, 6, '', 1, 0, 'C')
            pdf.cell(115, 6, '', 1, 0, 'L')
            pdf.cell(30, 6, '', 1, 0, 'R')
            pdf.cell(30, 6, '', 1, 1, 'R')
            
    pdf.ln(0) 
    y_tot = pdf.get_y()
    
    pdf.rect(10, y_tot, 130, 18)
    pdf.set_xy(12, y_tot + 2)
    pdf.set_font('Arial', '', 7)
    txt_leyenda = "En IO Security, nos dedicamos a ofrecer soluciones integrales para satisfacer las necesidades de tu negocio. Contamos con un amplio catalogo de productos y servicios, todos ellos cuidadosamente seleccionados para brindarte el mejor rendimiento y valor."
    pdf.multi_cell(126, 4, txt_leyenda, border=0)
    
    monto_iva = total_base * (iva_pct / 100.0)
    total_final = total_base + monto_iva

    pdf.set_xy(140, y_tot)
    pdf.set_font('Arial', 'B', 8)
    pdf.cell(25, 6, 'SUBTOTAL:', 1, 0, 'R')
    pdf.set_font('Arial', '', 8)
    pdf.cell(35, 6, f"$ {total_base:,.2f}", 1, 1, 'R')
    
    pdf.set_x(140)
    pdf.set_font('Arial', 'B', 8)
    pdf.cell(25, 6, 'IMPUESTOS:', 1, 0, 'R')
    pdf.set_font('Arial', '', 8)
    pdf.cell(35, 6, f"$ {monto_iva:,.2f}", 1, 1, 'R')
    
    pdf.set_x(140)
    pdf.set_font('Arial', 'B', 8)
    pdf.set_text_color(255,0,0)
    pdf.cell(25, 6, 'TOTAL:', 1, 0, 'R')
    pdf.set_text_color(0,0,0)
    pdf.set_font('Arial', 'B', 8)
    pdf.cell(35, 6, f"$ {total_final:,.2f}", 1, 1, 'R')
    
    pdf.set_y(y_tot + 18)
    pdf.set_font('Arial', 'B', 8)
    pdf.cell(190, 6, f'CANTIDAD CON LETRA: {numero_a_letras(total_final)}', 'L,T,R', 1, 'L')
    pdf.cell(40, 6, 'METODO DE PAGO:', 'L,B', 0, 'L')
    pdf.set_font('Arial', '', 8)
    pdf.cell(40, 6, '[   ] EFECTIVO', 'B', 0, 'C')
    pdf.cell(40, 6, '[   ] TARJETA', 'B', 0, 'C')
    pdf.cell(70, 6, '[   ] OTRO:', 'B,R', 1, 'L')
    
    pdf.ln(2)
    pdf.set_fill_color(164, 25, 25)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Arial', 'B', 8)
    pdf.cell(190, 6, 'CONSIDERACIONES', 1, 1, 'C', True)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', '', 8)
    txt_cons = f"Cotizacion con 20 dias de validez, a partir de la fecha elaborada. Se requiere de un anticipo del {anticipo_pct}% antes de la fecha de inicio de instalacion."
    pdf.cell(190, 6, txt_cons, 'L,R', 1, 'L')
    pdf.cell(190, 15, '', 'L,B,R', 1) 
    
    return pdf.output(dest='S').encode('latin-1')

# 3. GENERADOR DE PDF PARA CONTRATOS (INTACTO)
def generar_pdf_io(cli, items, total, tipo, sub_m, periodo, tec, n_cam, can, f_c_img, f_p_img, f_ini, dom, notas):
    pdf = FPDF()
    pdf.add_page()
    hoy = datetime.now()
    meses_txt = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    empresa_full = "IO SECURITY CONSULTORIA INTEGRAL EN SISTEMAS DE SEGURIDAD"

    pdf.set_font('Arial', 'B', 10)
    pdf.cell(0, 5, empresa_full, ln=True, align='C')
    pdf.set_font('Arial', '', 9)
    pdf.cell(0, 5, f"Fecha de Emision: {hoy.day} de {meses_txt[hoy.month-1]} de {hoy.year}", ln=True, align='R')
    pdf.ln(5)
    
    try: 
        pdf.image('logo.png', 10, 18, 35)
    except: 
        pass
        
    pdf.ln(32) 

    if tipo == "Servicio IO Prevent":
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'CONTRATO DE PRESTACION DE SERVICIO: "IO PREVENT"', ln=True, align='C')
        pdf.ln(5)
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(0, 7, "REUNIDOS", ln=True)
        pdf.set_font('Arial', '', 10)
        pdf.multi_cell(0, 5, f"De una parte, IO SECURITY, en adelante 'EL PRESTADOR'. Y de otra parte, {cli}, en adelante 'EL CLIENTE'. Ambas partes acuerdan celebrar el presente CONTRATO DE SOPORTE TÉCNICO REMOTO.")
        
        pdf.ln(2)
        pdf.set_fill_color(0, 0, 0)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font('Arial', 'B', 9)
        pdf.cell(140, 8, ' Descripcion del Equipo a Cubrir', 1, 0, 'L', True)
        pdf.cell(50, 8, 'Detalle', 1, 1, 'C', True)
        
        pdf.set_text_color(0, 0, 0)
        pdf.set_font('Arial', '', 9)
        pdf.cell(140, 8, f" Sistema de Videovigilancia {tec}", 1, 0, 'L')
        pdf.cell(50, 8, f"{n_cam} Camaras", 1, 1, 'C')
        pdf.cell(140, 8, f" Grabador Digital (DVR/NVR)", 1, 0, 'L')
        pdf.cell(50, 8, f"{can} Canales", 1, 1, 'C')

        pdf.ln(2)
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(0, 5, "CLAUSULAS", ln=True)
        pdf.ln(1)
        
        pdf.set_font('Arial', 'B', 9)
        pdf.cell(0, 5, "PRIMERA: OBJETO DEL SERVICIO", ln=True)
        pdf.set_font('Arial', '', 9)
        pdf.multi_cell(0, 4.5, "El presente contrato tiene como finalidad la prestacion de servicios de asistencia tecnica y monitoreo de salud del sistema de videovigilancia de manera exclusivamente remota. Este plan esta diseñado como una fase de prueba y aseguramiento digital para sistemas residenciales.")
        pdf.ln(1)
        
        pdf.set_font('Arial', 'B', 9)
        pdf.cell(0, 5, "SEGUNDA: VIGENCIA", ln=True)
        pdf.set_font('Arial', '', 9)
        f_t = f_ini + timedelta(days=365) 
        pdf.multi_cell(0, 4.5, f"La duracion de este contrato es de un (1) año a partir de la firma. \nFecha de Inicio: {f_ini.strftime('%d/%m/%Y')} \nFecha de Termino: {f_t.strftime('%d/%m/%Y')}")
        pdf.ln(1)
        
        pdf.set_font('Arial', 'B', 9)
        pdf.cell(0, 5, "TERCERA: ALCANCE TECNICO LIMITADO", ln=True)
        pdf.set_font('Arial', '', 9)
        pdf.multi_cell(0, 4.5, "Verificacion de Grabacion mensual y Soporte de Aplicacion Movil (Hasta 4 dispositivos).")
        pdf.ln(1)
        
        pdf.set_font('Arial', 'B', 9)
        pdf.cell(0, 5, "CUARTA: EXCLUSIONES", ln=True)
        pdf.set_font('Arial', '', 9)
        pdf.multi_cell(0, 4.5, "No incluye visitas fisicas ni refacciones. Visita fisica de emergencia: $200.00 MXN.")
        pdf.ln(1)
        
        pdf.set_font('Arial', 'B', 9)
        pdf.cell(0, 5, "SEPTIMA: HONORARIOS", ln=True)
        pdf.set_font('Arial', 'B', 10)
        if periodo == "Semestral":
            pdf.cell(0, 7, f"El costo total es de ${total:,.2f} MXN, cubierto en dos pagos semestrales de ${(total/2):,.2f} MXN.", ln=True)
        else:
            pdf.cell(0, 7, f"El costo total es de ${total:,.2f} MXN, cubierto en un pago anual de ${total:,.2f} MXN.", ln=True)

    else:
        tit_pdf = f"Contrato de Prestacion de Servicios de {tipo if tipo != 'Mantenimiento' else 'Mantenimiento ' + sub_m}"
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, tit_pdf, ln=True, align='C')
        pdf.ln(5)
        
        pdf.set_font('Arial', '', 10)
        pdf.multi_cell(0, 5, f"Este contrato lo celebran, por una parte, IO SECURITY, en adelante 'EL PRESTADOR', y por la otra, {cli}, en adelante 'EL CLIENTE'.")
        pdf.ln(3)

        pdf.set_font('Arial', 'B', 10)
        pdf.cell(0, 5, "CLAUSULA PRIMERA: OBJETO DEL CONTRATO", ln=True)
        pdf.set_font('Arial', '', 10)
        pdf.multi_cell(0, 5, f"EL PRESTADOR se compromete a instalar y poner en funcionamiento un sistema de camaras de seguridad (CCTV) en el domicilio de EL CLIENTE, ubicado en {dom}. Los equipos a instalar y los servicios a realizar se detallan en el Anexo 1, que forma parte integral de este contrato.")
        pdf.ln(2)

        pdf.set_font('Arial', 'B', 9)
        pdf.cell(0, 5, "ANEXO 1", ln=True)
        pdf.set_fill_color(0, 0, 0)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font('Arial', 'B', 9)
        pdf.cell(20, 8, ' Cant.', 1, 0, 'C', True)
        pdf.cell(120, 8, ' Descripcion', 1, 0, 'L', True)
        pdf.cell(50, 8, 'Total', 1, 1, 'C', True)
        
        pdf.set_text_color(0, 0, 0)
        pdf.set_font('Arial', '', 10)
        for it in items:
            pdf.cell(20, 8, f" {it['Cantidad']}", 1, 0, 'C')
            pdf.cell(120, 8, f" {it['Concepto']}", 1)
            pdf.cell(50, 8, f"$ {it['Subtotal_Final']:,.2f} ", 1, 1, 'R')
        pdf.ln(3)

        pdf.set_font('Arial', 'B', 10)
        pdf.cell(0, 5, "CLAUSULA SEGUNDA: VIGENCIA Y COSTO DEL SERVICIO", ln=True)
        pdf.set_font('Arial', '', 10)
        pdf.multi_cell(0, 5, f"El costo total por los equipos y la instalacion es de ${total:,.2f} MXN.\nLa fecha de inicio del servicio sera el dia {f_ini.strftime('%d/%m/%Y')}, y su finalizacion se estima para el mismo dia.")
        pdf.ln(3)

        pdf.set_font('Arial', 'B', 10)
        pdf.cell(0, 5, "CLAUSULA TERCERA: GARANTIAS", ln=True)
        pdf.set_font('Arial', '', 9)
        pdf.multi_cell(0, 4.5, "EL PRESTADOR ofrece las siguientes garantias, sujetas a las condiciones estipuladas en este documento:")
        gar_v = "8 meses" if tipo == "Nueva Instalación CCTV" else "6 meses"
        pdf.multi_cell(0, 4.5, f"- Garantia de Equipos: Se otorga una garantia de {gar_v} a partir de la fecha de instalacion contra cualquier defecto de fabricacion de los equipos (camaras, DVR/NVR, discos duros, etc.).\n- Garantia de Mano de Obra: Se ofrece una garantia de 4 meses a partir de la fecha de instalacion, que cubre cualquier falla o defecto relacionado con la instalacion o configuracion realizada por el personal de IO SECURITY.")
        pdf.ln(3)

        pdf.set_font('Arial', 'B', 10)
        pdf.cell(0, 5, "CLAUSULA CUARTA: PROCESO PARA HACER VALIDA LA GARANTIA", ln=True)
        pdf.set_font('Arial', '', 9)
        pdf.multi_cell(0, 4.5, "Para iniciar un proceso de garantia, EL CLIENTE debera notificar a EL PRESTADOR de la falla o defecto a traves de una llamada telefonica al numero 7711648186. IO SECURITY se compromete a dar una respuesta y programar una visita tecnica en un plazo no mayor a 72 horas habiles a partir de la recepcion del aviso.")
        pdf.ln(3)

        pdf.set_font('Arial', 'B', 10)
        pdf.cell(0, 5, "CLAUSULA QUINTA: ANULACION DE LA GARANTIA", ln=True)
        pdf.set_font('Arial', '', 9)
        pdf.multi_cell(0, 4.5, "Las garantias mencionadas en la Clausula Tercera quedaran automaticamente anuladas en las siguientes circunstancias:\n- Manipulacion: Cuando los equipos sean manipulados, reparados o intervenidos por personal ajeno a IO SECURITY.\n- Daños Electricos: Fallas o daños causados por sobrecargas, descargas o variaciones de voltaje en la red electrica del domicilio de EL CLIENTE.\n- Daño Fisico: Daños fisicos a los equipos, incluyendo, pero no limitandose a golpes, caidas o exposicion a condiciones ambientales extremas no contempladas para su uso.\n- Mal Uso: Uso indebido o diferente al proposito original de los equipos.\n- Desastres Naturales/Vandalismo: Daños ocasionados por desastres naturales (inundaciones, terremotos, incendios, etc.) o por actos de vandalismo.\n- Problemas de Red: Fallas derivadas de la red de internet o de los dispositivos de red de EL CLIENTE (routers, modems, etc.).")
        pdf.ln(3)

        pdf.set_font('Arial', 'B', 10)
        pdf.cell(0, 5, "CLAUSULA SEXTA: COSTOS ADICIONALES", ln=True)
        pdf.set_font('Arial', '', 9)
        pdf.multi_cell(0, 4.5, "Se establece que cualquier visita tecnica solicitada por EL CLIENTE que no sea por un motivo cubierto por las garantias (Clausula Tercera) tendra un costo de $250.00 MXN. Este costo debera ser cubierto por EL CLIENTE al momento de la visita.")
        pdf.ln(3)

        pdf.set_font('Arial', 'B', 10)
        pdf.cell(0, 5, "CLAUSULA SEPTIMA: JURISDICCION Y LEY APLICABLE", ln=True)
        pdf.set_font('Arial', '', 9)
        pdf.multi_cell(0, 4.5, "Para la interpretacion y cumplimiento de este contrato, las partes se someten a la jurisdiccion de los tribunales de la ciudad de Mineral de la reforma Hgo, renunciando a cualquier otro fuero que pudiera corresponderles por razon de sus domicilios presentes o futuros.")
        pdf.ln(5)

    pdf.set_font('Arial', 'I', 10)
    pdf.multi_cell(0, 5, f"Ambas partes leyeron este contrato, entienden su contenido y lo firman de conformidad en Mineral de la Reforma, a los {hoy.day} dias del mes de {meses_txt[hoy.month-1]} del año {hoy.year}.")
    
    if f_c_img is not None:
        y_f = pdf.get_y() + 8
        def g_t(d):
            img = Image.fromarray(d.astype('uint8'), 'RGBA')
            t = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            img.save(t.name)
            return t.name
        p1 = g_t(f_c_img)
        p2 = g_t(f_p_img)
        pdf.image(p1, 30, y_f, 50, 20)
        pdf.image(p2, 130, y_f, 50, 20)
        os.unlink(p1)
        os.unlink(p2)
        
        pdf.set_y(y_f + 22)
        pdf.set_font('Arial', 'B', 8)
        pdf.cell(95, 5, 'NOMBRE Y FIRMA DEL CLIENTE', 0, 0, 'C')
        pdf.cell(95, 5, 'IVAN ORTIZ', 0, 1, 'C')
        pdf.set_font('Arial', 'B', 7)
        pdf.cell(95, 4, '', 0, 0, 'C')
        pdf.cell(95, 4, f'({empresa_full})', 0, 1, 'C')
        
    return pdf.output(dest='S').encode('latin-1')


# --- FUNCIÓN PARA AGENDAR EN CALENDARIO ---
def agendar_recordatorio(tipo_evento, cliente, fecha, hora_elegida):
    url_script = "TU_URL_DE_GOOGLE_SCRIPT_AQUI" 
    
    dt_inicio = datetime.combine(fecha, hora_elegida)
    dt_fin = dt_inicio + timedelta(hours=2)
    
    str_inicio = dt_inicio.strftime("%Y-%m-%dT%H:%M:%S-06:00")
    str_fin = dt_fin.strftime("%Y-%m-%dT%H:%M:%S-06:00")
    
    datos = {
        "titulo": f"{tipo_evento} - {cliente} (IO SECURITY)",
        "fechaInicio": str_inicio,
        "fechaFin": str_fin,
        "descripcion": f"Recordatorio automático generado desde la App de IO SECURITY. Cliente: {cliente}"
    }
    try:
        requests.post(url_script, data=json.dumps(datos))
    except:
        pass 
# ------------------------------------------

# 4. INTERFAZ OPERATIVA Y PRORRATEO (MÓDULOS INTACTOS)
st.sidebar.title("🛡️ CONTROL IO")
tipo = st.sidebar.radio("Módulo:", ["Nueva Instalación CCTV", "Servicio IO Prevent", "Mantenimiento", "Cotización", "Anticipo", "Crear Cita"])
sub_m = st.sidebar.selectbox("Subtipo Mant.:", ["Preventivo", "Correctivo"]) if tipo == "Mantenimiento" else ""

# --- NUEVO MÓDULO: CREAR CITA ---
if tipo == "Crear Cita":
    st.markdown("## 📅 AGENDAR NUEVA CITA EN CALENDARIO")
    col_cita1, col_cita2 = st.columns(2)
    
    with col_cita1:
        nom_cita = st.text_input("👤 NOMBRE DEL CLIENTE")
        f_p_cita = st.date_input("📅 FECHA DE LA CITA")
        hora_rec_cita = st.time_input("⏰ HORA DE LA CITA", value=time(10, 0))
        
    with col_cita2:
        tipo_cita = st.selectbox("📌 TIPO DE SERVICIO / CITA", ["Presupuesto", "Mantenimiento", "Instalación Nueva", "Anticipo"])
        st.markdown("<br>", unsafe_allow_html=True) 
        
        if st.button("🚀 GUARDAR CITA EN CALENDARIO"):
            if nom_cita:
                agendar_recordatorio(tipo_cita, nom_cita, f_p_cita, hora_rec_cita)
                st.markdown(f"<div class='success-box'>✅ SISTEMA: CITA AGENDADA EN CALENDARIO CON ÉXITO.</div>", unsafe_allow_html=True)
            else:
                st.error("⚠️ REQUERIDO: Nombre del cliente.")

# --- TU CÓDIGO ORIGINAL INTACTO ---
elif tipo != "Crear Cita":
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            nom = st.text_input("👤 CLIENTE")
            tel = st.text_input("📞 WHATSAPP (10 DIG)")
            f_p = st.date_input("📅 FECHA")
            email_input = st.text_input("📧 EMAIL DEL CLIENTE") if tipo in ["Cotización", "Anticipo"] else ""
            
            if tipo == "Anticipo":
                id_fiscal = st.text_input("🪪 DOCUMENTO DE IDENTIDAD / ID FISCAL")
                proy_nom = st.text_input("🏗️ NOMBRE DEL PROYECTO/SERVICIO")
                proy_desc = st.text_area("📝 DESCRIPCIÓN BREVE DEL PROYECTO")
                
        with c2:
            m_sel = st.multiselect("📦 MATERIALES:", df_cat['Producto'].tolist()) if tipo not in ["Servicio IO Prevent", "Anticipo"] else []
            m_total = st.number_input("💵 MANO DE OBRA / COSTO ($)", min_value=0.0) if tipo != "Anticipo" else 0.0
            
            if tipo == "Cotización":
                folio_input = st.text_input("📝 NÚMERO DE FOLIO", value="001")
                iva_sel = st.selectbox("¿Agregar IVA (16%)?", ["NO", "SÍ"])
                iva_pct = 16 if iva_sel == "SÍ" else 0
                anticipo_sel = st.selectbox("Porcentaje de Anticipo:", ["50", "60", "70", "80", "100"])

            if tipo == "Anticipo":
                proy_plazo = st.text_input("⏱️ PLAZO DE ENTREGA ESTIMADO")
                proy_link = st.text_input("🔗 ENLACE AL CONTRATO/PROPUESTA")
                st.markdown("---")
                ant_fecha_rec = st.text_input("🕒 FECHA Y HORA DE RECEPCIÓN", value=datetime.now().strftime("%d %b %Y %I:%M %p"))
                ant_total = st.number_input("💰 MONTO TOTAL DEL PROYECTO ($)", min_value=0.0)
                ant_monto = st.number_input("💵 MONTO DEL ANTICIPO RECIBIDO ($)", min_value=0.0)
                ant_metodo = st.selectbox("💳 MÉTODO DE PAGO", ["Transferencia", "Efectivo", "Tarjeta"])
                ant_ref = st.text_input("🧾 REFERENCIA DE LA TRANSACCIÓN")

        dom_input = st.text_input("🏠 DOMICILIO CLIENTE") if tipo not in ["Cotización", "Anticipo"] else ""
        notas_input = st.text_area("📝 NOTAS ADICIONALES") if tipo not in ["Cotización", "Anticipo"] else ""

        items_pdf = []
        total_final = 0.0
        periodo_io = ""
        tec_io = ""
        n_cam_io = 0
        can_io = ""
        
        if tipo == "Servicio IO Prevent":
            periodo_io = st.sidebar.selectbox("Periodicidad Pago:", ["Semestral", "Anual"])
            with st.expander("🌐 CONFIGURACION IO PREVENT", expanded=True):
                e1, e2 = st.columns(2)
                tec_io = e1.selectbox("Tecnologia:", ["Analogica", "IP Digital"])
                n_cam_io = e1.number_input("Cámaras del sistema:", 1)
                can_io = e2.selectbox("DVR Canales:", ["4", "8", "16", "32"])
                total_final = m_total 
        
        elif tipo == "Mantenimiento":
            with st.expander("🛠️ CONFIGURACIÓN MANTENIMIENTO", expanded=True):
                col1, col2 = st.columns(2)
                c_m = col1.number_input("Cámaras", 0)
                p_m = col1.number_input("Precio Mant unitario $", min_value=0.0, value=0.0)
                c_b = col1.number_input("Pares Baluns", 0)
                p_b = col1.number_input("Precio Par $", min_value=0.0, value=0.0)
                sel_d = col2.selectbox("Tipo DVR", ["4 Can", "8 Can", "16 Can", "Placa Madre"])
                p_d_mnt = col2.number_input(f"Costo Limpieza {sel_d} $", min_value=0.0, value=0.0)
                
                opc_mnt = []
                if c_m > 0: opc_mnt.append(f"Mantenimiento {c_m} Cam")
                if c_b > 0: opc_mnt.append(f"Baluns {c_b} Par")
                opc_mnt.append(f"Limpieza {sel_d}")
                m_prorr = st.multiselect("💰 CARGAR COSTO ADICIONAL EN:", opc_mnt)
                act = len(m_prorr)
                ex = round(m_total / act, 2) if act > 0 else 0
                
                if c_m > 0:
                    v = round((c_m*p_m)+(ex if f"Mantenimiento {c_m} Cam" in m_prorr else 0), 2)
                    items_pdf.append({"Cantidad": c_m, "Concepto": f"Mantenimiento {sub_m} Camara", "Subtotal_Final": v})
                    total_final += v
                if c_b > 0:
                    v = round((c_b*p_b)+(ex if f"Baluns {c_b} Par" in m_prorr else 0), 2)
                    items_pdf.append({"Cantidad": c_b, "Concepto": "Reemplazo de Baluns", "Subtotal_Final": v})
                    total_final += v
                v_d = round(p_d_mnt+(ex if f"Limpieza {sel_d}" in m_prorr else 0), 2)
                items_pdf.append({"Cantidad": 1, "Concepto": f"Limpieza tecnica {sel_d}", "Subtotal_Final": v_d})
                total_final += v_d

        elif m_sel and tipo != "Anticipo": 
            with st.expander("📋 CONFIGURAR EQUIPOS Y CANTIDADES", expanded=True):
                m_gan = st.multiselect("💰 CARGAR GANANCIA / MANO DE OBRA EN:", m_sel)
                temp = {}
                t_u = 0
                for p in m_sel:
                    q = st.number_input(f"Cant. {p}", 1, key=f"q_{p}")
                    temp[p] = q
                    if p in m_gan: t_u += q
                ex_i = round(m_total / t_u, 2) if t_u > 0 else 0
                for p, q in temp.items():
                    base = df_cat[df_cat['Producto'] == p]['Precio'].values[0]
                    sub = round((base + (ex_i if p in m_gan else 0)) * q, 2)
                    items_pdf.append({"Cantidad": q, "Concepto": p, "Subtotal_Final": sub})
                    total_final += sub

        if tipo == "Cotización":
            visual_iva = total_final * (iva_pct / 100.0)
            visual_total = total_final + visual_iva
            st.divider()
            st.metric("TOTAL COTIZACIÓN (CON IVA)", f"${visual_total:,.2f}")
        elif tipo == "Anticipo":
            ant_saldo_pendiente = ant_total - ant_monto
            st.divider()
            c_a1, c_a2, c_a3 = st.columns(3)
            c_a1.metric("TOTAL PROYECTO", f"${ant_total:,.2f}")
            c_a2.metric("ANTICIPO RECIBIDO", f"${ant_monto:,.2f}")
            c_a3.metric("SALDO PENDIENTE", f"${ant_saldo_pendiente:,.2f}")
        else:
            st.divider()
            st.metric("VALOR TOTAL", f"${total_final:,.2f}")

    # LÓGICA DE BOTONES SEPARADA
    if tipo == "Cotización":
        if st.button("🚀 FINALIZAR Y GENERAR COTIZACIÓN"):
            if nom:
                try:
                    pdf_b = generar_pdf_cotizacion(nom, items_pdf, total_final, tel, email_input, iva_pct, anticipo_sel, folio_input)
                    st.markdown(f"<div class='success-box'>📝 SISTEMA: COTIZACIÓN CREADA CON ÉXITO.</div>", unsafe_allow_html=True)
                    st.markdown(f'<a href="data:application/octet-stream;base64,{base64.b64encode(pdf_b).decode()}" download="Cotizacion_{nom}.pdf" class="download-btn">1. 📥 DESCARGAR COTIZACIÓN</a>', unsafe_allow_html=True)
                    msg = urllib.parse.quote(f"Hola {nom}, soy Ivan de IO SECURITY. Le adjunto su cotizacion en formato PDF. Quedo a sus ordenes.")
                    st.markdown(f'<a href="https://wa.me/52{tel}?text={msg}" target="_blank" class="whatsapp-btn">2. 💬 ENVIAR POR WHATSAPP</a>', unsafe_allow_html=True)
                except Exception as e: 
                    st.error(f"ERROR TÉCNICO: {e}")
            else: 
                st.error("⚠️ REQUERIDO: Nombre del cliente.")

    elif tipo == "Anticipo":
        st.markdown("### ✍️ FIRMA DE RECIBIDO (IO SECURITY)")
        c_prov_ant = st_canvas(stroke_width=3, stroke_color="#000", background_color="#FFFFFF", height=150, width=350, key="prov_ant", display_toolbar=True)
        
        if st.button("🚀 FINALIZAR Y GENERAR RECIBO DE ANTICIPO"):
            if nom and proy_nom and c_prov_ant.image_data is not None:
                try:
                    pdf_b = generar_pdf_anticipo(nom, email_input, tel, id_fiscal, proy_nom, proy_desc, f_p.strftime('%d %b %Y'), proy_plazo, proy_link, ant_fecha_rec, ant_monto, ant_metodo, ant_ref, ant_total, ant_saldo_pendiente, c_prov_ant.image_data)
                    st.markdown(f"<div class='success-box'>💵 SISTEMA: RECIBO DE ANTICIPO CREADO CON ÉXITO.</div>", unsafe_allow_html=True)
                    st.markdown(f'<a href="data:application/octet-stream;base64,{base64.b64encode(pdf_b).decode()}" download="Anticipo_{nom}.pdf" class="download-btn">1. 📥 DESCARGAR RECIBO DE ANTICIPO</a>', unsafe_allow_html=True)
                    msg = urllib.parse.quote(f"Hola {nom}, soy Ivan de IO SECURITY. Le confirmo la recepcion de su anticipo por ${ant_monto:,.2f} MXN para el proyecto {proy_nom}. Le adjunto su comprobante en PDF.")
                    st.markdown(f'<a href="https://wa.me/52{tel}?text={msg}" target="_blank" class="whatsapp-btn">2. 💬 ENVIAR POR WHATSAPP</a>', unsafe_allow_html=True)
                except Exception as e: 
                    st.error(f"ERROR TÉCNICO: {e}")
            else: 
                st.error("⚠️ REQUERIDO: Nombre del Cliente, Nombre del Proyecto y tu Firma Digital.")

    # --- CAMBIO AQUÍ: Originalmente era "else:" ---
    elif tipo in ["Nueva Instalación CCTV", "Servicio IO Prevent", "Mantenimiento"]:
        st.markdown("### ✍️ FIRMAS DIGITALES")
        f1, f2 = st.columns(2)
        with f1: 
            c_cli = st_canvas(stroke_width=3, stroke_color="#000", background_color="#FFFFFF", height=180, width=350, key="cli", display_toolbar=True)
        with f2: 
            c_prov = st_canvas(stroke_width=3, stroke_color="#000", background_color="#FFFFFF", height=180, width=350, key="prov", display_toolbar=True)

        if st.button("🚀 FINALIZAR Y GENERAR EXPEDIENTE"):
            if c_cli.image_data is not None and nom and dom_input:
                try:
                    pdf_b = generar_pdf_io(nom, items_pdf, total_final, tipo, sub_m, periodo_io, tec_io, n_cam_io, can_io, c_cli.image_data, c_prov.image_data, f_p, dom_input, notas_input)
                    st.markdown(f"<div class='success-box'>🔒 SISTEMA: CONTRATO DE {tipo.upper()} GENERADO CON ÉXITO.</div>", unsafe_allow_html=True)
                    st.markdown(f'<a href="data:application/octet-stream;base64,{base64.b64encode(pdf_b).decode()}" download="Contrato_{nom}.pdf" class="download-btn">1. 📥 DESCARGAR CONTRATO</a>', unsafe_allow_html=True)
                    msg = urllib.parse.quote(f"Hola {nom}, soy Ivan de IO SECURITY. Confirmo la generacion de su contrato. Adjunto PDF.")
                    st.markdown(f'<a href="https://wa.me/52{tel}?text={msg}" target="_blank" class="whatsapp-btn">2. 💬 ENVIAR POR WHATSAPP</a>', unsafe_allow_html=True)
                except Exception as e: 
                    st.error(f"ERROR TÉCNICO: {e}")
            else: 
                st.error("⚠️ REQUERIDO: Nombre, Domicilio y Firmas.")           
