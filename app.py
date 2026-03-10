import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import sys
import time

# Настройка страницы
st.set_page_config(
    page_title="Цифровой советчик риформинга",
    page_icon="🧪",
    layout="wide"
)

# ОТЛАДКА: Пишем каждый шаг
debug = st.empty()
debug.write("🚀 Шаг 1: Скрипт запущен")

# Текущая директория
debug.write(f"📁 Текущая директория: {os.getcwd()}")

# Список файлов
files = os.listdir('.')
debug.write(f"📄 Файлы в директории: {files}")

# Проверка наличия файлов модели
if 'model_h2.pkl' in files:
    size_mb = os.path.getsize('model_h2.pkl') / (1024 * 1024)
    debug.write(f"✅ model_h2.pkl найден, размер: {size_mb:.2f} MB")
else:
    debug.write("❌ model_h2.pkl НЕ НАЙДЕН!")
    st.stop()

if 'scaler.pkl' in files:
    size_mb = os.path.getsize('scaler.pkl') / (1024 * 1024)
    debug.write(f"✅ scaler.pkl найден, размер: {size_mb:.2f} MB")
else:
    debug.write("❌ scaler.pkl НЕ НАЙДЕН!")
    st.stop()

# Загрузка модели
debug.write("⏳ Шаг 2: Загрузка модели...")
start_time = time.time()

try:
    # Загружаем с таймаутом
    model = joblib.load('model_h2.pkl')
    scaler = joblib.load('scaler.pkl')
    load_time = time.time() - start_time
    debug.write(f"✅ Модель загружена за {load_time:.2f} секунд")
except Exception as e:
    debug.write(f"❌ Ошибка загрузки: {str(e)}")
    st.stop()

debug.write("✅ Шаг 3: Модель загружена успешно")

# Функция предсказания
def predict_h2(T, P, HC):
    X_new = pd.DataFrame([[T, P, HC]], columns=['T', 'P', 'H:C'])
    X_scaled = scaler.transform(X_new)
    return model.predict(X_scaled)[0]

# Тестовый расчет
debug.write("🧪 Шаг 4: Тестовый расчет...")
try:
    test_h2 = predict_h2(450, 3.0, 4.0)
    debug.write(f"✅ Тестовый расчет: H2 = {test_h2:.6f}")
except Exception as e:
    debug.write(f"❌ Ошибка тестового расчета: {str(e)}")
    st.stop()

debug.write("🎉 Шаг 5: Все проверки пройдены! Запускаю интерфейс...")
debug.empty()  # убираем отладочные сообщения

# Заголовок
st.title("🧪 Цифровой советчик реактора паровой конверсии")
st.markdown("---")

# Загрузка модели (с кэшированием)
@st.cache_resource
def load_model():
    return joblib.load('model_h2.pkl'), joblib.load('scaler.pkl')

try:
    model, scaler = load_model()
    st.success("✅ Модель загружена")
except Exception as e:
    st.error(f"❌ Ошибка загрузки модели: {str(e)}")
    st.stop()

# Функция предсказания
def predict_h2(T, P, HC):
    X_new = pd.DataFrame([[T, P, HC]], columns=['T', 'P', 'H:C'])
    X_scaled = scaler.transform(X_new)
    return model.predict(X_scaled)[0]

# Боковая панель с вводом параметров
with st.sidebar:
    st.header("⚙️ Параметры режима")
    
    T = st.slider("Температура T (°C)", 400, 500, 450, step=5)
    P = st.slider("Давление P", 1.5, 4.5, 3.0, step=0.1)
    HC = st.slider("Соотношение H:C (пар:газ)", 2.0, 9.0, 4.0, step=0.5)
    
    st.markdown("---")
    st.markdown("### 📊 Диапазоны работы")
    st.markdown("T: 400-500°C")
    st.markdown("P: 1.5-4.5")
    st.markdown("H:C: 2.0-9.0")
    
    calculate = st.button("🚀 Рассчитать", type="primary", use_container_width=True)

# Основная панель
col1, col2, col3 = st.columns(3)

if calculate:
    # Расчет
    h2 = predict_h2(T, P, HC)
    
    # Метрики
    with col1:
        st.metric(
            label="🔥 Выход H2",
            value=f"{h2:.6f}",
            delta=f"{h2-0.75:.6f}",
            help="Мольная доля водорода"
        )
    
    with col2:
        base_h2 = predict_h2(450, 3.0, 4.0)
        diff = ((h2 - base_h2) / base_h2) * 100
        st.metric(
            label="📈 Отклонение от базового",
            value=f"{diff:+.2f}%",
            help="Сравнение с режимом T=450, P=3.0, H:C=4.0"
        )
    
    with col3:
        if h2 > 0.78:
            efficiency = "⚡ Высокий"
            color = "green"
        elif h2 > 0.75:
            efficiency = "📊 Средний"
            color = "orange"
        else:
            efficiency = "📉 Низкий"
            color = "red"
        
        st.markdown(f"### 🎯 Эффективность")
        st.markdown(f"### :{color}[{efficiency}]")

else:
    st.info("👈 Введите параметры в боковой панели и нажмите 'Рассчитать'")
