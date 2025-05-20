'''
Este modulo permite parametrizar 
'''
import yaml
import os
import pandas as pd
import plotly.express as px
import numpy as np

def cargar_config():
    """
    Carga el archivo de configuración (config.yml) en un objeto de Python.
    El archivo de configuración debe estar en la carpeta "Insumos" en el directorio de trabajo actual.
    Luego llama a la función menu() para mostrar el menú principal.
    return: None
    """
    ruta_config  = os.path.join(os.getcwd(),'insumos', 'config.yml')
    with open(ruta_config, 'r',encoding='utf-8') as file:
        config = yaml.safe_load(file)
    return config

config = cargar_config()  # cargando el archivo de configuraciones para todas las funciones que la usen.

def limpiar_datos(df):
    """
    Realiza la limpieza inicial de los datos
    ARG: df data frame    
    """

    columnas_esperadas = set(config['balanced_score_columnas'].keys())
  
    # Normalizar los nombres de las columnas (eliminar espacios, minúsculas, etc.)
    df.columns = [col.strip() for col in df.columns]
    
    # Verificar que todas las columnas esperadas existan
    columnas_faltantes = columnas_esperadas - set(df.columns)
    if columnas_faltantes:
        return (f"Advertencia: Faltan las siguientes columnas: {columnas_faltantes}")
    else:              
        # Reemplazar NaN con 0 (para el caso de ventas no reportadas)
        df.fillna(0, inplace=True)            
        return None

def cargar_datos(ruta_archivo,margen=False, col_usar=None, tipado_col = None,parse = None, nom_columnas=None):
    """
    Carga los datos desde un archivo Excel
    arg: ruta_archivo: str
        margen by defect False,
        col_usar by defect None
        tipado_col by defect none
    """  
   
    if margen== False:        
        try:
            df = pd.read_excel(ruta_archivo,
                            usecols=col_usar,
                            dtype=tipado_col,
                            )
            valida = limpiar_datos(df)
            if parse is not None:
                df[parse] = pd.to_datetime(df[parse])           
            if nom_columnas is not None:
                df.columns = nom_columnas           
            
            if valida is None:
                return df
            else:
                return valida
            
        except Exception as e:
            print(f"Error al cargar el archivo: {e}")
            return None
    else:
        try:
            lista_hojas = []
            for hojas in config['config_margen'].keys():
                lista_hojas.append(hojas)
        
            margen_sector = dfarchivoAFO(ruta_archivo,lista_hojas[0],config['config_margen'][lista_hojas[0]])
            margen_marca = dfarchivoAFO(ruta_archivo,lista_hojas[1],config['config_margen'][lista_hojas[1]])
            margen_material = dfarchivoAFO(ruta_archivo,lista_hojas[2],config['config_margen'][lista_hojas[2]])
            return margen_sector, margen_marca, margen_material
        except Exception as e:
            print(f"Error al cargar el archivo: {e}")
            return None

def completar_meses_faltantes(df, var_categorica, var_numericas):
    """
    Asegura que todas las marcas tengan registros para todos los meses.
    Si falta algún mes, se asume que las ventas fueron 0.

    ARG: df: data frame 
        var_categorica: str columna categorica
        var_numericas: lista var numericas
    """
    # Obtener lista única de marcas
    categorias = df[var_categorica].unique()
    
    # Crear un DataFrame completo con todas las combinaciones de marca y mes
    meses = range(1, 13)  # Meses 1 al 12
    datos_completos = []
    var_calculos = {clave: 0 for clave in var_numericas} # para marcar cada variable numerica con 0
    for items in categorias:
        for mes in meses:
            fila = df[(df[var_categorica] == items) & (df['mes'] == mes)]
            if len(fila) == 0:
                # Si no existe este mes para esta marca, crear un registro con ventas = 0
                datos_completos.append({
                    var_categorica: items      
                }.update(var_calculos))  # añade la informacion de cada variable numerica
            else:
                # Si ya existe, agregar la fila existente
                datos_completos.append(fila.iloc[0].to_dict())
    
    # Crear un nuevo DataFrame con los datos completos
    df_completo = pd.DataFrame(datos_completos)
    return df_completo





