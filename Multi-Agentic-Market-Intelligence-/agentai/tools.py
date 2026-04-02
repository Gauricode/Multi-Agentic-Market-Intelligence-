import os
import json

import pandas as pd
import requests
from crewai.tools import tool
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")

try:
    client = OpenAI()
except Exception:
    client = None


@tool("News Fetch Tool")
def news_tool(keyword: str):
    """Fetch latest news articles about a keyword using NewsAPI.org."""
    if not NEWS_API_KEY:
        raise RuntimeError("NEWS_API_KEY is not set. Add it to your .env file.")

    url = (
    f"https://api.massive.com/v2/reference/news?"
    f"ticker={keyword}&limit=20&sort=published_utc&order=desc&apiKey={NEWS_API_KEY}"
    )

    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    articles = list(data.get("results", [])[:5])
    pd.DataFrame(articles).to_csv("collected_sources.csv", index=False)
    return f"Collected {len(articles)} articles and saved to collected_sources.csv"


@tool("Relevance & Deduplication Tool")
def relevance_dedup_tool(competitors: str, keywords: str):
    """Filter, score, and save high-relevance articles."""
    if not os.path.exists("collected_sources.csv"):
        return "No collected data found. Run news_tool first."

    df = pd.read_csv("collected_sources.csv").drop_duplicates(subset=["title"])

    competitor_terms = [c.strip().lower() for c in competitors.split(",") if c.strip()]
    keyword_terms = [k.strip().lower() for k in keywords.split(",") if k.strip()]

    def keyword_score(text: str) -> int:
        value = str(text).lower()
        score = sum(2 for word in keyword_terms if word in value)
        score += sum(3 for comp in competitor_terms if comp in value)
        return score

    df["keyword_score"] = df["title"].apply(keyword_score)

    llm_available = client is not None
    if not llm_available:
        df["llm_score"] = 0
    else:
        llm_scores = []
        for title in df["title"]:
            prompt = (
                "Rate relevance for market intelligence about AI, smart home, and tech competitors. "
                f"Headline: {title}. Return only a number from 0 to 10."
            )
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                )
                llm_scores.append(response.choices[0].message.content.strip())
            except Exception:
                llm_available = False
                df["llm_score"] = 0
                break

        if llm_available and llm_scores:
            df["llm_score"] = pd.Series(llm_scores, index=df.index[: len(llm_scores)])
            df["llm_score"] = pd.to_numeric(df["llm_score"], errors="coerce").fillna(0)
        elif llm_available:
            df["llm_score"] = 0

    if llm_available:
        filtered = df[(df["keyword_score"] >= 2) & (df["llm_score"] >= 6)]
    else:
        filtered = df[df["keyword_score"] >= 2]

    filtered.to_csv("filtered_sources.csv", index=False)
    return f"Filtering complete. {len(filtered)} high-quality articles saved to filtered_sources.csv"


