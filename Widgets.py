from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QLineEdit, QComboBox

class TextBox(QLineEdit):
    def __init__(self, validator, text, fn):
        super().__init__()

        self.textBox = QLineEdit(self)
        self.textBox.setText(text)
        self.textBox.setValidator(validator)
        self.textBox.returnPressed.connect(self.return_pressed)
        self.fn = fn

    def return_pressed(self):
        self.fn(self.textBox.text())