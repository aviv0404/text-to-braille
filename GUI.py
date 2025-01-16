import sys
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QGridLayout,
    QFormLayout,
    QLabel,
    QLineEdit,
    QCheckBox,
    QComboBox,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import matplotlib.font_manager as fm
import logging

from text_to_braille import text_to_braille, settings

# Set up logging to print to console
logging.basicConfig(level=logging.ERROR)

FONT = "Arial"
FONT_SIZE = 12


class BrailleGUI(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self) -> None:
        self.setWindowTitle("Text-to-Braille Converter")

        # Set dark theme
        self.setStyleSheet("background-color: #2b2b2b; color: #ffffff")

        # Set font
        font = QFont(FONT, FONT_SIZE)
        self.setFont(font)

        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)

        self._initInputOutputLayout(mainLayout)
        self._initSettingsLayout(mainLayout)

    def _initSettingsLayout(self, mainLayout: QGridLayout) -> None:
        settingsLayout = QFormLayout()
        mainLayout.addLayout(settingsLayout)

        # Add width selection
        self.widthLabel = QLabel("Width:")
        self.widthLabel.setStyleSheet("color: #ffffff")
        self.widthLabel.setFont(QFont(FONT, FONT_SIZE, QFont.Bold))
        self.widthEntry = QLineEdit()
        self.widthEntry.setText(str(settings["width"]))
        self.widthEntry.setStyleSheet("background-color: #3b3b3b; color: #ffffff")
        self.widthEntry.setFont(QFont(FONT, FONT_SIZE, 14))
        self.widthEntry.textChanged.connect(self.convertText)
        settingsLayout.addRow(self.widthLabel, self.widthEntry)

        # Add monospace selection
        self.monospaceLabel = QLabel("Monospace:")
        self.monospaceLabel.setStyleSheet("color: #ffffff")
        self.monospaceLabel.setFont(QFont(FONT, FONT_SIZE, QFont.Bold))
        self.monospaceCheckbox = QCheckBox()
        self.monospaceCheckbox.setChecked(settings["monospace"])
        self.monospaceCheckbox.setStyleSheet("color: #ffffff")
        self.monospaceCheckbox.stateChanged.connect(self.convertText)
        settingsLayout.addRow(self.monospaceLabel, self.monospaceCheckbox)

        # Add inverted selection
        self.invertedLabel = QLabel("Inverted:")
        self.invertedLabel.setStyleSheet("color: #ffffff")
        self.invertedLabel.setFont(QFont(FONT, FONT_SIZE, QFont.Bold))
        self.invertedCheckbox = QCheckBox()
        self.invertedCheckbox.setChecked(settings["inverted"])
        self.invertedCheckbox.setStyleSheet("color: #ffffff")
        self.invertedCheckbox.stateChanged.connect(self.convertText)
        settingsLayout.addRow(self.invertedLabel, self.invertedCheckbox)

        # Add greyscale selection
        self.greyscaleLabel = QLabel("Greyscale Mode:")
        self.greyscaleLabel.setStyleSheet("color: #ffffff")
        self.greyscaleLabel.setFont(QFont(FONT, FONT_SIZE, QFont.Bold))
        self.greyscaleCombo = QComboBox()
        self.greyscaleCombo.addItems(["luminance", "lightness", "average", "value"])
        self.greyscaleCombo.setCurrentText(settings["greyscale_mode"])
        self.greyscaleCombo.setStyleSheet("background-color: #3b3b3b; color: #ffffff")
        self.greyscaleCombo.setFont(QFont(FONT, FONT_SIZE))
        self.greyscaleCombo.currentTextChanged.connect(self.convertText)
        settingsLayout.addRow(self.greyscaleLabel, self.greyscaleCombo)

        # Add font selection
        self.fontLabel = QLabel("Font:")
        self.fontLabel.setStyleSheet("color: #ffffff")
        self.fontLabel.setFont(QFont(FONT, FONT_SIZE, QFont.Bold))
        self.fontCombo = QComboBox()
        for font in fm.findSystemFonts(fontpaths=None, fontext="ttf"):
            font_name = font.split("\\")[-1]
            self.fontCombo.addItem(font_name)
        self.fontCombo.setCurrentText(settings["font_name"])
        self.fontCombo.setStyleSheet("background-color: #3b3b3b; color: #ffffff")
        self.fontCombo.setFont(QFont(FONT, FONT_SIZE))
        self.fontCombo.currentTextChanged.connect(self.convertText)
        settingsLayout.addRow(self.fontLabel, self.fontCombo)

    def _initInputOutputLayout(self, mainLayout: QGridLayout) -> None:
        inputOutputLayer = QVBoxLayout()  # Vertical layout for stacking
        inputOutputLayer.setContentsMargins(0, 0, 0, 0)  # Remove margins
        inputOutputLayer.setSpacing(5)  # Adjust spacing for a tighter layout

        # input
        self.inputTextLabel = QLabel("Input:")
        self.inputTextLabel.setStyleSheet("color: #ffffff")
        self.inputTextLabel.setFont(QFont(FONT, FONT_SIZE, QFont.Bold))
        inputOutputLayer.addWidget(self.inputTextLabel)

        self.textInput = QLineEdit()
        self.textInput.setStyleSheet("background-color: #3b3b3b; color: #ffffff")
        self.textInput.setFont(QFont(FONT, FONT_SIZE))
        self.textInput.textChanged.connect(self.convertText)
        inputOutputLayer.addWidget(self.textInput)

        self.outputTextLabel = QLabel("Output:")
        self.outputTextLabel.setStyleSheet("color: #ffffff")
        self.outputTextLabel.setFont(QFont(FONT, FONT_SIZE, QFont.Bold))
        inputOutputLayer.addWidget(self.outputTextLabel)

        self.brailleOutput = QTextEdit()
        self.brailleOutput.setReadOnly(True)
        self.brailleOutput.setStyleSheet("background-color: #3b3b3b; color: #ffffff")
        inputOutputLayer.addWidget(self.brailleOutput)

        inputOutputLayer.setStretchFactor(
            self.brailleOutput, 1
        )  # Give the text input priority to expand

        mainLayout.addLayout(inputOutputLayer)

    def convertText(self):
        try:
            # Get input text and settings
            text = self.textInput.text()
            width = int(self.widthEntry.text())
            monospace = self.monospaceCheckbox.isChecked()
            inverted = self.invertedCheckbox.isChecked()
            greyscaleMode = self.greyscaleCombo.currentText()
            fontName = self.fontCombo.currentText()

            # Update settings
            settings["width"] = width
            settings["monospace"] = monospace
            settings["inverted"] = inverted
            settings["greyscale_mode"] = greyscaleMode
            settings["font_name"] = fontName

            # Convert text to braille
            brailleText = text_to_braille(text, font_name=fontName)
            # Display braille text in output field
            self.brailleOutput.setText(brailleText)
        except Exception as e:
            logging.error(e)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = BrailleGUI()
    gui.show()
    sys.exit(app.exec_())
