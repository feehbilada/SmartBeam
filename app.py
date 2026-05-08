import streamlit as st
import cv2
import numpy as np
from PIL import Image
import os
from datetime import datetime

# ---------------- CONFIGURAÇÃO ----------------

st.set_page_config(
    page_title="Smart Beam System",
    page_icon="🚗",
    layout="centered"
)

st.title("🚗 Smart Beam - Sistema de Controle Inteligente")
st.markdown("---")

# ---------------- PASTAS DE FEEDBACK ----------------

os.makedirs("feedback/correct", exist_ok=True)
os.makedirs("feedback/wrong", exist_ok=True)

# ---------------- SENSOR CREPUSCULAR ----------------

st.sidebar.header("Configurações do Sensor")

lux_level = st.sidebar.slider(
    "Nível de Luz Ambiental (Lux)",
    0,
    1000,
    200
)

# Valor abaixo do qual considera noite
threshold_night = 300

# Define se é noite
is_night = lux_level < threshold_night

# ---------------- STATUS DO SISTEMA ----------------

st.subheader("Status do Sistema")

col1, col2 = st.columns(2)

with col1:

    st.metric(
        "Ambiente",
        "🌙 Escuro (Noite)" if is_night else "☀️ Claro (Dia)"
    )

with col2:

    status_system = (
        "ATIVO"
        if is_night
        else "DESATIVADO PELO SENSOR CREPUSCULAR"
    )

    st.metric(
        "Estado do Sistema",
        status_system
    )

# ---------------- UPLOAD DA IMAGEM ----------------

uploaded_file = st.file_uploader(
    "Upload do Feed da Câmera",
    type=["jpg", "jpeg", "png"]
)

# ---------------- PROCESSAMENTO ----------------

if uploaded_file is not None:

    image = Image.open(uploaded_file).convert("RGB")

    frame = np.array(image)

    # ==================================================
    # MODO NOTURNO
    # ==================================================

    if is_night:

        # Converte para escala de cinza
        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_RGB2GRAY
        )

        # Detecta pontos luminosos fortes
        _, thresh = cv2.threshold(
            gray,
            200,
            255,
            cv2.THRESH_BINARY
        )

        # Detecta contornos
        contours = cv2.findContours(
            thresh,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        contours = contours[0] if len(contours) == 2 else contours[1]

        # Variável de detecção
        car_detected = False

        # Analisa os contornos encontrados
        for cnt in contours:

            area = cv2.contourArea(cnt)

            # Ignora pequenos ruídos
            if area > 20:

                car_detected = True

                x, y, w, h = cv2.boundingRect(cnt)

                # Desenha retângulo
                cv2.rectangle(
                    frame,
                    (x, y),
                    (x + w, y + h),
                    (255, 0, 0),
                    2
                )

        # Exibe imagem processada
        st.image(
            frame,
            caption="Processamento Noturno",
            use_container_width=True
        )

        # ---------------- CONTROLE DO FAROL ----------------

        if car_detected:

            st.error(
                "🚫 VEÍCULO NA DIREÇÃO CONTRÁRIA DETECTADO\n\n"
                "Farol alto DESLIGADO automaticamente para evitar cegueira temporária."
            )

            headlight_status = "LOW_BEAM"

        else:

            st.success(
                "🔦 Nenhum veículo detectado.\n\n"
                "Farol alto ATIVADO."
            )

            headlight_status = "HIGH_BEAM"

        # ---------------- FEEDBACK DA IA ----------------

        st.markdown("---")
        st.subheader("Feedback da Detecção")

        col_ok, col_wrong = st.columns(2)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        with col_ok:

            if st.button("✅ IA Acertou"):

                cv2.imwrite(
                    f"feedback/correct/{timestamp}.jpg",
                    cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                )

                st.success("Feedback salvo como CORRETO")

        with col_wrong:

            if st.button("❌ IA Errou"):

                cv2.imwrite(
                    f"feedback/wrong/{timestamp}.jpg",
                    cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                )

                st.warning("Feedback salvo como ERRO")

    # ==================================================
    # MODO DIURNO
    # ==================================================

    else:

        st.image(
            frame,
            caption="Modo Diurno",
            use_container_width=True
        )

        st.info(
            "☀️ Ambiente claro detectado.\n\n"
            "Farol alto DESLIGADO automaticamente pelo sensor crepuscular."
        )

        headlight_status = "OFF"

# ---------------- SEM IMAGEM ----------------

else:

    st.info(
        "Aguardando imagem para análise..."
    )
