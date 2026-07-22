from textual.widgets import OptionList
from textual.widgets.option_list import Option


class ContainerListWidget(OptionList):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.containers_map = {}

    def update_containers(self, containers, error_msg: str = None):
        """Limpa e atualiza a lista com os containers ativas/parados."""
        self.clear_options()
        self.containers_map.clear()

        if error_msg:
            self.add_option(Option(f"❌ Erro Docker: {error_msg}", disabled=True))
            return

        if not containers:
            self.add_option(Option("⚠️ Nenhum container encontrado", disabled=True))
            return

        for c in containers:
            c_id = c.short_id if hasattr(c, "short_id") else str(c.id)[:12]
            c_name = c.name
            c_status = getattr(c, "status", "unknown")

            status_icon = "🟢" if c_status == "running" else "🔴"
            label = f"{status_icon} [bold]{c_name}[/bold]  [dim]({c_id})[/dim]"

            # Adicionamos 'cnt_' no início porque IDs do Textual não podem começar com números
            option_id = f"cnt_{c.id}"
            self.add_option(Option(label, id=option_id))
            self.containers_map[option_id] = c

    def get_selected_container(self):
        """Retorna o objeto do container selecionado na lista."""
        if self.highlighted is not None and self.option_count > 0:
            try:
                option = self.get_option_at_index(self.highlighted)
                if option and option.id:
                    return self.containers_map.get(option.id)
            except Exception:
                pass
        return None