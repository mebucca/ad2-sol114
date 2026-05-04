import numpy as np
import streamlit as st

#الحقيقة أبداً لا تموت

def sim_muestra(pesos: np.array, n_dados: int, n_muestras: int):
    """
    Retorna la media de la simulación
    """

    prob = pesos / pesos.sum() #prob normalizada
    muestra = np.arange(1, 7) # array de 1 a 6

    resultado = np.random.choice(muestra, size=(n_muestras, n_dados), p=prob)
    return resultado.mean(axis = 1)

def stat_poblacion(pesos: np.array):
    """
    retorna los valores teoricos de nuestra problacion
    """

    prob = pesos / pesos.sum()
    muestra = np.arange(1, 7)

    mu = np.sum(prob * muestra) #media
    var = np.sum((muestra - mu)**2 * prob) #var

    return mu, var

def sacar_prob(pesos: np.array):
    probs = pesos / pesos.sum()

    return probs


def add_footer():
    footer = """
        <style>
            .footer { position: fixed; bottom: 0; left: 0; width: 100%; text-align: center; padding: 10px; font-size: 14px; color: #888; }
        </style>
        <div class="footer">
            <p>© 2026 Tomás Leva - SOL512. Todos los derechos reservados.</p>
        </div>
    """
    st.markdown(footer, unsafe_allow_html=True)