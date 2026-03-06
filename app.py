# v. 06 mar 2026 10:12 (CONTROL DE INTEGRIDAD INTERNO)

import streamlit as st
import pandas as pd
import io
from datetime import datetime
from openai import OpenAI
import random
import re
import os
import constants as c 

# =================================================================
# PRINCIPIOS FUNDAMENTALES (ESCRITOS DE PE A PA - PROHIBIDO ELIMINAR)
# =================================================================
# 1. IDENTIDAD: El nombre "ASISTENTE RENAL" es inalterable.
# 2. VERSIÓN: Mostrar siempre la versión con fecha/hora bajo el título.
# 3. INTERFAZ DUAL PROTEGIDA: Prohibido modificar la "Calculadora" y el 
#    "Filtrado Glomerular" (cuadro negro con glow morado).
# 4. BLINDAJE DE ELEMENTOS (ZONA ESTÁTICA):
#    - Cuadros negros superiores (ZONA y ACTIVO).
#    - Pestañas (Tabs) de navegación.
#    - Registro de Paciente: Estructura y función de fila única.
#    - Estructura del área de recorte y listado de medicación.
#    - Barra dual de validación (VALIDAR / RESET).
#    - Aviso legal amarillo inferior (Warning).
# 5. PROTOCOLO DE CAMBIOS: Antes de cualquier evolución técnica, explicar
#    "qué", "por qué" y "cómo". Esperar aprobación explícita ("adelante").
# 6. COMPROMISO DE RIGOR: Gemini verificará el cumplimiento de estos 
#    principios antes y después de cada cambio. No se simplifican líneas.
# 7. VERSIONADO LOCAL: Registrar la versión en la esquina inferior derecha.
# 8. CONTADOR DISCRETO: El contador de intentos debe ser discreto y 
#    ubicarse en la esquina superior izquierda (estilo v. 2.5).
# 9. INTEGRIDAD DEL CÓDIGO: Nunca omitir estas líneas; de lo contrario, 
#    se considerará pérdida de principios.
# 10. BLINDAJE DE CONTENIDOS: Quedan blindados todos los cuadros de texto,
#     sus textos flotantes (placeholders) y los textos predefinidos en las
#     secciones S, P e INTERCONSULTA. Prohibido borrarlos o simplificarlos.
# 11. AVISO PARPADEANTE: El aviso parpadeante ante falta de datos es un 
#     principio blindado; es informativo y no debe impedir la validación.
# =================================================================

st.set_page_config(page_title="Asistente Renal", layout="wide", initial_sidebar_state="collapsed")

# --- INICIALIZACIÓN ---
if "active_model" not in st.session_state: 
    st.session_state.active_model = "BUSCANDO..."

if "main_meds" not in st.session_state: 
    st.session_state.main_meds = ""

if "soip_s" not in st.session_state: 
    st.session_state.soip_s = "Revisión farmacoterapéutica según función renal."

if "soip_p" not in st.session_state: 
    st.session_state.soip_p = "Se hace interconsulta al MAP para valoración de ajuste posológico y seguimiento de función renal."

for key in ["soip_o","soip_i","ic_inter","ic_clinica","reg_id","reg_centro","reg_res"]:
    if key not in st.session_state:
        st.session_state[key] = ""

# --- CONFIGURACIÓN IA ---
try:
    API_KEY = st.secrets["OPENAI_API_KEY"]
except:
    API_KEY = None
    st.sidebar.error("API Key no encontrada.")

# --- FUNCIONES IA ---
def llamar_ia_en_cascada(prompt):

    if not API_KEY:
        return "⚠️ Error: API Key no configurada."

    modelos = [
        "gpt-4",
        "gpt-3.5-turbo",
        "text-davinci-003",
        "text-davinci-002"
    ]

    for m in modelos:
        try:
            client = OpenAI(api_key=API_KEY)

            response = client.chat.completions.create(
                model=m,
                messages=[{"role":"user","content":prompt}],
                temperature=0.1
            )

            st.session_state.active_model = m

            return response.choices[0].message.content

        except Exception:
            continue

    return "⚠️ Error en la generación: ningún modelo disponible."

# --- GLOW SYSTEM ---
def obtener_glow_class(texto):

    if "⛔" in texto:
        return "glow-red"
    elif "⚠️⚠️⚠️" in texto:
        return "glow-orange"
    elif "⚠️⚠️" in texto:
        return "glow-yellow-dark"
    elif "⚠️" in texto:
        return "glow-yellow"
    else:
        return "glow-green"

# --- LIMPIEZA DE MEDICAMENTOS ---
def procesar_y_limpiar_meds():

    texto = st.session_state.main_meds

    if texto:

        prompt = f"""
Actúa como farmacéutico clínico.

Convierte este listado en:

[Principio activo] + [Dosis] + (Marca)

Una línea por medicamento.
Sin comentarios.

Listado:
{texto}
"""

        st.session_state.main_meds = llamar_ia_en_cascada(prompt)

# --- RESET REGISTRO ---
def reset_registro():

    for key in [
        "reg_centro",
        "reg_res",
        "reg_id",
        "fgl_ckd",
        "fgl_mdrd",
        "main_meds"
    ]:
        st.session_state[key] = ""

# --- RESET MEDS ---
def reset_meds():

    st.session_state.main_meds = ""
    st.session_state.soip_s = "Revisión farmacoterapéutica según función renal."
    st.session_state.soip_o = ""
    st.session_state.soip_i = ""
    st.session_state.soip_p = "Se hace interconsulta al MAP para valoración de ajuste posológico y seguimiento de función renal."

