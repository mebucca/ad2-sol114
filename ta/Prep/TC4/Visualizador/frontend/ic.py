from backend.funcs import sim_muestra, stat_poblacion, sacar_prob, add_footer

import numpy as np
import streamlit as st
import matplotlib.pyplot as plt

#书山有路勤为径
st.markdown("<h1 style='text-align: center;'>Intervalos de Confianza</h1>", unsafe_allow_html=True)

add_footer()

st.sidebar.header("Configuración del Dado:")
pesos = [st.sidebar.slider(f"Peso para {i}", 0.0, 10.0, 1.0, key=f"ic_w{i}") for i in range(1,7)] 
pesos = np.array(pesos)

st.sidebar.header("Parámetros del Intervalo:")
n_dados = st.sidebar.number_input("Tamaño de la muestra (n):", 2, 500, 30) 
n_muestras = st.sidebar.number_input("Número de muestras:", 1, 40000, 10000)

alpha_val = {
    "90%": 1.645,
    "95%": 1.960,
    "99%": 2.576
}
nivel_confianza_str = st.sidebar.selectbox("Nivel de Confianza (1 - α):", list(alpha_val.keys()), index=1)
z_val = alpha_val[nivel_confianza_str]

media_sim = sim_muestra(pesos, n_dados, n_muestras)
mu, var = stat_poblacion(pesos)
ee = (var/n_dados)**0.5  # ee
ee = max(ee, 1e-9) # fix si ee = 0'

me = z_val * ee

#formulas
st.markdown("### Construcción del Intervalo")
st.write("El Intervalo de Confianza se define con la Media Muestral ($\overline{X}$) y el Margen de Error (ME):")
col_f1, col_f2 = st.columns(2)
with col_f1:
    st.latex(r"IC = \bar{X} \pm ME")
with col_f2:
    st.latex(r"ME = Z_{\alpha/2} \times \frac{\sigma}{\sqrt{n}}")

#metricas
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Media Real ($\mu$):", f"{mu:.2f}")
with col2:
    st.metric("Error Estándar ($EE$):", f"{ee:.2f}")
with col3:
    st.metric(r"Valor $Z_{\alpha/2}$:", f"{z_val}")
with col4:
    st.metric("Margen de Error ($ME$):", f"{me:.2f}")


# --- GRÁFICOS ESTILO TLC ---
col_plot1, col_plot2 = st.columns(2)

with col_plot1: # Plot de Escala Real
    st.subheader("Distribución de Medias ($\overline{X}$)")
    st.write("Histograma con un Intervalo Muestral de Ejemplo")
    
    fig1, ax1 = plt.subplots()
    ax1.hist(media_sim, bins=30, color="salmon", edgecolor="black", density=True, alpha=0.7)
    
    ax1.axvline(mu, color="black", linestyle="--", linewidth=2, label=f"$\mu$ = {mu:.2f}")
    
    muestra_ejemplo = media_sim[0]
    lim_inf = muestra_ejemplo - me
    lim_sup = muestra_ejemplo + me
    
    hist_counts, _ = np.histogram(media_sim, bins=30, density=True)
    y_pos = np.max(hist_counts) * 0.15 
    
    ax1.plot([lim_inf, lim_sup], [y_pos, y_pos], color="blue", linewidth=3, label=f"IC ($\overline{{X}} \pm ME$)")
    ax1.plot(muestra_ejemplo, y_pos, 'o', color="white", markeredgecolor="blue", markersize=7)
    
    ax1.set_xlim(1, 6)
    ax1.set_xlabel(r"Media Muestral $\overline{X}$")
    ax1.set_ylabel("Densidad")
    ax1.legend()
    st.pyplot(fig1)

with col_plot2: # Plot de Valores Z
    st.subheader("Distribución Estándar ($Z$)")
    st.write(f"Área de Confianza del {nivel_confianza_str}")
    
    # Convertimos todas las muestras a puntajes Z
    punt_z = (media_sim - mu) / ee
    
    fig2, ax2 = plt.subplots()
    ax2.hist(punt_z, bins=30, color="mediumseagreen", edgecolor="black", density=True, alpha=0.6)
    
    # Curva Teórica Normal N(0,1)
    x_z = np.linspace(-4, 4, 100)
    p_z = (1 / np.sqrt(2 * np.pi)) * np.exp(-0.5 * x_z**2)
    ax2.plot(x_z, p_z, 'r', linewidth=2, label='Normal Estándar $N(0,1)$')
    
    # Sombreado de los límites Z(alpha/2)
    x_fill = np.linspace(-z_val, z_val, 100)
    p_fill = (1 / np.sqrt(2 * np.pi)) * np.exp(-0.5 * x_fill**2)
    ax2.fill_between(x_fill, p_fill, color="blue", alpha=0.2, label=f'Confianza {nivel_confianza_str}')
    
    # Líneas límite
    ax2.axvline(-z_val, color="blue", linestyle=":", linewidth=2, label=r"$-Z_{\alpha/2}$")
    ax2.axvline(z_val, color="blue", linestyle=":", linewidth=2, label=r"$+Z_{\alpha/2}$")
    
    ax2.set_xlim(-4, 4)
    ax2.set_xlabel(r"Puntaje $Z = \frac{\overline{X} - \mu}{EE}$")
    ax2.set_ylabel("Densidad")
    ax2.legend()
    st.pyplot(fig2)

st.info(f'**Interpretación Visual:** A la derecha vemos estandarizado lo mismo de la izquierda. Si calculamos el puntaje Z de tu muestra y este cae en el área sombreada azul entre $-Z_{{(\\alpha/2)}}$ y $+Z_{{(\\alpha/2)}}$, significa que tu intervalo $\overline{{X}} \pm ME$ logró atrapar a la media real $\mu$.')
