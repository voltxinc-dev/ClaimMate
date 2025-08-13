import subprocess
import webbrowser
import time
import socket
import tkinter as tk
from tkinter import messagebox
import sys

def is_flask_running(host='127.0.0.1', port=5000):
    """Check if Flask is running on the given port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((host, port)) == 0

def start_flask_server():
    # This runs only if called with --flask argument
    from app import create_app
    app = create_app()
    app.run(debug=False, use_reloader=False)

def start_flask_and_open_browser():
    try:
        # Start Flask in background with --flask argument
        subprocess.Popen(
            [sys.executable, __file__, "--flask"],
            shell=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        # Wait for Flask server to start
        for _ in range(20):
            time.sleep(0.5)
            if is_flask_running():
                webbrowser.open("http://127.0.0.1:5000")
                return
        messagebox.showerror("Timeout", "Flask app did not start in time.")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def main():
    window = tk.Tk()
    window.title("Car Parts Web App Launcher")
    window.geometry("320x180")
    window.configure(bg="#282c34")

    title = tk.Label(window, text="🚗 Car Parts App", font=("Segoe UI", 16), fg="white", bg="#282c34")
    title.pack(pady=(30, 10))

    start_btn = tk.Button(
        window,
        text="Start Web App",
        font=("Segoe UI", 12),
        width=20,
        bg="#61afef",
        fg="white",
        relief="flat",
        command=start_flask_and_open_browser
    )
    start_btn.pack(pady=10)

    window.mainloop()

if __name__ == "__main__":
    # Distinguish between GUI and Flask subprocess
    if "--flask" in sys.argv:
        start_flask_server()
    else:
        main()
