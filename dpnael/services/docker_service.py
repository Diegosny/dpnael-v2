import os
import docker


class ImageAdapter:
    def __init__(self, raw_image):
        self._raw = raw_image
        if isinstance(raw_image, dict):
            self.id = raw_image.get("Id", "")
            self.short_id = self.id.replace("sha256:", "")[:12]
            tags = raw_image.get("RepoTags") or []
            self.tags = tags if isinstance(tags, list) else []
            self.attrs = raw_image
        else:
            self.id = getattr(raw_image, "id", "")
            self.short_id = getattr(raw_image, "short_id", self.id[:12])
            tags = getattr(raw_image, "tags", []) or []
            self.tags = tags if isinstance(tags, list) else []
            self.attrs = getattr(raw_image, "attrs", {})


class ContainerAdapter:
    def __init__(self, raw_container, client):
        self.client = client
        self._raw = raw_container

        if isinstance(raw_container, dict):
            self.id = raw_container.get("Id", "")
            self.short_id = self.id[:12]
            names = raw_container.get("Names") or []
            if names:
                self.name = names[0].lstrip("/")
            else:
                self.name = raw_container.get("Name", "").lstrip("/") or self.short_id

            state = raw_container.get("State")
            if isinstance(state, dict):
                self.status = state.get("Status", "unknown")
            elif isinstance(state, str):
                self.status = state
            else:
                status_str = str(raw_container.get("Status", "")).lower()
                if "up" in status_str or "running" in status_str:
                    self.status = "running"
                elif "exited" in status_str:
                    self.status = "exited"
                else:
                    self.status = "stopped"

            img_name = raw_container.get("Image", "")
            img_id = raw_container.get("ImageID", "")
            self.image = ImageAdapter({"Id": img_id, "RepoTags": [img_name] if img_name else []})
            self.attrs = raw_container
        else:
            self.id = getattr(raw_container, "id", "")
            self.short_id = getattr(raw_container, "short_id", self.id[:12])
            self.name = getattr(raw_container, "name", "")
            self.status = getattr(raw_container, "status", "unknown")
            self.image = ImageAdapter(getattr(raw_container, "image", {}))
            self.attrs = getattr(raw_container, "attrs", {})

    def start(self):
        if hasattr(self._raw, "start") and callable(self._raw.start):
            return self._raw.start()
        elif hasattr(self.client, "start") and callable(self.client.start):
            return self.client.start(self.id)

    def stop(self):
        if hasattr(self._raw, "stop") and callable(self._raw.stop):
            return self._raw.stop()
        elif hasattr(self.client, "stop") and callable(self.client.stop):
            return self.client.stop(self.id)

    def restart(self):
        if hasattr(self._raw, "restart") and callable(self._raw.restart):
            return self._raw.restart()
        elif hasattr(self.client, "restart") and callable(self.client.restart):
            return self.client.restart(self.id)

    def pause(self):
        if hasattr(self._raw, "pause") and callable(self._raw.pause):
            return self._raw.pause()
        elif hasattr(self.client, "pause") and callable(self.client.pause):
            return self.client.pause(self.id)

    def unpause(self):
        if hasattr(self._raw, "unpause") and callable(self._raw.unpause):
            return self._raw.unpause()
        elif hasattr(self.client, "unpause") and callable(self.client.unpause):
            return self.client.unpause(self.id)

    def remove(self, force=False):
        if hasattr(self._raw, "remove") and callable(self._raw.remove):
            return self._raw.remove(force=force)
        elif hasattr(self.client, "remove_container") and callable(self.client.remove_container):
            return self.client.remove_container(self.id, force=force)

    def exec_run(self, cmd):
        if hasattr(self._raw, "exec_run") and callable(self._raw.exec_run):
            return self._raw.exec_run(cmd)
        elif hasattr(self.client, "exec_create") and hasattr(self.client, "exec_start"):
            exec_id = self.client.exec_create(self.id, cmd)["Id"]
            output = self.client.exec_start(exec_id)

            class ExecResult:
                def __init__(self, out):
                    self.output = out if isinstance(out, bytes) else str(out).encode("utf-8")

            return ExecResult(output)

        class EmptyResult:
            output = b""

        return EmptyResult()


class NetworkAdapter:
    def __init__(self, raw_net):
        self._raw = raw_net
        if isinstance(raw_net, dict):
            self.id = raw_net.get("Id", "")
            self.short_id = self.id[:12]
            self.name = raw_net.get("Name", "")
            self.attrs = raw_net
        else:
            self.id = getattr(raw_net, "id", "")
            self.short_id = getattr(raw_net, "short_id", self.id[:12])
            self.name = getattr(raw_net, "name", "")
            self.attrs = getattr(raw_net, "attrs", {})


