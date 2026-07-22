import os
import time


def make_bar(percent: float, length: int = 20) -> str:
    filled = int(round((percent / 100.0) * length))
    filled = max(0, min(length, filled))
    bar = "█" * filled + "░" * (length - filled)
    return f"[{bar}] {percent:5.1f}%"


def render_dashboard(summary: dict, telemetry_data: list[dict]):
    os.system("cls" if os.name == "nt" else "clear")

    print("=" * 70)
    print(" 📊 DPNAEL - TELEMETRIA E MÉTRICAS EM TEMPO REAL")
    print("=" * 70)
    print(f" Status dos Containers: Total: {summary['total_containers']} | "
          f"🟢 Rodando: {summary['running']} | "
          f"🔴 Parados: {summary['stopped']} | "
          f"🟡 Pausados: {summary['paused']}")
    print("-" * 70)

    if not telemetry_data:
        print(" NENHUM CONTAINER EM EXECUÇÃO NO MOMENTO.")
        print("=" * 70)
        return

    print(f"{'CONTAINER':<18} | {'USO DE CPU':<28} | {'MEMÓRIA (MB / %)':<25}")
    print("-" * 70)

    for item in telemetry_data:
        name = item["name"][:16]
        cpu_bar = make_bar(item["cpu_percent"], length=15)
        mem = item["memory"]
        mem_str = f"{mem['usage_mb']}MB / {mem['limit_mb']}MB ({mem['percent']}%)"

        print(f"{name:<18} | {cpu_bar:<28} | {mem_str:<25}")
        print(f" └─ Rede: Rx: {item['network']['rx_mb']} MB / Tx: {item['network']['tx_mb']} MB")
        print("-" * 70)

    print("\nPressione Ctrl+C para sair do Dashboard.")