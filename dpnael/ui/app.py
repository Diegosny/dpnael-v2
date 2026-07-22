import subprocess
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Footer, Static, Input, TabbedContent, TabPane, OptionList, DataTable

from dpnael.services.docker_service import DockerService
from dpnael.services.hosts_service import HostsService
from dpnael.ui.widgets.container_list import ContainerListWidget
from dpnael.ui.widgets.preview_panel import PreviewPanelWidget
from dpnael.ui.screens.tinker_screen import TinkerModal


class DpnaelApp(App):
    TITLE = "DPNAEL — Docker Management"

    CSS = """
    Screen { background: $surface; }
    Header { background: #D126F7; color: white; }
    Footer { background: $surface-darken-1; }

    #left_panel {
        width: 40%;
        height: 100%;
        border: round #D126F7;
        border-title-color: #D126F7;
        margin-right: 1;
    }

    #images_left_panel {
        width: 60%;
        height: 100%;
        border: round #D126F7;
        border-title-color: #D126F7;
        margin-right: 1;
    }

    #right_panel, #images_right_panel {
        height: 100%;
        border: round $accent;
        border-title-color: $accent;
        padding: 1 2;
    }

    #right_panel { width: 60%; }
    #images_right_panel { width: 40%; }

    Input { margin-bottom: 1; border: solid $accent; }
    ContainerListWidget { height: 1fr; }
    DataTable { height: 1fr; }

    #networks_panel, #hosts_panel {
        padding: 1 2;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Sair", show=True),
        Binding("r", "refresh", "Atualizar", show=True),
        Binding("space", "toggle_start_stop", "▶️ Start/Stop", show=True),
        Binding("R", "restart_container", "🔄 Restart", show=True),
        Binding("p", "toggle_pause", "⏸️ Pause", show=True),
        Binding("s", "open_shell", "🐚 Shell", show=True),
        Binding("l", "view_logs", "🔍 Logs", show=True),
        Binding("t", "run_tinker", "🐘 Tinker", show=True),
        Binding("i", "pull_image", "📥 Pull Imagem", show=True),
        Binding("x", "run_xray", "🩻 Dive", show=True),
        Binding("n", "run_sniffer", "🕸️ Sniffer", show=True),
        Binding("b", "backup_image", "🖼️ Backup", show=True),
        Binding("c", "to_compose", "🧬 Compose", show=True),
        Binding("h", "add_host_domain", "🔗 Hosts", show=True),
        Binding("P", "prune_system", "🧹 Prune", show=True),
        Binding("delete", "remove_item", "❌ Deletar", show=True),
    ]

    def __init__(self, docker_service: DockerService = None, **kwargs):
        super().__init__(**kwargs)
        self.docker_service = docker_service or DockerService()
        self.hosts_service = HostsService()
        self.containers_cache = []
        self.images_cache = []

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with TabbedContent(id="main_tabs"):
            # ABA 1: CONTAINERS
            with TabPane("📦 Containers", id="tab_containers"):
                with Horizontal():
                    with Vertical(id="left_panel") as v:
                        v.border_title = " Containers Ativos / Parados "
                        yield Input(placeholder="🔍 Digite para filtrar...", id="search_input")
                        yield ContainerListWidget(id="container_list")

                    with Vertical(id="right_panel") as v:
                        v.border_title = " Inspeção & Preview "
                        yield PreviewPanelWidget(id="preview")

            # ABA 2: IMAGENS
            with TabPane("🖼️ Imagens", id="tab_images"):
                with Horizontal():
                    with Vertical(id="images_left_panel") as v:
                        v.border_title = " Imagens Locais "
                        yield DataTable(id="images_table")
                    with Vertical(id="images_right_panel") as v:
                        v.border_title = " Detalhes da Imagem "
                        yield Static("Selecione uma imagem para inspecionar.", id="image_preview")

            # ABA 3: REDES
            with TabPane("🌐 Redes", id="tab_networks"):
                yield Static("🌐 Carregando redes...", id="networks_panel")

            # ABA 4: HOSTS
            with TabPane("🔗 Hosts", id="tab_hosts"):
                yield Static("🔗 Domínios Mapeados em /etc/hosts", id="hosts_panel")

        yield Footer()

    def on_mount(self) -> None:
        img_table = self.query_one("#images_table", DataTable)
        img_table.cursor_type = "row"
        img_table.add_columns("Repositório", "Tag", "ID", "Tamanho", "Criado em")

        self.action_refresh()

    def action_refresh(self) -> None:
        # 1. Containers
        self.containers_cache = self.docker_service.list_containers(show_all=True)
        list_widget = self.query_one("#container_list", ContainerListWidget)
        list_widget.update_containers(self.containers_cache, error_msg=self.docker_service.last_error)

        # 2. Imagens
        self.images_cache = self.docker_service.list_images()
        img_table = self.query_one("#images_table", DataTable)
        img_table.clear()

        for img in self.images_cache:
            tags = img.tags if img.tags else ["<none>:<none>"]
            for tag in tags:
                repo, t = tag.split(":", 1) if ":" in tag else (tag, "<none>")
                size_mb = f"{img.attrs.get('Size', 0) / (1024 * 1024):.1f} MB" if isinstance(img.attrs, dict) else "N/A"
                created = str(img.attrs.get('Created', ''))[:10] if isinstance(img.attrs, dict) else "N/A"
                img_table.add_row(repo, t, img.short_id, size_mb, created, key=f"{img.id}::{tag}")

        # 3. Redes
        networks = self.docker_service.list_networks()
        net_text = "🌐 [bold magenta]Redes Docker Registradas:[/bold magenta]\n\n"
        if networks:
            for net in networks:
                driver = net.attrs.get("Driver", "desconhecido") if isinstance(net.attrs, dict) else "N/A"
                driver_display = f"{driver} [dim](sem conectividade)[/dim]" if driver == "null" else driver
                net_text += f"• [bold green]{net.name}[/bold green] [dim]({net.short_id})[/dim]\n"
                net_text += f"  ├── Driver: [cyan]{driver_display}[/cyan]\n\n"
        else:
            net_text += "Nenhuma rede encontrada."

        self.query_one("#networks_panel", Static).update(net_text)

        # 4. Hosts
        hosts = self.hosts_service.list_domains()
        hosts_text = "🔗 [bold magenta]Mapeamentos Ativos no /etc/hosts:[/bold magenta]\n\n"
        if hosts:
            for domain, ip in hosts:
                hosts_text += f"• [bold green]{domain}[/bold green] ➔ {ip}\n"
        else:
            hosts_text += "Nenhum domínio mapeado pelo DPNAEL."
        self.query_one("#hosts_panel", Static).update(hosts_text)

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        if event.data_table.id != "images_table":
            return

        row_key = event.row_key.value
        if not row_key or "::" not in row_key:
            return

        img_id, tag = row_key.split("::", 1)
        for img in self.images_cache:
            if img.id == img_id:
                size_mb = f"{img.attrs.get('Size', 0) / (1024 * 1024):.2f} MB" if isinstance(img.attrs, dict) else "N/A"
                created = str(img.attrs.get("Created", ""))[:19] if isinstance(img.attrs, dict) else "N/A"

                info = f"""[bold magenta]🖼️  TAG:[/bold magenta] [green]{tag}[/green]
