from backend.funcs import stat_poblacion, add_footer

import streamlit as st
import numpy as np
import plotly.graph_objects as go

# Título
st.markdown("<h1 style='text-align: center;'>Ley de los Grandes Números</h1>", unsafe_allow_html=True)

add_footer()

# --- SIDEBAR ---
st.sidebar.header("Configuración del Dado:")
# Agregamos la key única para lln_w{i} para que no choque con las otras páginas
pesos = [st.sidebar.slider(f"Peso para {i}", 0.0, 10.0, 1.0, key=f"lln_w{i}") for i in range(1,7)] 
pesos = np.array(pesos)

# Parámetro principal (Lo ponemos un poco más alto para ver mejor la convergencia)
n_pasos = st.slider("Número de lanzamientos totales (n):", 50, 10000, 1000, step=50)


# --- CÁLCULOS Y SIMULACIÓN ---
mu, _ = stat_poblacion(pesos) 
probs = pesos / pesos.sum()

# 1. Simulación: Un solo camino de n lanzamientos
lanzamientos = np.random.choice([1, 2, 3, 4, 5, 6], size=n_pasos, p=probs)

# 2. Cálculo de la media acumulada paso a paso
# [x1, (x1+x2)/2, (x1+x2+x3)/3, ...]
medias_acumuladas = np.cumsum(lanzamientos) / np.arange(1, n_pasos + 1)
media_final = medias_acumuladas[-1]


# --- MÉTRICAS ---
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(r"Media Teórica ($\mu$)", f"{mu:.3f}")
with col2:
    st.metric(f"Media Observada (n={n_pasos})", f"{media_final:.3f}")
with col3:
    # Diferencia absoluta entre la realidad y la teoría
    st.metric("Margen de Error Actual", f"{abs(mu - media_final):.4f}")


# --- EXPLICACIÓN TEÓRICA ---
st.info("""
**¿Qué estamos observando?**  
La **Ley de los Grandes Números (LLN)** establece que el promedio de los resultados obtenidos de un gran número de ensayos (tu media observada) debe acercarse al valor esperado (la media teórica $\mu$). 

En términos sencillos: **A mayor tamaño de muestra ($n$), más converge la media empírica a la media real.**
""")


# --- GRÁFICO PLOTLY ---
fig_lgn = go.Figure()

# Línea de la simulación (Azul)
fig_lgn.add_trace(go.Scatter(
    y=medias_acumuladas, 
    mode='lines', 
    name='Media Empírica (Observada)',
    line=dict(color='royalblue', width=2)
))

# Línea de la Verdad (Roja punteada)
fig_lgn.add_trace(go.Scatter(
    y=[mu] * n_pasos, 
    mode='lines', 
    name=rf'Media Teórica ($\mu$)',
    line=dict(color='red', dash='dash', width=3)
))

fig_lgn.update_layout(
    title="Convergencia de la media a largo plazo",
    xaxis_title="Número de lanzamientos (n)",
    yaxis_title="Promedio acumulado",
    yaxis=dict(range=[1, 6]),
    template="plotly_white",
    legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99)
)

st.plotly_chart(fig_lgn, use_container_width=True)

# --- CONCLUSIÓN VISUAL ---
st.write("""
**Interpretación del Gráfico:** 
* Fíjate en la parte izquierda del gráfico (cuando $n$ es pequeño). La línea azul tiene saltos drásticos o "ruido". Esto sucede porque al principio, sacar un solo "6" o un "1" afecta drásticamente el promedio total.
* A medida que te mueves hacia la derecha (aumentando $n$), el peso de un lanzamiento individual se diluye en la inmensidad de los datos, haciendo que la línea azul **se estabilice y converja** hacia la línea roja.
""")