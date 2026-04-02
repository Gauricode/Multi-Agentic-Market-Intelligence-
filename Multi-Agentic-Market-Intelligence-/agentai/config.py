import os
from dotenv import load_dotenv


def load_and_validate_env() -> None:
    # Force .env values to override stale process-level variables.
    load_dotenv(override=True)

    # Backward compatibility: some setups used OPEN_API_KEY.
    if not os.getenv("OPENAI_API_KEY") and os.getenv("OPEN_API_KEY"):
        os.environ["OPENAI_API_KEY"] = os.getenv("OPEN_API_KEY", "")

    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is not set. Add it to your .env file.")

    if not os.getenv("NEWS_API_KEY"):
        raise RuntimeError("NEWS_API_KEY is not set. Add it to your .env file.")
