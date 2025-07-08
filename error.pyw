import ctypes

def show_error(message, title="Error"):
    ctypes.windll.user32.MessageBoxW(0, message, title, 0x10)

while True:
    try:
        raise ValueError("LOL")
    except ValueError as e:
        show_error(f"Ur dumb.\n\n{e}")
