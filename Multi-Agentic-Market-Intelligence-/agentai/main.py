from pathlib import Path
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from agentai.cli import main
else:
    from .cli import main


if __name__ == "__main__":
    main()
