import { useEffect, useRef, useState } from "react";

interface Candidate {
  text: string;
  source?: string;
}

interface DashboardFlow {
  flowId: string;
  mode: "quick" | "text";
  trigger: "candidate_quick_save" | "dashboard_submit";
  candidateSource: string;
  editedBeforeSubmit: boolean;
}

interface Msg {
  text: string;
  type: "ok" | "err" | "";
}

interface UiEventExtraData {
  flow_id?: string;
  mode?: "quick" | "text";
  trigger?: "candidate_quick_save" | "dashboard_submit";
  candidate_source?: string;
  edited_before_submit?: boolean;
  text_length?: number;
  status?: number;
  reason?: string;
}

function newDashboardFlowId() {
  return `dashboard-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`;
}

export default function QuickLog() {
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [draft, setDraft] = useState("");
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState<Msg>({ text: "", type: "" });
  const textRef = useRef<HTMLTextAreaElement>(null);
  const dashboardFlowRef = useRef<DashboardFlow | null>(null);
  const clearMsgTimeoutRef = useRef<number | null>(null);

  useEffect(() => {
    loadCandidates();

    return () => {
      if (clearMsgTimeoutRef.current !== null) {
        window.clearTimeout(clearMsgTimeoutRef.current);
      }
    };
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

  async function postUiEvent(eventName: string, extraData: UiEventExtraData) {
    try {
      await fetch("/events/ui", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          event_name: eventName,
          ui_mode: "dashboard",
          extra_data: extraData,
        }),
      });
    } catch {
      // UI telemetry should not block the primary save flow.
    }
  }

  function resolveCandidateSource(mode: DashboardFlow["mode"], candidateSource?: string) {
    const normalized = (candidateSource ?? "").trim();
    if (normalized) return normalized;
    if (mode === "text") return "free_text";
    return "";
  }

  async function startTextFlowIfNeeded(text: string) {
    if (dashboardFlowRef.current?.mode === "text") return dashboardFlowRef.current;

    const flow: DashboardFlow = {
      flowId: newDashboardFlowId(),
      mode: "text",
      trigger: "dashboard_submit",
      candidateSource: "free_text",
      editedBeforeSubmit: false,
    };
    dashboardFlowRef.current = flow;
    await postUiEvent("input_started", {
      flow_id: flow.flowId,
      mode: flow.mode,
      trigger: flow.trigger,
      candidate_source: flow.candidateSource,
      text_length: text.length,
    });
    return flow;
  }

  function resetDashboardFlow() {
    dashboardFlowRef.current = null;
  }

  function scheduleMessageClear() {
    if (clearMsgTimeoutRef.current !== null) {
      window.clearTimeout(clearMsgTimeoutRef.current);
    }
    clearMsgTimeoutRef.current = window.setTimeout(() => {
      setMsg((current) => (current.type === "ok" ? { text: "", type: "" } : current));
      clearMsgTimeoutRef.current = null;
    }, 3000);
  }

  async function saveLogText(text: string, flow: DashboardFlow) {
    const trimmed = text.trim();
    if (!trimmed || busy) return false;

    if (clearMsgTimeoutRef.current !== null) {
      window.clearTimeout(clearMsgTimeoutRef.current);
      clearMsgTimeoutRef.current = null;
    }

    setBusy(true);
    setMsg({ text: "", type: "" });

    const telemetryData: UiEventExtraData = {
      flow_id: flow.flowId,
      mode: flow.mode,
      trigger: flow.trigger,
      candidate_source: flow.candidateSource,
      edited_before_submit: flow.editedBeforeSubmit,
      text_length: trimmed.length,
    };

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
        await postUiEvent("input_submitted", telemetryData);
        await postUiEvent("save_success", telemetryData);
        await loadCandidates();
        resetDashboardFlow();
        scheduleMessageClear();
        return true;
      }

      let errorMessage = String(r.status);
      try {
        const err = await r.json();
        errorMessage = err.error ?? errorMessage;
      } catch {
        // Keep the HTTP status fallback when the error body is not JSON.
      }
      setMsg({ text: "エラー: " + errorMessage, type: "err" });
      await postUiEvent("save_error", { ...telemetryData, status: r.status });
      return false;
    } catch (ex: unknown) {
      const message = ex instanceof Error ? ex.message : String(ex);
      setMsg({ text: "接続エラー: " + message, type: "err" });
      await postUiEvent("save_error", { ...telemetryData, reason: "fetch_exception" });
      return false;
    } finally {
      setBusy(false);
    }
  }

  async function handleSubmit() {
    const trimmed = draft.trim();
    if (!trimmed || busy) return;
    const flow = await startTextFlowIfNeeded(trimmed);
    await saveLogText(trimmed, flow);
  }

  async function handleCandidateTap(candidate: Candidate) {
    if (busy) return;

    const flow: DashboardFlow = {
      flowId: newDashboardFlowId(),
      mode: "quick",
      trigger: "candidate_quick_save",
      candidateSource: resolveCandidateSource("quick", candidate.source),
      editedBeforeSubmit: false,
    };

    dashboardFlowRef.current = flow;
    await postUiEvent("input_started", {
      flow_id: flow.flowId,
      mode: flow.mode,
      trigger: flow.trigger,
      candidate_source: flow.candidateSource,
      text_length: candidate.text.trim().length,
    });
    await saveLogText(candidate.text, flow);
  }

  async function handleDraftFocus() {
    await startTextFlowIfNeeded(draft.trim());
  }

  async function handleDraftChange(nextDraft: string) {
    setDraft(nextDraft);
    await startTextFlowIfNeeded(nextDraft.trim());
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
      <div className="quicklog-intro">
        候補タグをタップするとそのまま保存されます。自由入力は下の欄から追加できます。
      </div>
      {candidates.length > 0 && (
        <div className="candidates">
          {candidates.map((c, i) => (
            <button
              key={i}
              type="button"
              className="candidate-tag"
              disabled={busy}
              onClick={() => void handleCandidateTap(c)}
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
          onChange={(e) => void handleDraftChange(e.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={() => void handleDraftFocus()}
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
