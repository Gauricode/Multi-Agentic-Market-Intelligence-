from argparse import ArgumentParser
import sys

from crewai import Crew, Process

from .config import load_and_validate_env


def _build_parser() -> ArgumentParser:
    parser = ArgumentParser(description="Run the market intelligence CrewAI pipeline.")
    parser.add_argument("--keyword", help="Keyword to search news for, e.g. AI")
    parser.add_argument("--competitors", help="Comma-separated competitors, e.g. Google,Amazon")
    parser.add_argument("--keywords", help="Comma-separated keywords, e.g. AI,Smart Home")
    return parser


def _is_interactive() -> bool:
    return sys.stdin is not None and sys.stdin.isatty()


def _prompt_if_missing(value: str | None, prompt: str) -> str | None:
    if value:
        return value
    if not _is_interactive():
        return None
    try:
        return input(prompt)
    except EOFError:
        return None


def _resolve_inputs(args):
    keyword = _prompt_if_missing(args.keyword, "Enter keyword (e.g. AI): ")
    competitors = _prompt_if_missing(
        args.competitors,
        "Enter competitors comma-separated (e.g. Google,Amazon): ",
    )
    keywords = _prompt_if_missing(
        args.keywords,
        "Enter keywords comma-separated (e.g. AI,Smart Home): ",
    )

    missing = [
        name
        for name, value in {
            "--keyword": keyword,
            "--competitors": competitors,
            "--keywords": keywords,
        }.items()
        if not value
    ]
    if missing:
        raise ValueError(
            "Missing required inputs: "
            + ", ".join(missing)
            + ". Pass them as CLI args when stdin is unavailable."
        )

    return keyword, competitors, keywords


def run_pipeline(keyword: str, competitors: str, keywords: str) -> str:
    load_and_validate_env()

    # Import after env loading so tool clients use the current API keys.
    from .agents import (
        insight_agent,
        relevance_agent,
        report_delivery_agent,
        source_agent,
        summarization_agent,
        trend_alert_agent,
    )
    from .tasks import build_tasks

    crew = Crew(
        agents=[
            source_agent,
            relevance_agent,
            summarization_agent,
            insight_agent,
            trend_alert_agent,
            report_delivery_agent,
        ],
        tasks=build_tasks(
            keyword,
            competitors,
            keywords,
            source_agent,
            relevance_agent,
            summarization_agent,
            insight_agent,
            trend_alert_agent,
            report_delivery_agent,
        ),
        process=Process.sequential,
        verbose=True,
    )

    try:
        result = crew.kickoff()
    except Exception as exc:
        message = str(exc)
        if "invalid_api_key" in message or "Incorrect API key provided" in message:
            raise RuntimeError(
                "OpenAI authentication failed. Check OPENAI_API_KEY in your .env file."
            ) from exc
        if "insufficient_quota" in message:
            raise RuntimeError(
                "OpenAI quota exceeded for this API key. Add billing/credits or use another key."
            ) from exc
        raise

    return str(result)


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    try:
        keyword, competitors, keywords = _resolve_inputs(args)
    except (ValueError, RuntimeError) as exc:
        parser.error(str(exc))

    try:
        result = run_pipeline(keyword, competitors, keywords)
    except RuntimeError as exc:
        print(str(exc))
        return

    print("\n" + "=" * 80)
    print("CREW EXECUTION COMPLETE")
    print("=" * 80)
    print(result)
