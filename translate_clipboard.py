import sys

from googletrans import Translator, LANGUAGES
from PyQt5 import Qt, QtCore, QtGui, QtWidgets, uic


GEOMETRY = "Window/geometry"
ALWAYS_ON_TOP = "Window/always_on_top"
BACKGROUND_COLOR = "Window/background_color"
OPACITY = "Window/opacity"
TEXT_COLOR = "Window/text_color"
FONT = "Window/font"
TRANSLATION_ENABLED = "Translate/translation_enabled"
DESTINATION_LANGUAGE = "Translate/destination_language"

translator = Translator()


def request_color(parent: QtWidgets.QWidget = None, initial: QtGui.QColor = None):
    color = QtWidgets.QColorDialog(parent).getColor(initial=initial)
    if color.isValid():
        return color


def request_font(parent: QtWidgets.QWidget = None, initial: QtGui.QFont = None):
    font, ok = QtWidgets.QFontDialog(parent).getFont(initial)
    if ok:
        return font


def request_item(parent, title, label, items, current=0):
    item, ok = QtWidgets.QInputDialog().getItem(parent, title, label, items, current)
    if ok:
        return item


def request_double_value(
    parent,
    title,
    label,
    value=0,
    min_value=-2147483647,
    max_value=2147483647,
    decimals=1,
):
    value, ok = QtWidgets.QInputDialog().getDouble(
        parent,
        title,
        label,
        value,
        min_value,
        max_value,
        decimals,
    )
    if ok:
        return value


