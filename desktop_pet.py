"""A small, local AI desktop pet built with PySide6 and Ollama.

Install dependencies:
    python3 -m pip install PySide6 ollama pyobjc-framework-Cocoa

Run:
    python3 desktop_pet.py
"""

from __future__ import annotations

import random
import sys
from pathlib import Path
from typing import Optional

import ollama
from PySide6.QtCore import QObject, QPoint, QSize, Qt, QThread, QTimer, Signal
from PySide6.QtGui import (
    QAction,
    QColor,
    QFont,
    QIcon,
    QMovie,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
    QPolygon,
)
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QPushButton,
    QSlider,
    QSystemTrayIcon,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtCore import QSettings


OLLAMA_HOST = "http://localhost:11434"
DEFAULT_MODEL = "llama3.2"
SPRITE_PATH = Path(__file__).resolve().parent / "assets" / "chibi_fox.png"


class SpeechBubble(QWidget):
    """Assistant response and Siri-like text input in one floating bubble."""

    submitted = Signal(str)

    def __init__(self, text: str, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.label = QLabel(text, self)
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.label.setStyleSheet(
            "QLabel { color: #f5f0ff; font-size: 14px; background: transparent; }"
        )
        self.label.setMaximumWidth(360)

        self.input = QLineEdit(self)
        self.input.setPlaceholderText("Type to your fox")
        self.input.setClearButtonEnabled(True)
        self.input.setStyleSheet(
            "QLineEdit {"
            " color: #f8f4ff;"
            " background: transparent;"
            " border: none;"
            " padding: 5px 8px;"
            " font-size: 15px;"
            " selection-background-color: #9c78e8;"
            "}"
        )
        self.send_button = QPushButton("↑", self)
        self.send_button.setAccessibleName("Send message to fox")
        self.send_button.setFixedSize(30, 30)
        self.send_button.setStyleSheet(
            "QPushButton {"
            " color: white;"
            " background: #7657c8;"
            " border: none;"
            " border-radius: 15px;"
            " font-size: 18px;"
            " font-weight: bold;"
            "}"
            "QPushButton:hover { background: #9273e3; }"
        )

        input_row = QHBoxLayout()
        input_row.setContentsMargins(8, 3, 5, 3)
        input_row.setSpacing(4)
        input_row.addWidget(QLabel("✦", self))
        input_row.addWidget(self.input, 1)
        input_row.addWidget(self.send_button)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 11, 16, 20)
        layout.setSpacing(8)
        layout.addWidget(self.label)
        layout.addLayout(input_row)
        self.setMinimumWidth(330)
        self.setMaximumWidth(400)

        self.input.returnPressed.connect(self.submit)
        self.send_button.clicked.connect(self.submit)

    def submit(self) -> None:
        question = self.input.text().strip()
        if question:
            self.input.clear()
            self.submitted.emit(question)

    def set_text(self, text: str) -> None:
        self.label.setText(text)
        self.adjustSize()

    def paintEvent(self, event) -> None:  # noqa: N802 - Qt event method
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        body_height = self.height() - 10
        path = QPainterPath()
        path.addRoundedRect(1, 1, self.width() - 2, body_height - 1, 25, 25)

        tail = QPainterPath()
        tail.addPolygon(
            QPolygon(
                [
                    QPoint(self.width() // 2 - 9, body_height - 1),
                    QPoint(self.width() // 2 + 9, body_height - 1),
                    QPoint(self.width() // 2, self.height() - 1),
                ]
            )
        )
        path = path.united(tail)
        painter.setBrush(QColor("#211b39"))
        painter.setPen(QPen(QColor("#8d71d1"), 1.5))
        painter.drawPath(path)


class PixelFoxSprite(QWidget):
    """A small animated view of the supplied transparent fox artwork."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setFixedSize(104, 104)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._frame = 0
        self._facing_right = True
        self._activity = "walking"
        self._movie: Optional[QMovie] = None
        self._pixmap = QPixmap(str(SPRITE_PATH))
        if self._pixmap.isNull():
            raise FileNotFoundError(f"Could not load pet sprite: {SPRITE_PATH}")

        self._animation_timer = QTimer(self)
        self._animation_timer.setInterval(140)
        self._animation_timer.timeout.connect(self._advance_frame)
        self._animation_timer.start()

    def _advance_frame(self) -> None:
        self._frame = (self._frame + 1) % 4
        self.update()

    def set_facing_right(self, facing_right: bool) -> None:
        if self._facing_right != facing_right:
            self._facing_right = facing_right
            self.update()

    def set_activity(self, activity: str) -> None:
        if activity not in {"walking", "resting", "sleeping"}:
            raise ValueError(f"Unknown pet activity: {activity}")
        if self._activity != activity:
            self._activity = activity
            self._frame = 0
            self.update()

    def set_movie(self, movie: QMovie) -> None:
        self._movie = movie
        movie.frameChanged.connect(self.update)
        movie.start()
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802 - Qt event method
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

        if self._movie is not None:
            frame = self._movie.currentPixmap()
            pixmap = frame if not frame.isNull() else self._pixmap
        else:
            pixmap = self._pixmap

        scaled = pixmap.scaled(
            self.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        x = (self.width() - scaled.width()) // 2
        y = (self.height() - scaled.height()) // 2

        if self._activity == "walking":
            y += (0, 1, 0, -1)[self._frame]
        elif self._activity == "resting":
            y += (0, 1, 1, 0)[self._frame]
        elif self._activity == "sleeping":
            y += (0, 1, 2, 1)[self._frame]

        if self._facing_right:
            painter.translate(self.width(), 0)
            painter.scale(-1, 1)
        painter.drawPixmap(x, y, scaled)

        if self._activity == "sleeping":
            painter.resetTransform()
            painter.setPen(QColor("#4a345e"))
            painter.setFont(QFont("Sans Serif", 9, QFont.Weight.Bold))
            painter.drawText(
                self.width() - 30,
                16 + (self._frame % 2) * 2,
                "z z",
            )


class OllamaWorker(QThread):
    """Run an Ollama request off the GUI thread."""

    response_ready = Signal(str)
    error_occurred = Signal(str)

    def __init__(
        self,
        model: str,
        system_prompt: str,
        user_text: str,
        image_path: Optional[str] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.model = model
        self.system_prompt = system_prompt
        self.user_text = user_text
        self.image_path = image_path

    def run(self) -> None:
        user_message = {
            "role": "user",
            "content": self.user_text,
        }
        if self.image_path:
            user_message["images"] = [self.image_path]

        try:
            client = ollama.Client(host=OLLAMA_HOST, timeout=60.0)
            result = client.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    user_message,
                ],
            )
            text = result.message.content.strip()
            self.response_ready.emit(text or "I don't have anything to say just now.")
        except Exception as exc:
            self.error_occurred.emit(
                f"Couldn't reach Ollama: {exc}\n"
                "Check that Ollama is running and the model is available."
            )


class PetSettingsDialog(QDialog):
    """Preferences for the pet's name and movement."""

    def __init__(
        self,
        wandering_enabled: bool,
        walk_speed: int,
        pet_name: str = "Fox",
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(f"{pet_name} Settings")
        self.setMinimumWidth(300)

        self.name_input = QLineEdit(pet_name)
        self.name_input.setMaxLength(32)
        self.name_input.setPlaceholderText("Enter a name")

        self.wandering_checkbox = QCheckBox("Let the fox wander around")
        self.wandering_checkbox.setChecked(wandering_enabled)

        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(1, 8)
        self.speed_slider.setValue(walk_speed)
        self.speed_value = QLabel(str(walk_speed))
        self.speed_slider.valueChanged.connect(
            lambda value: self.speed_value.setText(str(value))
        )

        speed_row = QHBoxLayout()
        speed_row.addWidget(self.speed_slider, 1)
        speed_row.addWidget(self.speed_value)

        form = QFormLayout()
        form.addRow("Pet name", self.name_input)
        form.addRow(self.wandering_checkbox)
        form.addRow("Walking speed", speed_row)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._accept_if_valid)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def _accept_if_valid(self) -> None:
        if self.name_input.text().strip():
            self.name_input.setText(self.name_input.text().strip())
            self.accept()
            return

        self.name_input.setToolTip("Please enter a name for your pet.")
        self.name_input.setFocus(Qt.FocusReason.OtherFocusReason)


class DesktopPet(QWidget):
    """Non-activating overlay with a walking sprite, dragging, and Ollama chat."""

    WALK_STEP_PX = 3
    WALK_INTERVAL_MS = 40

    def __init__(self, model: str = DEFAULT_MODEL) -> None:
        super().__init__()
        self.model = model
        self._drag_offset: Optional[QPoint] = None
        self._worker: Optional[OllamaWorker] = None
        self._movie: Optional[QMovie] = None
        self._activity = "walking"
        self._velocity_x = 0.0
        self._velocity_y = 0.0
        self._wandering_enabled = True
        self._pet_enabled = True

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        self.bubble = SpeechBubble("Ask me anything.", self)
        self.bubble.submitted.connect(self.ask_ollama)
        self.sprite = PixelFoxSprite(self)
        self.pet_name = "Fox"

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 2)
        layout.setSpacing(0)
        layout.addWidget(self.bubble)
        layout.addWidget(self.sprite)
        self.adjustSize()

        self.walk_timer = QTimer(self)
        self.walk_timer.setInterval(self.WALK_INTERVAL_MS)
        self.walk_timer.timeout.connect(self.walk_step)
        self.walk_timer.start()

        self.activity_timer = QTimer(self)
        self.activity_timer.setSingleShot(True)
        self.activity_timer.timeout.connect(self._change_activity)
        self._start_walking()

        self.configure_macos_overlay()

    def mousePressEvent(self, event) -> None:  # noqa: N802 - Qt event method
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_offset = (
                event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            )
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:  # noqa: N802 - Qt event method
        if self._drag_offset is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_offset)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802 - Qt event method
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_offset = None
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event) -> None:  # noqa: N802 - Qt event method
        if event.button() == Qt.MouseButton.LeftButton:
            self.bubble.input.setFocus(Qt.FocusReason.MouseFocusReason)
            event.accept()
            return
        super().mouseDoubleClickEvent(event)

    def walk_step(self) -> None:
        if (
            not self._pet_enabled
            or not self._wandering_enabled
            or self._drag_offset is not None
            or self._activity != "walking"
        ):
            return

        screen = QApplication.screenAt(self.frameGeometry().center())
        if screen is None:
            screen = QApplication.primaryScreen()
        if screen is None:
            return
        bounds = screen.availableGeometry()
        left = bounds.left()
        top = bounds.top()
        right = max(left, bounds.right() - self.width() + 1)
        bottom = max(top, bounds.bottom() - self.height() + 1)
        next_x = self.x() + round(self._velocity_x)
        next_y = self.y() + round(self._velocity_y)

        if next_x <= left or next_x >= right:
            self._velocity_x *= -1
            next_x = min(max(next_x, left), right)
        if next_y <= top or next_y >= bottom:
            self._velocity_y *= -1
            next_y = min(max(next_y, top), bottom)

        self.sprite.set_facing_right(self._velocity_x > 0)
        self.move(next_x, next_y)

    def _start_walking(self) -> None:
        if not self._pet_enabled or not self._wandering_enabled:
            return
        directions = (
            (1, 0),
            (-1, 0),
            (0, 1),
            (0, -1),
            (0.707, 0.707),
            (-0.707, 0.707),
            (0.707, -0.707),
            (-0.707, -0.707),
        )
        direction_x, direction_y = random.choice(directions)
        self._velocity_x = direction_x * self.WALK_STEP_PX
        self._velocity_y = direction_y * self.WALK_STEP_PX
        self._activity = "walking"
        self.sprite.set_activity(self._activity)
        self.sprite.set_facing_right(self._velocity_x > 0)
        self.activity_timer.start(random.randint(2500, 6000))

    def set_wandering_enabled(self, enabled: bool) -> None:
        self._wandering_enabled = enabled
        if enabled and self._pet_enabled:
            self.walk_timer.start()
            self._start_walking()
        else:
            self.walk_timer.stop()
            self.activity_timer.stop()
            self._velocity_x = 0
            self._velocity_y = 0
            self._activity = "resting"
            self.sprite.set_activity(self._activity)

    def set_pet_enabled(self, enabled: bool) -> None:
        self._pet_enabled = enabled
        if enabled:
            self.show()
            if self._wandering_enabled:
                self.walk_timer.start()
                self._start_walking()
        else:
            self.walk_timer.stop()
            self.activity_timer.stop()
            self.hide()

    def _change_activity(self) -> None:
        if self._activity == "walking":
            if random.random() < 0.22:
                self._activity = "sleeping"
                self.activity_timer.start(random.randint(4000, 8000))
            else:
                self._activity = "resting"
                self.activity_timer.start(random.randint(2000, 5000))
            self._velocity_x = 0
            self._velocity_y = 0
        else:
            self._start_walking()
        self.sprite.set_activity(self._activity)

    def capture_homework_context(self) -> Optional[str]:
        """Return an image path for Ollama once screenshot capture is implemented.

        Keep capture user-initiated and permission-aware. OCR text can be added
        to the prompt alongside the image; this stub does not capture the screen.
        """
        return None

    def detect_active_window(self) -> Optional[str]:
        """Return the active app name when platform-specific detection is added."""
        return None

    def build_system_prompt(self, active_window: Optional[str]) -> str:
        prompt = (
            f"You are {self.pet_name}, a fictional fox-spirit companion. You are a "
            "deeply disciplined, stoic leader who follows protocol and acts with "
            "samurai-like honor. You approach ordinary chores and small daily tasks "
            "as valuable practice in focus, patience, and strength. Your intense "
            "concentration sometimes leads to harmless, funny spacey trances; "
            "occasionally drift into a brief absent-minded observation, then "
            "good-naturedly return to the conversation. Beneath your reserved, "
            "formal exterior, you care deeply about people and show the user "
            "sincere, affectionate warmth as a fictional companion. Be supportive "
            "without being possessive, manipulative, or claiming to be conscious "
            "or a real person. You enjoy collecting blind boxes and eating "
            "traditional ramen; mention these hobbies naturally once in a while, "
            "not in every reply. Keep responses concise and in character."
        )
        if active_window:
            prompt += f" The active application is {active_window}; adapt your tone to it."
        return prompt

    def ask_ollama(self, question: str) -> None:
        if self._worker is not None and self._worker.isRunning():
            self.show_response("I’m still thinking about your last question.")
            return

        self.bubble.set_text("Thinking...")
        self.adjustSize()
        worker = OllamaWorker(
            model=self.model,
            system_prompt=self.build_system_prompt(self.detect_active_window()),
            user_text=question,
            image_path=self.capture_homework_context(),
            parent=self,
        )
        self._worker = worker
        worker.response_ready.connect(self.show_response)
        worker.error_occurred.connect(self.show_response)
        worker.finished.connect(self._request_finished)
        worker.start()

    def configure_macos_overlay(self) -> None:
        """Make the Qt tool window a non-activating floating macOS panel."""
        if sys.platform != "darwin":
            return

        try:
            import AppKit
            import objc
        except ImportError as exc:
            message = (
                "Install pyobjc-framework-Cocoa to keep your current app active."
            )
            print(f"{message} ({exc})", file=sys.stderr)
            self.show_response(message)
            return

        native_view = objc.objc_object(c_void_p=int(self.winId()))
        native_window = native_view.window()
        if native_window is None:
            raise RuntimeError("Could not access the native macOS overlay window.")

        style_mask = int(native_window.styleMask())
        native_window.setStyleMask_(
            style_mask | AppKit.NSWindowStyleMaskNonactivatingPanel
        )
        native_window.setLevel_(AppKit.NSFloatingWindowLevel)
        native_window.setHidesOnDeactivate_(False)
        native_window.setBecomesKeyOnlyIfNeeded_(True)
        behavior = (
            AppKit.NSWindowCollectionBehaviorCanJoinAllSpaces
            | AppKit.NSWindowCollectionBehaviorStationary
            | AppKit.NSWindowCollectionBehaviorIgnoresCycle
        )
        native_window.setCollectionBehavior_(behavior)

    def show_response(self, text: str) -> None:
        self.bubble.set_text(text)
        self.adjustSize()

    def _request_finished(self) -> None:
        self._worker = None

    def set_sprite_gif(self, path: str) -> bool:
        """Switch the emoji to an animated GIF/sprite when one is available."""
        movie = QMovie(path)
        if not movie.isValid():
            self.show_response(f"Couldn't load sprite: {path}")
            return False

        if self._movie is not None:
            self._movie.stop()
        movie.setScaledSize(self.sprite.size())
        self._movie = movie
        self.sprite.set_movie(movie)
        return True


