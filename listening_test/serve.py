"""Serve the listening test on the classroom LAN: python -m listening_test.serve"""

import argparse
import socket

from waitress import serve

from .app import create_app


def lan_ip():
    """The address other machines on the LAN can reach. A UDP connect sends no packets."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        try:
            s.connect(("10.255.255.255", 1))
            return s.getsockname()[0]
        except OSError:
            return "127.0.0.1"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--host", default="0.0.0.0", help="bind address (LAN only; never tunnel this server)")
    args = parser.parse_args()
    app = create_app()
    url = f"http://{lan_ip()}:{args.port}/"
    print("\n  Luistertest voor studenten:  " + url)
    print("  Resultaten (projector):      " + url + "resultaten\n")
    try:
        import segno
        segno.make(url).terminal(compact=True)
    except Exception:
        pass
    print("\n  Stop met Ctrl+C. Wis na de les met: make wipe-test\n")
    serve(app, host=args.host, port=args.port, threads=24, connection_limit=200, channel_timeout=30)


if __name__ == "__main__":
    main()
