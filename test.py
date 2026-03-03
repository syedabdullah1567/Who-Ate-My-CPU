from pathlib import Path
import os
import time

for entry in Path("/proc").iterdir():
    if entry.is_dir():
        if entry.name.isdigit():
            filePath = "/proc/" + entry.name + "/status"
            file_path = Path(filePath)
            content = file_path.read_text().splitlines()
            print(f"\nProcess {entry.name}:\n")
            for line in content:
                if line.startswith("Name"):
                    print(line.strip())
                if line.startswith("State"):
                    print(line.strip())
                if line.startswith("Pid"):
                    print(line.strip())
                    break
