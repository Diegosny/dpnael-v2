# 🐳 DPNAEL - Docker Management TUI

**DPNAEL** é uma interface de terminal (TUI) fluida e poderosa para gerenciamento de ambientes Docker, construída com [Textual](https://textual.textualize.io/) e Python. Focado na produtividade de desenvolvedores e profissionais de DevOps, o DPNAEL traz as operações mais complexas do Docker para atalhos rápidos direto do seu teclado.

---

## ✨ Funcionalidades

- **📦 Gestão Ágil de Containers:** Inicie, pare, pause, reinicie e delete containers com facilidade.
- **🖼️ Gestão de Imagens:** Liste, faça pull, backup (exportação `.tar`) e delete imagens locais.
- **🐚 Acesso e Logs:** Abra um shell interativo (`bash` ou `sh`) ou visualize logs em tempo real diretamente do painel.
- **🐘 Integração Laravel Tinker:** Execute códigos PHP/Tinker diretamente dentro do container selecionado (perfeito para devs Laravel).
- **🩻 Raio-X de Imagens (Dive):** Inspecione as camadas das imagens Docker de forma aprofundada utilizando o `dive`.
- **🕸️ Network Sniffer (Netshoot):** Inicie uma captura de tráfego (`tcpdump`) instantânea na rede do container.
- **🧬 Engenharia Reversa para Compose:** Gere automaticamente um arquivo `docker-compose.yml` a partir de um container em execução.
- **🔗 Mapeamento Automático de Hosts:** Adicione domínios locais ao seu `/etc/hosts` apontando diretamente para o IP interno do container na bridge network.
- **🧹 Manutenção Rápida:** Execute `docker system prune` facilmente para manter seu ambiente limpo.

## 🚀 Como Executar

Certifique-se de ter o Docker rodando em sua máquina e o gerenciador de pacotes [uv](https://docs.astral.sh/uv/) instalado.

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/dpnael.git
cd dpnael

# Execute a aplicação usando o uv
uv run python -m dpnael.main
```

> **Aviso:** Funcionalidades que alteram arquivos do sistema, como o mapeamento de rede no `/etc/hosts`, exigirão permissões de administrador (root/sudo) ao executar a aplicação.

## ⌨️ Atalhos de Teclado

| Tecla | Ação | Descrição |
| :--- | :--- | :--- |
| `[ Espaço ]` | Start/Stop | Inicia ou para o container selecionado |
| `[ Shift+R ]`| Restart | Reinicia o container |
| `[ p ]` | Pause/Unpause | Pausa ou retoma o container |
| `[ s ]` | Shell | Abre terminal interativo no container |
| `[ l ]` | Logs | Visualiza logs em tempo real (Ctrl+C para sair) |
| `[ t ]` | Tinker | Executa comandos do Laravel Tinker no container |
| `[ i ]` | Pull | Baixa uma nova imagem |
| `[ x ]` | Dive (Raio-X) | Analisa a imagem usando `wagoodman/dive` |
| `[ n ]` | Sniffer | Inicia tcpdump na rede com `nicolaka/netshoot` |
| `[ b ]` | Backup | Exporta a imagem selecionada para `.tar` |
| `[ c ]` | Compose | Gera um `docker-compose.yml` baseado no container |
| `[ h ]` | Hosts | Mapeia um domínio local apontando para o IP do container |
| `[ P ]` | Prune | Limpa o sistema Docker (containers, networks não usadas, etc) |
| `[ Delete ]` | Remover | Deleta container (force) ou imagem |
| `[ r ]` | Atualizar | Recarrega os dados do Docker |
| `[ q ]` | Sair | Encerra o DPNAEL |

## 🛠️ Tecnologias Utilizadas

- **Python 3+**
- **[Textual](https://textual.textualize.io/)**: Framework de interface de terminal assíncrono.
- **[Docker SDK for Python](https://docker-py.readthedocs.io/)**: Comunicação com a API nativa do Docker.

## 📄 Licença

## Instalar sem clonar

- Rode ``` curl -sSL https://raw.githubusercontent.com/Diegosny/dpnael-v2/refs/heads/master/install.sh  | bash ```

Este projeto está sob a licença MIT. Sinta-se livre para modificar e contribuir!
