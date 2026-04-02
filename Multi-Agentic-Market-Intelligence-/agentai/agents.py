from crewai import Agent

from .tools import (
    insight_tool,
    news_tool,
    relevance_dedup_tool,
    report_delivery_tool,
    summarization_tool,
    trend_alert_tool,
)


source_agent = Agent(
    role="Source Collector",
    goal="Collect latest news articles based on search keywords.",
    backstory=(
        "An expert researcher who efficiently gathers fresh and relevant "
        "industry information from various news sources."
    ),
    tools=[news_tool],
    verbose=True,
)

relevance_agent = Agent(
    role="Relevance and Deduplication Specialist",
    goal=(
        "Filter collected articles and keep only valuable market intelligence "
        "based on keywords and competitors."
    ),
    backstory=(
        "An expert research analyst who removes noise, eliminates duplicates, "
        "and keeps high-value insights aligned with business interests."
    ),
    tools=[relevance_dedup_tool],
    verbose=True,
)

summarization_agent = Agent(
    role="Summarization Specialist",
    goal="Create concise summaries from filtered market-relevant news.",
    backstory=(
        "A strategist who distills noisy article lists into crisp executive-level "
        "summaries."
    ),
    tools=[summarization_tool],
    verbose=True,
)

insight_agent = Agent(
    role="Insight Generator",
    goal="Extract actionable business insights from summarized and filtered news.",
    backstory=(
        "A market intelligence analyst who quantifies competitor and keyword signals "
        "to support product and strategy decisions."
    ),
    tools=[insight_tool],
    verbose=True,
)

trend_alert_agent = Agent(
    role="Trend and Alert Analyst",
    goal="Detect emerging trends and generate alerts from insight signals.",
    backstory=(
        "An analyst focused on early detection of competitive and market movement "
        "patterns."
    ),
    tools=[trend_alert_tool],
    verbose=True,
)

report_delivery_agent = Agent(
    role="Report Delivery Specialist",
    goal="Compile all outputs into a final deliverable report.",
    backstory=(
        "A reporting specialist who produces clean, stakeholder-ready intelligence "
        "reports."
    ),
    tools=[report_delivery_tool],
    verbose=True,
)
