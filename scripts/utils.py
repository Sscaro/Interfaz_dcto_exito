'''
Este modulo permite parametrizar 
'''
import yaml
import os
import pandas as pd
import plotly.express as px

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
        showlegend=False  # Oculta la leyenda si color y x son la misma variable
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
    
