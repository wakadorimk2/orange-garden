import { useEffect, useState } from "react";

interface HeatmapEntry {
  date: string;
  count: number;
  bucket_index: number;
}

function monthDay(iso: string): string {
  const parts = iso.split("-");
  if (parts.length !== 3) return iso;
  return `${Number(parts[1])}/${Number(parts[2])}`;
}

function weekRangeLabel(week: HeatmapEntry[]): string {
  if (!week.length) return "";
  return monthDay(week[0].date) + "–" + monthDay(week[week.length - 1].date);
}

function splitIntoWeeks(entries: HeatmapEntry[]): HeatmapEntry[][] {
  const weeks: HeatmapEntry[][] = [];
  for (let i = 0; i < entries.length; i += 7) {
    weeks.push(entries.slice(i, i + 7));
  }
  return weeks;
}

export default function Heatmap() {
  const [entries, setEntries] = useState<HeatmapEntry[]>([]);

  useEffect(() => {
    fetch("/api/heatmap")
      .then((r) => (r.ok ? r.json() : Promise.reject(r.status)))
      .then((data: unknown) => {
        setEntries(Array.isArray(data) ? (data as HeatmapEntry[]) : []);
      })
      .catch(() => setEntries([]));
  }, []);

  const weeks = splitIntoWeeks(entries);
  const startDate = entries[0]?.date ?? "";
  const endDate = entries[entries.length - 1]?.date ?? "";
  const rangeLabel = entries.length ? `${monthDay(startDate)} – ${monthDay(endDate)}` : "記録なし";

  return (
    <section className="heatmap-shell" aria-labelledby="heatmap-title">
      <div className="heatmap-header">
        <h2 id="heatmap-title">直近6週間</h2>
        <span className="heatmap-range-label">{rangeLabel}</span>
      </div>
      <div className="heatmap-grid" aria-label="直近6週間のヒートマップ">
        {weeks.map((week) => (
          <div key={week[0].date} className="heatmap-week">
            <div className="heatmap-week-label">{weekRangeLabel(week)}</div>
            {week.map((entry) => {
              const bucketIdx = Math.max(0, Math.min(4, entry.bucket_index));
              return (
                <div
                  key={entry.date}
                  className={`heatmap-cell heatmap-cell--bucket-${bucketIdx}${
                    entry.count === 0 ? " heatmap-cell--empty" : ""
                  }`}
                  aria-label={`${entry.date}: ${entry.count}件`}
                  title={`${entry.date}: ${entry.count}件`}
                />
              );
            })}
          </div>
        ))}
      </div>
    </section>
  );
}
