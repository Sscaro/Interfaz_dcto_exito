import streamlit as st
import pandas as pd
from scripts.utils import cargar_config
from scripts.utils import create_grupped_df
from scripts.utils import valores_atipicos
from scripts.utils import calculo_variaciones
from scripts.utils import creacion_graficos
from scripts.utils import agrupaciones_calculos
from scripts.utils import cargar_datos

config = cargar_config() # archivo de configuración

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


def sidebar_carga_archivos():
    """
        condifigura y Maneja la carga de archivos en el sidebar
    """
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
        
        # Carga arhcivo margen.
        st.markdown("#### Margen")
        archivo_margen = st.file_uploader("Seleccione el segundo archivo Excel", type=["xlsx", "xls"], key="Margen")
        
        if archivo_margen is not None:
            try:          
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
    """
        Gestiona el contenido principal de la aplicación
        Al principio muestra un ejemplo de que variables debe tener el archivo de ventas.
    
    """

    # Si ya estamos en la vista de análisis por producto, mostrar solo esa sección
    if 'vista_actual' in st.session_state and st.session_state.vista_actual == 'analisis_producto':
        st.success("¡AHORA PUEDES FILTRAR LAS MARCAS PARA REVISAR LOS MATERIALES POR MARCA!")
        seleccionar_marcas_para_analisis()
        return  # Salir de la función para no mostrar nada más
    
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
        mostrar_vista_analisis() # analisis general de las ventas.  
        # Mostrar información cuando se presione el botón continuar

