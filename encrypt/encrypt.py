#!/usr/bin/env python3
from pathlib import Path
from cryptography.fernet import Fernet

KEY_FILE = "key.key"

def load_key(key_path: Path) -> bytes:
    """
    Load a Fernet key from key_path, generating & saving a new one if it doesn’t exist.
    """
    if key_path.exists():
        print(f"🔑 Loading key from {key_path}")
        return key_path.read_bytes()
    else:
        key = Fernet.generate_key()
        key_path.write_bytes(key)
        print(f"🔑 Generated & saved new key to {key_path}")
        return key

def encrypt_file(path: Path, fernet: Fernet):
    """
    Encrypts the contents of path in-place using fernet.
    """
    data = path.read_bytes()
    encrypted = fernet.encrypt(data)
    # Fernet ciphertexts always start with "gAAAA"
    if not encrypted.startswith(b"gAAAA"):
        raise ValueError("Unexpected ciphertext format")
    path.write_bytes(encrypted)
    print(f"✔ Encrypted: {path.name}")

def prompt_for_path(prompt: str, default: str = None) -> Path:
    """
    Prompt the user for a filesystem path, strip quotes, expand ~, and apply a default.
    """
    raw = input(prompt).strip()
    if default and raw == "":
        raw = default
    # remove surrounding quotes if present
    raw = raw.strip().strip('"').strip("'")
    return Path(raw).expanduser()

def main():
    print("=== Fernet Encrypt Interactive ===")

    # 1) Prompt for the folder to encrypt
    target = prompt_for_path("📂 Enter the path of the folder to encrypt: ")
    if not target.is_dir():
        print(f"❌ “{target}” is not a directory.")
        return

    # 2) Prompt for the key file path (default to ./key.key)
    key_path = prompt_for_path(
        f"🔑 Enter the path to your key file [default: ./{KEY_FILE}]: ",
        default=KEY_FILE
    )
    try:
        key = load_key(key_path)
    except Exception as e:
        print(f"❌ {e}")
        return

    f = Fernet(key)
    script_path = Path(__file__).resolve()

    # 3) Encrypt each file in the chosen folder
    for item in target.iterdir():
        # skip non-files, the key file itself, and this script
        if not item.is_file() or item == key_path or item == script_path:
            continue
        try:
            encrypt_file(item, f)
        except Exception as e:
            print(f"⚠ Error encrypting {item.name}: {e}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Unhandled error: {e}")
    finally:
        input("\nPress Enter to exit...")
