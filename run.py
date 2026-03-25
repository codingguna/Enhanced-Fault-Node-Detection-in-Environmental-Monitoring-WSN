"""
run.py — One-command launcher for the WSN Fault Detection System.

Usage:
  python run.py train       # Train the ML model (required once)
  python run.py server      # Start the Flask server
  python run.py simulate    # Start the sensor simulator
  python run.py report      # Generate evaluation charts
  python run.py all         # Train + server + simulate (3 terminals auto-launched)
  python run.py status      # Check server health
"""

import sys
import os
import subprocess
import webbrowser
import time
import requests

BASE = os.path.dirname(os.path.abspath(__file__))
PY   = sys.executable


def cmd(args, **kwargs):
    return subprocess.run([PY] + args, cwd=BASE, **kwargs)


def train():
    print("\n▶  Training ML model ...\n")
    cmd(['-m', 'detection_system.ml_trainer'])


def server():
    print("\n▶  Starting Flask server on http://127.0.0.1:5000 ...\n")
    print("   Dashboard → http://127.0.0.1:5000/")
    print("   Press Ctrl+C to stop.\n")
    # Check model exists
    from config import PATHS
    if not os.path.exists(PATHS['model']):
        print("⚠️  ML model not found. Running trainer first ...\n")
        train()
    cmd(['server.py'])


def simulate():
    print("\n▶  Starting sensor simulator ...\n")
    cmd(['sensor_client.py'] + sys.argv[2:])


def report():
    print("\n▶  Generating evaluation report ...\n")
    cmd(['-m', 'evaluation.generate_report'])


def status():
    try:
        r = requests.get('http://127.0.0.1:5000/status', timeout=3)
        d = r.json()
        print("\n  Server Status")
        print("  " + "─"*40)
        for k, v in d.items():
            print(f"  {k:25s}: {v}")
    except Exception:
        print("\n  ❌  Server not reachable at http://127.0.0.1:5000")
        print("     Run: python run.py server")


def launch_all():
    """
    Open three OS terminal windows each running one component.
    Works on Windows, macOS, and Linux.
    """
    import platform
    plat = platform.system()

    train_first = input("\n  Train the ML model first? [Y/n]: ").strip().lower()
    if train_first != 'n':
        train()

    cmds = [
        ('Server',     [PY, 'server.py']),
        ('Simulator',  [PY, 'sensor_client.py']),
    ]

    for name, c in cmds:
        if plat == 'Windows':
            subprocess.Popen(['start', f'WSN {name}', 'cmd', '/k'] + c,
                              shell=True, cwd=BASE)
        elif plat == 'Darwin':
            script = f'tell app "Terminal" to do script "cd {BASE} && {" ".join(c)}"'
            subprocess.Popen(['osascript', '-e', script])
        else:  # Linux / WSL
            for term in ['gnome-terminal', 'xterm', 'konsole', 'xfce4-terminal']:
                try:
                    subprocess.Popen([term, '--', *c], cwd=BASE)
                    break
                except FileNotFoundError:
                    continue
        time.sleep(1.2)

    print("\n  ⏳  Waiting 3 s for server to start ...")
    time.sleep(3)
    webbrowser.open('http://127.0.0.1:5000/')
    print("  🌐  Dashboard opened in browser.")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    cmd_map = {
        'train':    train,
        'server':   server,
        'simulate': simulate,
        'report':   report,
        'status':   status,
        'all':      launch_all,
    }
    fn = cmd_map.get(sys.argv[1])
    if fn:
        fn()
    else:
        print(f"Unknown command: {sys.argv[1]}")
        print(__doc__)
        sys.exit(1)
