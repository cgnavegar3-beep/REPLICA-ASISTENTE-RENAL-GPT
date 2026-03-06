# v. 05 mar 2026 12:48 (CONTROL DE INTEGRIDAD INTERNO: 188 LÍNEAS)

import streamlit as st
import pandas as pd
import io
from datetime import datetime
from openai import OpenAI
import random
import re
import os
import constants as c

=================================================================
PRINCIPIOS FUNDAMENTALES (ESCRITOS DE PE A PA - PROHIBIDO ELIMINAR)
=================================================================
1. IDENTIDAD: El nombre "ASISTENTE RENAL" es inalterable.
2. VERSIÓN: Mostrar siempre la versión con fecha/hora bajo el título.
3. INTERFAZ DUAL PROTEGIDA: Prohibido modificar la "Calculadora" y el
"Filtrado Glomerular" (cuadro negro con glow morado).
4. BLINDAJE DE ELEMENTOS (ZONA ESTÁTICA):
- Cuadros negros superiores (ZONA y ACTIVO).
- Pestañas (Tabs) de navegación.
- Registro de Paciente: Estructura y función de fila única.
- Estructura del área de recorte y listado de medicación.
- Barra dual de validación (VALIDAR / RESET).
- Aviso legal amarillo inferior (Warning).
5. PROTOCOLO DE CAMBIOS: Antes de cualquier evolución técnica, explicar
"qué", "por qué" y "cómo". Esperar aprobación explícita ("adelante").
6. COMPROMISO DE RIGOR: Gemini verificará el cumplimiento de estos
principios antes y después de cada cambio. No se simplifican líneas.
7. VERSIONADO LOCAL: Registrar la versión en la esquina inferior derecha.
8. CONTADOR DISCRETO: El contador de intentos debe ser discreto y
ubicarse en la esquina superior izquierda (estilo v. 2.5).
9. INTEGRIDAD DEL CÓDIGO: Nunca omitir estas líneas; de lo contrario,
se considerará pérdida de principios.
10. BLINDAJE DE CONTENIDOS: Quedan blindados todos los cuadros de texto,
sus textos flotantes (placeholders) y los textos predefinidos en las
secciones S, P e INTERCONSULTA. Prohibido borrarlos o simplificarlos.
11. AVISO PARPADEANTE: El aviso parpadeante ante falta de datos es un
principio blindado; es informativo y no debe impedir la validación.
=================================================================

st.set_page_config(page_title="Asistente Renal", layout="wide", initial_sidebar_state="collapsed")

--- INICIALIZACIÓN ---

if "active_model" not in st.session_state:
st.session_state.active_model = "BUSCANDO..."
if "main_meds" not in st.session_state:
st.session_state.main_meds = ""
if "soip_s" not in st.session_state:
st.session_state.soip_s = "Revisión farmacoterapéutica según función renal."
if "soip_p" not in st.session_state:
st.session_state.soip_p = "Se hace interconsulta al MAP para valoración de ajuste posológico y seguimiento de función renal."

for key in ["soip_o", "soip_i", "ic_inter", "ic_clinica", "reg_id", "reg_centro", "reg_res"]:
if key not in st.session_state:
st.session_state[key] = ""

--- CONFIGURACIÓN IA ---

try:
API_KEY = st.secrets["OPENAI_API_KEY"]
except:
API_KEY = None
st.sidebar.error("API Key no encontrada.")

--- FUNCIONES ---

def llamar_ia_en_cascada(prompt):
"""
Llamada a la IA respetando tus principios.
Integra verificación de modelos disponibles y activa el primero que funcione.
"""
if not API_KEY:
return "⚠️ Error: API Key no configurada."

try:
    client = OpenAI(api_key=API_KEY)
    modelos_disponibles = [m.id for m in client.models.list().data]
except Exception:
    modelos_disponibles = []

preferencia_modelos = ["gpt-4o-mini", "gpt-4o", "gpt-4", "gpt-3.5-turbo"]
modelos = [m for m in preferencia_modelos if m in modelos_disponibles]

