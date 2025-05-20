# Interfaz_dcto_exito
Interfaz interactiva para análisis de información de ventas de grupo exito.

La aplicacion corre en una Browers es decir un Navegador de intenet (google chrome, Microsoft edge)
Esta diseñada para que un usuario interactua con ella para realizar diferentes analisis de información.

Nota: 
    Los insumos deben estar bien definidos y exactamente estantadirzados como se exige en este manual.

## insumos:
    * Archivo en excel .xlsx con las ventas 
    * Archivo excel .xlsx Margen Bruto, informacion con 3 hojas con los datos de margen bruto
        Nivel: Negocio, Marca, Material.
    * Archivo configuracion .yml.  Archivo con parametros de configuración.

## Activar Ambiente
    * streamlit run appi.py

## BALANCE SCORE EXITO  (ventas información con el equipo de category cadenas)
Se requieren minimo estas  columnas con estos nombres en el archivo
    Mes : str
    EAN : str
    Codigo SAP : str
    Nombre Producto : str
    PLU : str   
    Negocio : str
    Categoria : str
    Sub Categoria : str
    Marca : str
    Ventas COP: float64
    Ventas UN : float64
    
## MARGEN 
Se requieren archivo en excel con tres hojas con las sigueintes tablas
    - Margen Nivel negocio {Negocio: Margen}
    - Margen Nivel marca {Marca: margen}
    - Margen Nivel Material {Cod_material: Margen}


# Autor:
    Sebastian Caro Aguirre

# Fecha.
    Mayo 2025
# Version:
    1.0