# ---------------------------------------------------IMPORTS------------------------------------------------------#
# python -m streamlit run tu_archivo.py
# streamlit run herramienta.py
import calendar
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import seaborn as sns
import plotly.figure_factory as ff
from streamlit_option_menu import option_menu
from plotly.subplots import make_subplots
from datetime import datetime

# ------------------------------------------Título de la página------------------------------------------------------#
# Configuración de la página
st.set_page_config(layout="wide")

st.markdown(
    """
    <style>
    .title {
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)
st.markdown("<h1 class='title'>MARKETING MIX MODELING</h1>",
            unsafe_allow_html=True)

# ---------------------------------------------------SIDEBAR------------------------------------------------------#

# Imagen de la barra lateral (logo)
st.sidebar.image(
    'https://mms.businesswire.com/media/20231031341381/en/1930065/22/GlobalLogo_NTTDATA_FutureBlue_RGB.jpg', use_column_width=True)

# Load the dataset


@st.cache_data
def load_data():
    data = pd.read_excel('bbdd_mmm_20240111.xlsx')
    return data


data = load_data()

# ------------------------ ---------------------------PÁGINA STREAMLIT------------------------------------------------------#

# navegacion
with st.sidebar:
    menu = option_menu(
        menu_title=None,
        options=["Business", "Model", "Simulation", "Optimization"],
        icons=["book", "lock", "play", "check", "settings"],
        menu_icon="🏠",
        default_index=0,
        orientation="vertical",
    )

st.markdown("<hr>", unsafe_allow_html=True)  # Insert horizontal line

# Conditional for the opcion "Negocio"
if menu == "Business":
    # col1, col2 = st.columns([2, 2])  # Esto crea dos columnas

   # Crear métricas por canal
    # Ajusta el número de columnas según sea necesario
    col1, col2, col4 = st.columns([1, 2, 2])

    with col1:
        # Encuentra el último año en tus datos
        ultimo_año = data['fecha'].dt.year.max()
        año_anterior = ultimo_año - 1

        # Calcula la inversión total y las ventas para el último año y el año anterior
        columnas_inversion = [
            'publicidad_inversion_tv_comercial_pre_covid',
            'publicidad_inversion_tv_comercial_post_covid',
            'publicidad_inversion_exterior_comercial',
            'publicidad_inversion_radio_comercial',
            'publicidad_inversion_prensa_comercial',
            'publicidad_inversion_brandformance_total',
            'publicidad_inversion_agencias_on_comercial_total',
        ]
        # Total de inversiones para el último año y el año anterior
        inversion_ultimo_año = data.loc[data['fecha'].dt.year ==
                                        ultimo_año, columnas_inversion].sum().sum()
        inversion_año_anterior = data.loc[data['fecha'].dt.year ==
                                          año_anterior, columnas_inversion].sum().sum()

    # Calcula la diferencia en inversión y ventas
        diferencia_inversion = inversion_ultimo_año - inversion_año_anterior

        col3 = st.columns(1)  # Esto crea una sola columna

        st.metric(
            "Inversión del último año",
            f"{inversion_ultimo_año:,.2f} €",
            f"{diferencia_inversion:,.2f} € ({diferencia_inversion / inversion_año_anterior * 100:.2f}%)"
            if inversion_año_anterior else "N/A"
        )
        st.write("Inversión por canal respecto al año anterior")

        # Total de inversiones para el último año y el año anterior por canal
        inversiones_ultimo_año = data.loc[data['fecha'].dt.year ==
                                          ultimo_año, columnas_inversion].sum()
        inversiones_año_anterior = data.loc[data['fecha'].dt.year ==
                                            año_anterior, columnas_inversion].sum()

        diferencias_inversion = inversiones_ultimo_año - inversiones_año_anterior

        # Mostrar las métricas por canal
        for canal in columnas_inversion:
            st.metric(
                canal,
                f"{inversiones_ultimo_año[canal]:,.2f} €",
                f"{diferencias_inversion[canal]:,.2f} € ({diferencias_inversion[canal] / inversiones_año_anterior[canal] * 100:.2f}%)"
                if inversiones_año_anterior[canal] else "N/A"
            )

        # Total de ventas para el último año y el año anterior
        ventas_ultimo_año = data.loc[data['fecha'].dt.year ==
                                     ultimo_año, 'negocio_ventas_presencial'].sum()
        ventas_año_anterior = data.loc[data['fecha'].dt.year ==
                                       año_anterior, 'negocio_ventas_presencial'].sum()

        # Calcula la diferencia en ventas
        diferencia_ventas = ventas_ultimo_año - ventas_año_anterior

        st.metric(
            "Ventas del último año",
            f"{ventas_ultimo_año:,.2f} €",
            f"{diferencia_ventas:,.2f} € ({diferencia_ventas / ventas_año_anterior * 100:.2f}%)"
            if ventas_año_anterior else "N/A"
        )

    # col2, col3 = st.columns([2, 2])

    with col2:
      # Opción para alternar en Streamlit
        option_investment = st.selectbox(
            'Choose the investment view:',
            ('Total investment', 'Investment by channels')
        )

        # Lógica condicional para crear y mostrar los gráficos basados en la opción seleccionada
        if option_investment == 'Total investment':
            # Group by year and sum the investments
            investment_by_year = data.set_index('fecha')[[
                'publicidad_inversion_tv_comercial_pre_covid', 'publicidad_inversion_tv_comercial_post_covid',
                'publicidad_inversion_exterior_comercial', 'publicidad_inversion_radio_comercial',
                'publicidad_inversion_prensa_comercial', 'publicidad_inversion_brandformance_total',
                'publicidad_inversion_agencias_on_comercial_total',]].resample('Y').sum()  # 'Y' es para agrupar por año

        # Total investment per year rounded to two decimals
            investment_by_year['total_investment'] = investment_by_year.sum(
                axis=1)
            investment_by_year = investment_by_year.round(2)

        # Create a bar chart with Plotly
            fig_investment_per_year = go.Figure()
            fig_investment_per_year.add_trace(go.Bar(
                x=investment_by_year.index.year,  # Extrae el año de la fecha
                y=investment_by_year['total_investment'],
                text=investment_by_year['total_investment'],
                textposition='auto',  # Establece el color de las barras
            ))

        # Style the chart
            fig_investment_per_year.update_layout(
                title='Investment over years',
                xaxis_title='Year',
                yaxis_title='Total Investment',
                # Logarithmic scale for large ranges of values
                yaxis=dict(type='log'),
                plot_bgcolor='white',  # Colors of plot background
                title_x=0.5  # Center the chart title
            )
            # Show the investment chart
            st.plotly_chart(fig_investment_per_year)

        elif option_investment == 'Investment by channels':
            # Group by year and sum the investments by channels
            investment_by_year_and_channel = data.set_index(
                'fecha').resample('Y').sum()

            # Crear un gráfico de barras apiladas con Plotly
            fig_investment_by_channels = go.Figure()

            # Lista de medios para el desglose
            channels = [
                'publicidad_inversion_tv_comercial_pre_covid', 'publicidad_inversion_tv_comercial_post_covid',
                'publicidad_inversion_exterior_comercial', 'publicidad_inversion_radio_comercial',
                'publicidad_inversion_prensa_comercial', 'publicidad_inversion_brandformance_total',
                'publicidad_inversion_agencias_on_comercial_total',]

            colors_channels = [
                # azul marino;
                "#1f77b4",  # azul moderado
                "#84c9ff",  # naranja
                "#2cb49c",  # verde
                "#fab5b6",  # rosa
                "#fb3131",  # rojo
                "#7f7f7f",  # gris
                "#17becf",  # azul claro


            ]
            # Añadir cada medio como una barra apilada
            for i, medio in enumerate(channels):
                fig_investment_by_channels.add_trace(go.Bar(
                    x=investment_by_year_and_channel.index.year,
                    y=investment_by_year_and_channel[medio],
                    name=medio,
                    # Establece el color correspondiente
                    marker_color=colors_channels[i]
                ))

            # Estilizar el gráfico
            fig_investment_by_channels.update_layout(
                barmode='stack',  # Modo apilado para las barras
                title='Investment by Medium Over Years',
                xaxis_title='Year',
                yaxis_title='Investment by Medium',
                plot_bgcolor='white',
                title_x=0.5  # Centrar el título del gráfico
            )

            # Show the investment by channels chart
            st.plotly_chart(fig_investment_by_channels)

        # ---------------------OMIE----------------------------------#

        # Obtén una lista de los años únicos presentes en tus datos
        unique_years = sorted(data['fecha'].dt.year.unique(), reverse=True)

        # Crea una lista para guardar las selecciones de años
        selected_years = []

        selected_years = st.multiselect(
            'Select years to compare:', unique_years, default=unique_years[1:])

        # Crea la figura de Plotly para el gráfico de líneas
        fig_omie_month_years = go.Figure()

        # Para cada año seleccionado, filtra los datos, agrupa por mes, calcula la media del precio OMIE y añade una traza al gráfico
        for year in selected_years:
            filtered_data = data[data['fecha'].dt.year == year]
            monthly_prices = filtered_data.groupby(filtered_data['fecha'].dt.month)[
                'precio_omie'].mean()

            fig_omie_month_years.add_trace(go.Scatter(
                x=monthly_prices.index,  # El índice después de agrupar será el mes
                y=monthly_prices.values,
                mode='lines+markers',  # Líneas con marcadores
                name=f'Precio OMIE {year}'
            ))

        # Actualiza la disposición del gráfico
        fig_omie_month_years.update_layout(
            title='Valoration of OMIE price per years',
            xaxis_title='Mes',
            yaxis_title='Precio OMIE (€/MWh)',
            xaxis=dict(tickmode='array', tickvals=list(range(1, 13)),
                       ticktext=list(calendar.month_abbr[1:])),
            yaxis=dict(tickformat=".2f"),
            hovermode='x',  # Muestra el tooltip basado en el eje x
            title_x=0.5  # Centrar el título del gráfico
        )

        # Muestra el gráfico en Streamlit
        st.plotly_chart(fig_omie_month_years)

    with col4:
        # Asegúrate de que 'fecha' sea tipo datetime
        data['fecha'] = pd.to_datetime(data['fecha'])

        # Obtén una lista de los años únicos presentes en tus datos
        unique_years = sorted(data['fecha'].dt.year.unique(), reverse=True)

        # Crea un multiselect para que el usuario pueda seleccionar varios años
        selected_years = st.multiselect(
            'Select years to display:', unique_years, default=unique_years[:2])

        # Crea la figura de Plotly para el gráfico de barras
        fig_sales_month_years = go.Figure()

        # Para cada año seleccionado, filtra los datos, agrupa por mes y suma las ventas
        for year in selected_years:
            # Filtra los datos para el año seleccionado
            filtered_data = data[data['fecha'].dt.year == year]

            # Agrupa los datos por mes y suma las ventas
            monthly_sales = filtered_data.groupby(filtered_data['fecha'].dt.month)[
                'negocio_ventas_presencial'].sum()

            # Añade la traza para el gráfico de barras de las ventas mensuales
            fig_sales_month_years.add_trace(go.Bar(
                # Nombres abreviados de los meses
                x=[calendar.month_abbr[month]
                    for month in monthly_sales.index],
                y=monthly_sales.values,
                name=f'Sales {year}'
            ))

        # Actualiza la disposición del gráfico
        fig_sales_month_years.update_layout(
            title='Monthly sales by selected years',
            xaxis_title='Month',
            yaxis_title='Total Sales',
            barmode='group',  # Agrupa las barras en lugar de apilarlas
            yaxis=dict(tickformat=".2f"),
            title_x=0.5  # Centrar el título del gráfico
        )

        # Muestra el gráfico en Streamlit
        st.plotly_chart(fig_sales_month_years)

        # ---------------------TOTAL-SALES----------------------------------#
        # Agrupar los datos por año y sumar las ventas (solo negoio_ventas_presencial)
        sales_by_year = data.set_index('fecha')[['negocio_ventas_presencial']].resample(
            'Y').sum()  # 'Y' es para agrupar por año

        # Calcular el total de ventas por año redondeando a dos decimales
        sales_by_year['total_sales'] = sales_by_year.sum(axis=1)
        sales_by_year = sales_by_year.round(2)

        # Crear un gráfico de barras con Plotly
        fig_sales_per_year = go.Figure()
        fig_sales_per_year.add_trace(go.Bar(
            x=sales_by_year.index.year,  # Extrae el año de la fecha
            y=sales_by_year['total_sales'],
            text=sales_by_year['total_sales'],
            textposition='auto',  # Establece el color de las barras
        ))

        # Estilizar el gráfico
        fig_sales_per_year.update_layout(
            title='Sales over years',
            xaxis_title='Year',
            yaxis_title='Total Sales',
            # Escala logarítmica para grandes rangos de valores
            yaxis=dict(type='log'),
            plot_bgcolor='white',  # Color de fondo del gráfico
            title_x=0.5  # Centrar el título del gráfico
        )
        # Mostrar el gráfico en StreamliT DE SALES
        st.plotly_chart(fig_sales_per_year)

    # ----------------------INVESTMENTS-TIME-MONTH---------------------------------#
    # Selector de fechas para filtrar datos
    start_date, end_date = st.date_input(
        'Select date range', [data['fecha'].min(), data['fecha'].max()])
    start_date = datetime(start_date.year, start_date.month, start_date.day)
    end_date = datetime(end_date.year, end_date.month, end_date.day)

    # Filtrar datos por rango de fechas
    filtered_data = data[(data['fecha'] >= start_date)
                        & (data['fecha'] <= end_date)]

    # Multiselect para elegir las inversiones a mostrar
    selected_investments = st.multiselect('Select investment channels:',
                                        ['publicidad_inversion_tv_comercial_pre_covid',
                                        'publicidad_inversion_tv_comercial_post_covid',
                                        'publicidad_inversion_exterior_comercial',
                                        'publicidad_inversion_radio_comercial',
                                        'publicidad_inversion_prensa_comercial',
                                        'publicidad_inversion_brandformance_total',
                                        'publicidad_inversion_agencias_on_comercial_total'],
                                        default=['publicidad_inversion_tv_comercial_pre_covid',
                                                'publicidad_inversion_tv_comercial_post_covid',
                                                'publicidad_inversion_exterior_comercial',
                                                'publicidad_inversion_radio_comercial',
                                                'publicidad_inversion_prensa_comercial',
                                                'publicidad_inversion_brandformance_total',
                                                'publicidad_inversion_agencias_on_comercial_total'
                                                ])

    # Inicializar la figura de Plotly
    fig_investment_channels_date = make_subplots(
        specs=[[{"secondary_y": True}]])

    # Añadir trazas para cada tipo de inversión seleccionado
    for investment in selected_investments:
        # Agregar traza de línea para la inversión total por fecha
        fig_investment_channels_date.add_trace(go.Scatter(x=filtered_data['fecha'],
                                                        y=filtered_data[investment],
                                                        name=investment,
                                                        mode='lines',
                                                        stackgroup='one'),  # se usa para crear el área sombreada
                                            secondary_y=False)

    # Actualizar los layouts del gráfico
    fig_investment_channels_date.update_layout(title='Investment by channels over time',
                                            xaxis_title='Fecha',
                                            yaxis_title='Inversión Total',
                                            hovermode='x unified',
                                            title_x=0.5)

    # Mostrar gráfico
    st.plotly_chart(fig_investment_channels_date, use_container_width=True)
    # ----------------------------INVESTMENTS-LORENA-YEAR---------------------------------#

    # Agregar multiselect para años
    selected_years = st.multiselect(
        'Select years to compare:', sorted(data['fecha'].dt.year.unique()), default=[2021])

    # Agregar multiselect para canales de inversión en publicidad
    selected_channels = st.multiselect('Select investment channels:',
                                    ['publicidad_inversion_tv_comercial_pre_covid',
                                        'publicidad_inversion_tv_comercial_post_covid',
                                        'publicidad_inversion_exterior_comercial',
                                        'publicidad_inversion_radio_comercial',
                                        'publicidad_inversion_prensa_comercial',
                                        'publicidad_inversion_brandformance_total',
                                        'publicidad_inversion_agencias_on_comercial_total'],
                                    default=['publicidad_inversion_tv_comercial_pre_covid',
                                                'publicidad_inversion_tv_comercial_post_covid',
                                                'publicidad_inversion_exterior_comercial',
                                                'publicidad_inversion_radio_comercial',
                                                'publicidad_inversion_prensa_comercial',
                                                'publicidad_inversion_brandformance_total',
                                                'publicidad_inversion_agencias_on_comercial_total'
                                                ], key = '3')
                                                

    # Calcular la diferencia porcentual de inversión para los canales seleccionados
    investment_diff_percentages = {}
    for channel in selected_channels:
        channel_data = []
        for year in selected_years:
            current_year_investment = data.loc[data['fecha'].dt.year == year, channel].sum(
            )
            previous_year_investment = data.loc[data['fecha'].dt.year == (
                year - 1), channel].sum()
            percentage_diff = ((current_year_investment - previous_year_investment) /
                            previous_year_investment) * 100 if previous_year_investment != 0 else 0
            channel_data.append(percentage_diff)
        investment_diff_percentages[channel] = channel_data

    fig = go.Figure()
    increase_color = 'green'
    decrease_color = 'GREY'

    for channel in selected_channels:
        for i, year in enumerate(selected_years):
            # Si el porcentaje es negativo, se muestra hacia la izquierda en rojo, si no, hacia la derecha en verde
            color = increase_color if investment_diff_percentages[channel][i] > 0 else decrease_color
            # Se agrega una barra por cada año seleccionado
            fig.add_trace(go.Bar(
                y=[channel + ' ' + str(year)],
                x=[investment_diff_percentages[channel][i]],
                name=str(year),
                orientation='h',
                marker_color=color
            ))

    fig.update_layout(
        barmode='relative',
        title='Yearly Percentage Difference in Advertising Investment by Channel',
        xaxis_title='Percentage Difference',
        # Mostrar porcentajes
        xaxis_tickformat='%{value}%',
        yaxis_title='Channel',
        xaxis=dict(
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor='black'),
        yaxis=dict(
            autorange='reversed'  # Esto es para que el gráfico comience desde arriba hacia abajo
        ))

    st.plotly_chart(fig)

    # Waterfall chart para mostral la diferencia en inversión por año y canal
    # Agregar multiselect para años añadir ke

    selected_years = st.multiselect('Select years to compare:', sorted(
        data['fecha'].dt.year.unique()), key='1', default=[2020, 2019])

    # Agregar multiselect para canales de inversión en publicidad
    selected_channels = st.multiselect('Select investment channels:',
                                    ['publicidad_inversion_tv_comercial_pre_covid',
                                        'publicidad_inversion_tv_comercial_post_covid',
                                        'publicidad_inversion_exterior_comercial',
                                        'publicidad_inversion_radio_comercial',
                                        'publicidad_inversion_prensa_comercial',
                                        'publicidad_inversion_brandformance_total',
                                        'publicidad_inversion_agencias_on_comercial_total'],
                                    default=['publicidad_inversion_tv_comercial_pre_covid',
                                                'publicidad_inversion_tv_comercial_post_covid',
                                                'publicidad_inversion_exterior_comercial',
                                                'publicidad_inversion_radio_comercial',
                                                'publicidad_inversion_prensa_comercial',
                                                'publicidad_inversion_brandformance_total',
                                                'publicidad_inversion_agencias_on_comercial_total'
                                                ], key='2')

    # Calcular la diferencia porcentual de inversión para los canales seleccionados
    investment_diff_percentages = {}
    for channel in selected_channels:
        channel_data = []
        for year in selected_years:
            current_year_investment = data.loc[data['fecha'].dt.year == year, channel].sum(
            )
            previous_year_investment = data.loc[data['fecha'].dt.year == (
                year - 1), channel].sum()
            percentage_diff = ((current_year_investment - previous_year_investment) /
                            previous_year_investment) * 100 if previous_year_investment != 0 else 0
            channel_data.append(percentage_diff)
        investment_diff_percentages[channel] = channel_data

    # Crear un DataFrame con los datos de la diferencia porcentual de inversión
    investment_diff_percentages_df = pd.DataFrame(
        investment_diff_percentages, index=selected_years)
    # Transponer el DataFrame para que los canales sean las columnas y los años los índices
    investment_diff_percentages_df = investment_diff_percentages_df.T

    # Crear un gráfico de barras apiladas con Plotly
    fig = go.Figure()
    # Lista de colores para las barras
    colors = [
        "#1f77b4",  # azul moderado
        "#84c9ff",  # naranja
        "#2cb49c",  # verde
        "#fab5b6",  # rosa
        "#fb3131",  # rojo
        "#7f7f7f",  # gris
        "#17becf",  # azul claro
    ]
    # Lista de años
    years = investment_diff_percentages_df.columns
    # Lista de canales
    channels = investment_diff_percentages_df.index
    # Agregar cada canal como una barra apilada
    for i, channel in enumerate(channels):
        fig.add_trace(go.Bar(
            x=years,
            y=investment_diff_percentages_df.loc[channel],
            name=channel,
            marker_color=colors[i]  # Establecer el color correspondiente
        ))

    # Estilizar el gráfico
    fig.update_layout(
        barmode='stack',  # Modo apilado para las barras
        title='Yearly Percentage Difference in Advertising Investment by Channel',
        xaxis_title='Year',
        yaxis_title='Percentage Difference',
        yaxis=dict(tickformat=".2f"),
        plot_bgcolor='white',
        title_x=0.5,  # Centrar el título del gráfico

    )

    # Mostrar el gráfico en Streamlit
    st.plotly_chart(fig)


# Condicional para las otras opciones del menú
elif menu == "Model":
    st.write("Aquí va el contenido de Modelo")
elif menu == "Simulation":
    st.write("Aquí va el contenido de Simulación")
elif menu == "Optimization":
    st.write("Aquí va el contenido de Optimización")
