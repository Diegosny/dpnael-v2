from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Static
from textual.containers import Vertical


class RunContainerModal(ModalScreen[dict | None]):
    CSS = """
    RunContainerModal {
        align: center middle;
    }
    #dialog {
        width: 55;
        height: auto;
        border: round #D126F7;
        background: $surface;
        padding: 1 2;
    }
    Input {
        margin-bottom: 1;
        border: solid $accent;
    }
    .buttons {
        layout: horizontal;
        margin-top: 1;
    }
    Button {
        width: 50%;
    }
    """

    def __init__(self, default_image: str = "nginx:latest"):
        super().__init__()
        self.default_image = default_image

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Static("[bold magenta]🚀 Executar Novo Container[/bold magenta]\n")

            yield Label("Imagem (ex: nginx:latest):")
            yield Input(value=self.default_image, id="image_input")

            yield Label("Nome do Container (opcional):")
            yield Input(placeholder="ex: meu-web-server", id="name_input")

            yield Label("Portas [Host:Container] (ex: 8080:80):")
            yield Input(placeholder="8080:80", id="ports_input")

            yield Label("Volume [HostPath:ContainerPath] (opcional):")
            yield Input(placeholder="/var/www/html:/usr/share/nginx/html", id="volume_input")

            with Vertical(classes="buttons"):
                yield Button("▶ Executar", variant="success", id="btn_run")
                yield Button("Cancelar", variant="error", id="btn_cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_run":
            image = self.query_one("#image_input", Input).value.strip()
            name = self.query_one("#name_input", Input).value.strip()
            ports = self.query_one("#ports_input", Input).value.strip()
            volume = self.query_one("#volume_input", Input).value.strip()

            if not image:
                return

            self.dismiss({
                "image": image,
                "name": name if name else None,
                "ports": ports if ports else None,
                "volume": volume if volume else None
            })
        else:
            self.dismiss(None)