@tool("Summarization Tool")
def summarization_tool(max_items: int = 10):
    """Summarize filtered headlines and save to summary.md."""
    if not os.path.exists("filtered_sources.csv"):
        return "No filtered data found. Run relevance_dedup_tool first."

    df = pd.read_csv("filtered_sources.csv")
    if df.empty:
        summary = "# Market Summary\n\nNo qualifying articles were found."
        with open("summary.md", "w", encoding="utf-8") as f:
            f.write(summary)
        return "No filtered rows. summary.md created with empty summary."

    max_items = max(1, int(max_items))
    top = df.head(max_items)
    lines = ["# Market Summary", ""]
    for i, row in top.iterrows():
        title = str(row.get("title", "Untitled"))
        source = str(row.get("source", "Unknown"))
        url = str(row.get("url", ""))
        lines.append(f"{i + 1}. {title}")
        lines.append(f"   - Source: {source}")
        if url and url != "nan":
            lines.append(f"   - URL: {url}")

    with open("summary.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return f"Summary saved to summary.md with {len(top)} items."


@tool("Insight Tool")
def insight_tool(competitors: str = "", keywords: str = ""):
    """Generate basic keyword and competitor insights and save to insights.json."""
    if not os.path.exists("filtered_sources.csv"):
        return "No filtered data found. Run relevance_dedup_tool first."

    df = pd.read_csv("filtered_sources.csv")
    if df.empty:
        payload = {"total_articles": 0, "competitor_mentions": {}, "keyword_mentions": {}}
        with open("insights.json", "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        return "No filtered rows. insights.json created with empty insights."

    titles = df["title"].fillna("").astype(str).str.lower()
    competitor_terms = [c.strip() for c in str(competitors).split(",") if c.strip()]
    keyword_terms = [k.strip() for k in str(keywords).split(",") if k.strip()]

    competitor_mentions = {
        term: int(titles.str.contains(term.lower(), regex=False).sum())
        for term in competitor_terms
    }
    keyword_mentions = {
        term: int(titles.str.contains(term.lower(), regex=False).sum())
        for term in keyword_terms
    }

    payload = {
        "total_articles": int(len(df)),
        "competitor_mentions": competitor_mentions,
        "keyword_mentions": keyword_mentions,
    }
    with open("insights.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    return "Insights saved to insights.json."


@tool("Trend and Alert Tool")
def trend_alert_tool(alert_threshold: int = 2):
    """Detect simple trends and alerts from insights.json and save to alerts.json."""
    if not os.path.exists("insights.json"):
        return "No insights found. Run insight_tool first."

    with open("insights.json", "r", encoding="utf-8") as f:
        insights = json.load(f)

    threshold = max(1, int(alert_threshold))
    competitor_mentions = insights.get("competitor_mentions", {})
    keyword_mentions = insights.get("keyword_mentions", {})

    top_competitors = sorted(
        competitor_mentions.items(), key=lambda x: x[1], reverse=True
    )[:3]
    top_keywords = sorted(keyword_mentions.items(), key=lambda x: x[1], reverse=True)[:3]

    alerts = []
    for name, count in competitor_mentions.items():
        if count >= threshold:
            alerts.append(f"High competitor visibility: {name} appears {count} times.")
    for name, count in keyword_mentions.items():
        if count >= threshold:
            alerts.append(f"High keyword activity: {name} appears {count} times.")

    payload = {
        "top_competitors": top_competitors,
        "top_keywords": top_keywords,
        "alerts": alerts,
    }
    with open("alerts.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    return f"Trend and alert analysis saved to alerts.json with {len(alerts)} alerts."


@tool("Report Delivery Tool")
def report_delivery_tool():
    """Compile summary and alert outputs into final_report.md."""
    summary_text = ""
    alerts = {}

    if os.path.exists("summary.md"):
        with open("summary.md", "r", encoding="utf-8") as f:
            summary_text = f.read().strip()

    if os.path.exists("alerts.json"):
        with open("alerts.json", "r", encoding="utf-8") as f:
            alerts = json.load(f)

    report_lines = ["# Final Market Intelligence Report", ""]
    if summary_text:
        report_lines.append(summary_text)
        report_lines.append("")
    else:
        report_lines.append("No summary available.")
        report_lines.append("")

    report_lines.append("## Top Competitors")
    for name, count in alerts.get("top_competitors", []):
        report_lines.append(f"- {name}: {count}")
    if not alerts.get("top_competitors"):
        report_lines.append("- None")

    report_lines.append("")
    report_lines.append("## Top Keywords")
    for name, count in alerts.get("top_keywords", []):
        report_lines.append(f"- {name}: {count}")
    if not alerts.get("top_keywords"):
        report_lines.append("- None")

    report_lines.append("")
    report_lines.append("## Alerts")
    alert_items = alerts.get("alerts", [])
    if alert_items:
        for item in alert_items:
            report_lines.append(f"- {item}")
    else:
        report_lines.append("- None")

    with open("final_report.md", "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
    return "Final report saved to final_report.md."
