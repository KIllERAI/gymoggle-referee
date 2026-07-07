import sys
from PySide6.QtWidgets import QApplication
from ui.home import HomeWindow

app = QApplication(sys.argv)

window = HomeWindow()
window.show()

sys.exit(app.exec())