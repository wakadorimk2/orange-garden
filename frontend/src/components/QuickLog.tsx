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

function candidateRenderKey(candidate: Candidate) {
  return `${candidate.source ?? ""}\u0000${candidate.text}`;
}

function savedCandidateKey(candidate: Candidate) {
  return candidate.text.trim();
}

export default function QuickLog() {
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [draft, setDraft] = useState("");
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState<Msg>({ text: "", type: "" });
  const [savedTagKey, setSavedTagKey] = useState<string | null>(null); // #427
  const [textOpen, setTextOpen] = useState(false); // #428
  const textRef = useRef<HTMLTextAreaElement>(null);
  const textFlowRef = useRef<DashboardFlow | null>(null);
  const clearMsgTimeoutRef = useRef<number | null>(null);
  const savedTagTimeoutRef = useRef<number | null>(null); // #427
  const savedTagFrameRef = useRef<number | null>(null); // #427
  const savingRef = useRef(false);

  useEffect(() => {
    loadCandidates();

    return () => {
      if (clearMsgTimeoutRef.current !== null) {
        window.clearTimeout(clearMsgTimeoutRef.current);
      }
      if (savedTagTimeoutRef.current !== null) {
        window.clearTimeout(savedTagTimeoutRef.current);
      }
      if (savedTagFrameRef.current !== null) {
        window.cancelAnimationFrame(savedTagFrameRef.current);
      }
    };
  }, []);

  // #428: auto-focus textarea when opened
  useEffect(() => {
    if (textOpen && textRef.current) {
      textRef.current.focus();
    }
  }, [textOpen]);

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

  function startTextFlowIfNeeded(text: string) {
    if (textFlowRef.current) return textFlowRef.current;

    const flow: DashboardFlow = {
      flowId: newDashboardFlowId(),
      mode: "text",
      trigger: "dashboard_submit",
      candidateSource: "free_text",
      editedBeforeSubmit: false,
    };
    textFlowRef.current = flow;
    void postUiEvent("input_started", {
      flow_id: flow.flowId,
      mode: flow.mode,
      trigger: flow.trigger,
      candidate_source: flow.candidateSource,
      text_length: text.length,
    });
    return flow;
  }

  function resetTextFlow() {
    textFlowRef.current = null;
  }

  function beginSave() {
    if (savingRef.current) return false;
    savingRef.current = true;

    if (clearMsgTimeoutRef.current !== null) {
      window.clearTimeout(clearMsgTimeoutRef.current);
      clearMsgTimeoutRef.current = null;
    }

    setBusy(true);
    setMsg({ text: "", type: "" });
    return true;
  }

  function endSave() {
    savingRef.current = false;
    setBusy(false);
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

  function scheduleSavedTagClear() {
    if (savedTagTimeoutRef.current !== null) {
      window.clearTimeout(savedTagTimeoutRef.current);
    }
    savedTagTimeoutRef.current = window.setTimeout(() => {
      setSavedTagKey(null);
      savedTagTimeoutRef.current = null;
    }, 600);
  }

  function triggerSavedTagFeedback(nextSavedTagKey: string) {
    if (savedTagFrameRef.current !== null) {
      window.cancelAnimationFrame(savedTagFrameRef.current);
      savedTagFrameRef.current = null;
    }

    if (savedTagKey === nextSavedTagKey) {
      setSavedTagKey(null);
      savedTagFrameRef.current = window.requestAnimationFrame(() => {
        setSavedTagKey(nextSavedTagKey);
        savedTagFrameRef.current = null;
        scheduleSavedTagClear();
      });
      return;
    }

    setSavedTagKey(nextSavedTagKey);
    scheduleSavedTagClear();
  }

  async function saveLogText(
    text: string,
    flow: DashboardFlow,
    options?: { clearDraftOnSuccess?: boolean; savedCandidateKey?: string }
  ) {
    const trimmed = text.trim();
    if (!trimmed || !beginSave()) return false;

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
        await r.json();
        if (options?.clearDraftOnSuccess ?? true) {
          setDraft("");
          resetTextFlow();
        }
        setMsg({ text: "保存しました", type: "ok" }); // #427: simplified

        // #427: saved tag visual feedback
        if (options?.savedCandidateKey) {
          triggerSavedTagFeedback(options.savedCandidateKey);
        }

        void postUiEvent("input_submitted", telemetryData);
        void postUiEvent("save_success", telemetryData);
        await loadCandidates();
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
      void postUiEvent("save_error", { ...telemetryData, status: r.status });
      return false;
    } catch (ex: unknown) {
      const message = ex instanceof Error ? ex.message : String(ex);
      setMsg({ text: "接続エラー: " + message, type: "err" });
      void postUiEvent("save_error", { ...telemetryData, reason: "fetch_exception" });
      return false;
    } finally {
      endSave();
    }
  }

  async function handleSubmit() {
    const trimmed = draft.trim();
    if (!trimmed || savingRef.current) return;
    const flow = startTextFlowIfNeeded(trimmed);
    if (!flow) return;
    const ok = await saveLogText(trimmed, flow, { clearDraftOnSuccess: true });
    if (ok) {
      textRef.current?.blur(); // #427: auto blur after text save
      setTextOpen(false); // #428: collapse after save
    }
  }

  async function handleCandidateTap(candidate: Candidate) {
    if (savingRef.current) return;

    const flow: DashboardFlow = {
      flowId: newDashboardFlowId(),
      mode: "quick",
      trigger: "candidate_quick_save",
      candidateSource: resolveCandidateSource("quick", candidate.source),
      editedBeforeSubmit: false,
    };

    void postUiEvent("input_started", {
      flow_id: flow.flowId,
      mode: flow.mode,
      trigger: flow.trigger,
      candidate_source: flow.candidateSource,
      text_length: candidate.text.trim().length,
    });
    await saveLogText(candidate.text, flow, {
      clearDraftOnSuccess: false,
      savedCandidateKey: savedCandidateKey(candidate),
    });
  }

  function handleDraftFocus() {
    startTextFlowIfNeeded(draft.trim());
  }

  function handleDraftChange(nextDraft: string) {
    setDraft(nextDraft);
    const flow = startTextFlowIfNeeded(nextDraft.trim());
    if (flow) {
      flow.editedBeforeSubmit = true;
    }
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey && !e.nativeEvent.isComposing) {
      e.preventDefault();
      handleSubmit();
    }
  }

  // #428: collapse when textarea loses focus with no content
  function handleDraftBlur() {
    if (!draft.trim() && !busy) {
      setTextOpen(false);
    }
  }

  const trimmed = draft.trim();
  const draftLabel = trimmed.length <= 18 ? trimmed : trimmed.slice(0, 18) + "...";

  return (
    <>
      {/* #426: section wrapper; hidden when no candidates */}
      {candidates.length > 0 && (
        <section aria-label="候補" className="candidate-section">
          <div className="quicklog-intro">
            候補タグをタップするとそのまま保存されます。自由入力は下の欄から追加できます。
          </div>
          <div className="candidates">
            {candidates.map((c) => (
              <button
                key={candidateRenderKey(c)}
                type="button"
                className={`candidate-tag${savedTagKey === savedCandidateKey(c) ? " saved" : ""}`}
                disabled={busy}
                onClick={() => void handleCandidateTap(c)}
              >
                {c.text}
              </button>
            ))}
          </div>
        </section>
      )}
      <div className="log-form">
        {/* #428: on-demand text input */}
        {!textOpen ? (
          <button type="button" className="open-text-btn" onClick={() => setTextOpen(true)}>
            + テキスト入力
          </button>
        ) : (
          <>
            <textarea
              ref={textRef}
              className="log-text"
              value={draft}
              onChange={(e) => handleDraftChange(e.target.value)}
              onKeyDown={handleKeyDown}
              onFocus={handleDraftFocus}
              onBlur={handleDraftBlur}
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
          </>
        )}
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
