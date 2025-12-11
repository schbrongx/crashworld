#!/usr/bin/env python3
"""
Entry point for CrashWorld.
"""
from __future__ import annotations
import argparse
from core.app import CrashWorldApp


def main() -> None:
    parser = argparse.ArgumentParser(prog="crashworld", description="CrashWorld sandbox")
    parser.add_argument(
        "--config",
        default=None,
        help="Path to a JSON scene config file (spawns all cubes at startup).",
    )
    args = parser.parse_args()
    
    app = CrashWorldApp(config_path=args.config)
    app.run()


if __name__ == "__main__":
    main()