def dfarchivoAFO(ruta:str,sheet_name:str,nombrecol:dict): 
      '''
      Lee un archivo de excel que contiene una tabla extraida de AFO.
      ARG: ruta: str
            sheet_name : str: nombre de la hoja
            nombre_col : dict: con el nombre y tipo de dato de las columnas
      return : data frame
      '''      
      df = pd.ExcelFile(ruta)
      df = df.parse(sheet_name,dtype=str)
      df.columns = nombrecol.keys() 
      df = df.astype(nombrecol)
      return df

def valores_atipicos(df,columna):
    '''
    Permite exlcuir valores atipicos utilizando los quartiles
    arg: df: data frame
            columna str.  valor de la columna que se desea eliminar atipico
    '''
    Q1 = df[columna].quantile(0.25)
    Q3 = df[columna].quantile(0.75)
    IQR = Q3 - Q1
    limite_inferior = Q1 - 1.5 * IQR
    limite_superior = Q3 + 1.5 * IQR
    df = df[(df[columna] >= limite_inferior) & (df[columna] <= limite_superior)]
    return df


def preprocess_dataframe(df,config):

    '''
    Funcion para ajustar el data frma
    arg: df: data frame, a
        config: archivo de configuracion.
    return: df: data frame
    '''
    # Eliminamos registros con valores nulos en region y negocio
    df = df.dropna(subset=config['ajustes_balanced_scored'][0]['borrar_na'])
    
    # Ciclo para filtrar valores que no son necesarios en el analisis. (ver archivo config)
    for key, value in  config['ajustes_balanced_scored'][2]['filtros'].items():
        df = df[df[key] != value]
    
    # Imputamos los valores nulos según
    for col in config['ajustes_balanced_scored'][1]['filla_na_0']:  
        df[col] = df[col].fillna(0)
           
    return df


def create_grupped_df(df,var_cate,
                      var_num,
                      agrupa = True,
                      sort_values = None):
    '''
    funcion para agrupar data frame por difentes criterios
    ARG: df: pd.DataFrame
        var_cate = list: variables categoricas
        var_num = list: variables númericas

    return pd.DataFrame
    '''
    # Agrupamos por negocio y mes y sumamos las ventas en unidades del año anterior
    if agrupa == True:
        monthly_sales = df.groupby(var_cate)[var_num].sum().reset_index()
        monthly_sales = monthly_sales.sort_values(by=var_cate)
        return monthly_sales
    else:
        monthly_sales = df.groupby(var_cate).agg(var_num).reset_index()
        monthly_sales = monthly_sales.sort_values(by=sort_values)
        return monthly_sales

def calculo_variaciones(df, col_valor, col_grupo, col_fecha='fecha'):

    '''
    funcion para calcular variaciones mensuales, trimestales y anuales,
    arg: df: data frame
        mes_ref: int: mes referencia normalmente es el último mes.
        var_categorica: str  variable categorica para agrupar.
        var_numerica: str variable categorica.

    '''
    if isinstance(col_grupo, str):
        col_grupo = [col_grupo]
    
    df['anio_mes'] = pd.to_datetime(df[col_fecha]).dt.to_period('M')
   
    df_grouped = df.groupby(col_grupo + ['anio_mes'])[col_valor].sum().reset_index()
    
    ultimo_mes = df_grouped['anio_mes'].max()
    mes_anterior = ultimo_mes - 1
    tres_meses = [ultimo_mes - i for i in range(2, 5)]  # mes-2, mes-3, mes-4
    seis_meses = [ultimo_mes - i for i in range(1, 7)]  # mes-1 a mes-6
    mismo_mes_anio_anterior = ultimo_mes - 12

    # Variación vs mes anterior
    df_pivot = df_grouped.pivot_table(index=col_grupo, 
                columns='anio_mes', 
                values=col_valor).sort_index(axis=1)# Calcular variaciones
    
    resultado = pd.DataFrame(index=df_pivot.index)
    
    # Ventas último mes
    resultado['ventas_ultimo_mes'] = df_pivot.get(ultimo_mes, np.nan)

    # Variación vs mes anterior
    resultado['var_ultimo_mes'] = (
        (df_pivot.get(ultimo_mes, np.nan) - df_pivot.get(mes_anterior, np.nan)) 
        / df_pivot.get(mes_anterior, np.nan)
    )
    
    # Variación vs promedio 3 meses anteriores
    promedio_3m = df_pivot[tres_meses].mean(axis=1, skipna=True) if all(m in df_pivot.columns for m in tres_meses) else np.nan
    resultado['var_ultimo_trimestre'] = (
        (df_pivot.get(ultimo_mes, np.nan) - promedio_3m) / promedio_3m
    )

    # Variación vs promedio 6 meses anteriores
    promedio_6m = df_pivot[seis_meses].mean(axis=1, skipna=True) if all(m in df_pivot.columns for m in seis_meses) else np.nan
    resultado['var_vs_prom_semestre'] = (
        (df_pivot.get(ultimo_mes, np.nan) - promedio_6m) / promedio_6m
    )

    # Variación vs mismo mes año anterior
    resultado['var_vs_mismo_mes_anterior'] = (
        (df_pivot.get(ultimo_mes, np.nan) - df_pivot.get(mismo_mes_anio_anterior, np.nan)) 
        / df_pivot.get(mismo_mes_anio_anterior, np.nan)
    )
    resultado = resultado.reset_index()
    return resultado