[bold magenta]🆔 ID:[/bold magenta] {img.short_id}
[bold magenta]💾 TAMANHO:[/bold magenta] {size_mb}
[bold magenta]⏱️  CRIADA EM:[/bold magenta] {created}

[bold yellow]🛠️ AÇÕES DISPONÍVEIS:[/bold yellow]
  • [bold cyan]i[/bold cyan] : Fazer Pull de nova imagem
  • [bold cyan]b[/bold cyan] : Exportar Backup em .tar
  • [bold cyan]x[/bold cyan] : Analisar camadas com Dive
  • [bold red]DEL[/bold red] : Deletar esta imagem
"""
                self.query_one("#image_preview", Static).update(info)
                break

    def on_option_list_option_highlighted(self, event: OptionList.OptionHighlighted) -> None:
        list_widget = self.query_one("#container_list", ContainerListWidget)
        c = list_widget.get_selected_container()
        if c:
            self.update_container_preview(c)

    def update_container_preview(self, c) -> None:
        status_color = "green" if c.status == "running" else ("yellow" if c.status == "paused" else "red")
        image_name = c.image.tags[0] if c.image.tags else c.image.id[:12]
        ports = c.attrs.get("NetworkSettings", {}).get("Ports", {}) or {} if isinstance(c.attrs, dict) else {}

        c_ip = self.docker_service.get_container_ip(c.id) or "N/A"
        hosts_list = self.hosts_service.list_domains()
        mapped_hosts = [domain for domain, ip in hosts_list if ip == c_ip] if c_ip != "N/A" else []

        info = f"""[bold magenta]📦 CONTAINER:[/bold magenta] {c.name} ({c.short_id})