class Ui(QtWidgets.QDialog):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi("translate_clipboard.ui", self)
        self.status = QtWidgets.QLabel(self)
        self.status.move(20, 0)
        self.display.customContextMenuRequested.connect(self.context_menu)
        self.display.textChanged.connect(self.on_display_text_changed)
        self.display.setPlaceholderText(
            "Right click to change settings\n"
            "Click and drag on window edges to move, or the bottom right corner to resize"
        )
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_X11NetWmWindowTypeDialog)
        self.clicked = False

        self.read_settings()
        Qt.QApplication.clipboard().dataChanged.connect(self.on_clipboard_changed)
        self.show()

    @property
    def background_color(self):
        return self._background_color

    @background_color.setter
    def background_color(self, color):
        if color is not None or color.isValid():
            self._background_color = color
            self.repaint()
            self.settings.setValue(BACKGROUND_COLOR, color.name(QtGui.QColor.HexArgb))

    @property
    def text_color(self):
        return self.display.palette().windowText().color()

    @text_color.setter
    def text_color(self, color):
        if color is not None and color.isValid():
            self.status.setStyleSheet(f"color: {color.name(QtGui.QColor.HexRgb)};")
            self.display.setStyleSheet(f"color: {color.name(QtGui.QColor.HexRgb)};")
            self.settings.setValue(TEXT_COLOR, color.name(QtGui.QColor.HexRgb))

    @property
    def text_font(self):
        return self.display.document().defaultFont()

    @text_font.setter
    def text_font(self, font):
        if font is not None:
            self.display.document().setDefaultFont(font)
            self.settings.setValue(FONT, font.toString())

    @property
    def always_on_top(self):
        return self._always_on_top

    @always_on_top.setter
    def always_on_top(self, always_on_top):
        self._always_on_top = bool(always_on_top)
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint, self.always_on_top)
        self.show()
        self.settings.setValue(ALWAYS_ON_TOP, self.always_on_top)

    def update_translation_status(self):
        if self.translation_enabled:
            self.status.setText(
                f"Translating to {LANGUAGES[self.destination_language]}"
            )
        else:
            self.status.setText("Translation is disabled")

    def read_settings(self):
        self.settings = QtCore.QSettings(
            "translate_clipboard.ini",
            QtCore.QSettings.IniFormat,
        )
        self.setGeometry(self.settings.value(GEOMETRY, self.geometry()))
        self.always_on_top = self.settings.value(ALWAYS_ON_TOP, False)
        self.background_color = QtGui.QColor(
            self.settings.value(BACKGROUND_COLOR, self.palette().window().color())
        )
        self.text_color = QtGui.QColor(
            self.settings.value(TEXT_COLOR, self.palette().windowText().color())
        )
        font = QtGui.QFont()
        font.fromString(self.settings.value(FONT, self.display.font().toString()))
        self.display.setFont(font)
        self.translation_enabled = bool(self.settings.value(TRANSLATION_ENABLED, True))
        self.destination_language = self.settings.value(DESTINATION_LANGUAGE, "en")
        self.update_translation_status()

    def write_settings(self):
        self.settings.setValue(GEOMETRY, self.geometry())

    def context_menu(self):
        menu = self.display.createStandardContextMenu()

        toggle_translation_action = menu.addAction("Translate")
        toggle_translation_action.setCheckable(True)
        toggle_translation_action.setChecked(self.translation_enabled)
        toggle_translation_action.triggered.connect(self.toggle_translation_enabled)

        toggle_always_on_top_action = menu.addAction("Always on top")
        toggle_always_on_top_action.setCheckable(True)
        toggle_always_on_top_action.setChecked(self.always_on_top)
        toggle_always_on_top_action.triggered.connect(self.toggle_always_on_top)

        change_destination_language_action = menu.addAction("Translate to")
        change_destination_language_action.triggered.connect(
            self.change_destination_language
        )

        change_background_color_action = menu.addAction("Background")
        change_background_color_action.triggered.connect(self.change_background_color)

        change_text_color_action = menu.addAction("Text")
        change_text_color_action.triggered.connect(self.change_text_color)

        change_font_action = menu.addAction("Font")
        change_font_action.triggered.connect(self.change_font)

        quit_action = menu.addAction("Quit")
        quit_action.setShortcut("Ctrl+Q")
        quit_action.triggered.connect(self.close)
        menu.exec_(QtGui.QCursor.pos())

    @Qt.pyqtSlot()
    def toggle_translation_enabled(self):
        self.translation_enabled = not self.translation_enabled
        self.update_translation_status()
        self.settings.setValue(TRANSLATION_ENABLED, self.translation_enabled)

    @Qt.pyqtSlot()
    def toggle_always_on_top(self):
        self.always_on_top = not self.always_on_top

    @Qt.pyqtSlot()
    def change_background_color(self):
        color = request_color(self, self.background_color)
        if color is not None:
            opacity = request_double_value(
                self, "Opacity", "Opacity", self.background_color.alphaF(), 0, 1
            )
            color.setAlphaF(opacity)
        self.background_color = color

    @Qt.pyqtSlot()
    def change_text_color(self):
        color = request_color(self, self.text_color)
        self.text_color = color

    @Qt.pyqtSlot()
    def change_font(self):
        font = request_font(self, self.text_font)
        self.text_font = font

    @Qt.pyqtSlot()
    def change_destination_language(self):
        language_items = [
            f"{langcode} - {language}" for langcode, language in LANGUAGES.items()
        ]
        current = list(LANGUAGES.keys()).index(self.destination_language)
        language = request_item(
            self, "Translate to", "Language", language_items, current
        )
        if language is not None:
            self.destination_language = language[:2]
            self.update_translation_status()
            self.settings.setValue(DESTINATION_LANGUAGE, self.destination_language)

    @Qt.pyqtSlot()
    def on_clipboard_changed(self):
        raw_text = Qt.QApplication.clipboard().text()
        if self.translation_enabled:
            translated_text = translator.translate(
                raw_text, dest=self.destination_language
            ).text
        else:
            translated_text = ""
        self.display.insertPlainText(
            f"{raw_text}\n"
            f"----------------------------------------\n"
            f"{translated_text}\n"
            "****************************************\n"
            "****************************************\n"
        )

    @Qt.pyqtSlot()
    def on_display_text_changed(self):
        self.display.moveCursor(QtGui.QTextCursor.End)

    def resizeEvent(self, event):
        self.status.resize(self.width() - 40, 30)
        return super(Ui, self).resizeEvent(event)

    def paintEvent(self, event):
        QtGui.QPainter(self).fillRect(self.rect(), self._background_color)

    def mousePressEvent(self, event):
        self.old_pos = event.globalPos()
        self.clicked = True
        return super(Ui, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.clicked:
            self.move(self.pos() + event.globalPos() - self.old_pos)
            self.old_pos = event.globalPos()
        return super(Ui, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.clicked = False
        return super(Ui, self).mouseReleaseEvent(event)

    def closeEvent(self, event):
        self.write_settings()
        return super(Ui, self).closeEvent(event)


if __name__ == "__main__":
    app = Qt.QApplication(sys.argv)
    window = Ui()
    sys.exit(app.exec_())