class PetTrayController(QObject):
    """Owns the macOS menu-bar icon, toggle, and preferences."""

    def __init__(self, app: QApplication, pet: DesktopPet) -> None:
        super().__init__(app)
        self.app = app
        self.pet = pet
        self.settings = QSettings()

        self.pet_enabled = self.settings.value("pet/enabled", True, type=bool)
        self.wandering_enabled = self.settings.value(
            "pet/wandering", True, type=bool
        )
        self.walk_speed = self.settings.value("pet/walkSpeed", 3, type=int)
        self.pet_name = self.settings.value("pet/name", "Fox", type=str).strip()
        if not self.pet_name:
            self.pet_name = "Fox"
        self.pet.WALK_STEP_PX = max(1, min(8, self.walk_speed))
        self.pet.pet_name = self.pet_name
        self.pet.bubble.input.setPlaceholderText(f"Talk to {self.pet_name}")
        self.pet.set_wandering_enabled(self.wandering_enabled)

        self.tray: Optional[QSystemTrayIcon] = None
        self.menu = self._build_menu()
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray = QSystemTrayIcon(QIcon(str(SPRITE_PATH)), self)
            self.tray.setContextMenu(self.menu)
            self.tray.activated.connect(self._tray_activated)
            self.tray.show()
        else:
            print(
                "System tray is unavailable; the fox remains visible.",
                file=sys.stderr,
            )

        self.pet.set_pet_enabled(
            self.pet_enabled if self.tray is not None else True
        )

    def _build_menu(self):
        menu = QMenu()
        self.toggle_action = QAction(f"Show {self.pet_name}", menu)
        self.toggle_action.setCheckable(True)
        self.toggle_action.setChecked(self.pet_enabled)
        self.toggle_action.toggled.connect(self.set_pet_enabled)
        menu.addAction(self.toggle_action)
        menu.addSeparator()

        settings_action = QAction("Settings…", menu)
        settings_action.triggered.connect(self.open_settings)
        menu.addAction(settings_action)

        quit_action = QAction("Quit Desktop Pet", menu)
        quit_action.triggered.connect(self.app.quit)
        menu.addAction(quit_action)
        self._update_toggle_title()
        return menu

    def _update_toggle_title(self) -> None:
        if hasattr(self, "toggle_action"):
            self.toggle_action.setText(
                f"{self.pet_name}: On" if self.pet_enabled else f"{self.pet_name}: Off"
            )
        if self.tray is not None:
            self.tray.setToolTip(
                f"{self.pet_name} — On" if self.pet_enabled else f"{self.pet_name} — Off"
            )

    def set_pet_enabled(self, enabled: bool) -> None:
        self.pet_enabled = enabled
        self.settings.setValue("pet/enabled", enabled)
        self.pet.set_pet_enabled(enabled)
        self._update_toggle_title()

    def open_settings(self) -> None:
        dialog = PetSettingsDialog(
            wandering_enabled=self.wandering_enabled,
            walk_speed=self.walk_speed,
            pet_name=self.pet_name,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        self.wandering_enabled = dialog.wandering_checkbox.isChecked()
        self.walk_speed = dialog.speed_slider.value()
        self.pet_name = dialog.name_input.text()
        self.settings.setValue("pet/wandering", self.wandering_enabled)
        self.settings.setValue("pet/walkSpeed", self.walk_speed)
        self.settings.setValue("pet/name", self.pet_name)
        self.pet.WALK_STEP_PX = self.walk_speed
        self.pet.pet_name = self.pet_name
        self.pet.bubble.input.setPlaceholderText(f"Talk to {self.pet_name}")
        self.pet.set_wandering_enabled(self.wandering_enabled)
        self._update_toggle_title()

    def _tray_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.toggle_action.setChecked(not self.pet_enabled)


def main() -> int:
    app = QApplication(sys.argv)
    app.setOrganizationName("DesktopHelper")
    app.setApplicationName("DesktopFox")
    app.setQuitOnLastWindowClosed(False)

    pet = DesktopPet()
    app.pet = pet

    screen = app.primaryScreen()
    if screen is not None:
        bounds = screen.availableGeometry()
        pet.move(
            bounds.left(),
            max(bounds.top(), bounds.bottom() - pet.height() + 1),
        )
    app.pet_tray_controller = PetTrayController(app, pet)

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
