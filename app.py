import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys

import os
import time

st.write("🚀 Начало выполнения скрипта")
st.write(f"Текущая директория: {os.getcwd()}")
st.write(f"Файлы в директории: {os.listdir('.')}")

# Проверка размера файлов
if os.path.exists('model_h2.pkl'):
    size_mb = os.path.getsize('model_h2.pkl') / (1024 * 1024)
    st.write(f"📊 model_h2.pkl: {size_mb:.2f} MB")
else:
    st.error("❌ model_h2.pkl НЕ НАЙДЕН!")

if os.path.exists('scaler.pkl'):
    size_mb = os.path.getsize('scaler.pkl') / (1024 * 1024)
    st.write(f"📊 scaler.pkl: {size_mb:.2f} MB")
else:
    st.error("❌ scaler.pkl НЕ НАЙДЕН!")

st.write("⏳ Загрузка модели...")
start_time = time.time()

# Загрузка модели
try:
    model = joblib.load('model_h2.pkl')
    scaler = joblib.load('scaler.pkl')
    load_time = time.time() - start_time
    st.success(f"✅ Модель загружена за {load_time:.2f} секунд")
except Exception as e:
    st.error(f"❌ Ошибка загрузки модели: {e}")
    st.stop()

st.write("✅ Скрипт продолжает работу...")
# Настройка страницы
st.set_page_config(
    page_title="Цифровой советчик риформинга",
    page_icon="🧪",
    layout="wide"
)

# Заголовок
st.title("🧪 Цифровой советчик реактора паровой конверсии")
st.markdown("---")

# Загрузка модели
@st.cache_resource
def load_model():
    model = joblib.load('model_h2.pkl')
    scaler = joblib.load('scaler.pkl')
    return model, scaler

try:
    model, scaler = load_model()
    st.success("✅ Модель загружена")
except:
    st.error("❌ Ошибка загрузки модели. Убедитесь, что файлы model_h2.pkl и scaler.pkl в той же папке")
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
        # Сравнение с типовым режимом
        base_h2 = predict_h2(450, 3.0, 4.0)
        diff = ((h2 - base_h2) / base_h2) * 100
        st.metric(
            label="📈 Отклонение от базового",
            value=f"{diff:+.2f}%",
            delta=None,
            help="Сравнение с режимом T=450, P=3.0, H:C=4.0"
        )
    
    with col3:
        # Оценка эффективности
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
    
    # График зависимости от H:C
    st.markdown("---")
    st.subheader("📈 Анализ зависимостей")
    
    tab1, tab2, tab3 = st.tabs(["Зависимость от H:C", "Зависимость от T", "3D визуализация"])
    
    with tab1:
        # Фиксируем T и P
        hc_range = np.arange(2.0, 9.1, 0.5)
        h2_values = [predict_h2(T, P, hc) for hc in hc_range]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=hc_range, 
            y=h2_values,
            mode='lines+markers',
            name='H2',
            line=dict(color='firebrick', width=3)
        ))
        fig.add_vline(x=HC, line_dash="dash", line_color="gray")
        fig.add_hline(y=h2, line_dash="dash", line_color="gray")
        
        fig.update_layout(
            title=f"Зависимость H2 от H:C (при T={T}°C, P={P})",
            xaxis_title="H:C (пар:газ)",
            yaxis_title="H2 (мольн. доля)",
            hovermode='x'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        # Фиксируем P и H:C
        t_range = np.arange(400, 501, 10)
        h2_values = [predict_h2(t, P, HC) for t in t_range]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=t_range, 
            y=h2_values,
            mode='lines+markers',
            name='H2',
            line=dict(color='blue', width=3)
        ))
        fig.add_vline(x=T, line_dash="dash", line_color="gray")
        fig.add_hline(y=h2, line_dash="dash", line_color="gray")
        
        fig.update_layout(
            title=f"Зависимость H2 от T (при P={P}, H:C={HC})",
            xaxis_title="Температура T (°C)",
            yaxis_title="H2 (мольн. доля)",
            hovermode='x'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        # 3D график
        t_grid = np.arange(400, 501, 10)
        hc_grid = np.arange(2.0, 9.1, 0.5)
        T_grid, HC_grid = np.meshgrid(t_grid, hc_grid)
        
        H2_grid = np.zeros_like(T_grid)
        for i in range(len(hc_grid)):
            for j in range(len(t_grid)):
                H2_grid[i, j] = predict_h2(T_grid[i, j], P, HC_grid[i, j])
        
        fig = go.Figure(data=[go.Surface(z=H2_grid, x=t_grid, y=hc_grid, colorscale='viridis')])
        fig.update_layout(
            title=f"3D зависимость H2 от T и H:C (при P={P})",
            scene=dict(
                xaxis_title='T (°C)',
                yaxis_title='H:C',
                zaxis_title='H2'
            )
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Таблица сравнения режимов
    st.markdown("---")
    st.subheader("📋 Сравнение с другими режимами")
    
    compare_modes = pd.DataFrame({
        'Режим': ['Текущий', 'Минимальный', 'Средний', 'Максимальный', 'Экономичный'],
        'T (°C)': [T, 400, 450, 500, 425],
        'P': [P, 1.5, 3.0, 4.5, 2.5],
        'H:C': [HC, 2.0, 4.0, 8.0, 6.0]
    })
    
    compare_modes['H2'] = compare_modes.apply(
        lambda row: predict_h2(row['T (°C)'], row['P'], row['H:C']), axis=1
    )
    
    st.dataframe(compare_modes, use_container_width=True)

else:
    st.info("👈 Введите параметры в боковой панели и нажмите 'Рассчитать'")

# Информация о модели
with st.expander("📘 О модели"):
    st.markdown("""
    **Цифровой двойник реактора паровой конверсии природного газа**
    
    **Характеристики модели:**
    - Точность (R²): 0.99994
    - Средняя ошибка: 0.000135
    - Обучающих данных: 5004 строки
    
    **Входные параметры:**
    - T: температура на входе (400-500°C)
    - P: давление (1.5-4.5)
    - H:C: соотношение пар:газ (2.0-9.0)
    
    **Выход:**
    - H2: мольная доля водорода
    """)
