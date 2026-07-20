"""Backward-compatible. Prefer: uv run farzana webhook """
from farzana.cli import main

if __name__ == "__main__":
    main(["webhook"])
