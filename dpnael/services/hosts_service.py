import sys
import subprocess


class HostsService:
    HOSTS_FILE = "/etc/hosts"

    @staticmethod
    def add_domain(ip: str, domain: str, container_name: str) -> tuple[bool, str]:
        line = f"{ip}\t{domain}\t# dpnael:{container_name}\n"
        try:
            HostsService.remove_domain(domain)

            cmd = f'echo "{line.strip()}" | sudo tee -a {HostsService.HOSTS_FILE}'
            subprocess.run(cmd, shell=True, check=True, stdout=subprocess.DEVNULL)
            return True, "Domínio mapeado com sucesso!"
        except Exception as e:
            return False, f"Erro ao editar /etc/hosts: {e}"

    @staticmethod
    def list_domains() -> list[tuple[str, str]]:
        domains = []
        try:
            with open(HostsService.HOSTS_FILE, "r") as f:
                for line in f:
                    if "# dpnael:" in line:
                        parts = line.strip().split()
                        if len(parts) >= 2:
                            ip, domain = parts[0], parts[1]
                            domains.append((domain, ip))
        except Exception:
            pass
        return domains

    @staticmethod
    def remove_domain(domain: str) -> tuple[bool, str]:
        try:
            if sys.platform == "darwin":
                cmd = f"sudo sed -i '' '/[[:space:]]{domain}\t# dpnael:/d' {HostsService.HOSTS_FILE}"
            else:
                cmd = f"sudo sed -i '/[[:space:]]{domain}\t# dpnael:/d' {HostsService.HOSTS_FILE}"
            subprocess.run(cmd, shell=True, check=True)
            return True, "Domínio removido!"
        except Exception as e:
            return False, f"Erro ao remover domínio: {e}"