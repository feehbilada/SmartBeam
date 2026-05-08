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
threshold_night = 300 # Abaixo disso, o sistema considera "noite"

# --- LÓGICA DO SISTEMA ---
is_night = lux_level < threshold_night

st.subheader("Status do Sistema")
col1, col2 = st.columns(2)

with col1:
    st.metric("Ambiente", "Escuro (Noite)" if is_night else "Claro (Dia)")
with col2:
    status_sensor = "ATIVO" if is_night else "STANDBY (Inibido pelo Sensor Crepuscular)"
    st.write(f"Estado do Processamento: **{status_sensor}**")

# --- PROCESSAMENTO DE IMAGEM ---
uploaded_file = st.file_uploader("Upload do Feed da Câmera (Imagem/Frame)", type=['jpg', 'png', 'jpeg'])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    frame = np.array(image)
    
    if is_night:
        # Converte para escala de cinza e aplica threshold para achar pontos de luz intensos
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
        
        # Encontra contornos (possíveis faróis de outros carros)
        contours, _ = cv2.find_contours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        car_detected = len(contours) > 0
        
        # Desenha os alertas na imagem
        for cnt in contours:
            (x, y, w, h) = cv2.boundingRect(cnt)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

        st.image(frame, caption="Processamento em Tempo Real", use_column_width=True)
        
        if car_detected:
            st.error("🚫 FAROL ALTO DESLIGADO (Veículo Detectado)")
        else:
            st.success("🔦 FAROL ALTO ATIVADO")
            
    else:
        st.image(frame, caption="Visão Diurna - Processamento de Farol Desativado", use_column_width=True)
        st.info("O Farol Alto permanece desligado durante o dia.")

else:
    st.info("Aguardando feed de vídeo/imagem para análise...")
