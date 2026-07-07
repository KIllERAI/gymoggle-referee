from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout
)

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class HomeWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("GymOggle")
        self.resize(1000, 700)

        title = QLabel("GYMOGGLE")
        title.setAlignment(Qt.AlignCenter)

        title.setFont(QFont("Arial", 30, QFont.Bold))

        self.playButton = QPushButton("PLAY")
        self.settingsButton = QPushButton("SETTINGS")
        self.exitButton = QPushButton("EXIT")

        self.playButton.setFixedHeight(55)
        self.settingsButton.setFixedHeight(55)
        self.exitButton.setFixedHeight(55)

        self.exitButton.clicked.connect(self.close)

        layout = QVBoxLayout()

        layout.addStretch()

        layout.addWidget(title)

        layout.addSpacing(40)

        layout.addWidget(self.playButton)
        layout.addWidget(self.settingsButton)
        layout.addWidget(self.exitButton)

        layout.addStretch()

        self.setLayout(layout)