#!/usr/bin/env python3
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from cryptography.fernet import Fernet
import os
import sys

class FileCryptApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Encrypt/Decrypt Files")
        self.resizable(False, False)

        # Set window icon (support PyInstaller)
        base_path = Path(getattr(sys, '_MEIPASS', Path(__file__).parent))
        ico_path = base_path / "encrypt.ico"
        png_path = base_path / "encrypt.png"

        try:
            if ico_path.exists():
                self.iconbitmap(default=str(ico_path))
            elif png_path.exists():
                icon_img = tk.PhotoImage(file=str(png_path))
                self.iconphoto(True, icon_img)
        except Exception:
            pass  # If loading icon fails, continue without crashing

        # --- Center the window ---
        self.update_idletasks()
        width, height = 550, 120
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

        # --- Folder path row ---
        tk.Label(self, text="Folder Path:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.folder_entry = tk.Entry(self, width=50)
        self.folder_entry.grid(row=0, column=1, padx=5, pady=5)
        tk.Button(self, text="Browse…", command=self.browse_folder).grid(row=0, column=2, padx=5, pady=5)

        # --- Key file path row ---
        tk.Label(self, text="Key File:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.key_entry = tk.Entry(self, width=50)
        self.key_entry.grid(row=1, column=1, padx=5, pady=5)
        tk.Button(self, text="Browse…", command=self.browse_key).grid(row=1, column=2, padx=5, pady=5)

        # --- Buttons ---
        btn_frame = tk.Frame(self)
        btn_frame.grid(row=2, column=1, pady=10)
        tk.Button(btn_frame, text="Generate Key", width=12, command=self.generate_key).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Encrypt",      width=12, command=self.encrypt).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Decrypt",      width=12, command=self.decrypt).pack(side="left", padx=5)

    def browse_folder(self):
        d = filedialog.askdirectory()
        if d:
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, d)

    def browse_key(self):
        f = filedialog.askopenfilename(filetypes=[("Key files","*.key;*.*")])
        if f:
            self.key_entry.delete(0, tk.END)
            self.key_entry.insert(0, f)

    def generate_key(self):
        try:
            folder = Path(self.folder_entry.get()).expanduser().resolve()
            if not folder.is_dir():
                raise ValueError(f"Not a directory: {folder}")
            key = Fernet.generate_key()
            key_path = folder / "key.key"
            key_path.write_bytes(key)
            messagebox.showinfo("Key Generated", f"🔑 New key saved to:\n{key_path}")
            self.key_entry.delete(0, tk.END)
            self.key_entry.insert(0, str(key_path))
        except Exception as e:
            messagebox.showerror("Error Generating Key", str(e))

    def load_or_create_key(self, key_path: Path) -> bytes:
        if key_path.exists():
            return key_path.read_bytes()
        else:
            key = Fernet.generate_key()
            key_path.parent.mkdir(parents=True, exist_ok=True)
            key_path.write_bytes(key)
            return key

    def get_all_files(self, base_dir: Path):
        """Recursively get all files, including hidden ones."""
        files = []
        for root, dirs, filenames in os.walk(base_dir):
            for fn in filenames:
                files.append(Path(root) / fn)
        return files

    def encrypt(self):
        try:
            target = Path(self.folder_entry.get()).expanduser().resolve()
            if not target.is_dir():
                raise ValueError(f"Not a directory: {target}")

            key_str = self.key_entry.get().strip()
            key_path = Path(key_str) if key_str else Path(__file__).parent / "key.key"
            key_path = key_path.expanduser().resolve()
            script = Path(__file__).resolve()

            key = self.load_or_create_key(key_path)
            f = Fernet(key)

            done, skipped = 0, []
            for file_path in self.get_all_files(target):
                if file_path in {key_path, script}:
                    continue
                try:
                    data = file_path.read_bytes()
                    token = f.encrypt(data)
                    file_path.write_bytes(token)
                    done += 1
                except Exception as e:
                    skipped.append(f"{file_path}: {e}")

            messagebox.showinfo("Encryption Complete", f"✅ Encrypted {done} files\n⚠ Skipped {len(skipped)} files")
        except Exception as e:
            messagebox.showerror("Encryption Error", str(e))

    def decrypt(self):
        try:
            target = Path(self.folder_entry.get()).expanduser().resolve()
            if not target.is_dir():
                raise ValueError(f"Not a directory: {target}")

            key_path = Path(self.key_entry.get().strip()).expanduser().resolve()
            if not key_path.exists():
                raise FileNotFoundError(f"Key file not found: {key_path}")

            key = key_path.read_bytes()
            f = Fernet(key)

            done, skipped = 0, []
            for file_path in self.get_all_files(target):
                if file_path == key_path:
                    continue
                try:
                    data = file_path.read_bytes()
                    plain = f.decrypt(data)
                    file_path.write_bytes(plain)
                    done += 1
                except Exception as e:
                    skipped.append(f"{file_path}: {e}")

            messagebox.showinfo("Decryption Complete", f"✅ Decrypted {done} files\n⚠ Skipped {len(skipped)} files")
        except Exception as e:
            messagebox.showerror("Decryption Error", str(e))


if __name__ == "__main__":
    app = FileCryptApp()
    app.mainloop()
