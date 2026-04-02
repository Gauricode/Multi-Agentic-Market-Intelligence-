"use client";

import { Activity, FileText, Radar, Sparkles } from "lucide-react";
import { useState } from "react";

const apiBaseUrl =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

export default function Dashboard() {
  const [searchKeyword, setSearchKeyword] = useState("");
  const [competitors, setCompetitors] = useState("");
  const [keywords, setKeywords] = useState("");
  const [logs, setLogs] = useState("");
  const [report, setReport] = useState("");
  const [loading, setLoading] = useState(false);

  const runPipeline = async () => {
    if (!searchKeyword || !competitors || !keywords) {
      setReport("Please fill in keyword, competitors, and keywords before running.");
      return;
    }

    setLoading(true);
    setReport("");
    setLogs("Connecting to backend and starting the market-intelligence run...");

    try {
      const res = await fetch(`${apiBaseUrl}/run-agent`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          search_keyword: searchKeyword,
          competitors,
          keywords,
        }),
      });

      if (!res.ok) {
        const errorData = await res.json().catch(() => null);
        const detail =
          errorData && typeof errorData.detail === "string"
            ? errorData.detail
            : "Backend request failed.";
        throw new Error(detail);
      }

      const data = await res.json();
      setLogs(
        [
          "Pipeline finished successfully.",
          `Keyword: ${searchKeyword}`,
          `Competitors: ${competitors}`,
          `Keywords: ${keywords}`,
          "",
          `Crew result: ${data.message ?? "Completed"}`,
        ].join("\n"),
      );
      setReport(data.report || "No report content was returned.");
    } catch (err) {
      const message =
        err instanceof Error
          ? err.message
          : "Error connecting to backend. Ensure FastAPI is running.";
      setLogs("Pipeline failed before completing.");
      setReport(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top,_#123257_0%,_#08111d_45%,_#05080d_100%)] px-5 py-8 text-slate-100 sm:px-8 lg:px-12">
      <section className="mx-auto max-w-6xl">
        <div className="mb-8 grid gap-4 rounded-[28px] border border-white/10 bg-white/6 p-6 shadow-[0_20px_80px_rgba(0,0,0,0.35)] backdrop-blur md:grid-cols-[1.6fr_1fr]">
          <div>
            <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-cyan-300/20 bg-cyan-300/10 px-3 py-1 text-sm text-cyan-100">
              <Radar size={16} />
              Multi-Agent Market Intelligence
            </div>
            <h1 className="max-w-3xl text-4xl font-semibold tracking-tight sm:text-5xl">
              Generate market intelligence reports from one clean workspace.
            </h1>
            <p className="mt-4 max-w-2xl text-base leading-7 text-slate-300">
              Enter a target ticker, define the competitive frame, and generate a
              stakeholder-ready report backed by your CrewAI workflow.
            </p>
          </div>

          <div className="grid gap-3 rounded-3xl border border-white/10 bg-slate-950/40 p-4">
            <Metric icon={<Sparkles size={18} />} label="Backend" value={apiBaseUrl} />
            <Metric icon={<Activity size={18} />} label="Mode" value="FastAPI + Next.js" />
            <Metric icon={<FileText size={18} />} label="Output" value="Live report preview" />
          </div>
        </div>

        <div className="grid gap-6 lg:grid-cols-[1.05fr_0.95fr]">
          <section className="rounded-[28px] border border-white/10 bg-white/6 p-6 backdrop-blur">
            <h2 className="text-2xl font-semibold">Pipeline Controls</h2>
            <p className="mt-2 text-sm leading-6 text-slate-300">
              Massive works best with stock tickers like <span className="font-medium text-cyan-200">NVDA</span>,{" "}
              <span className="font-medium text-cyan-200">AAPL</span>, or{" "}
              <span className="font-medium text-cyan-200">TSLA</span>.
            </p>

            <div className="mt-6 grid gap-4">
              <Field
                label="Search keyword"
                placeholder="NVDA"
                value={searchKeyword}
                onChange={setSearchKeyword}
              />
              <Field
                label="Competitors"
                placeholder="AMD,Intel,TSMC"
                value={competitors}
                onChange={setCompetitors}
              />
              <Field
                label="Keywords"
                placeholder="AI,GPU,datacenter,chip,semiconductor"
                value={keywords}
                onChange={setKeywords}
              />
            </div>

            <button
              className="mt-6 w-full rounded-2xl bg-cyan-300 px-4 py-4 text-base font-semibold text-slate-950 transition hover:bg-cyan-200 disabled:cursor-not-allowed disabled:bg-cyan-500/50"
              onClick={runPipeline}
              disabled={loading}
            >
              {loading ? "Running agents..." : "Run intelligence pipeline"}
            </button>
          </section>

          <section className="grid gap-6">
            <Panel
              title="Agent Execution Logs"
              content={logs}
              placeholder="Execution updates will appear here."
            />
            <Panel
              title="Generated Intelligence Report"
              content={report}
              placeholder="The final report will appear here after the run completes."
              large
            />
          </section>
        </div>
      </section>
    </main>
  );
}

function Metric({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
}) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
      <div className="mb-2 flex items-center gap-2 text-cyan-200">{icon}</div>
      <div className="text-xs uppercase tracking-[0.2em] text-slate-400">{label}</div>
      <div className="mt-1 break-all text-sm text-slate-100">{value}</div>
    </div>
  );
}

function Field({
  label,
  placeholder,
  value,
  onChange,
}: {
  label: string;
  placeholder: string;
  value: string;
  onChange: (value: string) => void;
}) {
  return (
    <label className="grid gap-2 text-sm text-slate-200">
      <span>{label}</span>
      <input
        className="rounded-2xl border border-white/10 bg-slate-950/50 px-4 py-3 text-base text-white outline-none placeholder:text-slate-500 focus:border-cyan-300/50"
        placeholder={placeholder}
        value={value}
        onChange={(e) => onChange(e.target.value)}
      />
    </label>
  );
}

function Panel({
  title,
  content,
  placeholder,
  large = false,
}: {
  title: string;
  content: string;
  placeholder: string;
  large?: boolean;
}) {
  return (
    <div className="rounded-[28px] border border-white/10 bg-white/6 p-6 backdrop-blur">
      <h2 className="text-xl font-semibold">{title}</h2>
      <textarea
        className={`mt-4 w-full rounded-3xl border border-white/10 bg-slate-950/60 p-4 font-mono text-sm leading-6 text-slate-100 outline-none placeholder:text-slate-500 ${
          large ? "min-h-[360px]" : "min-h-[180px]"
        }`}
        value={content}
        readOnly
        placeholder={placeholder}
      />
    </div>
  );
}
