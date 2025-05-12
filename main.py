import uvicorn
import socket
import sys
import argparse
from src.dashborges.api import app


def is_port_in_use(port):
    """Check if a port is already in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0


if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Run the DashBorges API server")
    parser.add_argument(
        "--port", type=int, default=8000, help="Port to run the server on"
    )
    args = parser.parse_args()

    port = args.port

    # If the specified port is in use, try the next 10 ports
    max_attempts = 10
    for attempt in range(max_attempts):
        if not is_port_in_use(port):
            break
        port += 1
        if attempt == max_attempts - 1:
            print(
                f"ERROR: Could not find an available port after {max_attempts} attempts."
            )
            sys.exit(1)

    if port != args.port:
        print(f"Port {args.port} is in use. Using port {port} instead.")

    print(f"API server running at: http://127.0.0.1:{port}")

    # Store the port in a file for other processes to use
    with open(".api_port", "w") as f:
        f.write(str(port))

    uvicorn.run(app, host="0.0.0.0", port=port)
