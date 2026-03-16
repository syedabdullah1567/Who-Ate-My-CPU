import sys
import os
import select
from pathlib import Path
import time


def read_total_cpu_ticks():
    with open("/proc/stat") as f:
        line = f.readline()
        return sum(int(x) for x in line.split()[1:])


def read_proc_ticks(pid):
    try:
        content = Path(f"/proc/{pid}/stat").read_text().split()
        utime = int(content[13])
        stime = int(content[14])
        return utime + stime
    except (FileNotFoundError, IndexError, ValueError):
        return 0


def read_proc_status(pid):
    try:
        content = Path(f"/proc/{pid}/status").read_text().splitlines()
        name = state = ""
        memory = 0
        for line in content:
            if line.startswith("Name:"):
                name = line.split()[1]
            elif line.startswith("State:"):
                state = line.split()[1]
            elif line.startswith("VmRSS:"):
                memory = int(line.split()[1]) / 1024
        return name, state, memory
    except (FileNotFoundError, PermissionError):
        return "", "", 0


def read_system_memory():
    meminfo = {}

    with open("/proc/meminfo") as f:
        for line in f:
            key, value = line.split(":")
            meminfo[key] = int(value.split()[0])

    total = meminfo["MemTotal"] // 1024
    available = meminfo["MemAvailable"] // 1024

    used = total - available

    return total, used


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


def get_input_nowait():

    if select.select([sys.stdin], [], [], 0)[0]:
        return sys.stdin.readline().strip()
    return None


def main():

    isGrouped = False

    while True:
        user_input = get_input_nowait()
        if user_input:
            if user_input == "g" or user_input == "G":
                isGrouped = not isGrouped
        processes = []
        total_ticks1 = read_total_cpu_ticks()

        totalCPU = 0

        for entry in Path("/proc").iterdir():
            if entry.is_dir() and entry.name.isdigit():
                pid = entry.name
                name, state, memory = read_proc_status(pid)
                proc_ticks1 = read_proc_ticks(pid)
                processes.append(
                    {
                        "pid": pid,
                        "name": name,
                        "state": state,
                        "memory": memory,
                        "proc_ticks1": proc_ticks1,
                    }
                )

        time.sleep(1)

        total_ticks2 = read_total_cpu_ticks()

        for proc in processes:
            proc_ticks2 = read_proc_ticks(proc["pid"])
            proc_delta = proc_ticks2 - proc["proc_ticks1"]
            total_delta = total_ticks2 - total_ticks1
            proc["cpu_usage"] = (proc_delta / total_delta) * 100
            totalCPU += proc["cpu_usage"]

        if isGrouped:
            processes = groupedProcesses(processes)

        processes.sort(key=lambda x: x["memory"], reverse=True)

        totalMem, usedMem = read_system_memory()

        os.system("clear")

        print(
            "*                  Who-Ate-My-CPU Resource Manager                    *\n\n"
        )
        print("Total memory: " + str(totalMem) + "MB\n")
        print("Used memory: " + str(usedMem) + "MB\n")
        print("Total CPU usage: " + str(int(totalCPU)) + "\n\n")

        print("PID\tNAME               \tMEMORY\tCPU")
        print("-------------------------------------------")

        for proc in processes[:20]:
            print(
                f"{proc['pid']}\t{proc['name']}               \t{proc['memory']:.2f}\t{proc['cpu_usage']:.2f}"
            )

        time.sleep(1)


if __name__ == "__main__":
    main()
