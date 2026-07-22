from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Input, TabbedContent, TabPane
from textual.containers import Horizontal, Vertical

# Importe seus widgets das pastas corretas
from dpnael.ui.widgets.container_list import ContainerListWidget
from dpnael.ui.widgets.preview_panel import PreviewPanelWidget


class DpnaelApp(App):
    # CSS Corrigido com variáveis válidas do Textual
    CSS = """
    Screen {
        background: $surface;
    }

    Header {
        background: #D126F7;
        color: white;
    }

    #left_panel {
        width: 40%;
        height: 100%;
        border: round #D126F7;
        border-title-color: #D126F7;
        margin-right: 1;
    }

    #right_panel {
        width: 60%;
        height: 100%;
        border: round $accent;
        border-title-color: $accent;
        padding: 1 2;
    }

    Input {
        margin-bottom: 1;
        border: solid $accent;
    }
    """

    def __init__(self, docker_service=None, **kwargs):
        super().__init__(**kwargs)
        self.docker_service = docker_service

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        with TabbedContent():
            with TabPane("📦 Containers", id="tab_containers"):
                with Horizontal():
                    # Lado Esquerdo - Filtro + Lista
                    with Vertical(id="left_panel") as v:
                        v.border_title = " Lista de Containers "
                        yield Input(placeholder="🔍 Digite para filtrar...", id="search_input")
                        yield ContainerListWidget(id="container_list")

                    # Lado Direito - Preview
                    with Vertical(id="right_panel") as v:
                        v.border_title = " Inspeção & Preview "
                        yield PreviewPanelWidget(id="preview")

            with TabPane("🖼️ Imagens", id="tab_images"):
                yield Static("Gerenciador de Imagens...")

            with TabPane("🌐 Redes", id="tab_networks"):
                yield Static("Mapeamento de Redes...")

        yield Footer()

    def on_mount(self) -> None:
        """Carrega os dados assim que o app é renderizado."""
        self.action_refresh()

    def action_refresh(self) -> None:
        """Busca os containers através da camada de serviço."""
        if not self.docker_service:
            return

        containers = self.docker_service.list_containers()
        list_widget = self.query_one("#container_list", ContainerListWidget)

        # Atualiza o widget da lista se o método update_containers existir nele
        if hasattr(list_widget, "update_containers"):
            list_widget.update_containers(containers)