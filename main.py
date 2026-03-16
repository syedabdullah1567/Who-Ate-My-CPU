import sys
import os
import select
from pathlib import Path
import time

from processing import (
    read_total_cpu_ticks,
    read_proc_ticks,
    read_proc_status,
    read_system_memory,
)
from display import groupedProcesses, display_grouped, display_processes


def get_key():
    if select.select([sys.stdin], [], [], 0)[0]:
        return sys.stdin.read(1)
    return None


def main():

    isGrouped = False

    while True:
        key = get_key()

        if key:
            if key.lower() == "g":
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

        if isGrouped:
            display_grouped(processes)
        else:
            display_processes(processes)


if __name__ == "__main__":
    main()
