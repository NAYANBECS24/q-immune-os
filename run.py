"""Main entrypoint runner for Q-IMMUNE QDS.

Usage:
    python run.py                  # Launches the Streamlit Cyber-Quantum Command Center
    python run.py --test           # Runs the complete unit and integration test suite
    python run.py --smoke          # Runs the quick smoke test verification (< 1 sec)
    python run.py --seed           # Seeds the database with clean and adversarial transactions
    python run.py --reproduce      # Runs the 100% deterministic offline reproducibility benchmark
    python run.py --port 8501      # Custom server port
"""

import sys
import os
import argparse
import subprocess
import time

# Ensure workspace root is in sys.path
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)


def print_banner():
    banner = """
================================================================================
                ⚛️  Q-IMMUNE QDS // CYBER-QUANTUM SECURITY OS  ⚛️
    Information-Theoretic Threat Detection for Quantum Digital Signatures
        SIH 2026 | Problem Statement 26141 | Theme: Blockchain & Cybersecurity
================================================================================
"""
    print(banner)


def run_tests():
    print("[*] Running Complete Unit & Integration Test Suite...")
    cmd = [sys.executable, "-m", "unittest", "discover", "tests"]
    result = subprocess.run(cmd, cwd=ROOT_DIR)
    sys.exit(result.returncode)


def run_smoke():
    print("[*] Running Fast Smoke Test Pipeline...")
    smoke_script = os.path.join(ROOT_DIR, "scripts", "smoke_test.py")
    result = subprocess.run([sys.executable, smoke_script], cwd=ROOT_DIR)
    sys.exit(result.returncode)


def run_seed():
    print("[*] Seeding Database with Demonstration Scenarios...")
    seed_script = os.path.join(ROOT_DIR, "scripts", "seed_demo.py")
    result = subprocess.run([sys.executable, seed_script], cwd=ROOT_DIR)
    sys.exit(result.returncode)


def run_reproduce():
    print("[*] Running 100% Deterministic Reproducibility Benchmark...")
    reproduce_script = os.path.join(ROOT_DIR, "scripts", "reproduce_all.py")
    result = subprocess.run([sys.executable, reproduce_script], cwd=ROOT_DIR)
    sys.exit(result.returncode)


import socket


def is_port_in_use(port: int) -> bool:
    """Checks if a TCP port is currently open/in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", port)) == 0


def find_available_port(start_port: int = 8501, max_attempts: int = 20) -> int:
    """Finds the first available TCP port starting from start_port."""
    for p in range(start_port, start_port + max_attempts):
        if not is_port_in_use(p):
            return p
    return start_port


def launch_dashboard(port: int = 8501, headless: bool = False, auto_seed: bool = True):
    # Auto-seed database if it doesn't exist
    db_path = os.path.join(ROOT_DIR, "q_immune_qds.db")
    if auto_seed and not os.path.exists(db_path):
        print("[*] First-time setup detected. Seeding demo database...")
        seed_script = os.path.join(ROOT_DIR, "scripts", "seed_demo.py")
        subprocess.run([sys.executable, seed_script], cwd=ROOT_DIR)

    # Check port availability and auto-fallback if busy
    if is_port_in_use(port):
        free_port = find_available_port(start_port=port + 1)
        print(f"[!] Warning: Port {port} is already in use by another process.")
        print(f"[+] Automatically switching to next available port: {free_port}")
        port = free_port

    dashboard_path = os.path.join(ROOT_DIR, "app", "dashboard.py")
    print(f"[*] Starting Streamlit Command Center on port {port}...")
    print(f"[*] Local URL: http://localhost:{port}\n")

    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        dashboard_path,
        f"--server.port={port}",
        f"--server.headless={'true' if headless else 'false'}",
    ]


    try:
        subprocess.run(cmd, cwd=ROOT_DIR)
    except KeyboardInterrupt:
        print("\n[+] Q-IMMUNE QDS Command Center stopped gracefully.")


def main():
    print_banner()

    parser = argparse.ArgumentParser(description="Q-IMMUNE QDS Master Runner")
    parser.add_argument("--test", action="store_true", help="Run full test suite (26 tests)")
    parser.add_argument("--smoke", action="store_true", help="Run fast smoke test (< 1 sec)")
    parser.add_argument("--seed", action="store_true", help="Seed database with sample sessions")
    parser.add_argument("--reproduce", action="store_true", help="Run offline reproducibility benchmark")
    parser.add_argument("--port", type=int, default=8501, help="Port to run Streamlit on (default: 8501)")
    parser.add_argument("--headless", action="store_true", help="Run Streamlit in headless mode")

    args = parser.parse_args()

    if args.test:
        run_tests()
    elif args.smoke:
        run_smoke()
    elif args.seed:
        run_seed()
    elif args.reproduce:
        run_reproduce()
    else:
        launch_dashboard(port=args.port, headless=args.headless)


if __name__ == "__main__":
    main()
