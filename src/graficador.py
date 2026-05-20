import matplotlib.pyplot as plt
import os

class GraficadorRed:
    def __init__(self, carpeta_salida="output"):
        """Inicializa el módulo definiendo dónde se guardarán las imágenes de reporte."""
        self.output_dir = carpeta_salida
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
        # Configurar un estilo limpio y profesional para las gráficas
        plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')

    def generar_graficas_reporte(self, df_resultados):
        """Genera y guarda los archivos de imagen para las alertas e ingeniería de la red."""
        rutas_imagenes = {}
        
        if df_resultados.empty:
            return rutas_imagenes

        # --- GRÁFICA 1: VELOCIDADES DEL AIRE POR TRAMO ---
        fig, ax = plt.subplots(figsize=(8, 4.5))
        tramos = df_resultados["ID_Tramo"].astype(str)
        velocidades = df_resultados["Velocidad_ms"]
        
        # Asignar colores según las alertas que configuramos en el motor
        colores = []
        for _, fila in df_resultados.iterrows():
            if "SUBDIMENSIONADO" in fila["Alerta_Ingenieria"]:
                colores.append("#E74C3C") # Rojo para peligro por alta velocidad
            elif "SOBREDIMENSIONADO" in fila["Alerta_Ingenieria"]:
                colores.append("#F39C12") # Naranja por baja velocidad / exceso de diámetro
            else:
                colores.append("#2ECC71") # Verde: Operación óptima

        barras = ax.bar(tramos, velocidades, color=colores, edgecolor='#2C3E50', alpha=0.85)
        
        # Línea guía de tus Datos Generales de Diseño (Límite de 10 m/s)
        ax.axhline(y=10.0, color='#C0392B', linestyle='--', linewidth=1.5, label='Límite de Diseño (10 m/s)')
        
        ax.set_title("Perfil de Velocidades Reales del Aire por Tramo", fontsize=12, fontweight='bold', pad=15)
        ax.set_xlabel("Identificador del Tramo de Tubería", fontsize=10, labelpad=10)
        ax.set_ylabel("Velocidad Real (m/s)", fontsize=10)
        ax.legend(loc='upper right')
        
        # Añadir los valores numéricos arriba de cada barra
        for barra in barras:
            yval = barra.get_height()
            if yval > 0:
                ax.text(barra.get_x() + barra.get_width()/2.0, yval + 0.3, f"{yval:.2f}", ha='center', va='bottom', fontsize=9)

        plt.tight_layout()
        ruta_vel = os.path.join(self.output_dir, "perfil_velocidades.png")
        plt.savefig(ruta_vel, dpi=150)
        plt.close()
        rutas_imagenes["velocidades"] = ruta_vel

        # --- GRÁFICA 2: PÉRDIDAS DE CARGA POR TRAMO (Colebrook-White) ---
        fig, ax = plt.subplots(figsize=(8, 4.5))
        perdidas = df_resultados["Perdida_Carga_bar"]
        
        ax.stem(tramos, perdidas, linefmt='-b', markerfmt='ob', basefmt='r-')
        
        ax.set_title("Caída de Presión Estimada por Tramo (Fricción + Accesorios)", fontsize=12, fontweight='bold', pad=15)
        ax.set_xlabel("Identificador del Tramo de Tubería", fontsize=10, labelpad=10)
        ax.set_ylabel("Pérdida de Carga (bar)", fontsize=10)
        
        for i, txt in enumerate(perdidas):
            if txt > 0:
                ax.annotate(f"{txt:.4f} bar", (tramos[i], perdidas[i]), textcoords="offset points", xytext=(0,7), ha='center', fontsize=8.5)

        plt.tight_layout()
        ruta_pda = os.path.join(self.output_dir, "perfil_perdidas.png")
        plt.savefig(ruta_pda, dpi=150)
        plt.close()
        rutas_imagenes["perdidas"] = ruta_pda

        return rutas_imagenes
