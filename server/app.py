import argparse

from golden_hour_dispatch_env.server.app import app as app
from golden_hour_dispatch_env.server.app import main as package_main

__all__ = ["app", "main"]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    package_main(host=args.host, port=args.port)


if __name__ == "__main__":
    main()
