from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas
import os

class CanvasConMarcaDeAgua(canvas.Canvas):
    """
    Clase personalizada para dibujar elementos repetitivos en el fondo de las páginas,
    como los números de página y la marca de agua con el logotipo.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ruta_logo = "assets/logo.png"

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#7F8C8D"))
        # Encabezado sutil
        self.drawString(54, 750, "Reporte Técnico de Suministro: Red de Aire Comprimido Industrial")
        self.setStrokeColor(colors.HexColor("#BDC3C7"))
        self.setLineWidth(0.5)
        self.line(54, 742, 558, 742)
        
        # Pie de página
        texto_pagina = f"Página {self._pageNumber} de {page_count}"
        self.drawRightString(558, 40, texto_pagina)
        self.restoreState()

    def showPage(self):
        # Antes de cambiar de página, si existe el logotipo, lo dibujamos como marca de agua
        if os.path.exists(self.ruta_logo):
            self.saveState()
            # Guardar estado de transparencia (Opacidad reducida al 8% para no estorbar el texto)
            self.setFillAlpha(0.08)
            # Centrar la marca de agua en la hoja tamaño Carta
            self.drawImage(self.ruta_logo, 150, 250, width=300, height=300, mask='auto')
            self.restoreState()
        
        self.draw_page_number("?")
        super().showPage()

class ReporteroPDF:
    def __init__(self, carpeta_salida="output"):
        self.output_dir = carpeta_salida
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def generar_reporte_pdf(self, df_resultados, rutas_imagenes):
        """Construye la estructura completa del documento PDF industrial."""
        ruta_pdf = os.path.join(self.output_dir, "reporte_red.pdf")
        
        # Configurar márgenes de la hoja (0.75 pulgadas = 54 puntos)
        doc = SimpleDocTemplate(
            ruta_pdf, 
            pagesize=letter,
            leftMargin=54, rightMargin=54,
            topMargin=72, bottomMargin=54
        )
        
        estilos = getSampleStyleSheet()
        
        # Estilos tipográficos personalizados basados en tus Datos Generales
        estilo_titulo = ParagraphStyle(
            'TituloIndustrial',
            parent=estilos['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=22,
            textColor=colors.HexColor("#2C3E50"),
            spaceAfter=15
        )
        
        estilo_subtitulo = ParagraphStyle(
            'SubtituloIndustrial',
            parent=estilos['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=14,
            textColor=colors.HexColor("#16A085"),
            spaceBefore=12,
            spaceAfter=8
        )

        estilo_cuerpo = ParagraphStyle(
            'CuerpoIndustrial',
            parent=estilos['Normal'],
            fontName='Helvetica',
            fontSize=10.5,
            leading=14,
            textColor=colors.HexColor("#34495E"),
            spaceAfter=8
        )

        historia = []

        # --- SECCIÓN 1: ENCABEZADO Y PRESENTACIÓN ---
        historia.append(Paragraph("MEMORIA DE CÁLCULO NEUMÁTICO", estilo_titulo))
        historia.append(Paragraph("Evaluación de Suministro, Caudales Acumulados y Pérdidas de Carga", estilo_cuerpo))
        historia.append(Spacer(1, 15))

        # --- SECCIÓN 2: CRITERIOS DE INGENIERÍA INFERIDOS ---
        historia.append(Paragraph("1. Criterios de Diseño Neumático Seleccionados", estilo_subtitulo))
        texto_criterios = (
            "El análisis de la red de distribución se ha ejecutado mediante aproximaciones iterativas de la ecuación "
            "de <b>Colebrook-White</b>, tomando como semilla el estimador de Swamee-Jain. Con base en las buenas prácticas "
            "y los datos maestros proporcionados, se configuró una velocidad límite recomendada de <b>10.0 m/s</b> "
            "para tramos de distribución y una penalización automática del <b>20%</b> sobre las longitudes lineales para "
            "absorber las pérdidas singulares provocadas por accesorios (codos, tees y válvulas)."
        )
        historia.append(Paragraph(texto_criterios, estilo_cuerpo))
        historia.append(Spacer(1, 10))

        # --- SECCIÓN 3: TABLA DE RESULTADOS MATEMÁTICOS ---
        historia.append(Paragraph("2. Resumen General de Cálculos por Tramo", estilo_subtitulo))
        
        # Convertir el DataFrame de resultados a una matriz de texto aceptada por ReportLab
        datos_tabla = [["Tramo", "Inicio", "Fin", "Caudal\n(Nm³/h)", "Velocidad\n(m/s)", "ΔP Fricción\n(bar)", "Estatus"]]
        
        for _, fila in df_resultados.iterrows():
            estatus_corto = "OK" if "OK" in fila["Alerta_Ingenieria"] else "ALERTA"
            datos_tabla.append([
                str(fila["ID_Tramo"]),
                str(fila["Nodo_Inicio"]),
                str(fila["Nodo_Fin"]),
                f"{fila['Caudal_Nm3h']:.2f}",
                f"{fila['Velocidad_ms']:.2f}",
                f"{fila['Perdida_Carga_bar']:.4f}",
                estatus_corto
            ])

        # Dar formato visual de ingeniería a la tabla
        tabla_res = Table(datos_tabla, colWidths=[65, 55, 55, 75, 75, 85, 65])
        tabla_res.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2C3E50")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9.5),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#F8F9F9")),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#BDC3C7")),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8.5),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        historia.append(tabla_res)
        historia.append(Spacer(1, 15))

        # --- SECCIÓN 4: INCRUSTACIÓN DE GRÁFICAS DEL REPORTE ---
        historia.append(Paragraph("3. Análisis de Gráficas de Desempeño", estilo_subtitulo))
        
        elementos_graficas = []
        if "velocidades" in rutas_imagenes and os.path.exists(rutas_imagenes["velocidades"]):
            elementos_graficas.append(Paragraph("<b>Perfil de Velocidades (Límite 10 m/s):</b>", estilo_cuerpo))
            elementos_graficas.append(Image(rutas_imagenes["velocidades"], width=420, height=236))
            elementos_graficas.append(Spacer(1, 15))
            
        if "perdidas" in rutas_imagenes and os.path.exists(rutas_imagenes["perdidas"]):
            elementos_graficas.append(Paragraph("<b>Pérdidas de Carga por Fricción (Colebrook-White):</b>", estilo_cuerpo))
            elementos_graficas.append(Image(rutas_imagenes["perdidas"], width=420, height=236))

        # Agrupamos las gráficas para evitar que se partan de forma fea entre dos páginas
        historia.append(KeepTogether(elementos_graficas))

        # --- CONSTRUCCIÓN FINAL DEL ARCHIVO ---
        def callback_paginas(canvas, document):
            canvas.draw_page_number(len(document.pages))

        doc.build(historia, canvasmaker=CanvasConMarcaDeAgua)
        return ruta_pdf
