from pathlib import Path


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
