import streamlit as st
import cv2
import numpy as np
from PIL import Image

st.set_page_config(page_title="Smart Beam System", page_icon="🚗")

st.title("🚗 Smart Beam - Sistema de Controle Inteligente")
st.markdown("---")

# --- SIMULAÇÃO DE HARDWARE (Inputs) ---
st.sidebar.header("Configurações do Sensor")

# Simula o valor vindo do sensor crepuscular (0 a 1000 lux)
lux_level = st.sidebar.slider("Nível de Luz Ambiental (Lux)", 0, 1000, 200)

# Abaixo disso, o sistema considera "noite"
threshold_night = 300

# --- LÓGICA DO SISTEMA ---
is_night = lux_level < threshold_night

st.subheader("Status do Sistema")

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "Ambiente",
        "Escuro (Noite)" if is_night else "Claro (Dia)"
    )

with col2:
    status_sensor = (
        "ATIVO"
        if is_night
        else "STANDBY (Inibido pelo Sensor Crepuscular)"
    )

    st.write(f"Estado do Processamento: **{status_sensor}**")

# --- PROCESSAMENTO DE IMAGEM ---
uploaded_file = st.file_uploader(
    "Upload do Feed da Câmera (Imagem/Frame)",
    type=['jpg', 'png', 'jpeg']
)

if uploaded_file is not None:

    image = Image.open(uploaded_file).convert("RGB")
    frame = np.array(image)

    if is_night:

        # Converte para escala de cinza
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

        # Detecta pontos muito brilhantes
        _, thresh = cv2.threshold(
            gray,
            200,
            255,
            cv2.THRESH_BINARY
        )

        # Encontra contornos (compatível com várias versões do OpenCV)
        contours = cv2.findContours(
            thresh,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        contours = contours[0] if len(contours) == 2 else contours[1]

        # Verifica se detectou possíveis faróis
        car_detected = len(contours) > 0

        # Desenha retângulos nos pontos detectados
        for cnt in contours:

            area = cv2.contourArea(cnt)

            # Ignora ruídos pequenos
            if area > 20:

                x, y, w, h = cv2.boundingRect(cnt)

                cv2.rectangle(
                    frame,
                    (x, y),
                    (x + w, y + h),
                    (255, 0, 0),
                    2
                )

        # Mostra imagem processada
        st.image(
            frame,
            caption="Processamento em Tempo Real",
            use_container_width=True
        )

        # Estado do farol
        if car_detected:
            st.error(
                "🚫 FAROL ALTO DESLIGADO (Veículo Detectado)"
            )
        else:
            st.success(
                "🔦 FAROL ALTO ATIVADO"
            )

    else:

        st.image(
            frame,
            caption="Visão Diurna - Processamento Desativado",
            use_container_width=True
        )

        st.info(
            "O Farol Alto permanece desligado durante o dia."
        )

else:
    st.info(
        "Aguardando feed de vídeo/imagem para análise..."
    )