[bold magenta]🏷️  STATUS:[/bold magenta] [{status_color}]{c.status.upper()}[/{status_color}]
[bold magenta]🖼️  IMAGEM:[/bold magenta] {image_name}
[bold magenta]🌐 IP INTERNO:[/bold magenta] {c_ip}

[bold yellow]🔌 PORTAS MAPEADAS:[/bold yellow]
"""
        if ports:
            for container_port, host_bindings in ports.items():
                if host_bindings:
                    for binding in host_bindings:
                        info += f"  • Host [green]{binding.get('HostPort')}[/green] ➔ Container {container_port}\n"
                else:
                    info += f"  • Container {container_port} (Interna)\n"
        else:
            info += "  Nenhuma porta exposta.\n"

        info += "\n[bold yellow]🔗 DOMÍNIOS MAPEADOS (/etc/hosts):[/bold yellow]\n"
        if mapped_hosts:
            for domain in mapped_hosts:
                info += f"  • [bold green]{domain}[/bold green] ➔ {c_ip}\n"
        else:
            info += "  [dim]Nenhum domínio vinculado (Pressione 'h' para adicionar)[/dim]\n"

        self.query_one("#preview", PreviewPanelWidget).update(info)

    def get_selected_container(self):
        return self.query_one("#container_list", ContainerListWidget).get_selected_container()

    # =========================================================================
    # AÇÕES DE CICLO DE VIDA
    # =========================================================================

    def action_toggle_start_stop(self) -> None:
        c = self.get_selected_container()
        if not c: return
        try:
            if c.status == "running":
                c.stop()
            else:
                c.start()
        except Exception as e:
            self.query_one("#preview", PreviewPanelWidget).update(f"[red]❌ Erro ao alterar estado: {e}[/red]")
        self.action_refresh()

    def action_restart_container(self) -> None:
        c = self.get_selected_container()
        if not c: return
        try:
            c.restart()
        except Exception as e:
            self.query_one("#preview", PreviewPanelWidget).update(f"[red]❌ Erro ao reiniciar: {e}[/red]")
        self.action_refresh()

    def action_toggle_pause(self) -> None:
        c = self.get_selected_container()
        if not c: return
        try:
            if c.status == "paused":
                c.unpause()
            else:
                c.pause()
        except Exception as e:
            self.query_one("#preview", PreviewPanelWidget).update(f"[red]❌ Erro ao pausar/despausar: {e}[/red]")
        self.action_refresh()

    # =========================================================================
    # DEMAIS AÇÕES
    # =========================================================================

    def action_pull_image(self) -> None:
        with self.suspend():
            image_name = input("\n📥 Nome da imagem para Pull (ex: nginx:latest): ").strip()
            if image_name:
                print(f"Baixando '{image_name}'...")
                ok, msg = self.docker_service.pull_image(image_name)
                print(f"\n{msg}\n")
                input("Pressione Enter para continuar...")
        self.action_refresh()

    def action_open_shell(self) -> None:
        c = self.get_selected_container()
        if not c: return
        with self.suspend():
            print(f"\n🐚 Conectando ao shell de {c.name}...\n")
            subprocess.run(f"docker exec -it {c.id} bash 2>/dev/null || docker exec -it {c.id} sh", shell=True)
        self.action_refresh()

    def action_view_logs(self) -> None:
        c = self.get_selected_container()
        if not c: return
        with self.suspend():
            print(f"\n🔍 Lendo logs de {c.name} (Ctrl+C para sair)...\n")
            try:
                subprocess.run(f"docker logs -f --tail 100 {c.id}", shell=True)
            except KeyboardInterrupt:
                pass

    def action_run_tinker(self) -> None:
        c = self.get_selected_container()
        if not c: return

        def on_tinker_submit(php_code: str | None):
            if php_code:
                res = self.docker_service.run_laravel_tinker(c.id, php_code)
                self.query_one("#preview", PreviewPanelWidget).update(
                    f"🐘 [bold magenta]Tinker Result:[/bold magenta]\n\n{res}")

        self.push_screen(TinkerModal(c.name), on_tinker_submit)

    def action_run_xray(self) -> None:
        tabbed_content = self.query_one("#main_tabs", TabbedContent)
        active_tab = tabbed_content.active

        img_target = None
        if active_tab == "tab_containers":
            c = self.get_selected_container()
            if c:
                img_target = c.image.tags[0] if c.image.tags else c.image.id
        elif active_tab == "tab_images":
            table = self.query_one("#images_table", DataTable)
            if table.cursor_row is not None:
                row_key = table.coordinate_to_cell_key(table.cursor_coordinate).row_key.value
                if row_key and "::" in row_key:
                    img_target = row_key.split("::", 1)[1]

        if img_target:
            with self.suspend():
                subprocess.run(
                    f"docker run --rm -it -v /var/run/docker.sock:/var/run/docker.sock wagoodman/dive:latest {img_target}",
                    shell=True)

    def action_run_sniffer(self) -> None:
        c = self.get_selected_container()
        if not c: return
        with self.suspend():
            port = input("Porta (ex: 80) [Enter para todas]: ").strip()
            filter_cmd = f"port {port}" if port else ""
            subprocess.run(
                f"docker run -it --rm --network 'container:{c.id}' nicolaka/netshoot tcpdump -i any -A -nn {filter_cmd}",
                shell=True)

    def action_backup_image(self) -> None:
        tabbed_content = self.query_one("#main_tabs", TabbedContent)
        active_tab = tabbed_content.active

        img_target = None
        if active_tab == "tab_containers":
            c = self.get_selected_container()
            if c:
                img_target = c.image.tags[0] if c.image.tags else c.image.id
        elif active_tab == "tab_images":
            table = self.query_one("#images_table", DataTable)
            if table.cursor_row is not None:
                row_key = table.coordinate_to_cell_key(table.cursor_coordinate).row_key.value
                if row_key and "::" in row_key:
                    img_target = row_key.split("::", 1)[1]

        if img_target:
            ok, msg = self.docker_service.backup_image(img_target)
            if active_tab == "tab_containers":
                self.query_one("#preview", PreviewPanelWidget).update(msg)
            else:
                self.query_one("#image_preview", Static).update(msg)

    def action_to_compose(self) -> None:
        c = self.get_selected_container()
        if not c: return
        ok, msg = self.docker_service.container_to_compose(c.name)
        self.query_one("#preview", PreviewPanelWidget).update(msg)

    def action_add_host_domain(self) -> None:
        c = self.get_selected_container()
        if not c: return
        ip = self.docker_service.get_container_ip(c.id)
        if not ip:
            self.query_one("#preview", PreviewPanelWidget).update("[red]❌ Container sem IP bridge interno.[/red]")
            return
        with self.suspend():
            domain = input(f"Domínio para {ip} (ex: api.local): ").strip()
            if domain:
                ok, msg = self.hosts_service.add_domain(ip, domain, c.name)
                print(f"\n{msg}\n")
                input("Pressione Enter para continuar...")
        self.action_refresh()

    def action_prune_system(self) -> None:
        with self.suspend():
            if input("Executar 'docker system prune'? [y/N]: ").strip().lower() == 'y':
                print(f"\n✔ {self.docker_service.prune_system()}\n")
                input("Pressione Enter...")
        self.action_refresh()

    def action_remove_item(self) -> None:
        tabbed_content = self.query_one("#main_tabs", TabbedContent)
        active_tab = tabbed_content.active

        if active_tab == "tab_containers":
            c = self.get_selected_container()
            if not c: return
            with self.suspend():
                if input(f"DELETAR CONTAINER '{c.name}'? [y/N]: ").strip().lower() == 'y':
                    try:
                        c.remove(force=True)
                        print(f"\n✔ Container removido.\n")
                    except Exception as e:
                        print(f"\n❌ Erro: {e}\n")
                    input("Pressione Enter...")
        elif active_tab == "tab_images":
            table = self.query_one("#images_table", DataTable)
            if table.cursor_row is not None:
                row_key = table.coordinate_to_cell_key(table.cursor_coordinate).row_key.value
                if row_key and "::" in row_key:
                    img_id, tag = row_key.split("::", 1)
                    with self.suspend():
                        if input(f"DELETAR IMAGEM '{tag}'? [y/N]: ").strip().lower() == 'y':
                            ok, msg = self.docker_service.remove_image(tag, force=True)
                            print(f"\n{msg}\n")
                            input("Pressione Enter...")

        self.action_refresh()

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "search_input":
            query = event.value.lower()
            filtered = [
                c for c in self.containers_cache
                if query in c.name.lower() or query in (c.image.tags[0] if c.image.tags else "").lower()
            ]
            self.query_one("#container_list", ContainerListWidget).update_containers(filtered,
                                                                                     error_msg=self.docker_service.last_error)


def main():
    DpnaelApp().run()


if __name__ == "__main__":
    main()