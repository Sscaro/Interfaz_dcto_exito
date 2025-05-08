import streamlit as st
import pandas as pd
import numpy as np
import io
from scripts.utils import cargar_config
from scripts.utils import dfarchivoAFO
from scripts.utils import create_grupped_df 
from scripts.utils import creacion_graficos 
from scripts.utils import agrupaciones_calculos

config = cargar_config()

def cargar_datos_margen(ruta_margen):
    '''
        Función que carga las diferentes hojas de la consulta AFO con los margenes.
    '''
    lista_hojas = []
    for hojas in config['config_margen'].keys():
        lista_hojas.append(hojas)
        print(ruta_margen)
    margen_sector = dfarchivoAFO(ruta_margen,lista_hojas[0],config['config_margen'][lista_hojas[0]])
    margen_marca = dfarchivoAFO(ruta_margen,lista_hojas[1],config['config_margen'][lista_hojas[1]])
    margen_material = dfarchivoAFO(ruta_margen,lista_hojas[2],config['config_margen'][lista_hojas[2]])
    return margen_sector, margen_marca, margen_material


def configurar_pagina():
    """Configura el estilo y apariencia de la página"""
    st.set_page_config(
        page_title="Análisis Descriptivo Balanced Score",
        layout="wide",
    )

    # Estilos personalizados CSS
    st.markdown("""
    <style>
        .main {
            background-color: #f0f8f0;
        }
        .st-bw {
            background-color: #e6f2e6;
        }
        .css-1aumxhk {
            background-color: #dce8dc;
        }
        .stButton>button {
            background-color: #4CAF50;
            color: white;
            font-weight: bold;
            border: none;
            border-radius: 4px;
            padding: 10px 20px;
            width: 100%;
        }
        .stButton>button:disabled {
            background-color: #cccccc;
            color: #666666;
        }
        .title {
            color: #2e7d32;
            text-align: center;
            padding: 20px;
            font-size: 36px;
            font-weight: bold;
            background-color: #e8f5e9;
            border-radius: 10px;
            margin-bottom: 30px;
            border-left: 8px solid #388e3c;
        }
        .sidebar-content {
            padding: 20px;
            background-color: #e8f5e9;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .instrucciones {
            background-color: #e8f5e9;
            padding: 20px;
            border-radius: 10px;
            border-left: 5px solid #4CAF50;
            margin-bottom: 20px;
        }
    </style>
    """, unsafe_allow_html=True)

def inicializar_estado():
    """Inicializa las variables de estado si no existen"""
    if 'balance_cargado' not in st.session_state:
        st.session_state.balance_cargado = False
    if 'margen_cargado' not in st.session_state:
        st.session_state.margen_cargado = False
    #if 'df1' not in st.session_state:
    #    st.session_state.df1 = None
    #if 'df2' not in st.session_state:
    #    st.session_state.df2 = None

def sidebar_carga_archivos():
    """Maneja la carga de archivos en el sidebar"""
    with st.sidebar:
        st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
        st.markdown("### Carga de Archivos")
        
        # archivo de balance score
        st.markdown("#### Balanced Scored")
        balanced_score = st.file_uploader("Seleccione el primer archivo Excel", type=["xlsx", "xls"], key="balanced_score")
        
        if balanced_score is not None:
            try:
                #df1 = pd.read_excel(balanced_score)
                st.session_state.df_balance = balanced_score
                st.session_state.balance_cargado = True
                st.success(f"✅ balanced_score cargado exitosamente: {balanced_score.name}")
            except Exception as e:
                st.error(f"Error al cargar el archivo 1: {e}")
                st.session_state.balance_cargado = False
        else:
            st.warning("⚠️ El balanced_score aún no ha sido cargado")
        
        # margen
        st.markdown("#### Margen")
        archivo_margen = st.file_uploader("Seleccione el segundo archivo Excel", type=["xlsx", "xls"], key="Margen")
        
        if archivo_margen is not None:
            try:
                #df2 = pd.read_excel(archivo2)
                st.session_state.df_margen = archivo_margen
                st.session_state.margen_cargado = True
                st.success(f"✅ Margen cargado exitosamente: {archivo_margen.name}")
            except Exception as e:
                st.error(f"Error al cargar el margen: {e}")
                st.session_state.margen_cargado = False
        else:
            st.warning("⚠️ El Margen aún no ha sido cargado")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Mostrar el estado de los archivos
        st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
        estado_archivos = f"""
        ### Estado de carga:
        - Balance Scored: {"✅ Cargado" if st.session_state.balance_cargado else "⚠️ Pendiente"}
        - Margen {"✅ Cargado" if st.session_state.margen_cargado else "⚠️ Pendiente"}
        """
        st.markdown(estado_archivos)
        st.markdown('</div>', unsafe_allow_html=True)

