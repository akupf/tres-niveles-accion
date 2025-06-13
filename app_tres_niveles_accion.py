"""
app_tres_niveles_accion.py

Aplicación Streamlit para el Método de los 3 Niveles de Acción
-------------------------------------------------------------
Autor: Usuario (creador y primer aplicador del método)

Descripción
===========
Esta app permite planificar y hacer seguimiento diario de las tareas del Método de los 3 Niveles de Acción:
    - 1 tarea Estratégica (Nivel 1)
    - 2 tareas Operativas (Nivel 2)
    - 3 Micro‑tareas (Nivel 3)

Entradas:
    • Fecha (por defecto hoy)
    • Formulario para registrar las tareas de cada nivel
    • Checkboxes para marcar tareas como completadas

Resultados/Salidas:
    • Tabla con las tareas del día y su estado
    • Resumen de progreso (tareas completadas vs. totales)
    • Registro persistente en un CSV local llamado "registro_tareas.csv"

Cómo ejecutar:
    1. Instalar Streamlit si es necesario:  
       pip install streamlit pandas
    2. Ejecutar la app:  
       streamlit run app_tres_niveles_accion.py

La app crea/actualiza automáticamente el archivo CSV en la carpeta donde se ejecute.
"""

import streamlit as st
import pandas as pd
from datetime import date
from pathlib import Path

# ---------- Configuración de la página ----------
st.set_page_config(
    page_title="Método 3 Niveles de Acción",
    layout="centered",
    initial_sidebar_state="auto",
)

st.title("📋 Método de los 3 Niveles de Acción")
st.write(
    "Planifica tu día con una tarea **Estratégica**, dos **Operativas** y tres **Micro‑tareas**. "
    "Marca las tareas cuando las completes para llevar un seguimiento.")

# ---------- Utilidades ----------

CSV_PATH = Path("registro_tareas.csv")

LEVEL_MAPPING = {
    "Estratégica (1)": 1,
    "Operativa (2‑a)": 2,
    "Operativa (2‑b)": 2,
    "Micro (3‑a)": 3,
    "Micro (3‑b)": 3,
    "Micro (3‑c)": 3,
}

COLUMNS = ["fecha", "nivel", "descripcion", "completada"]


def load_data() -> pd.DataFrame:
    if CSV_PATH.exists():
        df = pd.read_csv(CSV_PATH, parse_dates=["fecha"])
        # Asegurar columnas
        missing_cols = [c for c in COLUMNS if c not in df.columns]
        for col in missing_cols:
            df[col] = None
        return df[COLUMNS]
    return pd.DataFrame(columns=COLUMNS)


def save_data(df: pd.DataFrame):
    df.to_csv(CSV_PATH, index=False)


# ---------- Cargar datos ----------
df_tasks = load_data()

# ---------- Seleccionar fecha ----------
selected_date = st.date_input("Selecciona la fecha", value=date.today())

# Filtrar tareas existentes del día
mask_today = df_tasks["fecha"] == pd.to_datetime(selected_date)

df_today = df_tasks[mask_today].copy()

st.subheader("Tareas para el día")

# Si no hay tareas registradas para la fecha, mostrar formulario para crearlas
if df_today.empty:
    st.info("No hay tareas definidas para esta fecha. Registra tus tareas a continuación.")
    with st.form("form_tareas"):
        t_estrategica = st.text_input("Tarea Estratégica (Nivel 1)")
        t_op1 = st.text_input("Tarea Operativa 1 (Nivel 2‑a)")
        t_op2 = st.text_input("Tarea Operativa 2 (Nivel 2‑b)")
        t_micro1 = st.text_input("Micro‑tarea 1 (Nivel 3‑a)")
        t_micro2 = st.text_input("Micro‑tarea 2 (Nivel 3‑b)")
        t_micro3 = st.text_input("Micro‑tarea 3 (Nivel 3‑c)")
        submitted = st.form_submit_button("Guardar tareas del día")

        if submitted:
            new_rows = [
                {"fecha": selected_date, "nivel": LEVEL_MAPPING["Estratégica (1)"], "descripcion": t_estrategica, "completada": False},
                {"fecha": selected_date, "nivel": LEVEL_MAPPING["Operativa (2‑a)"], "descripcion": t_op1, "completada": False},
                {"fecha": selected_date, "nivel": LEVEL_MAPPING["Operativa (2‑b)"], "descripcion": t_op2, "completada": False},
                {"fecha": selected_date, "nivel": LEVEL_MAPPING["Micro (3‑a)"], "descripcion": t_micro1, "completada": False},
                {"fecha": selected_date, "nivel": LEVEL_MAPPING["Micro (3‑b)"], "descripcion": t_micro2, "completada": False},
                {"fecha": selected_date, "nivel": LEVEL_MAPPING["Micro (3‑c)"], "descripcion": t_micro3, "completada": False},
            ]
            df_tasks = pd.concat([df_tasks, pd.DataFrame(new_rows)], ignore_index=True)
            save_data(df_tasks)
            st.success("¡Tareas guardadas!")
            st.rerun()
else:
    # Mostrar tareas existentes con opción de marcar como completadas
    st.write("Marca las tareas completadas:")
    for idx, row in df_today.iterrows():
        col1, col2 = st.columns([0.08, 0.92])
        with col1:
            done = st.checkbox("", value=row["completada"], key=f"chk_{idx}")
        with col2:
            st.write(f"**{row['descripcion']}**")

        # Actualizar estado si cambia
        if done != row["completada"]:
            df_tasks.at[idx, "completada"] = done
            save_data(df_tasks)

    # Resumen de progreso
    total = len(df_today)
    completed = df_today["completada"].sum()
    st.success(f"Progreso del día: {completed} / {total} tareas completadas")

st.sidebar.header("Historial")

# Mostrar resumen histórico
if not df_tasks.empty:
    df_tasks_sorted = df_tasks.sort_values("fecha", ascending=False)
    # Mostrar las últimas 14 entradas
    st.sidebar.dataframe(df_tasks_sorted.head(14))
else:
    st.sidebar.write("Aún no hay histórico disponible.")
