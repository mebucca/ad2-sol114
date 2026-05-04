from backend.funcs import add_footer
from streamlit_ace import st_ace

import streamlit as st
import subprocess

add_footer()

# --- Configuración de Ejercicios ---
EJERCICIOS = [
    {
        "id": 1,
        "nivel": "🟢 Básico",
        "titulo": "Calculando la Media Esperada ($\mu$)",
        "enunciado": """
            Un dado está trucado de modo que el **6** tiene una probabilidad de 0.5, 
            mientras que las otras caras tienen 0.1 cada una.
            
            Crea un vector llamado `caras` (1 al 6) y un vector `p` con estas probabilidades. 
            Calcula la media esperada y guárdala en la variable **`resultado`**.
        """,
        "esperado": "4.5",
        "pista": "Usa sum(caras * p) para obtener la esperanza matemática.",
        "solucion": "caras <- 1:6\np <- c(0.1, 0.1, 0.1, 0.1, 0.1, 0.5)\nresultado <- sum(caras * p)"
    },
    {
        "id": 2,
        "nivel": "🟡 Intermedio",
        "titulo": "El Error Estándar ($EE$)",
        "enunciado": """
            Si sabemos que la desviación estándar poblacional ($\sigma$) es **1.70** y lanzamos **49** dados por muestra ($n$), 
            ¿cuál es el Error Estándar de la distribución de medias muestrales? 
            
            Calcula este valor y guárdalo en la variable **`resultado`**.
        """,
        "esperado": f"{round(1.7/49**0.5, 4)}",
        "pista": "La fórmula es SE = sigma / sqrt(n).",
        "solucion": "resultado <- 1.7 / sqrt(49)"
    },
    {
        "id": 3,
        "nivel": "🔴 Avanzado",
        "titulo": "Construcción de Intervalos de Confianza",
        "enunciado": """
            > ⚠️ **Nota Importante:** Los Intervalos de Confianza **NO** entrarán en la TC4, pero es un excelente ejercicio de preparación para el futuro.

            Tomaste una muestra y obtuviste una media muestral $\\bar{X} = 15.2$.
            Sabes que tu error estándar calculado es $EE = 0.8$. 
            
            Utilizando un nivel de confianza del **95%** (asume que $Z_{\\alpha/2} = 1.96$), 
            calcula el **límite superior** del intervalo de confianza y guárdalo en la variable **`resultado`**.
        """,
        "esperado": "16.768",
        "pista": "El límite superior es la media muestral MÁS el margen de error (Z * EE).",
        "solucion": "media_muestral <- 15.2\nZ <- 1.96\nEE <- 0.8\nresultado <- media_muestral + (Z * EE)"
    }
]

def run_r_full(user_code):
    full_code = f"""
    {user_code}
    cat("\\n---VALIDACION---\\n")
    if(exists('resultado')) cat(as.character(round(resultado, 4)))
    """
    try:
        proc = subprocess.run(
            ['Rscript', '-e', full_code],
            capture_output=True, text=True, timeout=5
        )
        return proc.stdout, proc.stderr
    except Exception as e:
        return None, str(e)

# --- UI de Streamlit ---
st.title("Practiquemos con R")
st.markdown("Resuelve los desafíos para validar tus conocimientos estadísticos directamente escribiendo código.")

# Selector de ejercicio
nombres_ej = [f"{e['nivel']} - {e['titulo']}" for e in EJERCICIOS]
seleccion = st.selectbox("Elige un desafío:", range(len(EJERCICIOS)), format_func=lambda x: nombres_ej[x])
ej = EJERCICIOS[seleccion]

# --- Manejo del Estado (Si el usuario ha fallado) ---
clave_fallo = f"fallo_{ej['id']}"
if clave_fallo not in st.session_state:
    st.session_state[clave_fallo] = False

# Panel de Instrucciones
with st.container(border=True):
    st.subheader(ej["titulo"])
    st.markdown(ej["enunciado"])
    
    col_pista, col_rendirse = st.columns(2)
    with col_pista:
        with st.expander("💡 Ver pista"):
            st.info(ej["pista"])
            
    # Creamos un espacio vacío reservado para el botón de solución
    espacio_solucion = col_rendirse.empty()
    
    # Si en la memoria guardamos que ya falló en intentos previos, dibujamos el botón de rendirse
    if st.session_state[clave_fallo]:
        with espacio_solucion.expander("👀 Me rindo, ver solución"):
            st.write(f"El valor esperado era: **{ej['esperado']}**")
            st.write("Código de ejemplo:")
            st.code(ej["solucion"], language="r")

# Editor de Código
st.markdown("### 💻 Tu Código R")
codigo = st_ace(language="r", theme="monokai", height=250, key=f"editor_r_{ej['id']}")

col_btn1, col_btn2 = st.columns([1, 4])
with col_btn1:
    ejecutar = st.button("🏃 Ejecutar Código", type="primary")

# --- AREA DE CONSOLA ---
st.write("### 🖥️ Consola de Salida")
contenedor_consola = st.empty() 

if ejecutar:
    with st.spinner("Corriendo R..."):
        stdout, stderr = run_r_full(codigo)
        
        # 1. Separar el output de la consola de la validación
        if stdout and "---VALIDACION---" in stdout:
            partes = stdout.split("---VALIDACION---")
            output_consola = partes[0].strip()
            resultado_final = partes[1].strip()
        else:
            output_consola = stdout
            resultado_final = None

        # 2. Mostrar la consola (stdout y stderr)
        with contenedor_consola.container():
            if stderr:
                st.error("⚠️ Error detectado:")
                st.code(stderr, language="r")
            
            if output_consola:
                st.code(output_consola, language="r")
            elif not stderr:
                st.caption("El código se ejecutó correctamente pero no imprimió nada en consola. Recuerda que la validación ocurre revisando la variable 'resultado'.")

        # 3. Validar si el resultado es correcto 
        if resultado_final == ej["esperado"]:
            st.success("🎉 ¡Resultado correcto! Has cumplido el objetivo.")
            st.balloons()
            st.session_state[clave_fallo] = False  # Reiniciamos el estado si lo logra
            espacio_solucion.empty() # Escondemos el botón de solución si lo logra
            
        else:
            # Marcamos en la sesión que falló para que el botón se mantenga visible
            st.session_state[clave_fallo] = True 
            
            # Mostramos el mensaje de error correspondiente
            if resultado_final:
                st.warning(f"Obtuviste el valor: {resultado_final}. No es el esperado, ¡sigue intentando o revisa las pistas!")
            elif not stderr:
                st.info("No se encontró la variable `resultado`. Asegúrate de guardar tu respuesta final en esa variable.")
            
            # Inyectamos el botón de solución INMEDIATAMENTE en el espacio vacío que reservamos arriba
            with espacio_solucion.expander("👀 Me rindo, ver solución"):
                st.write(f"El valor esperado era: **{ej['esperado']}**")
                st.write("Código de ejemplo:")
                st.code(ej["solucion"], language="r")