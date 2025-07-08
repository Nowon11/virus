import time
import random

total_steps = 20
items = [
    "winlibraries823",
    "coreutils512",
    "netframework456",
    "pythonlibs777",
    "datascience999",
    "winRAR",
    "Tr0gan2424",
    "logger.exe",
    "3ryptohax"
]

for item in items:
    for i in range(total_steps + 1):
        hashes = '#' * i
        dashes = '-' * (total_steps - i)
        bar = f"Installing {item} [{hashes}{dashes}]"
        
        # Pad the string to clear leftovers if item names differ in length
        print(bar.ljust(50), end='\r')
        
        time.sleep(random.uniform(0.05, 0.25))
    print()  # Move to next line after each item's bar finishes
print("Download Successful")
time.sleep(3)