from crewai import Task


def build_tasks(
    keyword: str,
    competitors: str,
    keywords: str,
    source_agent,
    relevance_agent,
    summarization_agent,
    insight_agent,
    trend_alert_agent,
    report_delivery_agent,
):
    collect_task = Task(
        description=(
            f"Search for recent news articles about '{keyword}'. "
            f"Use the exact keyword '{keyword}' when invoking the news collection tool."
        ),
        agent=source_agent,
        expected_output=(
            "A collection step confirmation indicating that recent news articles were "
            "saved to collected_sources.csv."
        ),
    )

    filter_task = Task(
        description=(
            "Filter the collected articles for market intelligence relevance. "
            f"Use these competitors: {competitors}. "
            f"Use these keywords: {keywords}. "
            "Deduplicate the results and retain only high-signal articles."
        ),
        agent=relevance_agent,
        expected_output=(
            "A filtering step confirmation indicating that the curated and deduplicated "
            "articles were saved to filtered_sources.csv."
        ),
        context=[collect_task],
    )

    summarize_task = Task(
        description=(
            "Summarize the filtered market intelligence articles into concise bullet points "
            "for a stakeholder audience."
        ),
        agent=summarization_agent,
        expected_output="A markdown summary saved to summary.md.",
        context=[filter_task],
    )

    insight_task = Task(
        description=(
            "Generate structured insights from the filtered dataset. "
            f"Track mentions for competitors: {competitors}. "
            f"Track mentions for keywords: {keywords}."
        ),
        agent=insight_agent,
        expected_output="A JSON insights payload saved to insights.json.",
        context=[filter_task],
    )

    alert_task = Task(
        description=(
            "Identify notable trends and create alert-worthy signals from the generated insights."
        ),
        agent=trend_alert_agent,
        expected_output="A JSON alerts payload saved to alerts.json.",
        context=[insight_task],
    )

    report_task = Task(
        description=(
            "Assemble the summary, insights, and alerts into a final stakeholder-ready report."
        ),
        agent=report_delivery_agent,
        expected_output="A final markdown report saved to final_report.md.",
        context=[summarize_task, insight_task, alert_task],
    )

    return [
        collect_task,
        filter_task,
        summarize_task,
        insight_task,
        alert_task,
        report_task,
    ]
