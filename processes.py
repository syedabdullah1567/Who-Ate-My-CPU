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


processes = []
total_ticks1 = read_total_cpu_ticks()

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

processes.sort(key=lambda x: x["memory"], reverse=True)

with open("processes.txt", "w") as procFile:
    procFile.write(
        "*                  Who-Ate-My-CPU Resource Manager                    *\n\n"
    )
    for proc in processes:
        procFile.write(f"Process {proc['pid']}:\n\n")
        procFile.write(f"Name: {proc['name']}\n")
        procFile.write(f"State: {proc['state']}\n")
        procFile.write(f"Memory (MB): {proc['memory']:.2f}\n")
        procFile.write(f"CPU Usage (%): {proc['cpu_usage']:.2f}\n\n")

print(f"File created in path {Path.cwd().name}")


# for proc in processes:
#   print(f"\nProcess {proc['pid']}:")
#   print(f"Name: {proc['name']}")
#   print(f"State: {proc['state']}")
#   print(f"Memory (kB): {proc['memory']}")
