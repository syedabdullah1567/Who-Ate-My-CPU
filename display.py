import sys
import select


def groupedProcesses(processes):
    aggregated = {}

    for proc in processes:
        name = proc["name"]

        if name not in aggregated:
            aggregated[name] = {
                "name": name,
                "memory": proc["memory"],
                "cpu_usage": proc["cpu_usage"],
                "count": 1,
            }
        else:
            aggregated[name]["memory"] += proc["memory"]
            aggregated[name]["cpu_usage"] += proc["cpu_usage"]
            aggregated[name]["count"] += 1

    return list(aggregated.values())


def get_key():
    if select.select([sys.stdin], [], [], 0)[0]:
        return sys.stdin.read(1)
    return None


def display_processes(processes):

    print(f"{'PID':<8}{'NAME':<35}{'MEMORY(MB)':<15}{'CPU(%)':<10}")
    print("-" * 70)

    for proc in processes[:20]:
        name_display = proc["name"][:33]  # truncate if name is too long
        print(
            f"{proc['pid']:<8}{name_display:<35}{proc['memory']:<15.2f}{proc['cpu_usage']:<10.2f}"
        )


def display_grouped(processes):

    print(f"{'NAME':<35}{'INSTANCES':<12}{'MEMORY(MB)':<15}{'CPU(%)':<10}")
    print("-" * 75)

    for proc in processes[:20]:
        name_display = proc["name"][:33]  # truncate if name is too long
        print(
            f"{name_display:<35}{proc['count']:<12}{proc['memory']:<15.2f}{proc['cpu_usage']:<10.2f}"
        )
