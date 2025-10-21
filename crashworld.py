#!/usr/bin/env python3
"""
Entry point for CrashWorld.
"""
from core.app import CrashWorldApp


def main() -> None:
    app = CrashWorldApp()
    app.run()


if __name__ == "__main__":
    main()
