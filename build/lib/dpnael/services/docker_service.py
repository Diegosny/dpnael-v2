import docker
from typing import List
from dpnael.models.container import ContainerInfo  # Ajuste conforme seu model


class DockerService:
    def __init__(self):
        try:
            self.client = docker.from_env()
        except Exception:
            self.client = None

    def list_containers(self, show_all: bool = True) -> List[ContainerInfo]:
        if not self.client:
            return []

        try:
            raw_containers = self.client.containers.list(all=show_all)
            containers = []

            for c in raw_containers:
                # Sua lógica de mapeamento para o model aqui...
                pass

            return containers
        except Exception as e:
            # Em vez de quebrar a aplicação, retorna uma lista vazia
            print(f"Erro ao conectar com o Docker: {e}")
            return []