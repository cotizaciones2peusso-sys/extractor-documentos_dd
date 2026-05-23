import streamlit as st
import pandas as pd
from datetime import datetime
import io

# Configuración de la página
st.set_page_config(page_title="Extractor Documental Inteligente", layout="wide")

st.markdown("""
    <style>
    .main-title { font-size: 28px; font-weight: bold; color: #1E3A8A; margin-bottom: 20px; }
    .section-header { font-size: 20px; font-weight: bold; color: #2563EB; margin-top: 20px; margin-bottom: 10px; }
    .card { background-color: #F3F4F6; padding: 15px; border-radius: 8px; margin-bottom: 15px; border-left: 5px solid #2563EB; }
    .alert-card { background-color: #FEF3C7; padding: 15px; border-radius: 8px; margin-bottom: 15px; border-left: 5px solid #D97706; }
    .success-text { color: #10B981; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">Plataforma Web de Extracción Documental con Validación Variable</div>', unsafe_allow_html=True)

# Configuración barra lateral
st.sidebar.markdown("### Configuración del Motor de IA")
modo_ia = st.sidebar.selectbox(
    "Seleccione el modo de verificación:",
    options=["Una sola IA (Auto-Auditoría)", "Multi-IA en Paralelo (Consenso Cruzado)"]
)

if modo_ia == "Una sola IA (Auto-Auditoría)":
    ia_unica = st.sidebar.selectbox("Seleccione la IA Principal:", ["Google Gemini 1.5 Pro", "GPT-4o", "Claude 3.5 Sonnet"])
else:
    ias_seleccionadas = st.sidebar.multiselect(
        "Seleccione las IAs a combinar (Mínimo 2):",
        options=["Google Gemini 1.5 Pro", "GPT-4o", "Claude 3.5 Sonnet"],
        default=["Google Gemini 1.5 Pro", "GPT-4o"]
    )

if 'resumen_diario' not in st.session_state:
    st.session_state.resumen_diario = []
if 'documento_procesado' not in st.session_state:
    st.session_state.documento_procesado = None

st.markdown('<div class="section-header">1. Ingesta de Documentos</div>', unsafe_allow_html=True)
uploaded_file = st.file_uploader("Arrastre o seleccione el archivo, email guardado o recorte de pantalla:", type=["pdf", "png", "jpg", "jpeg", "docx", "xlsx", "txt"])

if uploaded_file:
    id_proceso_actual = f"{uploaded_file.name}_{modo_ia}"
    if st.session_state.documento_procesado is None or st.session_state.documento_procesado.get('id_proceso') != id_proceso_actual:
        with st.spinner("Ejecutando algoritmos de extracción y verificación..."):
            if modo_ia == "Una sola IA (Auto-Auditoría)":
                datos_simulados = {
                    "id_proceso": id_proceso_actual, "nombre": uploaded_file.name, "modo": "Auto-Auditoría",
                    "label_fuente_1": "Extracción Inicial", "label_fuente_2": "Fase de Auto-Auditoría",
                    "cabecera": {"remitente": "Juan Carlos Díaz", "cliente": "Minera Alumbrera Limited", "fecha_doc": "2026-05-23"},
                    "items": [
                        {"item": 1, "descripcion": "Interruptor Termomagnético ABB S201-C16", "val_1": "S201-C16", "val_2": "S201-C16", "cant_1": 12, "cant_2": 12},
                        {"item": 2, "descripcion": "Guardamotor ABB MS116-10", "val_1": "MS116-10", "val_2": "MS116-1.0", "cant_1": 5, "cant_2": 5}
                    ]
                }
            else:
                datos_simulados = {
                    "id_proceso": id_proceso_actual, "nombre": uploaded_file.name, "modo": "Consenso Cruzado",
                    "label_fuente_1": "IA Alfa (Gemini 1.5 Pro)", "label_fuente_2": "IA Beta (GPT-4o)",
                    "cabecera": {"remitente": "Juan Carlos Díaz", "cliente": "Minera Alumbrera Limited", "fecha_doc": "2026-05-23"},
                    "items": [
                        {"item": 1, "descripcion": "Interruptor Termomagnético ABB S201-C16", "val_1": "S201-C16", "val_2": "S201-C16", "cant_1": 12, "cant_2": 12},
                        {"item": 2, "descripcion": "Guardamotor ABB MS116-10", "val_1": "MS116-10", "val_2": "MS116-1.0", "cant_1": 5, "cant_2": None}
                    ]
                }
            st.session_state.documento_procesado = datos_simulados

if uploaded_file and st.session_state.documento_processed:
    doc = st.session_state.documento_procesado
    st.markdown('<div class="section-header">2. Panel de Conciliación de Datos y Control de Calidad</div>', unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    c1.markdown(f"**Archivo:** `{doc['nombre']}`")
    c2.markdown(f"**Remitente:** {doc['cabecera']['remitente']}")
    c3.markdown(f"**Cliente:** {doc['cabecera']['cliente']}")
    
    with st.form("formulario_conciliacion_dinamico"):
        items_validados = []
        alertas_totales = 0
        
        for item in doc['items']:
            st.markdown(f"**Ítem Nro {item['item']}:** {item['descripcion']}")
            codigo_final = item['val_1']
            cantidad_final = item['cant_1']
            
            if item['val_1'] != item['val_2']:
                alertas_totales += 1
                st.markdown('<div class="alert-card"><strong>Inconsistencia en Código de Artículo:</strong></div>', unsafe_allow_html=True)
                opcion_cod = st.radio(f"Seleccione variante para Ítem {item['item']}:", options=[f"{doc['label_fuente_1']}: {item['val_1']}", f"{doc['label_fuente_2']}: {item['val_2']}", "Valor manual"], key=f"dinamico_cod_{item['item']}")
                codigo_final = item['val_1'] if doc['label_fuente_1'] in opcion_cod else (item['val_2'] if doc['label_fuente_2'] in opcion_cod else st.text_input("Código manual:", key=f"m_c_{item['item']}"))
            
            if item['cant_1'] != item['cant_2']:
                alertas_totales += 1
                st.markdown('<div class="alert-card"><strong>Inconsistencia o Duda en Cantidad:</strong></div>', unsafe_allow_html=True)
                label_2 = "null (Ilegible)" if item['cant_2'] is None else str(item['cant_2'])
                opcion_cant = st.radio(f"Seleccione cantidad para Ítem {item['item']}:", options=[f"{doc['label_fuente_1']}: {item['cant_1']}", f"{doc['label_fuente_2']}: {label_2}", "Valor manual"], key=f"dinamico_cant_{item['item']}")
                cantidad_final = float(item['cant_1']) if doc['label_fuente_1'] in opcion_cant else (None if item['cant_2'] is None else float(item['cant_2']))
            
            items_validados.append({"Item_Nro": item['item'], "Codigo_Articulo": codigo_final, "Descripcion": item['descripcion'], "Cantidad": cantidad_final})
            st.markdown("---")
            
        if st.form_submit_button("Validar e Incorporar a Reporte Diario"):
            df_cabecera = pd.DataFrame([{"ID_Documento": f"DOC-{int(datetime.now().timestamp())}", "Fecha_Lectura": datetime.now().strftime("%Y-%m-%d"), "Modo": doc['modo'], "Remitente": doc['cabecera']['remitente'], "Cliente": doc['cabecera']['cliente'], "Fecha_Doc": doc['cabecera']['fecha_doc'], "Estado": "Conciliado" if alertas_totales > 0 else "Consenso Directo"}])
            df_detalle = pd.DataFrame(items_validados)
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_cabecera.to_excel(writer, sheet_name='Cabecera', index=False)
                df_detalle.to_excel(writer, sheet_name='Detalle_Items', index=False)
            output.seek(0)
            
            st.session_state.resumen_diario.append({"Fecha Proceso": datetime.now().strftime("%Y-%m-%d %H:%M"), "Remitente": doc['cabecera']['remitente'], "Cliente": doc['cabecera']['cliente'], "Resumen": f"Procesados {len(items_validados)} ítems.", "Estado": "⚠ Ajuste Humano" if alertas_totales > 0 else "✓ Consenso"})
            st.markdown('<p class="success-text">✓ Guardado. Descargue el Excel abajo.</p>', unsafe_allow_html=True)
            st.download_button(label="📥 Descargar Excel de este Documento", data=output, file_name=f"Resultado_{doc['nombre']}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

st.markdown('<div class="section-header">3. Resumen Diario de Operaciones</div>', unsafe_allow_html=True)
if st.session_state.resumen_diario:
    df_resumen = pd.DataFrame(st.session_state.resumen_diario)
    st.dataframe(df_resumen, use_container_width=True)
    output_diario = io.BytesIO()
    with pd.ExcelWriter(output_diario, engine='openpyxl') as writer:
        df_resumen.to_excel(writer, sheet_name='Resumen_Diario', index=False)
    output_diario.seek(0)
    st.download_button(label="📥 Descargar Reporte Consolidado Diario", data=output_diario, file_name="Resumen_Diario.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
else:
    st.info("No se registran documentos procesados en la jornada actual.")
