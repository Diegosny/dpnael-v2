from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, TextArea, Label
from textual.containers import Vertical

class TinkerModal(ModalScreen[str]):
    def __init__(self, container_name: str):
        super().__init__()
        self.container_name = container_name

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Label(f"🐘 Laravel Tinker — Executar em: {self.container_name}")
            yield TextArea(id="php_code", language="php")
            yield Button("🚀 Executar (Ctrl+Enter)", id="btn_run", variant="primary")
            yield Button("Cancelar", id="btn_cancel", variant="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_run":
            code = self.query_one("#php_code", TextArea).text
            self.dismiss(code)
        else:
            self.dismiss(None)