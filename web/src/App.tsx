import { useEffect, useMemo, useRef, useState } from "react";
import "./index.css";

type AppConfig = {
  folder_name?: string;
  element_name?: string;
  element_path?: string;
  local_path?: string;
  remote_path?: string;
  watermark_path?: string;
};

type LogLine = { ts: number; text: string };

async function apiGet<T>(path: string): Promise<T> {
  const res = await fetch(path);
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return (await res.json()) as T;
}

async function apiPost<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(path, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const msg = await res.text().catch(() => "");
    throw new Error(msg || `${res.status} ${res.statusText}`);
  }
  return (await res.json()) as T;
}

export default function App() {
  const [cfg, setCfg] = useState<AppConfig>({});
  const [saveStatus, setSaveStatus] = useState<string>("");
  const [busy, setBusy] = useState(false);
  const [logs, setLogs] = useState<LogLine[]>([]);
  const logEndRef = useRef<HTMLDivElement | null>(null);

  const canRunStep8 = Boolean(cfg.folder_name && cfg.local_path);
  const canRunStep14 = Boolean(
    cfg.folder_name && cfg.local_path && cfg.remote_path && cfg.element_name && cfg.element_path,
  );

  useEffect(() => {
    let cancelled = false;
    apiGet<AppConfig>("/api/config")
      .then((c) => {
        if (cancelled) return;
        setCfg(c || {});
      })
      .catch(() => {
        // ignore
      });
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    const es = new EventSource("/logs");
    es.addEventListener("log", (ev) => {
      const e = ev as MessageEvent;
      const text = String(e.data ?? "");
      setLogs((prev) => {
        const next = prev.length > 2000 ? prev.slice(prev.length - 1500) : prev;
        return next.concat({ ts: Date.now(), text });
      });
    });
    es.addEventListener("status", (ev) => {
      const e = ev as MessageEvent;
      const text = String(e.data ?? "");
      setLogs((prev) => prev.concat({ ts: Date.now(), text: `status: ${text}` }));
    });
    es.onerror = () => {
      // Browser will retry automatically.
    };
    return () => {
      es.close();
    };
  }, []);

  useEffect(() => {
    logEndRef.current?.scrollIntoView({ block: "end" });
  }, [logs.length]);

  async function saveConfig() {
    setSaveStatus("saving...");
    try {
      await apiPost<{ ok: boolean }>("/api/config", cfg);
      setSaveStatus("saved");
      window.setTimeout(() => setSaveStatus(""), 1200);
    } catch (e) {
      setSaveStatus(`save failed: ${(e as Error).message}`);
    }
  }

  async function runStep8() {
    if (!canRunStep8) return;
    setBusy(true);
    try {
      await apiPost<{ ok: boolean }>("/api/step/8", {
        folder_name: cfg.folder_name,
        local_path: cfg.local_path,
      });
    } catch (e) {
      setLogs((prev) => prev.concat({ ts: Date.now(), text: `error: ${(e as Error).message}` }));
    } finally {
      setBusy(false);
    }
  }

  async function runStep14() {
    if (!canRunStep14) return;
    setBusy(true);
    try {
      await apiPost<{ ok: boolean }>("/api/step/14", {
        folder_name: cfg.folder_name,
        local_path: cfg.local_path,
        remote_path: cfg.remote_path,
        element_name: cfg.element_name,
        element_path: cfg.element_path,
      });
    } catch (e) {
      setLogs((prev) => prev.concat({ ts: Date.now(), text: `error: ${(e as Error).message}` }));
    } finally {
      setBusy(false);
    }
  }

  const header = useMemo(() => {
    const name = (cfg.folder_name || "").trim();
    if (!name) return "DDCM Workflow";
    return `DDCM Workflow: ${name}`;
  }, [cfg.folder_name]);

  return (
    <div className="page">
      <header className="topbar">
        <div className="topbarTitle">{header}</div>
        <div className="topbarActions">
          <button className="btn" onClick={saveConfig} disabled={busy}>
            Save config
          </button>
          {saveStatus ? <div className="muted">{saveStatus}</div> : null}
        </div>
      </header>

      <main className="grid">
        <section className="card">
          <div className="cardTitle">Config</div>
          <div className="form">
            <label>
              <span>Folder Name</span>
              <input
                value={cfg.folder_name || ""}
                onChange={(e) => setCfg((p) => ({ ...p, folder_name: e.target.value }))}
                placeholder='e.g. "33 - Abyssinian in Songkran"'
              />
            </label>
            <label>
              <span>Local Path</span>
              <input
                value={cfg.local_path || ""}
                onChange={(e) => setCfg((p) => ({ ...p, local_path: e.target.value }))}
                placeholder="/Users/.../Documents/DDCM"
              />
            </label>
            <label>
              <span>Remote Path</span>
              <input
                value={cfg.remote_path || ""}
                onChange={(e) => setCfg((p) => ({ ...p, remote_path: e.target.value }))}
                placeholder="/Users/.../GoogleDrive/..."
              />
            </label>
            <label>
              <span>Element Name</span>
              <input
                value={cfg.element_name || ""}
                onChange={(e) => setCfg((p) => ({ ...p, element_name: e.target.value }))}
                placeholder="Songkran"
              />
            </label>
            <label>
              <span>Element Path</span>
              <input
                value={cfg.element_path || ""}
                onChange={(e) => setCfg((p) => ({ ...p, element_path: e.target.value }))}
                placeholder="/Users/.../Elements"
              />
            </label>
          </div>
        </section>

        <section className="card">
          <div className="cardTitle">Actions</div>
          <div className="actions">
            <button className="btn primary" onClick={runStep8} disabled={!canRunStep8 || busy}>
              Step 8: Downloads/images to Local
            </button>
            <button className="btn primary" onClick={runStep14} disabled={!canRunStep14 || busy}>
              Step 14: Local to Remote
            </button>
            <div className="muted">
              Logs stream below. Keep Chrome debug profile running on port 9222.
            </div>
          </div>
        </section>

        <section className="card logs">
          <div className="cardTitle">Realtime Logs</div>
          <div className="logPane">
            {logs.map((l, idx) => (
              <div className="logLine" key={idx}>
                {l.text}
              </div>
            ))}
            <div ref={logEndRef} />
          </div>
        </section>
      </main>
    </div>
  );
}