class creacion_graficos:
    '''
    Clase para construccion de grafico. 
    ARG: monthly_sales: df con los datos 
        x_label: str valor del eje x
        y_label: str valor eje y
        heu: str categorias
        titulo: str
    return fig
    '''

    def __init__(self, df,x_label , y_label, heu, titulo ):
        self.df = df
        self.x_label = x_label
        self.y_label = y_label
        self.heu = heu
        self.titulo = titulo


    def create_line_chart(self):       
         
        # Gráfico de lineas por mes y negocio
        fig = px.line(
            self.df,
            x=self.x_label,
            y=self.y_label,
            color=self.heu,  # Cada negocio una línea distinta
            markers=True,     # Opcional: puntos en cada mes
            line_shape='linear',  # Forzamos línea continua (opcional, pero ayuda)
        )
        fig.update_layout(
            title=self.titulo,
            xaxis_title=self.x_label,
            yaxis_title=self.y_label,
            height=700,
            width=1100,
            template='plotly_white',
            legend_title=self.heu,
        )
        return fig

    def create_bar_chart(self): 
        fig = px.bar(
        self.df,
        x=self.x_label,
        y=self.y_label,
        color=self.x_label,
        text=self.y_label  # Mostrar el valor de marge_real como etiqueta
        )

    # Ajustes estéticos
        fig.update_traces(textposition='outside')  # Coloca las etiquetas por fuera de las barras
        fig.update_layout(
        uniformtext_minsize=8,
        uniformtext_mode='hide',
        title=self.titulo,
        xaxis_title=self.x_label,
        yaxis_title=self.y_label,
        showlegend=self.heu != self.x_label
    )
        return fig

class agrupaciones_calculos:
    '''
        Clase para realizar ciertos agrupacines
        arg: df
    '''
    def __init__(self,df_principal ):
        self.df_principal = df_principal

    
    def tabla_metricas(self,var_categoricas, var_numerica):
        
        '''
        Agrupar data frame
        ARG: car_categoricas: variable Categorica
            var_numerica: str: variable numerica
        '''
        self.df_principal = self.df_principal.groupby([var_categoricas]).agg(
        total = (var_numerica,'sum'),
        media = (var_numerica,'mean'),
        desviacion = (var_numerica,'std'),
        mediana = (var_numerica,'median'),
        minimo = (var_numerica,'min'),
        maximo = (var_numerica,'max')
        ).reset_index().sort_values('total',ascending=False)

        return self.df_principal
    
    @classmethod
    def transformaciones(cls,valor,decimales=1, mmill=True):
        '''
        Metodo para dar formato a los numeros grandes
        ARG: decimales : int: 
        mill: bool, True
        '''
        if mmill == True:
            return  f"{valor / 1e9:.{decimales}f} M mill"
        else:
            return f"{valor / 1e8:.{decimales}f} mill"

    def combinar_tablas(self, df_auxiliar, union, cardinal = 'left'):
        '''
        Metodo para realizar merge entre data frame
        ARG:    df_auxiliar: df
                union: list: variables a uniir
                cardinal: str, cardinalidad
        '''
     
        if len(union) == 1:
            self.df_principal  = pd.merge(self.df_principal,
                                      df_auxiliar, on = union[0], how= cardinal)          
            return self.df_principal          
        else:
            self.df_principal  = pd.merge(self.df_principal,
                                      df_auxiliar, left_on= union[0],
                                      right_on= union[1],
                                      how= cardinal)   
            return self.df_principal
    
