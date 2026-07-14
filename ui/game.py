from logic.engine import GameEngine
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class GameWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.engine = GameEngine()
        title = QLabel("GAME SCREEN")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 24, QFont.Bold))

        subtitle = QLabel("Camera Coming Soon")
        subtitle.setAlignment(Qt.AlignCenter)

        self.backButton = QPushButton("BACK")
        self.backButton.setFixedHeight(55)

        layout = QVBoxLayout()

        layout.addStretch()
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addStretch()
        layout.addWidget(self.backButton)

        self.setLayout(layout)

        