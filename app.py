import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración inicial de la página
st.set_page_config(
    page_title="Análisis de Vehículos Usados",
    layout="wide",
    page_icon="🚗"
)

# Título de la aplicación
st.title("📊 Dashboard Exploratorio de Vehículos Usados")
st.markdown("---")

# Cargar datos con manejo de errores
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("data/vehicles_us.csv")
        
        # Verificación y limpieza de datos
        if 'model_year' not in df.columns:
            st.error("Error: La columna 'model_year' no existe en el dataset.")
            return None
            
        # Convertir columnas numéricas y manejar valores faltantes
        numeric_cols = ['model_year', 'odometer', 'price']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df.dropna(subset=['model_year', 'odometer', 'price'])
    
    except FileNotFoundError:
        st.error("Error: Archivo 'vehicles_us.csv' no encontrado en la carpeta 'data'")
        return None
    except Exception as e:
        st.error(f"Error al cargar datos: {str(e)}")
        return None

df = load_data()

# Solo continuar si los datos se cargaron correctamente
if df is not None:
    # Sidebar con filtros
    with st.sidebar:
        st.title("🔧 Filtros")
        st.markdown("---")
        
        # Filtro por año
        min_year = int(df["model_year"].min())
        max_year = int(df["model_year"].max())
        selected_years = st.slider(
            "Selecciona el rango de años de fabricación",
            min_value=min_year,
            max_value=max_year,
            value=(min_year, max_year)
        )
        # Filtro por tipo de combustible si existe la columna
        if 'fuel' in df.columns:
            fuel_types = df['fuel'].unique()
            selected_fuels = st.multiselect(
                "Tipo de combustible",
                options=fuel_types,
                default=fuel_types)
        
        # Filtro por condición si existe la columna
        if 'condition' in df.columns:
            conditions = df['condition'].unique()
            selected_conditions = st.multiselect(
                "Condición del vehículo",
                options=conditions,
                default=conditions)

    # Aplicar filtros
    filtered_df = df[df["model_year"].between(selected_years[0], selected_years[1])]
    
    if 'fuel' in df.columns:
        filtered_df = filtered_df[filtered_df['fuel'].isin(selected_fuels)]
    
    if 'condition' in df.columns:
        filtered_df = filtered_df[filtered_df['condition'].isin(selected_conditions)]

    # Sección principal
    st.subheader("📈 Métricas Clave")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Vehículos", len(filtered_df))
    col2.metric("Año promedio", int(filtered_df["model_year"].mean()))
    col3.metric("Precio promedio", f"${filtered_df['price'].mean():,.0f}")
    col4.metric("Km promedio", f"{filtered_df['odometer'].mean():,.0f} km")
    
    st.markdown("---")
    
    # Selector de visualización
    st.subheader("📊 Visualizaciones")
    visualization = st.radio(
        "Tipo de gráfico:",
        options=["Histograma", "Dispersión", "Ambos"],
        horizontal=True,
        label_visibility="collapsed"
    )
    
    # Gráficos
    if visualization in ["Histograma", "Ambos"]:
        st.write("#### Distribución de Kilometraje")
        fig_hist = px.histogram(
            filtered_df,
            x="odometer",
            nbins=30,
            color="fuel" if 'fuel' in df.columns else None,
            labels={"odometer": "Kilometraje"},
            height=500
        )
        st.plotly_chart(fig_hist, use_container_width=True)
    
    if visualization in ["Dispersión", "Ambos"]:
        st.write("#### Relación Precio vs. Kilometraje")
        fig_scatter = px.scatter(
            filtered_df,
            x="odometer",
            y="price",
            color="condition" if 'condition' in df.columns else "fuel",
            hover_name="model" if 'model' in df.columns else None,
            labels={"odometer": "Kilometraje", "price": "Precio"},
            height=500
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Datos filtrados (opcional)
    st.markdown("---")
    if st.checkbox("Mostrar datos filtrados", key="show_data"):
        st.dataframe(
            filtered_df,
            height=300,
            use_container_width=True,
            hide_index=True
        )
else:
    st.warning("No se pueden mostrar visualizaciones debido a problemas con los datos.")