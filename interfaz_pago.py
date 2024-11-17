import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QComboBox, QLineEdit, QFormLayout, QWidget, QPushButton, QVBoxLayout, QMessageBox, QHBoxLayout
from PyQt5.QtGui import QPalette, QColor
from base_datos import cancelar_reserva  # Importamos la función cancelar_reserva

class VentanaPago(QMainWindow):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent  # Guardamos la referencia al padre
        self.setWindowTitle("Registro de Pago")
        self.setGeometry(100, 100, 400, 350)

        # Layout principal (vertical)
        self.layout = QVBoxLayout()

        # Etiqueta para seleccionar el método de pago
        self.label_metodo_pago = QLabel("Selecciona el método de pago:")
        self.layout.addWidget(self.label_metodo_pago)

        # ComboBox para elegir el método de pago
        self.combo_metodo_pago = QComboBox()
        self.combo_metodo_pago.addItems(["Tarjeta de Debito/Credito", "Transferencia Bancaria"])
        self.combo_metodo_pago.currentIndexChanged.connect(self.cambiar_metodo_pago)
        self.layout.addWidget(self.combo_metodo_pago)

        # Layout para los campos del formulario (usaremos QFormLayout para alinearlos)
        self.form_layout = QFormLayout()

        # Campos para la tarjeta de débito/crédito
        self.label_numero_tarjeta = QLabel("Número de tarjeta:")
        self.input_numero_tarjeta = QLineEdit()
        self.label_nombre_tarjeta = QLabel("Nombre en la tarjeta:")
        self.input_nombre_tarjeta = QLineEdit()
        self.label_cv_tarjeta = QLabel("CVV:")
        self.input_cv_tarjeta = QLineEdit()

        # Campos para la transferencia bancaria
        self.label_numero_cuenta = QLabel("Número de cuenta:")
        self.input_numero_cuenta = QLineEdit()
        self.label_banco = QLabel("Banco:")
        self.input_banco = QLineEdit()

        # Añadimos los campos al formulario
        self.layout.addLayout(self.form_layout)

        # Botón para confirmar el pago
        self.boton_confirmar = QPushButton("Confirmar Pago")
        self.boton_confirmar.clicked.connect(self.confirmar_pago)
        self.layout.addWidget(self.boton_confirmar)

        # Sección para la cancelación de reserva
        self.layout_cancelar = QHBoxLayout()
        self.label_telefono_cancelar = QLabel("Si desea eliminar su registro, ingrese su número de teléfono:")
        self.input_telefono_cancelar = QLineEdit()
        self.layout_cancelar.addWidget(self.label_telefono_cancelar)
        self.layout_cancelar.addWidget(self.input_telefono_cancelar)

        # Botón para cancelar la reserva
        self.boton_cancelar = QPushButton("Cancelar")
        self.boton_cancelar.setFixedSize(150, 30)
        self.boton_cancelar.clicked.connect(self.confirmar_cancelacion)
        self.layout_cancelar.addWidget(self.boton_cancelar)
        self.layout.addLayout(self.layout_cancelar)

        # Botón para volver a la reserva (deshabilitado inicialmente y transparente)
        self.boton_volver = QPushButton("Volver a Reserva")
        self.boton_volver.setEnabled(False)
        self.boton_volver.setStyleSheet("background-color: transparent; color: transparent; border: none;")
        self.boton_volver.clicked.connect(self.volver_a_reserva)
        self.layout.addWidget(self.boton_volver)

        # Establecer el widget central
        central_widget = QWidget()
        central_widget.setLayout(self.layout)
        self.setCentralWidget(central_widget)

        # Llamamos a la función para mostrar el formulario adecuado según el método de pago seleccionado
        self.cambiar_metodo_pago()

    def cambiar_metodo_pago(self):
        # Limpiar los campos del formulario antes de mostrar nuevos
        self.limpiar_formulario()

        # Obtener el método de pago seleccionado
        metodo = self.combo_metodo_pago.currentText()

        # Mostrar campos específicos según el método de pago
        if metodo == "Tarjeta de Debito/Credito":
            self.form_layout.addRow(self.label_nombre_tarjeta, self.input_nombre_tarjeta)
            self.form_layout.addRow(self.label_numero_tarjeta, self.input_numero_tarjeta)
            self.form_layout.addRow(self.label_cv_tarjeta, self.input_cv_tarjeta)
        elif metodo == "Transferencia Bancaria":
            self.form_layout.addRow(self.label_numero_cuenta, self.input_numero_cuenta)
            self.form_layout.addRow(self.label_banco, self.input_banco)

    def limpiar_formulario(self):
        # Limpiar los campos del formulario
        for i in reversed(range(self.form_layout.count())):
            self.form_layout.itemAt(i).widget().setParent(None)

    def confirmar_pago(self):
        # Validar los campos dependiendo del método de pago
        metodo = self.combo_metodo_pago.currentText()
        if metodo == "Tarjeta de Debito/Credito" and self.validar_campos_tarjeta():
            self.mostrar_confirmacion("El pago ha sido confirmado exitosamente.")
            self.habilitar_boton_volver()  # Habilitar el botón volver
        elif metodo == "Transferencia Bancaria" and self.validar_campos_transferencia():
            self.mostrar_confirmacion("El pago ha sido confirmado exitosamente.")
            self.habilitar_boton_volver()  # Habilitar el botón volver
        else:
            return

    def validar_campos_tarjeta(self):
        if not self.input_numero_tarjeta.text() or not self.input_nombre_tarjeta.text() or not self.input_cv_tarjeta.text():
            self.mostrar_error("Por favor, complete todos los campos de la tarjeta.")
            return False
        return True

    def validar_campos_transferencia(self):
        if not self.input_numero_cuenta.text() or not self.input_banco.text():
            self.mostrar_error("Por favor, complete todos los campos de la transferencia bancaria.")
            return False
        return True

    def confirmar_cancelacion(self):
        telefono = self.input_telefono_cancelar.text()
        if telefono:
            self.mostrar_confirmacion_cancelacion(telefono)
        else:
            self.mostrar_error("Por favor, ingrese un número de teléfono.")

    def mostrar_confirmacion_cancelacion(self, telefono):
        mensaje = QMessageBox.question(self, "Confirmar Cancelación", "¿Está seguro de que desea cancelar la reservación?",
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if mensaje == QMessageBox.Yes:
            self.cancelar_reserva(telefono)
            self.habilitar_boton_volver()  # Habilitar el botón volver

    def cancelar_reserva(self, telefono):
        try:
            if cancelar_reserva(telefono):
                self.mostrar_confirmacion("La reserva ha sido cancelada exitosamente.")
            else:
                self.mostrar_error("No se encontró ninguna reserva con este teléfono.")
        except Exception as e:
            self.mostrar_error(f"Ocurrió un error al intentar cancelar la reserva: {e}")
        self.input_telefono_cancelar.clear()

    def habilitar_boton_volver(self):
        self.boton_volver.setEnabled(True)
        self.boton_volver.setStyleSheet("")  # Quitamos el estilo transparente

    def volver_a_reserva(self):
        self.parent.stacked_widget.setCurrentWidget(self.parent.pagina_reserva)

    def mostrar_confirmacion(self, mensaje):
        self.mostrar_mensaje(mensaje, QMessageBox.Information)

    def mostrar_error(self, mensaje):
        self.mostrar_mensaje(mensaje, QMessageBox.Critical)

    def mostrar_mensaje(self, mensaje, tipo):
        msg_box = QMessageBox()
        msg_box.setIcon(tipo)
        msg_box.setWindowTitle("Mensaje")
        msg_box.setText(mensaje)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

# Ejecutar la aplicación
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaPago()
    ventana.show()
    sys.exit(app.exec_())

