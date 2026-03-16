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
    print("PID\tNAME\t\t\tMEMORY\tCPU")
    print("--------------------------------------------------")

    for proc in processes[:20]:
        print(
            f"{proc['pid']:<7}{proc['name']:<20}{proc['memory']:<10.2f}{proc['cpu_usage']:.2f}"
        )


def display_grouped(processes):
    print("NAME\t\t\tINSTANCES\tMEMORY\tCPU")
    print("--------------------------------------------------")

    for proc in processes[:20]:
        print(
            f"{proc['name']:<20}{proc['count']:<10}{proc['memory']:<10.2f}{proc['cpu_usage']:.2f}"
        )
