from PyQt5.QtWidgets import QMainWindow, QWidget, QStackedWidget, QAction, QMessageBox, QVBoxLayout, QLineEdit, QLabel, QComboBox, QDateTimeEdit, QPushButton, QGroupBox
from PyQt5.QtCore import QDateTime
from interfaz_pago import VentanaPago  # Importamos la clase VentanaPago
from base_datos import calcular_costo, guardar_reserva, mesas

class InterfazReservas(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestor de Reservaciones - Restaurante")
        self.resize(600, 400)
        self.setStyleSheet(self.obtener_estilos())
        self.initUI()

    def initUI(self):
        self.stacked_widget = QStackedWidget()
        self.pagina_reserva = self.crear_pagina_reserva()
        self.interfaz_pago = VentanaPago(parent=self)  # Pasamos 'self' como padre
        self.stacked_widget.addWidget(self.pagina_reserva)
        self.stacked_widget.addWidget(self.interfaz_pago)
        
        menu_gestion = self.menuBar().addMenu("Gestión")
        ver_mesas_action = QAction("Ver Mesas Disponibles", self)
        ver_mesas_action.triggered.connect(self.mostrar_mesas_disponibles)
        menu_gestion.addAction(ver_mesas_action)

        self.setCentralWidget(self.stacked_widget)

    # Métodos adicionales seguirían aquí...

    def crear_pagina_reserva(self):
        pagina = QWidget() # Creamos un widget para la pagina de reservacion

        # Campos de cliente
        self.entrada_nombre = QLineEdit() # Entrada para el nombre del cliente
        self.entrada_telefono = QLineEdit() # Entrada para el telefono
        self.entrada_correo = QLineEdit() # Entrada para el correo electronico

        # Campos de reserva 
        self.combo_capacidad = QComboBox() # Combo box para seleccionar la mesa disponible
        self.combo_capacidad.addItems(["2", "4", "6"]) 
        self.combo_capacidad.currentTextChanged.connect(self.actualizar_mesas_disponibles)  # Actualiza las mesas disponibles al cambiar la capacidad
        
        self.combo_mesas = QComboBox() # Combo box para seleccionar la mesa que este disponible
        self.entrada_fecha = QDateTimeEdit(QDateTime.currentDateTime()) # Entrada para la fecha y hora de la reserva
        self.label_costo = QLabel("Costo de la Reservación: $0") # Etiqueta para mostrar el costo de la reserva
        
        # Botón de reserva
        boton_reservar = QPushButton("Realizar Reservación")
        boton_reservar.clicked.connect(self.procesar_reserva) # Conectamos el clic del botón al método para procesar la reserva

        # Disposición de la página
        layout_principal = QVBoxLayout()  # Layout vertical para organizar los widgets
        layout_principal.addWidget(self.crear_grupo_cliente())  # Añadimos el grupo de cliente
        layout_principal.addWidget(self.crear_grupo_reserva())  # Añadimos el grupo de reserva
        layout_principal.addWidget(boton_reservar)
        pagina.setLayout(layout_principal)
        
        return pagina

    def crear_grupo_cliente(self):
        grupo = QGroupBox("Información del Cliente") # Creamos un grupo para los datos del cliente
        layout = QVBoxLayout()
        for label_text, entrada in [("Nombre:", self.entrada_nombre),
                                    ("Teléfono:", self.entrada_telefono),
                                    ("Correo:", self.entrada_correo)]:
            layout.addWidget(QLabel(label_text)) # Etiquetas para los campos
            layout.addWidget(entrada)
        grupo.setLayout(layout)
        return grupo

    def crear_grupo_reserva(self):
        grupo = QGroupBox("Detalles de la Reservación") # Creamos un grupo para los detalles de la reserva
        layout = QVBoxLayout()
        for label_text, widget in [("Fecha y Hora:", self.entrada_fecha),
                                   ("Número de Personas:", self.combo_capacidad),
                                   ("Mesas Disponibles:", self.combo_mesas),
                                   ("", self.label_costo)]:
            if label_text:
                layout.addWidget(QLabel(label_text))
            layout.addWidget(widget) # Añadimos los widgets correspondientes (campos de entrada, combo box, etc.)
        grupo.setLayout(layout)
        return grupo

    def actualizar_mesas_disponibles(self):  # Obtenemos la capacidad seleccionada
        capacidad = int(self.combo_capacidad.currentText())
        mesas_disponibles = [m for m in mesas if m["capacidad"] == capacidad and m["disponible"]]  # Filtramos las mesas disponibles
        self.combo_mesas.clear() # Limpiamos el combo box de mesas
        self.combo_mesas.addItems([f"Mesa {m['numero']}" for m in mesas_disponibles]) # Añadimos las mesas disponibles
        self.label_costo.setText(f"Costo de la Reservación: ${calcular_costo(capacidad)}") # Mostramos el costo correspondiente

    def mostrar_mesas_disponibles(self):
     # Mostramos un mensaje con las mesas disponibles y su estado
        mensaje = "Mesas Disponibles:\n" + "\n".join(
            f"Mesa {m['numero']} - Capacidad: {m['capacidad']} - {'Disponible' if m['disponible'] else 'Reservada'}"
            for m in mesas)
        QMessageBox.information(self, "Mesas Disponibles", mensaje) # Mostramos el mensaje en una ventana emergente

    def procesar_reserva(self):
        if not all([self.entrada_nombre.text(), self.entrada_telefono.text(), self.entrada_correo.text()]):
            QMessageBox.warning(self, "Error", "Todos los campos son obligatorios.")
            return

        mesa_texto = self.combo_mesas.currentText()  # Obtenemos el texto de la mesa seleccionada
        if not mesa_texto: # Si no se selecciona ninguna mesa, mostramos un mensaje de error
            QMessageBox.warning(self, "Error", "Seleccione una mesa disponible.")
            return

        mesa_numero = int(mesa_texto.split()[1])  # Extraemos el número de la mesa
        capacidad = int(self.combo_capacidad.currentText()) # Obtenemos la capacidad seleccionada
        costo = calcular_costo(capacidad)  # Calculamos el costo de la reserva

        if not self.reservar_mesa(mesa_numero): # Verificamos si la mesa está disponible
            QMessageBox.warning(self, "Error", "La mesa seleccionada no está disponible.")
            return
        # Guardamos la reserva en la base de datos
        guardar_reserva(
            self.entrada_nombre.text(),
            self.entrada_telefono.text(),
            self.entrada_correo.text(),
            self.entrada_fecha.dateTime().toString("yyyy-MM-dd HH:mm"),
            capacidad, mesa_numero, costo
        )
        QMessageBox.information(self, "Reserva Exitosa", f"Su reservación para la {mesa_texto} ha sido registrada.")
        self.limpiar_campos() # Llamamos a la funcion para limpiar los campos
        self.stacked_widget.setCurrentWidget(self.interfaz_pago)

    def limpiar_campos(self):
        self.entrada_nombre.clear() # Limpiar el campo de nombre
        self.entrada_telefono.clear() # Limpia el campo telefono
        self.entrada_correo.clear() # Limpia el campo correo (y asi con el esto de campos)
        self.combo_capacidad.setCurrentIndex(0) 
        self.combo_mesas.clear() #
        self.entrada_fecha.setDateTime(QDateTime.currentDateTime()) #
        self.label_costo.setText("Costo de la Reservacion: $0") #

    def reservar_mesa(self, numero_mesa):
         # Buscamos la mesa y la marcamos como no disponible si está disponible
        for mesa in mesas:
            if mesa["numero"] == numero_mesa and mesa["disponible"]:
                mesa["disponible"] = False # Marcamos la mesa como reservada
                return True
        return False # Retornamos False si no se encontró una mesa disponible

    def obtener_estilos(self):
        # Retornamos los estilos personalizados para la interfaz
        return """
            QWidget { background-color: #f0f0f0; font-family: Arial; }
            QLabel { color: #333; font-size: 14px; padding: 5px; }
            QLineEdit, QComboBox, QDateTimeEdit { border: 1px solid #ccc; border-radius: 5px; padding: 5px; font-size: 14px; }
            QPushButton { background-color: #4CAF50; color: white; font-size: 14px; border-radius: 5px; padding: 10px; }
            QPushButton:hover { background-color: #45a049; }
            QGroupBox { font-size: 16px; font-weight: bold; color: #4CAF50; border: 1px solid #4CAF50; border-radius: 5px; margin-top: 10px; }
            QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top center; padding: 0 3px; }
        """
