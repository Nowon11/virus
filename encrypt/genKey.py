#!/usr/bin/env python3
import sys
from pathlib import Path
from cryptography.fernet import Fernet

def main():
    # Ensure we write next to this script
    script_dir = Path(__file__).parent.resolve()
    key_file = script_dir / "key.key"

    # Generate & save
    key = Fernet.generate_key()
    key_file.write_bytes(key)
    print(f"🔑 New key generated and saved to:\n  {key_file}")

    # Pause so the window doesn’t instantly close
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        input("\nPress Enter to exit...")
        sys.exit(1)
