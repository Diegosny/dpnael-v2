from textual.widgets import Static
from dpnael.models.container import ContainerInfo

class PreviewPanelWidget(Static):
    def show_container_info(self, container: ContainerInfo):
        content = f"""
🔍 [bold magenta]INFORMAÇÕES DO CONTAINER[/bold magenta]

[bold]Nome:[/bold]       {container.name}
[bold]ID:[/bold]         {container.short_id}
[bold]Status:[/bold]     {container.status.upper()}
[bold]Imagem:[/bold]     {container.image}
[bold]IP Interno:[/bold] {container.ip_address or "N/A"}
[bold]Comando:[/bold]    [dim]{container.command}[/dim]
        """
        self.update(content)

    def clear_info(self):
        self.update("[dim]Selecione um container na lista...[/dim]")