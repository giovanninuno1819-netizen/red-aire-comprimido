import pandas as pd
import numpy as np
import networkx as nx
class LectorRed:
    def __init__(self, ruta_materiales="materiales.json"):
        """Inicializa el lector cargando el catálogo maestro de materiales."""
        if os.path.exists(ruta_materiales):
            with open(ruta_materiales, "r") as f:
                self.catalogo_materiales = json.load(f)
        else:
            self.catalogo_materiales = {}

    def cargar_y_validar_excel(self, ruta_excel):
        """
        Lee las pestañas de la red y consumos, validando la integridad 
        de los datos neumáticas.
        """
        # 1. Lectura de hojas con Pandas
        try:
            df_tramos = pd.read_excel(ruta_excel, sheet_name="Estructura_Red")
            df_consumos = pd.read_excel(ruta_excel, sheet_name="Puntos_Consumo")
        except Exception as e:
            raise ValueError(f"Error al leer las pestañas del Excel: {e}. Asegúrate de usar los nombres correctos.")

        # 2. Validación de columnas obligatorias
        columnas_tramos_req = ["ID_Tramo", "Nodo_Inicio", "Nodo_Fin", "Longitud_m", "Material", "DN_pulgadas"]
        columnas_consumos_req = ["TAG_Equipo", "Nodo_Conexion", "Caudal_Nm3h", "Presion_Min_bar"]

        for col in columnas_tramos_req:
            if col not in df_tramos.columns:
                raise ValueError(f"Falta la columna obligatoria '{col}' en la pestaña Estructura_Red.")
        
        for col in columnas_consumos_req:
            if col not in df_consumos.columns:
                raise ValueError(f"Falta la columna obligatoria '{col}' en la pestaña Puntos_Consumo.")

        # 3. Limpieza básica de datos vacíos
        df_tramos = df_tramos.dropna(subset=["ID_Tramo", "Nodo_Inicio", "Nodo_Fin"])
        df_consumos = df_consumos.dropna(subset=["TAG_Equipo", "Nodo_Conexion"])

        # 4. Mapeo Automático de Diámetros Interiores Reales (Tu criterio de ingeniería)
        df_tramos["Diametro_Int_mm"] = df_tramos.apply(self._obtener_diametro_interior, axis=1)
        df_tramos["Rugosidad_mm"] = df_tramos.apply(self._obtener_rugosidad, axis=1)

        return df_tramos, df_consumos

    def _obtener_diametro_interior(self, fila):
        mat = str(fila["Material"]).upper()
        dn = str(fila["DN_pulgadas"])
        
        if mat in self.catalogo_materiales:
            lista_dn = self.catalogo_materiales[mat]["diametros"]
            if dn in lista_dn:
                return lista_dn[dn]["int_mm"]
        
        # Inferencia por si no se encuentra en el catálogo (Criterio por defecto para 1/2 pulgada)
        return 15.76 

    def _obtener_rugosidad(self, fila):
        mat = str(fila["Material"]).upper()
        if mat in self.catalogo_materiales:
            return self.catalogo_materiales[mat]["rugosidad_mm"]
        return 0.05 # Rugosidad base del acero comercial por defecto