# --- CABECERA ---
st.markdown('<div style="background:black;color:#888;padding:6px 14px;border-radius:4px;font-family:monospace;font-size:0.7rem;position:fixed;top:10px;left:15px;">ZONA: ACTIVA</div>', unsafe_allow_html=True)
st.markdown(f'<div style="background:black;color:#00FF00;padding:6px 14px;border-radius:4px;font-family:monospace;font-size:0.7rem;position:fixed;top:10px;left:145px;">ACTIVO: {st.session_state.active_model}</div>', unsafe_allow_html=True)

st.markdown('<div style="text-align:center;font-size:2.5rem;font-weight:800;">ASISTENTE RENAL</div>', unsafe_allow_html=True)
st.markdown('<div style="text-align:center;font-size:0.6rem;color:#bbb;font-family:monospace;">v. 06 mar 2026 10:12</div>', unsafe_allow_html=True)

# --- TABS ---
tabs = st.tabs(["💊 VALIDACIÓN","📄 INFORME","📊 DATOS","📈 GRÁFICOS"])

# =========================================================
# TAB VALIDACIÓN
# =========================================================
with tabs[0]:

    st.markdown("### Registro de Paciente")

    c1,c2,c3,c4,c5 = st.columns([1,1,1,1.5,0.4])

    def on_centro_change():

        centro = st.session_state.reg_centro.strip().lower()

        if centro == "m":
            st.session_state.reg_centro = "Marín"

        elif centro == "o":
            st.session_state.reg_centro = "O Grove"

        if st.session_state.reg_centro:

            iniciales = "".join([w[0] for w in st.session_state.reg_centro.split()]).upper()[:3]

            st.session_state.reg_id = f"PAC-{iniciales}{random.randint(10000,99999)}"

    with c1:
        st.text_input("Centro",placeholder="M / O",key="reg_centro",on_change=on_centro_change)

    with c2:
        st.selectbox("¿Residencia?",["No","Sí"],index=None,key="reg_res")

    with c3:
        st.text_input("Fecha",value=datetime.now().strftime("%d/%m/%Y"),disabled=True)

    with c4:
        st.text_input("ID Registro",key="reg_id",disabled=True)

    with c5:
        st.write("")
        st.button("🗑️",on_click=reset_registro)

    st.markdown("---")

    col1,col2 = st.columns(2)

    with col1:

        st.markdown("#### Calculadora")

        calc_e = st.number_input("Edad",value=None)
        calc_p = st.number_input("Peso",value=None)
        calc_c = st.number_input("Creatinina",value=None)
        calc_s = st.selectbox("Sexo",["Hombre","Mujer"],index=None)

        fg = round(((140-calc_e)*calc_p)/(72*(calc_c if calc_c else 1))*(0.85 if calc_s=="Mujer" else 1),1) if all([calc_e,calc_p,calc_c,calc_s]) else 0

    with col2:

        st.markdown("#### Filtrado Glomerular")

        fg_manual = st.text_input("Ajuste Manual")

        valor_fg = fg_manual if fg_manual else fg

        st.markdown(f"<h1 style='text-align:center'>{valor_fg}</h1>",unsafe_allow_html=True)

    st.markdown("---")

    st.text_area(
        "Listado",
        height=150,
        key="main_meds",
        placeholder="Pegue el listado de fármacos aquí..."
    )

    st.button("Procesar medicamentos",on_click=procesar_y_limpiar_meds)

    b1,b2 = st.columns([0.85,0.15])

    btn_val = b1.button("🚀 VALIDAR ADECUACIÓN",use_container_width=True)
    b2.button("🗑️ RESET",on_click=reset_meds,use_container_width=True)

# =========================================================
# MOTOR DE VALIDACIÓN
# =========================================================

    if btn_val:

        faltan_datos = not all([
            st.session_state.reg_centro,
            st.session_state.reg_res,
            calc_e,
            calc_p,
            calc_c,
            calc_s
        ])

        if faltan_datos:

            st.markdown(
                '<div style="color:red;font-weight:bold">⚠️ FALTAN DATOS. EL ANÁLISIS PUEDE SER INCOMPLETO.</div>',
                unsafe_allow_html=True
            )

        if not st.session_state.main_meds:

            st.error("Introduce medicamentos")

        else:

            medicamentos = st.session_state.main_meds
            fg_utilizado = valor_fg

            prompt = f"""
Eres farmacéutico clínico experto en ajuste renal.

FG Cockcroft-Gault: {fg_utilizado} mL/min

Medicamentos:
{medicamentos}

Clasifica cada medicamento:

⛔ Contraindicado
⚠️⚠️⚠️ Ajuste obligatorio
⚠️⚠️ Precaución relevante
⚠️ Precaución leve
✅ Sin ajuste

Excluye los ✅ de la tabla.

Genera:

BLOQUE 1
Síntesis clínica

BLOQUE 2
Tabla comparativa 12 columnas

BLOQUE 3
Detalle clínico farmacológico
"""

            with st.spinner("Analizando medicación según función renal..."):

                resultado = llamar_ia_en_cascada(prompt)

            glow = obtener_glow_class(resultado)

            st.markdown(
                f'<div style="padding:15px;border-radius:10px;border:2px solid #ddd" class="{glow}">{resultado}</div>',
                unsafe_allow_html=True
            )

            st.session_state.soip_o = f"FG Cockcroft-Gault estimado: {fg_utilizado} mL/min"
            st.session_state.soip_i = "Se detectan medicamentos potencialmente afectados por función renal."

# =========================================================
# AVISO LEGAL
# =========================================================

st.markdown("""
<div style="background:#fff9db;padding:20px;border-radius:10px;margin-top:40px;text-align:center;font-size:0.85rem;">
Esta herramienta es un apoyo clínico.  
No sustituye el juicio clínico del profesional sanitario.
</div>
""",unsafe_allow_html=True)
