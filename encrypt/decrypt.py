#!/usr/bin/env python3
from pathlib import Path
from cryptography.fernet import Fernet

def load_key(key_path: Path) -> bytes:
    if not key_path.exists():
        raise FileNotFoundError(f"Encryption key not found at {key_path}")
    return key_path.read_bytes()

def decrypt_file(path: Path, fernet: Fernet):
    data = path.read_bytes()
    try:
        plaintext = fernet.decrypt(data)
    except Exception as e:
        print(f"⚠ Skipping {path.name}: not valid ciphertext ({e})")
        return
    path.write_bytes(plaintext)
    print(f"✔ Decrypted {path.name}")

def prompt_for_path(prompt: str, default: str = None) -> Path:
    raw = input(prompt).strip()
    if default and raw == "":
        raw = default
    raw = raw.strip().strip('"').strip("'")
    return Path(raw).expanduser()

def main():
    print("=== Fernet Decrypt Interactive ===")

    # Prompt for the target folder
    target = prompt_for_path(
        "📂 Enter the path of the folder to decrypt: "
    )
    if not target.is_dir():
        print(f"❌ \u201c{target}\u201d is not a directory.")
        return

    # Prompt for the key file path (default to ./key.key)
    key_path = prompt_for_path(
        "🔑 Enter the path to your key file [default: ./key.key]: ",
        default="key.key"
    )
    try:
        key = load_key(key_path)
    except FileNotFoundError as e:
        print(f"❌ {e}")
        return

    f = Fernet(key)
    # Decrypt each file in the target directory
    for item in target.iterdir():
        if item.is_file() and item != key_path:
            decrypt_file(item, f)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Unhandled error: {e}")
    finally:
        input("\nPress Enter to exit...")