def mostrar_vista_analisis():
    """Vista principal para mostrar resumen y gráficos tras cargar los archivos"""

    # Inicializar variable de estado si no existe
    if 'vista_actual' not in st.session_state:
        st.session_state.vista_actual = 'general'
    
    if st.session_state.vista_actual == 'analisis_producto':
        st.success("¡AHORA PUEDES FILTRAR LAS MARCAS PARA REVISAR LOS MATERIALES POR MARCA.")
        seleccionar_marcas_para_analisis()
        return  # Salir de la función para no mostrar el análisis general

    st.title("Vista de Análisis de Datos")

    df_balance = st.session_state.get("df_balance")
    df_margen = st.session_state.get("df_margen")

    if df_balance is not None and df_margen is not None:


        # Leer y procesar los archivos
        col_usar = config['balanced_score_columnas'].keys()
        tipado_col = {nomcol: tipo[0]  for nomcol, tipo in config['balanced_score_columnas'].items()}

        columnas_fecha = config['columnas_fechas'][0]       
       
        nombre_col = [tipo[1] for tipo in config['balanced_score_columnas'].values()]
        balance = cargar_datos(df_balance,margen=False, 
                               col_usar = col_usar,
                               tipado_col=tipado_col,
                               parse = columnas_fecha,
                               nom_columnas = nombre_col)      
      
        if isinstance(balance, str):
             st.info(balance)
        
        # realizando transformacion para el poner el nombre de los meses        
        mg_sector,mg_marca,mg_material = cargar_datos(df_margen,margen=True)

        
        #Guardando en la session state los dataframes
        st.session_state.df2_balance = balance
        st.session_state.df_margen = mg_sector
        st.session_state.mg_marca = mg_marca
        st.session_state.mg_material = mg_material


        # realiazando limpiza del data frame balance
        #try:
        filtros = config['filtros']
        for key,value in  filtros.items(): ## ciclo para filtrar valores segun la parametrizacion en el archivo de config
            for valor in value:
                balance = balance[balance[key] != valor]
        
        valores_nulos = config['balanced_score_fill']
        for key,value in valores_nulos.items(): # ciclo para completar informacion nula con 0
            if key == 'borrar_na':
                    for columna in value:
                        balance = balance.dropna(subset=[columna])
            else:
                    for columna in value:
                        balance[columna] = balance[columna].fillna(0)
        #except:
        #   st.warning("No se ha filtrado ningún tipo de información!")
     
        # agrupando variables de mes y negocio y sumando las ventas
        #try:
        variables = config['agrupaciones']['agrupa_a']

        balance['mes_agrupado'] = balance['mes'].dt.to_period('M').dt.to_timestamp()
        df_mes_negocio = create_grupped_df(balance, variables['var_categoricas'],variables['var_numericas'] )
        graph_linea = creacion_graficos(df_mes_negocio, x_label='mes_agrupado', y_label='venta_cop', heu='negocio',
        titulo = 'Tendencia de Ventas por Negocio y Mes' )
        ## Grafico de lineas de ventas por negocio
        fig = graph_linea.create_line_chart()
        st.markdown('''###''')
        st.write('Gráfico de lineas para conocer series de tiempo por negocio')
        st.plotly_chart(fig, use_container_width=True)
    
       # except:
       #    st.warning("No encontró columnas para agrupacion!!")

        ## Grafico de barras de margen por negocio
        mg_sector['marge_real_label'] = mg_sector['marge_real_negocio'].round(2) # redondeando los margenes
        graph_bar = creacion_graficos(mg_sector, x_label='negocio', y_label='marge_real_label', heu='negocio',
                               titulo = 'Margen año actual por Negocio' )
        fig = graph_bar.create_bar_chart()
        st.markdown('''###''')
        st.write('Grafico de barra para el margen año actual por negocio')
        st.plotly_chart(fig, use_container_width=True)


        # Actualiza el estado si hay cambios
        var_agrupar = 'negocio'
        var_calculo = 'venta_cop'
        # funcion que agrupa por "negocio"
        df_negocio = create_grupped_df(balance,['mes',var_agrupar],var_num=var_calculo)
        
        # funcion para completar meses
     
        agrupaciones = agrupaciones_calculos(df_negocio)  # instancia de objeto para agrupar.
        st.markdown(f"Resultado **{var_agrupar}** con total de **{var_calculo}**")
        resultado = agrupaciones.tabla_metricas(var_agrupar, var_calculo)  
          
        resultado = agrupaciones.combinar_tablas(mg_sector[[var_agrupar,'marge_real_label']],union= [var_agrupar])                
        
        resultado['total'] = resultado['total'].apply(
        lambda x: agrupaciones.transformaciones(x) )
       
        resultado['media'] = resultado['media'].apply(
        lambda x: agrupaciones.transformaciones(x,mmill=False))
       
        resultado['desviacion'] = resultado['desviacion'].apply(
        lambda x: agrupaciones.transformaciones(x, mmill=False))

        resultado['mediana'] = resultado['mediana'].apply(
        lambda x: agrupaciones.transformaciones(x,mmill=False))

        resultado['minimo'] = resultado['minimo'].apply(
        lambda x: agrupaciones.transformaciones(x) )

        resultado['maximo'] = resultado['maximo'].apply(
        lambda x: agrupaciones.transformaciones(x))       
                
        resultado.sort_values(by='total', ascending=False)
        resultado.set_index("negocio",inplace=True)               
        st.dataframe(resultado, use_container_width=True)
  
        ## analisis por  marca

        variables_a_agrupar= ['marca'] # variables a agrupar
        variables_numericas ={'venta_cop':'sum', 'venta_un':'sum','cod_material': pd.Series.nunique} # agrupa por suma ventas para tabla
        variables_numericas_grafico ={'venta_cop':'mean'} # agrupa por promedio de ventas

        ventas_por_marca_sorted = create_grupped_df(balance,variables_a_agrupar,variables_numericas,agrupa=False,sort_values='venta_cop').reset_index()
        
        ventas_por_marca_sorted_grafico = create_grupped_df(ventas_por_marca_sorted,variables_a_agrupar,variables_numericas_grafico,agrupa=False,sort_values='venta_cop').reset_index()
        del ventas_por_marca_sorted_grafico['index']
        
        variables_a_agrupar_variacion = ['marca','mes'] # SE UTILIZARA MAS ADELANTE
        variables_numericas_ventas = {'venta_cop':'sum','venta_un':'sum'} # SE UTILIZARA MAS ADELANTE
        #variables_numericas_ventas_UN = {'venta_un':'sum','venta_cop':'sum'}
                             
        ventas_marca_agrup_promedio = create_grupped_df(balance,variables_a_agrupar_variacion,variables_numericas_ventas,agrupa=False,sort_values='venta_cop').reset_index()
        
        ventas_promedio  = create_grupped_df(ventas_marca_agrup_promedio,'marca',{'venta_cop':'mean','venta_un':'mean'},agrupa=False,sort_values='venta_cop').reset_index()
        del ventas_promedio['index']
        graph_bar_marca = creacion_graficos(ventas_promedio, x_label='venta_cop', y_label='marca',
                                            heu='marca',
                                            titulo = 'Ventas promedio Marca')
        fig_marca = graph_bar_marca.create_bar_chart()
        st.markdown('''###''')
        st.write('Gráfico de barra ventas promedio por marca')
        st.plotly_chart(fig_marca, use_container_width=True)
        
        ## linea para conocer cuales son los margenes por marca, adicionalmente, 
        ## utiliza una funcion para exlcuir posibles valores atipicos, muestra al
        # usuario cuales fueron las marcas que no se tendran en cuenta
        st.subheader("Resumen analisis por marca:")
        marcas_inciales = set(mg_marca['marca'])
        marge_bruto_ajus_marcas = valores_atipicos(mg_marca,'margen_real')
        marcas_resultantes = set(marge_bruto_ajus_marcas['marca'])

        #ventas_por_marca_sorted['ventas_acumuladas'] = round(ventas_por_marca_sorted['venta_cop_año_ant'].cumsum())
        total_ventas = round(ventas_por_marca_sorted['venta_cop'].sum())
        ventas_por_marca_sorted['venta_cop'] = ventas_por_marca_sorted['venta_cop'].round().astype(float)      

        ventas_por_marca_sorted = pd.merge(ventas_por_marca_sorted,mg_marca[['marca','margen_real']], on = 'marca', how='left')
       
        ## agrupaciones variaciones...
        
        df_variaciones = calculo_variaciones(ventas_marca_agrup_promedio,col_valor = 'venta_cop'
                                             ,col_grupo='marca', col_fecha= 'mes')
        
        ventas_promedio.columns = ['marca','prom_venta_cop','prom_venta_un']
        ventas_por_marca_sorted = pd.merge(ventas_por_marca_sorted,df_variaciones, on = 'marca', how='left').merge(
                            ventas_promedio, on='marca', how = 'left')
               
        ventas_por_marca_sorted['margen_real'] = (ventas_por_marca_sorted['margen_real']/100).round(3)        
        ventas_por_marca_sorted['%_ventas'] = (ventas_por_marca_sorted['venta_cop']) / total_ventas
        del ventas_por_marca_sorted['index']
        ventas_por_marca_sorted = ventas_por_marca_sorted.sort_values(by='venta_cop', ascending=False)
        ventas_por_marca_sorted = ventas_por_marca_sorted.rename(columns={'venta_cop': 'ventas_totales',
                                                                          'venta_un':'venta_totales_un',
                                                                          'cod_material':'num_materiales'})        
       
        ## ordenando las columnas
        orden_columnas = ['marca','ventas_totales','venta_totales_un','prom_venta_cop','prom_venta_un','ventas_ultimo_mes',
                          'margen_real','num_materiales','%_ventas','var_vs_mismo_mes_anterior','var_ultimo_mes','var_ultimo_trimestre',
                          'var_vs_prom_semestre']
        ventas_por_marca_sorted = ventas_por_marca_sorted[orden_columnas]
        ventas_por_marca_sorted.set_index("marca",inplace=True)
        formateado = ventas_por_marca_sorted.style.format({
        'ventas_totales': lambda x: f"{x:,.0f}".replace(",", "."),
        'venta_totales_un':lambda x: f"{x:,.0f}".replace(",", "."),
        'prom_venta_cop':lambda x: f"{x:,.0f}".replace(",", "."),
        'prom_venta_un':lambda x: f"{x:,.0f}".replace(",", "."),
        'ventas_ultimo_mes': lambda x: f"{x:,.0f}".replace(",", "."),    
        '%_ventas': '{:.1%}',   # Formato porcentaje con 2 decimales
        'margen_real': '{:.1%}',
        'var_ultimo_mes': '{:.1%}',  
        'var_ultimo_trimestre': '{:.1%}',
        'var_vs_prom_semestre':  '{:.1%}',  
        'var_vs_mismo_mes_anterior': '{:.1%}'
        })
     
        st.dataframe(formateado, use_container_width=True)
       
        st.write('Marcas que no se tendran en cuenta con ser consideradas atipicas.')
        marge_bruto_ajus_marcas = marge_bruto_ajus_marcas.sort_values(by= 'margen_real')
        st.markdown(f"Marcas consideras atípicas en sus margenes **{marcas_inciales.difference(marcas_resultantes)}**")
        graph_bar_marca = creacion_graficos(marge_bruto_ajus_marcas, x_label='marca', y_label='margen_real', heu='marca',
                               titulo = 'Margen por marca')
        fig_marca = graph_bar_marca.create_bar_chart()


        st.plotly_chart(fig_marca, use_container_width=True)
        
        # capturando las marcas unicas.
        # marcas_disponibles  = ventas_por_marca_sorted['marca'].unique().tolist()
        # marcas_seleccionadas = st.multiselect("Seleccione una o más marcas:", marcas_disponibles)
           # Controlar el flujo basado en el estado actual
     
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            boton_continuar_producto = st.button(
            "CONTINUAR CON EL ANALISIS POR PRODUCTO",         
            on_click=cambiar_a_analisis_producto)
      

