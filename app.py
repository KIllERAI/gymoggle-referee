from PySide6.QtWidgets import QMainWindow, QStackedWidget

from ui.home import HomeWindow
from ui.game import GameWindow


class GymOggleApp(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("GymOggle")
        self.resize(1000, 700)

        self.stack = QStackedWidget()

        self.home = HomeWindow()
        self.game = GameWindow()

        self.stack.addWidget(self.home)
        self.stack.addWidget(self.game)

        self.setCentralWidget(self.stack)

        self.home.playButton.clicked.connect(self.show_game)
        self.game.backButton.clicked.connect(self.show_home)

    def show_home(self):
        self.stack.setCurrentWidget(self.home)

    def show_game(self):
        self.stack.setCurrentWidget(self.game)