from backend.funcs import sim_muestra, stat_poblacion, sacar_prob, add_footer

import numpy as np
import streamlit as st
import matplotlib.pyplot as plt

#玉树临风
st.markdown("<h1 style='text-align: center;'>Teorema del Límite Central</h1>", unsafe_allow_html=True)

add_footer()

st.sidebar.header("Configuración del Dado:")

#st.sb.slider(texto, min, max, default)
pesos = [st.sidebar.slider(f"Peso para {i}", 0.0, 10.0, 1.0) for i in range(1,7)] #4to parametro a key=f["w{i}"]
n_dados = st.sidebar.number_input(f"Número de dados por muestra (n):", 0, 100, 30) 
n_muestras = st.sidebar.number_input(f"Número de muestras:", 1, 40000, 10000)

pesos = np.array(pesos)

media_sim = sim_muestra(pesos, n_dados, n_muestras)
mu, var = stat_poblacion(pesos)

ee = (var/n_dados)**0.5

col1, col2 = st.columns(2)
with col1:
    st.metric("Media Teórica ($\mu$):", f"{mu:.2f}")

with col2:
    st.metric("Error estándar ($\\frac{{\sigma}}{{\sqrt{{n}}}}$):", f"{ee:.2f}")


col3, col4 = st.columns(2)

with col3: #plot probs
    st.subheader("Distribución poblacional")
    st.write("Estas son las probabilidad de tu dado trucado")
    fig1, ax1 = plt.subplots()
    ax1.bar([1, 2, 3, 4, 5, 6], sacar_prob(pesos), color="skyblue", edgecolor="black")
    ax1.set_ylim(0, 1)
    ax1.set_xlabel("Cara")
    ax1.set_ylabel("Probabilidad")
    st.pyplot(fig1)

with col4: #prob muestras
    st.subheader("Distribución Muestral")
    st.write(f"Distribución de {n_muestras} medias (n={n_dados})")
    fig2, ax2 = plt.subplots()
    ax2.hist(media_sim, bins=30, color="salmon", edgecolor="black", density=True)
    ax2.set_xlim(1, 6)
    ax2.set_xlabel("Media Muestral")
    st.pyplot(fig2)

st.info(f'Podemos ver que a pesar de por cuanto truquemos el dado, se mantendrá esa forma de distribución "normal". Solo realmente cambia su forma al reducir el tamaño muestral')


st.markdown("### ¿Y cómo se ve si la estandarizamos en Z?")

#tabla Z

punt_z = (media_sim - mu) / ee
fig3, ax3 = plt.subplots(figsize=(12, 4))
ax3.hist(punt_z, bins=30, color="mediumseagreen", edgecolor="black", density=True, alpha=0.7)

x = np.linspace(-4, 4, 100)
p = (1 / np.sqrt(2 * np.pi)) * np.exp(-0.5 * x**2)
ax3.plot(x, p, 'r', linewidth=2, label='Normal Estándar $N(0,1)$')

ax3.set_title("Distribución de Puntajes Z")
ax3.set_xlabel(r"Puntaje $Z = \frac{\bar{X} - \mu}{SE}$")
ax3.set_ylabel("Densidad")
ax3.set_xlim(-4, 4) 
ax3.legend()

st.pyplot(fig3)

st.link_button("Recomendadísimo este video para entender bien los TLC!", "https://www.youtube.com/watch?v=zeJD6dqJ5lo")

#fix:

# def resetear():
#     for i in range(1,7):
#         st.session_state[f"w{i}"] = 1.0

# for i in range(1, 7):
#     st.session_state[f"w{i}"] = 5.0 if i == 5 else 1.0

# st.sidebar.button("Reset a un dado justo", on_click=resetear, type="primary") por algun motivo lo brickea, chao