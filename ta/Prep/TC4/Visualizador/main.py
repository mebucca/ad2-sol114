import streamlit as st

#page objs
welcome = st.Page(
    "frontend/welcome.py", 
    title="Introducción y Tutorial",
    default=True
)


clt_sim = st.Page(
    "frontend/tlc.py", 
    title="Teorema del Límite Central"
)

ic_sim = st.Page(
    "frontend/ic.py", 
    title="Intervalos de Confianza"
)

lln_sim = st.Page(
    "frontend/lln.py", 
    title="Ley de los Grandes Números"
)

estimator_guide = st.Page(
    "frontend/estimador.py", 
    title="Estimado y Estimador"
)

ejercicios = st.Page(
    "frontend/code/ejercicios.py", 
    title="Practica con R"
)

#sidebar
pg = st.navigation(
    {
    "Bienvenida": [welcome],
    "Simuladores": [lln_sim, clt_sim, estimator_guide, ic_sim],
    "Ejercicios": [ejercicios],
})


st.set_page_config(page_title="SOL512 - Prep. TC4", page_icon="📊", layout="wide")
pg.run()