def cambiar_a_analisis_producto():
    """Función para cambiar directamente a la vista de análisis por producto"""
    st.session_state.vista_actual = 'analisis_producto'

def seleccionar_marcas_para_analisis():
    
    st.title("Analisis materiales...")
    df_balance = st.session_state.df2_balance 
    mg_sector = st.session_state.df_margen
    mg_marca =  st.session_state.mg_marca
    mg_material = st.session_state.mg_material

  
    marcas_disponibles = sorted(df_balance['marca'].dropna().unique())
    marcas_seleccionadas = st.multiselect(
    "Selecciona una o más marcas para filtrar:",
    options=marcas_disponibles
    )
    variables_a_agrupar_variacion = ['cod_material','nombre_material','PLU','negocio','categoria','marca'] # SE UTILIZARA MAS ADELANTE
    variables_numericas_ventas = {'venta_cop':'mean','venta_un':'mean'} # SE UTILIZARA MAS ADELANTE
                           
    ventas_material = create_grupped_df(df_balance,variables_a_agrupar_variacion,variables_numericas_ventas,agrupa=False,sort_values='venta_cop').reset_index()
    ventas_material = pd.merge(ventas_material,mg_material[['cod_material','margen_real']], on= 'cod_material', how='left').merge(mg_marca[['marca','margen_real']], 
                        on = 'marca', how = 'left',suffixes=('_material', '_marca'))
    print(type(mg_sector))
    #ventas_material = pd.merge(ventas_material,mg_sector, on ='negocio', how='left' )
    del ventas_material['index']
    ventas_material = ventas_material.sort_values(by =  ['marca', 'venta_cop'], ascending=False)

    ventas_material.set_index(['cod_material','nombre_material'], inplace=True)
    if st.button("Clic Marcas seleccionadas"):
        if marcas_seleccionadas:
            st.markdown(f"Marcas Selccionadas **{marcas_seleccionadas}** ")         
            ventas_filtradas = ventas_material[ventas_material['marca'].isin(marcas_seleccionadas)]
            ventas_filtradas['margen_real_material'] = (ventas_filtradas['margen_real_material']/100).round(3)
            ventas_filtradas['margen_real_marca'] = (ventas_filtradas['margen_real_marca']/100).round(3)
            
            ventas_filtradas = ventas_filtradas.rename(columns={'venta_cop': 'venta_prom_cop',
                                                                'venta_un':'venta_prom_un'}) 
        
            
            formateado = ventas_filtradas.style.format({
            'margen_real_material':'{:.1%}',
            'margen_real_marca':'{:.1%}',
            'venta_prom_cop':lambda x: f"{x:,.0f}".replace(",", "."),
            'venta_prom_un':lambda x: f"{x:,.0f}".replace(",", ".")
            })
            st.dataframe(formateado, use_container_width=True)
        else:
            st.warning("No se seleccionaron marcas. Por favor selecciona al menos una marca para filtrar.")
   
def main():
    """Función principal que ejecuta la aplicación"""
    configurar_pagina()
    inicializar_estado()
    sidebar_carga_archivos()
    if 'vista_actual' in st.session_state and st.session_state.vista_actual == 'analisis_producto':
        st.success("¡AHORA PUEDES FILTRAR LAS MARCAS PARA REVISAR LOS MATERIALES POR MARCA!")
        seleccionar_marcas_para_analisis()
    else:
        contenido_principal()
   

if __name__ == "__main__":
    main()