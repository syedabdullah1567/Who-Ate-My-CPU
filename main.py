import sys
import os
import signal
import select

from processing import createProcesses, read_system_memory, read_cpu_times

from display import groupedProcesses, display_grouped, display_processes


def get_key():
    if select.select([sys.stdin], [], [], 0)[0]:
        return sys.stdin.read(1)
    return None


def main():

    isGrouped = False
    isSortMem = True

    while True:
        key = get_key()

        if key:
            if key.lower() == "g":
                isGrouped = not isGrouped
            elif key.lower() == "q":
                break
            elif key.lower() == "m":
                isSortMem = True
            elif key.lower() == "c":
                isSortMem = False
            elif key.lower() == "k":
                if isGrouped:
                    procName = input("Enter the name of process to kill: ")
                    processes = createProcesses()
                    for proc in processes:
                        if proc["name"] == procName:
                            os.kill(int(proc["pid"]), signal.SIGTERM)

                else:
                    pid = int(input("Enter pid to terminate: "))
                    try:
                        os.kill(pid, signal.SIGTERM)
                        print(f"Signal SIGTERM sent to process {pid}")
                    except ProcessLookupError:
                        print(f"Process {pid} not found")
                    except Exception as e:
                        print(f"An error occurred: {e}")

        totalCPU = 0

        idle1, total1 = read_cpu_times()

        processes = createProcesses()

        idle2, total2 = read_cpu_times()
        idle_delta = idle2 - idle1
        total_delta = total2 - total1
        if total_delta > 0:
            totalCPU = (1 - idle_delta / total_delta) * 100
        else:
            totalCPU = 0

        if isGrouped:
            processes = groupedProcesses(processes)

        sort_key = ""
        if isSortMem:
            sort_key = "memory"
        else:
            sort_key = "cpu_usage"
        processes.sort(key=lambda x: x[sort_key], reverse=True)

        totalMem, usedMem = read_system_memory()

        os.system("clear")

        print(
            "*                  Who-Ate-My-CPU Resource Manager                    *\n\n"
        )

        print(
            "Commands (Press enter after writing command):\ng → toggle grouped mode\nk → kill process\nq → quit application\nm → sort by memory\nc → sort by cpu\n"
        )

        print("Total memory: " + str(totalMem) + "MB\n")
        print("Used memory: " + str(usedMem) + "MB\n")
        print(f"Total CPU usage: {totalCPU:.2f}%\n\n")

        if isGrouped:
            display_grouped(processes)
        else:
            display_processes(processes)


if __name__ == "__main__":
    main()
