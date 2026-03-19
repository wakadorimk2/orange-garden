import { useState, useEffect, useRef } from "react";

interface Candidate {
  text: string;
  source?: string;
}

interface Msg {
  text: string;
  type: "ok" | "err" | "";
}

export default function QuickLog() {
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [draft, setDraft] = useState("");
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState<Msg>({ text: "", type: "" });
  const textRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    loadCandidates();
  }, []);

  async function loadCandidates() {
    try {
      const r = await fetch("/api/candidates");
      if (!r.ok) throw new Error("http " + r.status);
      const data = await r.json();
      setCandidates(Array.isArray(data) ? (data as Candidate[]) : []);
    } catch {
      setCandidates([]);
    }
  }

  function handleCandidateTap(text: string) {
    setDraft(text);
    textRef.current?.focus();
  }

  async function handleSubmit() {
    const trimmed = draft.trim();
    if (!trimmed || busy) return;
    setBusy(true);
    setMsg({ text: "", type: "" });
    try {
      const r = await fetch("/events", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: trimmed }),
      });
      if (r.ok) {
        const saved = await r.json();
        setDraft("");
        setMsg({ text: `保存しました: ${saved.domain} / ${saved.kind}`, type: "ok" });
        await loadCandidates();
        setTimeout(
          () => setMsg((m) => (m.type === "ok" ? { text: "", type: "" } : m)),
          3000
        );
      } else {
        const err = await r.json();
        setMsg({ text: "エラー: " + (err.error ?? String(r.status)), type: "err" });
      }
    } catch (ex: unknown) {
      const message = ex instanceof Error ? ex.message : String(ex);
      setMsg({ text: "接続エラー: " + message, type: "err" });
    } finally {
      setBusy(false);
    }
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey && !e.nativeEvent.isComposing) {
      e.preventDefault();
      handleSubmit();
    }
  }

  const trimmed = draft.trim();
  const draftLabel = trimmed.length <= 18 ? trimmed : trimmed.slice(0, 18) + "...";

  return (
    <>
      {candidates.length > 0 && (
        <div className="candidates">
          {candidates.map((c, i) => (
            <button
              key={i}
              type="button"
              className="candidate-tag"
              disabled={busy}
              onClick={() => handleCandidateTap(c.text)}
            >
              {c.text}
            </button>
          ))}
        </div>
      )}
      <div className="log-form">
        <textarea
          ref={textRef}
          className="log-text"
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="いま起きたことを短く記録"
          enterKeyHint="done"
          disabled={busy}
        />
        <div className="composer-meta">
          <div className="draft-preview" aria-live="polite">
            {trimmed ? "保存対象: " + trimmed : "候補をタップするか短文を入力"}
          </div>
          <button
            type="button"
            className="log-submit"
            disabled={!trimmed || busy}
            onClick={handleSubmit}
          >
            {busy ? "保存中..." : trimmed ? `「${draftLabel}」を保存` : "保存"}
          </button>
        </div>
        <div
          className={`log-msg${msg.type === "ok" ? " msg-ok" : msg.type === "err" ? " msg-err" : ""}`}
          aria-live="polite"
        >
          {msg.text}
        </div>
      </div>
    </>
  );
}
