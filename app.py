import streamlit as st
import geopandas as gpd
import folium
import altair as alt
import matplotlib.pyplot as plt
from streamlit_folium import folium_static
from folium.features import GeoJsonTooltip

# Configurar la página
st.set_page_config(
    page_title='Límites de Comunas y Corregimientos en Medellín',
    page_icon='🌍',
    layout='wide',
    initial_sidebar_state='expanded')

# Título de la aplicación
st.title('Límites de Comunas y Corregimientos en Medellín')

# Carga de datos GeoJSON
geojson_file = 'medellin.geojson'  # Asegúrate de ajustar esta ruta según sea necesario
gdf = gpd.read_file(geojson_file)

# Filtrar por Comuna o Corregimiento
st.sidebar.header('Filtros')
comuna_options = gdf['NOMBRE'].unique().tolist()
selected_comunas = st.sidebar.multiselect('Selecciona una o más Comunas o Corregimientos', comuna_options, comuna_options)

# Filtrar por área solo si se seleccionó "Todas"
if not selected_comunas:
    min_area, max_area = gdf['SHAPEAREA'].min(), gdf['SHAPEAREA'].max()

    if min_area != max_area:
        selected_area = st.sidebar.slider('Selecciona un rango de área', min_area, max_area, (min_area, max_area))
        gdf = gdf[(gdf['SHAPEAREA'] >= selected_area[0]) & (gdf['SHAPEAREA'] <= selected_area[1])]
    else:
        st.sidebar.text('No hay suficiente variación en el área para filtrar.')

    # Mostrar histograma de áreas
    st.subheader('Histograma de Áreas')
    chart = alt.Chart(gdf[['NOMBRE', 'SHAPEAREA']]).mark_bar().encode(
        alt.X('NOMBRE:N', title='Comuna o Corregimiento'),
        alt.Y('SHAPEAREA:Q', aggregate='sum', title='Área total')
    )
    st.altair_chart(chart, use_container_width=True)

elif selected_comunas:
    gdf = gdf[gdf['NOMBRE'].isin(selected_comunas)]

# Mostrar estadísticas básicas
st.sidebar.header('Estadísticas')
total_area = gdf['SHAPEAREA'].sum()
total_perimeter = gdf['SHAPELEN'].sum()
mean_area = gdf['SHAPEAREA'].mean()
st.sidebar.write(f'Área total: {total_area:.2f} m²')
st.sidebar.write(f'Perímetro total: {total_perimeter:.2f} m')
st.sidebar.write(f'Área media: {mean_area:.2f} m²')

# Mostrar histograma de áreas
if len(selected_comunas) > 1:
    st.subheader('Histograma de Áreas')
    chart = alt.Chart(gdf[gdf['NOMBRE'].isin(selected_comunas)][['NOMBRE', 'SHAPEAREA']]).mark_bar().encode(
        alt.X('NOMBRE:N', title='Comuna o Corregimiento'),
        alt.Y('SHAPEAREA:Q', aggregate='sum', title='Área total')
    )
    st.altair_chart(chart, use_container_width=True)

# Buscar por nombre
search_term = st.sidebar.text_input('Buscar por nombre')
if search_term:
    gdf = gdf[gdf['NOMBRE'].str.contains(search_term, case=False)]

# Creación del mapa con Folium
st.subheader('Mapa de Límites de Comunas y Corregimientos')
m = folium.Map(location=[6.2442, -75.5812], zoom_start=12)

# Agregar límites al mapa
folium.GeoJson(gdf, tooltip=GeoJsonTooltip(fields=['NOMBRE', 'SHAPEAREA', 'SHAPELEN'], localize=True)).add_to(m)

# Mostrar el mapa en la aplicación
folium_static(m, width=700, height=500)

# Mostrar la tabla de datos en formato de DataFrame, excluyendo la columna 'geometry'
st.subheader('Tabla de Datos Geoespaciales')
st.dataframe(gdf.drop(columns='geometry'))