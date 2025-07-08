import os
x = 1

while True:
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, f"idiot{x}.txt")

    # Write the file
    with open(file_path, "w") as f:
        f.write("You are an idiot")
    x += 1