import json


class TelemetryService:
    def __init__(self, docker_service=None, docker_client=None):
        self.docker_service = docker_service
        self.client = docker_client or (docker_service.client if docker_service else None)

    def _calculate_cpu_percent(self, stats: dict) -> float:
        try:
            cpu_stats = stats.get("cpu_stats", {})
            precpu_stats = stats.get("precpu_stats", {})

            cpu_usage = cpu_stats.get("cpu_usage", {}).get("total_usage", 0)
            precpu_usage = precpu_stats.get("cpu_usage", {}).get("total_usage", 0)
            cpu_delta = cpu_usage - precpu_usage

            system_cpu_usage = cpu_stats.get("system_cpu_usage", 0)
            system_precpu_usage = precpu_stats.get("system_precpu_usage", 0)
            system_delta = system_cpu_usage - system_precpu_usage

            online_cpus = cpu_stats.get(
                "online_cpus",
                len(cpu_stats.get("cpu_usage", {}).get("percpu_usage", [1]))
            )

            if system_delta > 0.0 and cpu_delta > 0.0:
                return round((cpu_delta / system_delta) * online_cpus * 100.0, 2)
        except Exception:
            pass
        return 0.0

    def _calculate_memory_info(self, stats: dict) -> dict:
        try:
            mem_stats = stats.get("memory_stats", {})
            usage = mem_stats.get("usage", 0)

            stats_detail = mem_stats.get("stats", {})
            cache = stats_detail.get("inactive_file", stats_detail.get("cache", 0))

            real_usage = max(0, usage - cache)
            limit = mem_stats.get("limit", 1)

            usage_mb = round(real_usage / (1024 * 1024), 2)
            limit_mb = round(limit / (1024 * 1024), 2)
            percent = round((real_usage / limit) * 100.0, 2) if limit > 0 else 0.0

            return {
                "usage_mb": usage_mb,
                "limit_mb": limit_mb,
                "percent": percent
            }
        except Exception:
            return {"usage_mb": 0.0, "limit_mb": 0.0, "percent": 0.0}

    def _calculate_network_io(self, stats: dict) -> dict:
        rx_bytes = 0
        tx_bytes = 0
        try:
            networks = stats.get("networks", {})
            if isinstance(networks, dict):
                for net_info in networks.values():
                    rx_bytes += net_info.get("rx_bytes", 0)
                    tx_bytes += net_info.get("tx_bytes", 0)
        except Exception:
            pass
        return {
            "rx_mb": round(rx_bytes / (1024 * 1024), 2),
            "tx_mb": round(tx_bytes / (1024 * 1024), 2)
        }

    def get_container_telemetry(self, container) -> dict | None:
        try:
            if not container:
                return None

            status = getattr(container, "status", "unknown")
            name = getattr(container, "name", "N/A")
            short_id = getattr(container, "short_id", "N/A")

            if status != "running":
                return {
                    "id": short_id,
                    "name": name,
                    "status": status,
                    "cpu_percent": 0.0,
                    "memory": {"usage_mb": 0.0, "limit_mb": 0.0, "percent": 0.0},
                    "network": {"rx_mb": 0.0, "tx_mb": 0.0}
                }

            raw_stats = None
            if hasattr(container, "stats") and callable(container.stats):
                raw_stats = container.stats(stream=False)

            if raw_stats is None:
                return None

            if isinstance(raw_stats, (str, bytes)):
                stats = json.loads(raw_stats)
            elif isinstance(raw_stats, dict):
                stats = raw_stats
            else:
                stats = {}

            return {
                "id": short_id,
                "name": name,
                "status": status,
                "cpu_percent": self._calculate_cpu_percent(stats),
                "memory": self._calculate_memory_info(stats),
                "network": self._calculate_network_io(stats)
            }
        except Exception:
            return None

    def get_all_containers_telemetry(self) -> list[dict]:
        results = []
        try:
            if self.docker_service:
                containers = self.docker_service.list_containers(show_all=True)
            else:
                return results

            for c in containers:
                telemetry = self.get_container_telemetry(c)
                if telemetry:
                    results.append(telemetry)
        except Exception:
            pass
        return results