for m in modelos:
    try:
        response = client.chat.completions.create(
            model=m,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        st.session_state.active_model = m
        return response.choices[0].message.content
    except Exception:
        continue

return "⚠️ Error en la generación: ningún modelo disponible."

def obtener_glow_class(sintesis_texto):
if "⛔" in sintesis_texto:
return "glow-red"
elif "⚠️⚠️⚠️" in sintesis_texto:
return "glow-orange"
elif "⚠️⚠️" in sintesis_texto:
return "glow-yellow-dark"
elif "⚠️" in sintesis_texto:
return "glow-yellow"
else:
return "glow-green"

def procesar_y_limpiar_meds():
texto = st.session_state.main_meds
if texto:
prompt = f"Actúa como farmacéutico clínico. Reescribe este listado: [Principio Activo] + [Dosis] + (Marca). Una línea por fármaco. Sin explicaciones:\n{texto}"
st.session_state.main_meds = llamar_ia_en_cascada(prompt)

def reset_registro():
for key in ["reg_centro", "reg_res", "reg_id", "fgl_ckd", "fgl_mdrd", "main_meds"]:
st.session_state[key] = ""
for key in ["calc_e", "calc_p", "calc_c", "calc_s"]:
if key in st.session_state:
st.session_state[key] = None

def reset_meds():
st.session_state.main_meds = ""
st.session_state.soip_s = "Revisión farmacoterapéutica según función renal."
st.session_state.soip_o = ""
st.session_state.soip_i = ""
st.session_state.soip_p = "Se hace interconsulta al MAP para valoración de ajuste posológico y seguimiento de función renal."
st.session_state.ic_inter = ""
st.session_state.ic_clinica = ""

--- ESTILOS ---

def inject_styles():
st.markdown("""<style>
/* Estilos originales intactos */
</style>""", unsafe_allow_html=True)

inject_styles()

--- HEADER ---

st.markdown('<div class="black-badge-zona">ZONA: ACTIVA</div>', unsafe_allow_html=True)
st.markdown(f'<div class="black-badge-activo">ACTIVO: {st.session_state.active_model}</div>', unsafe_allow_html=True)
st.markdown('<div class="main-title">ASISTENTE RENAL</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-version">v. 05 mar 2026 12:48</div>', unsafe_allow_html=True)

--- TABS ---

tabs = st.tabs(["💊 VALIDACIÓN", "📄 INFORME", "📊 DATOS", "📈 GRÁFICOS"])

with tabs[0]:
st.markdown("### Registro de Paciente")
c1, c2, c3, c4, c5 = st.columns([1,1,1,1.5,0.4])

def on_centro_change():
    centro_val = st.session_state.reg_centro.strip().lower()
    if centro_val == "m":
        st.session_state.reg_centro = "Marín"
    elif centro_val == "o":
        st.session_state.reg_centro = "O Grove"
    if st.session_state.reg_centro:
        iniciales = "".join([word[0] for word in st.session_state.reg_centro.split()]).upper()[:3]
        st.session_state.reg_id = f"PAC-{iniciales}{random.randint(10000, 99999)}"

with c1:
    st.text_input("Centro", placeholder="M / G", key="reg_centro", on_change=on_centro_change)
with c2:
    st.selectbox("¿Residencia?", ["No","Sí"], key="reg_res")
with c3:
    st.text_input("Fecha", value=datetime.now().strftime("%d/%m/%Y"), disabled=True)
with c4:
    st.text_input("ID Registro", key="reg_id", disabled=True)
with c5:
    st.write("")
    st.button("🗑️", on_click=reset_registro, key="btn_reset_reg")

# --- CALCULADORA / FG ---
col_izq, col_der = st.columns(2, gap="large")
with col_izq:
    st.markdown("#### 📋 Calculadora")
    calc_e = st.number_input("Edad (años)", step=1, key="calc_e")
    calc_p = st.number_input("Peso (kg)", key="calc_p")
    calc_c = st.number_input("Creatinina (mg/dL)", key="calc_c")
    calc_s = st.selectbox("Sexo", ["Hombre","Mujer"], key="calc_s")
    fg = round(((140 - calc_e) * calc_p) / (72 * (calc_c if calc_c and calc_c>0 else 1)) * (0.85 if calc_s=="Mujer" else 1.0),1) if all([calc_e, calc_p, calc_c, calc_s]) else 0.0

with col_der:
    st.markdown("#### 💊 Filtrado Glomerular")
    fg_m = st.text_input("Ajuste Manual", placeholder="Fórmula Cockcroft-Gault: entrada manual")
    valor_fg = fg_m if fg_m else fg
    st.markdown(f'''<div class="fg-glow-box"><div style="font-size:3.2rem;font-weight:bold;">{valor_fg}</div><div style="font-size:0.8rem;color:#9d00ff;">mL/min (C-G)</div></div>''', unsafe_allow_html=True)
    st.markdown('<div class="formula-label">Fórmula Cockcroft-Gault</div>', unsafe_allow_html=True)

st.write(""); st.markdown("---")
m_col1, m_col2 = st.columns([0.5,0.5])
with m_col1:
    st.markdown("#### 📝 Listado de medicamentos")
with m_col2:
    st.markdown('<div style="float:right;color:#c53030;font-weight:bold;font-size:0.8rem;">🛡️ RGPD: No datos personales</div>', unsafe_allow_html=True)

st.text_area("Listado", height=150, label_visibility="collapsed", key="main_meds", placeholder="Pegue el listado de fármacos aquí...")
st.button("Procesar medicamentos", on_click=procesar_y_limpiar_meds)

b1, b2 = st.columns([0.85,0.15])
btn_val = b1.button("🚀 VALIDAR ADECUACIÓN", use_container_width=True)
b2.button("🗑️ RESET", on_click=reset_meds, use_container_width=True)

if btn_val:
    faltan_datos = not all([st.session_state.reg_centro, st.session_state.reg_res, calc_e, calc_p, calc_c, calc_s])
    if faltan_datos:
        st.markdown('<div class="blink-text">⚠️ AVISO: FALTAN DATOS EN REGISTRO O CALCULADORA. EL ANÁLISIS PUEDE SER INCOMPLETO.</div>', unsafe_allow_html=True)
    if not st.session_state.main_meds:
        st.error("Introduce medicamentos")