def contenido_principal():
    """Gestiona el contenido principal de la aplicación"""
    
    st.markdown('<div class="title">ANÁLISIS DESCRIPTIVO BALANCE SCORE</div>', unsafe_allow_html=True)
    
    st.markdown("### Bienvenido al sistema de Análisis Descriptivo Balance Score")
    
    # Comprobamos si están cargados ambos archivos
    ambos_archivos_cargados = st.session_state.get("balance_cargado", False) and st.session_state.get("margen_cargado", False)
    
    if not ambos_archivos_cargados:
        st.markdown("""
        ### Instrucciones:
        
        1. El archivo del balanced score debe contener las siguientes columnas:
           - mes (formato entero del 1 al 12)
           - region
           - negocio (formato texto)
           - marca (formato texto)
           - codigo_sap (formato texto)
           - peso (formato numerico)
           - venta_cop_año_ant (formato numerico)
           - venta_cop_año_act (formato numerico)
           - venta_un_ant (formato numerico)
           - venta_un_act (formato numerico)
        2. El archivo del margen score debe contener la siguiente informacion:
           - Margen bruto por negocio
           - Margen bruto por marca
           - Margen bruto por material
           
        Debes cargar los dos archivos en la parte izquierda para continuar.
                              
        3. La aplicación realizará automáticamente:
           - Eliminación de registros con valores nulos en región y negocio
           - Eliminación de registros con 'Otros Oper Cciales' en la columna negocio
           - Imputación de valores nulos en las columnas de ventas con 0
           - eliminará del archivo de margen tanto por marca y material valores atípicos
           
        4. Una vez cargado el archivo, podrás:
           - Ver análisis de ventas por negocio y mes
           - Comparar ventas entre diferentes periodos
           - Analizar ventas por región
           - Ver el ranking de las mejores marcas
           - Explorar los datos originales
        """, unsafe_allow_html=True)

        st.subheader("Ejemplo de formato esperado del archivo balanced score:")
        example_data = {
            'mes': [1, 2, 3, 4],
            'region': ['R Pereira', 'R Cali', 'R Ibague', 'R Medellin'],
            'negocio': ['Café', 'Cárnico', 'Chocolates', 'Pastas'],
            'marca': ['Noel', 'Colcafé', 'Doria', 'Jet'],
            'ean': ['7702007062724', '7702025149520', '7702025103904', '7702025149292'],
            'codigo_sap': ['1062365', '1062363', '1001573', '1001563'],
            'peso': [59, 60, 45, 30],
            'plu': ['Si', 'nan', 'Si', 'nan'],
            'venta_cop_año_ant': [1000000, 2000000, 1500000, 3000000],
            'venta_cop_año_act': [1200000, 1800000, 1650000, 3300000],
            'venta_un_ant': [100, 200, 150, 300],
            'venta_un_act': [120, 180, 165, 330]
        }
        example_df = pd.DataFrame(example_data)
        st.dataframe(example_df, use_container_width=True)

    # Botón para continuar (siempre visible, pero deshabilitado si no están los archivos)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        boton_continuar = st.button(
            "CONTINUAR CON EL ANÁLISIS",
            disabled=not ambos_archivos_cargados
        )

    # Acción al presionar el botón
    if boton_continuar:
        st.success("¡Ambos archivos están cargados! Presione 'CONTINUAR' para avanzar con el análisis.")
        mostrar_vista_analisis()      
    # Mostrar información cuando se presione el botón continuar

