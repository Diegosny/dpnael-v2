from textual.widgets import OptionList
from textual.widgets.option_list import Option
from typing import List
from dpnael.models.container import ContainerInfo
from dpnael.config import ICON_CONTAINER

class ContainerListWidget(OptionList):
    def update_containers(self, containers: List[ContainerInfo]):
        self.clear_options()
        for c in containers:
            label = f"{ICON_CONTAINER}  {c.name}  [{c.status}]"
            # Atribui o ID do container à opção para resgate rápido
            self.add_option(Option(label, id=c.id))