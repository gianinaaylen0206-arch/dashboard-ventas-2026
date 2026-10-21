# app.py - Dashboard Analítico de Ventas (Modo Seguro a Prueba de Fallos)

import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración básica de la página
st.set_page_config(page_title="Dashboard de Ventas 2026", layout="wide", page_icon="🎀")

# 2. Carga de Datos con Atrapador de Errores (Try/Except)
@st.cache_data
def cargar_datos():
    # Añadimos encoding='utf-8' por si el archivo tiene tildes o que bloqueen la lectura
    return pd.read_csv('ventas.csv', encoding='utf-8')

try:
    df = cargar_datos()
    df['fecha'] = pd.to_datetime(df['fecha'])
except Exception as e:
    # Si hay un error al leer el archivo, te lo mostrará en pantalla grande y roja
    st.error(f"🚨 ERROR AL LEER EL ARCHIVO: {e}")
    st.stop() # Detiene el código aquí para no generar más errores

# 3. Título y Filtros
st.title("🎀 Dashboard Analítico de Ventas 2026")
st.markdown("### 🔍 Filtros de Exploración")

col_f1, col_f2, col_f3 = st.columns(3)
# Abre el espacio de trabajo para la primera columna
with col_f1:
    # Crea un selector desplegable con las regiones únicas ordenadas, agregando la opción 'Todas' al inicio
    region_sel = st.selectbox("📍 Región", ['Todas'] + sorted(df['region'].unique()))
with col_f2:
    # Crea un selector desplegable con las categorías únicas ordenadas, agregando la opción 'Todas' al inicio
    categoria_sel = st.selectbox("🏷️ Categoría", ['Todas'] + sorted(df['categoria'].unique()))
with col_f3:
    #Crea un selector desplegable con los canales únicos ordenados, agregando la opción 'Todos' al inicio
    canal_sel = st.selectbox("🌐 Canal", ['Todos'] + sorted(df['canal'].unique()))

# Lógica de Filtrado
# Crea una copia independiente del DataFrame original para no alterar los datos base durante el filtrado
df_fil = df.copy()

# Verifica si el usuario seleccionó una región específica (distinta a la opción por defecto)
if region_sel != 'Todas': 
    # Sobrescribe el DataFrame filtrado manteniendo únicamente las filas que coincidan con la región seleccionada
    df_fil = df_fil[df_fil['region'] == region_sel]
# Verifica si el usuario seleccionó una categoría específica (distinta a la opción por defecto)
if categoria_sel != 'Todas': 
    # Sobrescribe el DataFrame filtrado manteniendo únicamente las filas que coincidan con la categoría seleccionada
    df_fil = df_fil[df_fil['categoria'] == categoria_sel]
# Verifica si el usuario seleccionó un canal específico (distinto a la opción por defecto)    
if canal_sel != 'Todos': 
    df_fil = df_fil[df_fil['canal'] == canal_sel]

# Protección por si los filtros dejan la tabla vacía
if df_fil.empty:
    st.warning("No hay datos para mostrar con esa combinación de filtros. Intenta con otros.")
    st.stop()

# 4. Tarjetas de Indicadores (KPIs)
st.markdown("---")
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
# Calcula la suma total de ventas netas, formateando el número como moneda y usando puntos para los miles
with kpi1:
    st.metric("💰 Ventas Totales", f"${df_fil['ventas_netas'].sum():,.0f}".replace(",", "."))
# Muestra el total de transacciones contando la cantidad de filas resultantes en el DataFrame filtrado
with kpi2:
    st.metric("🛒 Transacciones", f"{len(df_fil):,}".replace(",", "."))
# Calcula y muestra el ticket promedio de ventas, formateado sin decimales y con puntos de miles
with kpi3:
    st.metric("🎟️ Ticket Promedio", f"${df_fil['ventas_netas'].mean():,.0f}".replace(",", "."))
# Calcula y muestra la calificación promedio de satisfacción del cliente, limitando el resultado a un solo decimal
with kpi4:
    st.metric("⭐ Satisfacción", f"{df_fil['satisfaccion'].mean():.1f} / 10")

# 5. Paleta Rosada Profesional
paleta_rosada = ['#FF1493', '#FF69B4', '#FFB6C1', '#C71585', '#DB7093']

# 6. Visualizaciones (Estructura de 3 Actos)

# ACTO 1: Evolución
st.markdown("### 📌 Evolución Mensual")
# Agrupa el DataFrame por mes y región, sumando las ventas netas y reseteando el índice para convertirlo en tabla
ventas_mes = df_fil.groupby(['mes', 'region'])['ventas_netas'].sum().reset_index()
# Define una lista estática para forzar el ordenamiento cronológico de los meses en el eje X
orden_meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
# Genera un gráfico de líneas utilizando Plotly Express, asignando colores por región y aplicando la paleta y orden personalizados
fig_lineas = px.line(ventas_mes, x='mes', y='ventas_netas', color='region', markers=True, 
                     category_orders={'mes': orden_meses}, color_discrete_sequence=paleta_rosada)
st.plotly_chart(fig_lineas, use_container_width=True)

# ACTO 2: Comparación
st.markdown("### ⚡ Desempeño por Categoría y Canal")
col_g1, col_g2 = st.columns(2)

# Abre el espacio de trabajo para la primera columna (Gráfico de Barras)
with col_g1:
    # Agrupa los datos por categoría sumando las ventas netas
    ventas_cat = df_fil.groupby('categoria')['ventas_netas'].sum().reset_index()
    # Genera un gráfico de barras horizontales, ordenando las barras de menor a mayor venta
    fig_barras = px.bar(ventas_cat.sort_values('ventas_netas'), x='ventas_netas', y='categoria', 
                        orientation='h', color='categoria', color_discrete_sequence=paleta_rosada)
    # Oculta la leyenda lateral del gráfico de barras para un diseño más limpio
    fig_barras.update_layout(showlegend=False)
    # Renderiza el gráfico de barras en Streamlit ocupando el 100% de la columna
    st.plotly_chart(fig_barras, use_container_width=True)
    
with col_g2:
    # Agrupa los datos según el canal de venta, sumando el total de ventas netas
    ventas_canal = df_fil.groupby('canal')['ventas_netas'].sum().reset_index()
    # Genera un gráfico de dona (pastel con un agujero central del 60%) usando colores fijos de la gama
    fig_donut = px.pie(ventas_canal, values='ventas_netas', names='canal', hole=0.6, 
                       color_discrete_sequence=['#FF1493', '#FFB6C1'])
    # Renderiza el gráfico de dona en Streamlit ocupando el 100% de la columna
    st.plotly_chart(fig_donut, use_container_width=True)

# ACTO 3: Sucursales
st.markdown("### ✅  Contribución por Sucursal")
# Agrupa los datos combinando sucursal y región para obtener el detalle de las ventas en puntos físicos
ventas_sucursal = df_fil.groupby(['sucursal', 'region'])['ventas_netas'].sum().reset_index()
# Genera un gráfico de barras agrupadas donde el eje X son las sucursales y se colorean según su región
fig_res = px.bar(ventas_sucursal, x='sucursal', y='ventas_netas', color='region', 
                 color_discrete_sequence=paleta_rosada)
st.plotly_chart(fig_res, use_container_width=True)