class DockerService:
    def __init__(self, backup_dir: str = "/tmp/dpnael_backups"):
        self.backup_dir = backup_dir
        self.last_error = None
        self.client = None
        os.makedirs(self.backup_dir, exist_ok=True)
        self._connect()

    def _connect(self):
        try:
            self.client = docker.from_env(version="auto")
            self.last_error = None
        except Exception:
            try:
                self.client = docker.DockerClient(base_url="unix://var/run/docker.sock", version="auto")
                self.last_error = None
            except Exception as e:
                self.client = None
                self.last_error = str(e)

    def list_containers(self, show_all: bool = True):
        if not self.client:
            self._connect()
            if not self.client:
                return []
        try:
            containers_attr = getattr(self.client, "containers", None)
            if containers_attr is None:
                return []

            if callable(containers_attr):
                raw_list = containers_attr(all=show_all)
                return [ContainerAdapter(c, self.client) for c in raw_list]
            elif hasattr(containers_attr, "list"):
                return containers_attr.list(all=show_all)
            return []
        except Exception as e:
            self.last_error = str(e)
            return []

    def list_images(self):
        if not self.client:
            self._connect()
            if not self.client:
                return []
        try:
            images_attr = getattr(self.client, "images", None)
            if images_attr is None:
                return []
            if callable(images_attr):
                raw_list = images_attr()
                return [ImageAdapter(img) for img in raw_list]
            elif hasattr(images_attr, "list"):
                return images_attr.list()
            return []
        except Exception as e:
            self.last_error = str(e)
            return []

    def list_networks(self):
        if not self.client:
            self._connect()
            if not self.client:
                return []
        try:
            networks_attr = getattr(self.client, "networks", None)
            if networks_attr is None:
                return []
            if callable(networks_attr):
                raw_list = networks_attr()
                return [NetworkAdapter(net) for net in raw_list]
            elif hasattr(networks_attr, "list"):
                return networks_attr.list()
            return []
        except Exception as e:
            self.last_error = str(e)
            return []

    def get_container(self, container_id: str):
        if not self.client:
            self._connect()
            if not self.client:
                return None
        try:
            containers_attr = getattr(self.client, "containers", None)
            if callable(containers_attr):
                data = self.client.inspect_container(container_id)
                return ContainerAdapter(data, self.client)
            elif hasattr(containers_attr, "get"):
                return containers_attr.get(container_id)
        except Exception:
            pass
        return None

    def get_container_ip(self, container_id: str) -> str | None:
        container = self.get_container(container_id)
        if not container:
            return None
        try:
            net_settings = container.attrs.get("NetworkSettings", {}) or {}
            networks = net_settings.get("Networks", {}) or {}
            for net_name, net_info in networks.items():
                ip = net_info.get("IPAddress")
                if ip:
                    return ip
            ip = net_settings.get("IPAddress")
            if ip:
                return ip
        except Exception:
            pass
        return None

    def run_laravel_tinker(self, container_id: str, php_code: str) -> str:
        container = self.get_container(container_id)
        if not container:
            return "❌ Container não encontrado."
        try:
            escaped_code = php_code.replace('"', '\\"')
            cmd = f'php artisan tinker --execute="{escaped_code}"'
            res = container.exec_run(cmd)
            out = res.output
            if isinstance(out, bytes):
                return out.decode("utf-8", errors="ignore")
            return str(out)
        except Exception as e:
            return f"❌ Erro ao executar Tinker: {e}"

    def backup_image(self, image_tag: str) -> tuple[bool, str]:
        if not self.client:
            self._connect()
            if not self.client:
                return False, "❌ Cliente Docker não conectado."
        try:
            sanitized_tag = image_tag.replace(":", "_").replace("/", "_")
            dest_path = os.path.join(self.backup_dir, f"{sanitized_tag}.tar")

            if hasattr(self.client, "images") and hasattr(self.client.images, "get"):
                image = self.client.images.get(image_tag)
                chunks = image.save()
            elif hasattr(self.client, "get_image"):
                chunks = self.client.get_image(image_tag)
            else:
                return False, "❌ Operação save não suportada."

            with open(dest_path, "wb") as f:
                for chunk in chunks:
                    f.write(chunk)
            return True, f"✔ Imagem salva em:\n{dest_path}"
        except Exception as e:
            return False, f"❌ Erro ao exportar imagem: {e}"

    def container_to_compose(self, container_name: str, dest_dir: str = ".") -> tuple[bool, str]:
        container = self.get_container(container_name)
        if not container:
            return False, "❌ Container não encontrado."
        try:
            image = container.image.tags[0] if container.image.tags else container.image.id
            host_cfg = container.attrs.get("HostConfig", {}) or {}
            ports = host_cfg.get("PortBindings", {}) or {}

            port_list = []
            for container_port, host_bindings in ports.items():
                if host_bindings:
                    for binding in host_bindings:
                        host_port = binding.get("HostPort")
                        if host_port:
                            port_list.append(f"      - '{host_port}:{container_port.split('/')[0]}'")

            ports_section = ("    ports:\n" + "\n".join(port_list) + "\n") if port_list else ""

            compose_content = f"""version: '3.8'
services:
  {container.name}:
    image: {image}
    container_name: {container.name}
    restart: unless-stopped
{ports_section}"""

            dest_path = os.path.join(dest_dir, f"docker-compose-{container.name}.yml")
            with open(dest_path, "w") as f:
                f.write(compose_content)

            return True, f"✔ docker-compose gerado em:\n{dest_path}"
        except Exception as e:
            return False, f"❌ Erro ao gerar docker-compose: {e}"

    def prune_system(self) -> str:
        if not self.client:
            self._connect()
            if not self.client:
                return "❌ Cliente Docker não conectado."
        try:
            if hasattr(self.client, "containers") and hasattr(self.client.containers, "prune"):
                self.client.containers.prune()
            elif hasattr(self.client, "prune_containers"):
                self.client.prune_containers()
            return "Limpeza do sistema Docker executada com sucesso!"
        except Exception as e:
            return f"Erro ao realizar prune: {e}"

    def remove_image(self, image_id_or_tag: str, force: bool = False) -> tuple[bool, str]:
        if not self.client:
            self._connect()
            if not self.client:
                return False, "❌ Cliente Docker não conectado."
        try:
            if hasattr(self.client, "images") and hasattr(self.client.images, "remove"):
                self.client.images.remove(image=image_id_or_tag, force=force)
            elif hasattr(self.client, "remove_image"):
                self.client.remove_image(image=image_id_or_tag, force=force)
            return True, "✔ Imagem removida com sucesso!"
        except Exception as e:
            return False, f"❌ Erro ao remover imagem: {e}"

    def pull_image(self, image_name: str) -> tuple[bool, str]:
        if not self.client:
            self._connect()
            if not self.client:
                return False, "❌ Cliente Docker não conectado."
        try:
            if hasattr(self.client, "images") and hasattr(self.client.images, "pull"):
                self.client.images.pull(image_name)
            elif hasattr(self.client, "pull"):
                self.client.pull(image_name)
            return True, f"✔ Imagem '{image_name}' baixada com sucesso!"
        except Exception as e:
            return False, f"❌ Erro ao realizar pull: {e}"

    def run_container(self, image_name: str, container_name: str = None, ports_str: str = None,
                      volume_str: str = None) -> tuple[bool, str]:
        """Faz o pull e executa um novo container usando a API universal compatível."""
        if not self.client:
            self._connect()
            if not self.client:
                return False, "❌ Cliente Docker não conectado."
        try:
            # 1. Garante o download da imagem
            try:
                if hasattr(self.client, "images") and hasattr(self.client.images, "pull"):
                    self.client.images.pull(image_name)
                elif hasattr(self.client, "pull"):
                    self.client.pull(image_name)
            except Exception as e:
                return False, f"❌ Erro ao baixar imagem '{image_name}': {e}"

            # 2. Configura portas (Ex: 9090:80)
            port_bindings = {}
            exposed_ports = {}
            if ports_str and ":" in ports_str:
                parts = ports_str.split(":")
                host_p, container_p = parts[0].strip(), parts[1].strip()
                container_key = f"{container_p}/tcp"
                exposed_ports[container_key] = {}
                port_bindings[container_key] = [{"HostPort": host_p}]

            # 3. Configura volumes (Ex: /host/path:/container/path)
            binds = {}
            volumes_list = []
            if volume_str and ":" in volume_str:
                parts = volume_str.split(":")
                host_path, container_path = parts[0].strip(), parts[1].strip()
                if not os.path.exists(host_path):
                    return False, f"❌ Caminho do host não existe: {host_path}"
                binds[host_path] = {'bind': container_path, 'mode': 'rw'}
                volumes_list = [container_path]

            # 4. Tenta usar o high-level containers.run se disponível
            if hasattr(self.client, "containers") and hasattr(self.client.containers, "run"):
                try:
                    kwargs = {"detach": True}
                    if container_name: kwargs["name"] = container_name
                    if port_bindings: kwargs["ports"] = {k: v[0]["HostPort"] for k, v in port_bindings.items()}
                    if binds: kwargs["volumes"] = binds

                    self.client.containers.run(image_name, **kwargs)
                    return True, f"✔ Container executado com sucesso!"
                except Exception:
                    pass  # Se falhar, recorre ao método universal abaixo

            # 5. Método universal de baixo nível (APIClient / Low-level API)
            api_client = getattr(self.client, "api", self.client)

            host_config = api_client.create_host_config(
                port_bindings=port_bindings,
                binds=binds
            )

            container_info = api_client.create_container(
                image=image_name,
                name=container_name if container_name else None,
                ports=list(exposed_ports.keys()) if exposed_ports else None,
                volumes=volumes_list if volumes_list else None,
                host_config=host_config,
                detach=True
            )

            container_id = container_info.get("Id")
            api_client.start(container=container_id)

            return True, f"✔ Container executado com sucesso!"
        except Exception as e:
            return False, f"❌ Erro ao rodar container: {e}"