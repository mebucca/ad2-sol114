from backend.funcs import sim_muestra, stat_poblacion, add_footer

import numpy as np
import streamlit as st
import matplotlib.pyplot as plt

st.markdown("<h1 style='text-align: center;'>Estimando, Estimador y Estimado</h1>", unsafe_allow_html=True)

add_footer()

st.sidebar.header("Configuración del Dado:")
pesos = [st.sidebar.slider(f"Peso para {i}", 0.0, 10.0, 1.0, key=f"est_w{i}") for i in range(1, 7)]
pesos = np.array(pesos)

st.sidebar.header("Parámetro de la Muestra:")
n_dados = st.sidebar.number_input("Tamaño de una sola muestra (n):", 2, 500, 100)

mu, var = stat_poblacion(pesos)
ee = (var / n_dados)**0.5
ee = max(ee, 1e-9)

#sim
prob = pesos / pesos.sum()
muestra_unica = np.random.choice(np.arange(1, 7), size=n_dados, p=prob)
estimado_puntual = muestra_unica.mean()


# --- CONCEPTOS CLAVE ---
st.markdown("### 1. La Teoría: ¿Cuál es la diferencia?")
st.write("A menudo usamos estas palabras como sinónimos, pero en inferencia estadística tienen significados muy distintos. Vamos a definirlos usando nuestro dado trucado:")

col1, col2, col3 = st.columns(3)

with col1:
    st.info("**1. El Estimando (Parámetro)**")
    st.write("Es aquello que *queremos conocer* (el parámetro poblacional real).")
    st.latex(r"\beta = \mu")
    st.write(f"En nuestro dado, la verdadera media teórica si lo lanzáramos infinitas veces es **{mu:.2f}**.")

with col2:
    st.success("**2. El Estimador (La Función)**")
    st.write("Es la *fórmula matemática* o regla que aplicamos a los datos para intentar adivinar el estimando.")
    st.latex(r"f(\text{datos}) = \frac{\sum_{i=1}^{n} X_i}{n}")
    st.write("Aquí, nuestro estimador es la **Media Muestral** ($\overline{X}$).")

with col3:
    st.warning("**3. El Estimado (El Valor)**")
    st.write("Es el número específico (la *estimación puntual*) que obtenemos al aplicar el estimador a una **única muestra**.")
    st.latex(r"\hat{\beta} = \bar{x}")
    st.write("Nuestro estimado obtenido de *esta* muestra particular.")

# --- MOSTRANDO LA MUESTRA ÚNICA ---
st.markdown("---")
st.markdown("### 2. Nuestro Experimento (La Estimación Puntual)")
st.write(f"Supongamos que lanzamos nuestro dado trucado **{n_dados} veces** (n={n_dados}).")
st.write(f"**Tus lanzamientos:** {muestra_unica[:15]}... *(y {n_dados - 15} más)*")

st.metric(r"Tu Estimado Puntual ($\hat{\beta}$)", f"{estimado_puntual:.2f}", delta=f"{estimado_puntual - mu:.2f} (Error respecto al estimando real)", delta_color="inverse")

st.write("¿Qué tanto podemos confiar en nuestro **estimado** basado en *esta* muestra en particular? Sabemos que la media muestral es un estimador insesgado (en promedio acierta), pero en una sola muestra, **la estimación puntual casi nunca es exactamente igual al parámetro poblacional.**")

st.markdown("---")
st.markdown("### 3. La Distribución Muestral del Estimador")
st.write("Para saber qué tan confiable es nuestro estimado puntual, necesitamos conocer la distribución muestral de nuestro estimador. Vamos a simular 10,000 muestras más para ver dónde cayó *tu estimado* en el panorama general.")

medias_sim = sim_muestra(pesos, n_dados, 10000)

fig, ax = plt.subplots(figsize=(10, 5))

ax.hist(medias_sim, bins=30, color="gold", edgecolor="goldenrod", density=True, alpha=0.5, label="Simulación de 10,000 estimados")

x = np.linspace(mu - 4*ee, mu + 4*ee, 200)
p = (1 / (ee * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x - mu) / ee)**2)
ax.plot(x, p, 'r-', linewidth=2, label=r"Teoría (Normal $\mu, \sigma/\sqrt{n}$)")

ax.axvline(mu, color="black", linestyle="--", linewidth=2, label=f"Estimando real ($\mu$ = {mu:.2f})") #linea estimado

y_estimado = (1 / (ee * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((estimado_puntual - mu) / ee)**2) #posicion estimado
ax.plot(estimado_puntual, y_estimado, 'o', color="red", markersize=10, markeredgecolor="black", label=rf"Tu Estimado ($\hat{{\beta}}$ = {estimado_puntual:.2f})")
# Línea vertical desde el punto hasta el eje X
ax.vlines(estimado_puntual, ymin=0, ymax=y_estimado, color="red", linestyle=":", linewidth=2)

ax.set_title("Tu Estimado dentro de la Distribución Muestral")
ax.set_xlabel(r"Posibles valores del Estimador ($\overline{X}$)")
ax.set_ylabel("Densidad")
ax.legend(loc="upper left")

st.pyplot(fig)

st.info("💡 **Conclusión:** Como puedes ver, cuando cuentas con **UNA** sola muestra, obtienes solo el punto rojo de arriba. Al ser un solo número, no refleja la incertidumbre. Es por esto que en estadística no nos tomamos las estimaciones puntuales *tan en serio*, y preferimos construir **Intervalos de Confianza** (que puedes explorar en la siguiente sección).")