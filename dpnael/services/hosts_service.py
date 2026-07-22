import os
import tempfile
import subprocess


class HostsService:
    def __init__(self, hosts_path="/etc/hosts"):
        self.hosts_path = hosts_path
        self.marker_start = "# --- DPNAEL START ---"
        self.marker_end = "# --- DPNAEL END ---"

    def list_domains(self) -> list[tuple[str, str]]:
        """Retorna lista de tuplas (domain, ip) geridos pelo DPNAEL."""
        domains = []
        try:
            if not os.path.exists(self.hosts_path):
                return domains
            with open(self.hosts_path, "r") as f:
                lines = f.readlines()

            inside_block = False
            for line in lines:
                if self.marker_start in line:
                    inside_block = True
                    continue
                if self.marker_end in line:
                    inside_block = False
                    continue
                if inside_block:
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        ip = parts[0]
                        domain = parts[1]
                        domains.append((domain, ip))
        except Exception:
            pass
        return domains

    def _save_hosts_with_sudo(self, new_lines: list[str]) -> tuple[bool, str]:
        """Salva as alterações no /etc/hosts usando um arquivo temporário e sudo."""
        temp_file_path = None
        try:
            # 1. Cria um arquivo temporário com as novas linhas
            with tempfile.NamedTemporaryFile(mode="w", delete=False, encoding="utf-8") as tmp:
                tmp.writelines(new_lines)
                temp_file_path = tmp.name

            # 2. Move o arquivo temporário para /etc/hosts usando sudo
            # O subprocess vai solicitar a senha do sudo no terminal se necessário
            result = subprocess.run(
                ["sudo", "mv", temp_file_path, self.hosts_path],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                return True, "✔ Arquivo /etc/hosts atualizado com sucesso!"
            else:
                error_msg = result.stderr.strip() or "Permissão negada ou senha incorreta."
                return False, f"❌ Erro ao atualizar /etc/hosts: {error_msg}"
        except Exception as e:
            return False, f"❌ Erro interno ao gravar /etc/hosts: {e}"
        finally:
            # Garante a limpeza do arquivo temporário caso tenha sobra
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                except Exception:
                    pass

    def add_domain(self, ip: str, domain: str, container_name: str) -> tuple[bool, str]:
        """Adiciona um domínio ao /etc/hosts dentro do bloco gerenciado."""
        try:
            lines = []
            if os.path.exists(self.hosts_path):
                with open(self.hosts_path, "r") as f:
                    lines = f.readlines()

            has_start = any(self.marker_start in line for line in lines)
            has_end = any(self.marker_end in line for line in lines)

            if not has_start or not has_end:
                lines.append(f"\n{self.marker_start}\n")
                lines.append(f"{self.marker_end}\n")

            new_lines = []
            inside_block = False
            added = False
            entry = f"{ip}\t{domain}\t# container: {container_name}\n"

            for line in lines:
                if self.marker_start in line:
                    inside_block = True
                    new_lines.append(line)
                    continue
                if self.marker_end in line:
                    if not added:
                        new_lines.append(entry)
                        added = True
                    inside_block = False
                    new_lines.append(line)
                    continue

                if inside_block:
                    if domain in line:
                        continue
                    new_lines.append(line)
                else:
                    new_lines.append(line)

            return self._save_hosts_with_sudo(new_lines)
        except Exception as e:
            return False, f"❌ Erro ao processar adição: {e}"

    def remove_domain(self, domain_to_remove: str) -> tuple[bool, str]:
        """Remove um domínio específico do bloco gerenciado no /etc/hosts."""
        try:
            if not os.path.exists(self.hosts_path):
                return False, "Arquivo /etc/hosts não encontrado."

            with open(self.hosts_path, "r") as f:
                lines = f.readlines()

            new_lines = []
            inside_block = False
            removed = False

            for line in lines:
                if self.marker_start in line:
                    inside_block = True
                    new_lines.append(line)
                    continue
                if self.marker_end in line:
                    inside_block = False
                    new_lines.append(line)
                    continue

                if inside_block:
                    parts = line.strip().split()
                    if len(parts) >= 2 and parts[1] == domain_to_remove:
                        removed = True
                        continue  # Pula esta linha para removê-la

                new_lines.append(line)

            if not removed:
                return False, f"❌ Domínio '{domain_to_remove}' não encontrado."

            return self._save_hosts_with_sudo(new_lines)
        except Exception as e:
            return False, f"❌ Erro ao processar remoção: {e}"