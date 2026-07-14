import sys

from PySide6.QtWidgets import QApplication
from app import GymOggleApp

app = QApplication(sys.argv)

window = GymOggleApp()
window.show()

sys.exit(app.exec())