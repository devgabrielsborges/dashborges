import subprocess
import time
import threading
import webbrowser
import argparse


def run_api_server():
    """Run the FastAPI backend server."""
    print("Starting API server...")
    return subprocess.Popen(
        ["python", "main.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )


def run_streamlit():
    """Run the Streamlit dashboard."""
    print("Starting Streamlit dashboard...")
    return subprocess.Popen(
        ["streamlit", "run", "src/dashborges/dashborges.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def log_output(process, name):
    """Log the output from a subprocess to console."""
    for line in iter(process.stdout.readline, b""):
        print(f"[{name}] {line.decode().strip()}")
    for line in iter(process.stderr.readline, b""):
        print(f"[{name} ERROR] {line.decode().strip()}")


def open_browser(url="http://localhost:8501", delay=3):
    """Open web browser after a delay."""
    time.sleep(delay)  # Give Streamlit time to start
    print(f"Opening dashboard in browser: {url}")
    webbrowser.open(url)


def handle_shutdown(api_process, streamlit_process):
    """Handle graceful shutdown of processes."""
    print("\nShutting down services...")

    # Try graceful termination first
    if api_process and api_process.poll() is None:
        api_process.terminate()
        try:
            api_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            api_process.kill()

    if streamlit_process and streamlit_process.poll() is None:
        streamlit_process.terminate()
        try:
            streamlit_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            streamlit_process.kill()

    print("All services stopped.")


def main():
    parser = argparse.ArgumentParser(description="Run DashBorges application")
    parser.add_argument(
        "--api-only", action="store_true", help="Run only the API server"
    )
    parser.add_argument(
        "--dashboard-only", action="store_true", help="Run only the Streamlit dashboard"
    )
    parser.add_argument(
        "--no-browser", action="store_true", help="Don't open browser automatically"
    )

    args = parser.parse_args()

    api_process = None
    streamlit_process = None

    try:
        # Start API server unless dashboard-only flag is set
        if not args.dashboard_only:
            api_process = run_api_server()
            threading.Thread(
                target=log_output, args=(api_process, "API"), daemon=True
            ).start()
            # Give API time to start before launching dashboard
            time.sleep(2)
            print("API server running at: http://127.0.0.1:8000")

        # Start Streamlit unless api-only flag is set
        if not args.api_only:
            streamlit_process = run_streamlit()
            threading.Thread(
                target=log_output, args=(streamlit_process, "Streamlit"), daemon=True
            ).start()

            # Open browser unless no-browser flag is set
            if not args.no_browser:
                threading.Thread(target=open_browser, daemon=True).start()

            print("Streamlit dashboard will be available at: http://localhost:8501")

        # Keep the main thread alive while processes are running
        while True:
            time.sleep(1)
            if api_process and api_process.poll() is not None:
                print("API server has stopped. Return code:", api_process.returncode)
                break
            if streamlit_process and streamlit_process.poll() is not None:
                print(
                    "Streamlit dashboard has stopped. Return code:",
                    streamlit_process.returncode,
                )
                break

    except KeyboardInterrupt:
        print("Received interrupt signal")
    finally:
        handle_shutdown(api_process, streamlit_process)


if __name__ == "__main__":
    main()