def mostrar_vista_analisis():
    """Vista principal para mostrar resumen y gráficos tras cargar los archivos"""

    st.title("Vista de Análisis de Datos")

    df_balance = st.session_state.get("df_balance")
    df_margen = st.session_state.get("df_margen")

    if df_balance is not None and df_margen is not None:


        # Leer y procesar los archivos
        col_usar = config['balanced_score_columnas'].keys()
        tipado_col = {nomcol: tipo[0]  for nomcol, tipo in config['balanced_score_columnas'].items()}
        nombre_col = [tipo[1] for tipo in config['balanced_score_columnas'].values()]
        balance = pd.read_excel(df_balance,usecols=col_usar,dtype=tipado_col)
        balance.columns = nombre_col
        mg_sector,mg_marca,mg_material = cargar_datos_margen(df_margen)
        #df2 = pd.read_excel(archivo2)

        # 👉 Aquí puedes aplicar tus modificaciones a df1 y df2
        # Por ejemplo:
        balance = balance.dropna(subset=["region", "negocio"])
        balance = balance[balance["negocio"] != "Otros Oper Cciales"]

        columnas_ventas = ["venta_cop_año_ant", "venta_cop_año_act", "venta_un_ant", "venta_un_act"]
        for col in columnas_ventas:
            if col in balance.columns:
                balance[col] = balance[col].fillna(0)

        # Guardarlos en session_state para otras funciones si es necesario
        # st.session_state["df_balance1"] = balance
        # st.session_state["df_margen_negocio"] = mg_sector
        # st.session_state["df_margen_marca"] = mg_marca
        # st.session_state["df_margen_material"] = mg_material

        # agrupando variables de mes y negocio y sumando las ventas
        df_mes_negocio = create_grupped_df(balance, ['mes','negocio'],['venta_cop_año_ant'])



        graph_linea = creacion_graficos(df_mes_negocio, x_label='mes', y_label='venta_cop_año_ant', heu='negocio',
                               titulo = 'Tendencia de Ventas por Negocio y Mes' )
        ## Grafico de lineas de ventas por negocio
        fig = graph_linea.create_line_chart()
        st.markdown('''###''')
        st.write('Grafico de linea para conocer comportamiento')
        st.plotly_chart(fig, use_container_width=True)


        ## Grafico de barras de margen por negocio
        mg_sector['marge_real_label'] = mg_sector['marge_real'].round(2) # redondeando los margenes
        graph_bar = creacion_graficos(mg_sector, x_label='negocio', y_label='marge_real_label', heu='negocio',
                               titulo = 'Margen por Negocio' )
        fig = graph_bar.create_bar_chart()
        st.markdown('''###''')
        st.write('Grafico de barra para el margen por negocio')
        st.plotly_chart(fig, use_container_width=True)


        # Actualiza el estado si hay cambios
        var_agrupar = 'negocio'
        var_calculo = 'venta_cop_año_ant'
            
        df_negocio = create_grupped_df(balance,['mes',var_agrupar],var_num=var_calculo)
        agrupaciones = agrupaciones_calculos(df_negocio)  # instancia de objeto para agrupar.
        st.markdown(f"Resultado **{var_agrupar}** con total de **{var_calculo}**")
        resultado = agrupaciones.tabla_metricas(var_agrupar, var_calculo)           
        resultado = agrupaciones.combinar_tablas(mg_sector[[var_agrupar,'marge_real_label']],union= [var_agrupar])                
        resultado.sort_values(by='total', ascending=False)
        st.dataframe(resultado, use_container_width=True)
  


        ## analisis por  marca

        variables_a_agrupar= ['marca'] # variables a agrupar
        variables_numericas ={'venta_cop_año_ant':'sum', 'codigo_sap': pd.Series.nunique}
        
        ventas_por_marca_sorted = create_grupped_df(balance,variables_a_agrupar,variables_numericas,agrupa=False,sort_values='venta_cop_año_ant').reset_index()


        graph_bar_marca = creacion_graficos(ventas_por_marca_sorted, x_label='venta_cop_año_ant', y_label='marca',
                                             heu='marca',
                               titulo = 'Ventas por Marca - Año Anterior')
        
        fig_marca = graph_bar_marca.create_bar_chart()
        st.markdown('''###''')
        st.write('Grafico de barra para el margen por negocio')
        st.plotly_chart(fig_marca, use_container_width=True)
        
        #ventas_por_sector_sorted = pd.merge(ventas_por_sector_sorted,margen_sector[['negocio','marge_real_label']], on = 'negocio', how='left')
        #ventas_por_sector_sorted.sort_values(by='total_ventas', ascending=False)


        st.subheader("Resumen del margen negocio:")
        st.dataframe(mg_sector.head(), use_container_width=True)

    else:
        st.warning("No se encontraron los archivos cargados.")



def main():
    """Función principal que ejecuta la aplicación"""
    configurar_pagina()
    inicializar_estado()
    sidebar_carga_archivos()
    contenido_principal()
   

if __name__ == "__main__":
    main()