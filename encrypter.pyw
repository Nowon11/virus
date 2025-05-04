#!/usr/bin/env python3
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
import tkinter as tk
from tkinter import ttk, simpledialog, filedialog, messagebox
from pathlib import Path
from cryptography.fernet import Fernet
import sys
import os
import requests

LISTEN_PORT = 5000

class RemoteRequestHandler(BaseHTTPRequestHandler):
    def _handle(self, action):
        length = int(self.headers.get('Content-Length', 0))
        data = self.rfile.read(length).decode()
        params = urllib.parse.parse_qs(data)
        folder = params.get('folder', [''])[0]
        key    = params.get('key',    [''])[0]
        # Execute locally without popping up GUI
        try:
            app = self.server.app_ref
            if action == 'encrypt':
                done, skipped = app._encrypt_local(Path(folder), Path(key) if key else None)
                resp = f"Encrypted {done}, skipped {len(skipped)}"
            else:
                done, skipped = app._decrypt_local(Path(folder), Path(key))
                resp = f"Decrypted {done}, skipped {len(skipped)}"
            self.send_response(200)
            self.end_headers()
            self.wfile.write(resp.encode())
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode())

    def do_POST(self):
        if self.path == '/encrypt':
            self._handle('encrypt')
        elif self.path == '/decrypt':
            self._handle('decrypt')
        else:
            self.send_response(404)
            self.end_headers()

class FileCryptApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Encrypt/Decrypt Files (with Remote Control)")
        self.resizable(False, False)
        self._setup_icon()
        self._setup_gui()
        # start HTTP server in background
        self._start_server()

    def _setup_icon(self):
        base = Path(getattr(sys, '_MEIPASS', Path(__file__).parent))
        ico = base / "encrypt.ico"
        png = base / "encrypt.png"
        try:
            if ico.exists():
                self.iconbitmap(str(ico))
            elif png.exists():
                img = tk.PhotoImage(file=str(png))
                self.iconphoto(True, img)
        except:
            pass

    def _setup_gui(self):
        pad = dict(padx=5, pady=5)
        # Device selector
        tk.Label(self, text="Device:").grid(row=0, column=0, **pad, sticky="e")
        self.device_var = tk.StringVar(value="local")
        self.device_cb = ttk.Combobox(self, textvariable=self.device_var, width=30,
                                      values=["local"], state="readonly")
        self.device_cb.grid(row=0, column=1, **pad)
        ttk.Button(self, text="Add Device…", command=self._add_device).grid(row=0, column=2, **pad)
        # Folder
        tk.Label(self, text="Folder Path:").grid(row=1, column=0, **pad, sticky="e")
        self.folder_entry = tk.Entry(self, width=50)
        self.folder_entry.grid(row=1, column=1, **pad)
        tk.Button(self, text="Browse…", command=self._browse_folder).grid(row=1, column=2, **pad)
        # Key
        tk.Label(self, text="Key File:").grid(row=2, column=0, **pad, sticky="e")
        self.key_entry = tk.Entry(self, width=50)
        self.key_entry.grid(row=2, column=1, **pad)
        tk.Button(self, text="Browse…", command=self._browse_key).grid(row=2, column=2, **pad)
        # Buttons
        btnf = tk.Frame(self)
        btnf.grid(row=3, column=1, pady=10)
        tk.Button(btnf, text="Generate Key", width=12, command=self._generate_key).pack(side="left", padx=5)
        tk.Button(btnf, text="Encrypt",      width=12, command=lambda: self._run_action('encrypt')).pack(side="left", padx=5)
        tk.Button(btnf, text="Decrypt",      width=12, command=lambda: self._run_action('decrypt')).pack(side="left", padx=5)

    def _add_device(self):
        addr = simpledialog.askstring("Add Device", "Enter address (ip:port):", parent=self)
        if addr:
            vals = list(self.device_cb['values'])
            if addr not in vals:
                vals.append(addr)
                self.device_cb['values'] = vals
                self.device_var.set(addr)

    def _browse_folder(self):
        d = filedialog.askdirectory()
        if d: self.folder_entry.delete(0,tk.END); self.folder_entry.insert(0,d)

    def _browse_key(self):
        f = filedialog.askopenfilename(filetypes=[("Key","*.key;*.*")])
        if f: self.key_entry.delete(0,tk.END); self.key_entry.insert(0,f)

    def _generate_key(self):
        folder = Path(self.folder_entry.get()).expanduser().resolve()
        if not folder.is_dir():
            return messagebox.showerror("Error","Please select a valid folder first.")
        key = Fernet.generate_key()
        kp = folder / "key.key"
        kp.write_bytes(key)
        messagebox.showinfo("Key Generated", f"🔑 Saved to:\n{kp}")
        self.key_entry.delete(0,tk.END)
        self.key_entry.insert(0,str(kp))

    def _run_action(self, action):
        device = self.device_var.get()
        folder = self.folder_entry.get().strip()
        key    = self.key_entry.get().strip()
        if not folder:
            return messagebox.showerror("Error","Select a folder first.")
        if device == "local":
            # local
            if action == 'encrypt':
                done, skipped = self._encrypt_local(Path(folder), Path(key) if key else None)
                messagebox.showinfo("Encryption Complete", f"✅ Encrypted {done} files\n⚠ Skipped {len(skipped)}")
            else:
                done, skipped = self._decrypt_local(Path(folder), Path(key))
                messagebox.showinfo("Decryption Complete", f"✅ Decrypted {done} files\n⚠ Skipped {len(skipped)}")
        else:
            # remote
            url = f"http://{device}/{action}"
            try:
                resp = requests.post(url, data={'folder': folder, 'key': key})
                resp.raise_for_status()
                messagebox.showinfo(action.title()+" Remote", resp.text)
            except Exception as e:
                messagebox.showerror("Remote Error", str(e))

    def load_or_create_key(self, key_path: Path) -> bytes:
        if key_path and key_path.exists():
            return key_path.read_bytes()
        key = Fernet.generate_key()
        key_path.parent.mkdir(exist_ok=True, parents=True)
        key_path.write_bytes(key)
        return key

    def get_all_files(self, base_dir: Path):
        return [p for p in base_dir.rglob("*") if p.is_file()]

    def _encrypt_local(self, target: Path, key_path: Path):
        if not target.is_dir():
            raise ValueError(f"Not a directory: {target}")
        if key_path is None:
            key_path = Path(__file__).parent / "key.key"
        key = self.load_or_create_key(key_path)
        f = Fernet(key)
        done, skipped = 0, []
        me = Path(__file__).resolve()
        for p in self.get_all_files(target):
            if p in {key_path, me}: continue
            try:
                data = p.read_bytes()
                p.write_bytes(f.encrypt(data))
                done += 1
            except Exception as e:
                skipped.append(f"{p}: {e}")
        return done, skipped

    def _decrypt_local(self, target: Path, key_path: Path):
        if not target.is_dir():
            raise ValueError(f"Not a directory: {target}")
        if not key_path or not key_path.exists():
            raise FileNotFoundError(f"Key not found: {key_path}")
        key = key_path.read_bytes()
        f = Fernet(key)
        done, skipped = 0, []
        for p in self.get_all_files(target):
            if p == key_path: continue
            try:
                data = p.read_bytes()
                p.write_bytes(f.decrypt(data))
                done += 1
            except Exception as e:
                skipped.append(f"{p}: {e}")
        return done, skipped

    def _start_server(self):
        server = HTTPServer(('', LISTEN_PORT), RemoteRequestHandler)
        server.app_ref = self
        t = threading.Thread(target=server.serve_forever, daemon=True)
        t.start()

if __name__ == "__main__":
    # suppress HTTP logs in console
    import logging
    logging.getLogger('urllib3').setLevel(logging.CRITICAL)
    app = FileCryptApp()
    app.mainloop()
