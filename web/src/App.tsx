import { useEffect, useMemo, useRef, useState } from "react";
import "./index.css";

type AppConfig = {
  folder_name?: string;
  element_name?: string;
  element_path?: string;
  local_path?: string;
  remote_path?: string;
  watermark_path?: string;
  first_preview_watermark_path?: string;
  single_count?: string;
  companion_count?: string;
  elements_count?: string;
  png_pages?: string;
  jpg_pages?: string;
  pdf_pages?: string;
  primary_color?: string;
  secondary_color?: string;
  focus_browser_tabs?: boolean;
  canva_design_url_part?: string;
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
  const [busy, setBusy] = useState(false);
  const busyTimeoutRef = useRef<number | null>(null);
  const [logs, setLogs] = useState<LogLine[]>([]);
  const logEndRef = useRef<HTMLDivElement | null>(null);

  const canRunStep8 = Boolean(cfg.folder_name && cfg.local_path);
  const canRunStep2 = Boolean(cfg.folder_name && cfg.local_path && cfg.remote_path);
  const canRunStep9 = Boolean(cfg.element_name && cfg.element_path);
  const canRunStep10 = Boolean(cfg.folder_name && cfg.local_path);
  const canRunStep13 = Boolean(cfg.folder_name && cfg.local_path);
  const canRunStep15 = Boolean(cfg.primary_color && cfg.secondary_color);
  const canRunStep14 = Boolean(
    cfg.folder_name && cfg.local_path && cfg.remote_path && cfg.element_name && cfg.element_path,
  );
  const canRunStep14NoElements = Boolean(cfg.folder_name && cfg.local_path && cfg.remote_path);

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

  function beginBusy() {
    setBusy(true);
    if (busyTimeoutRef.current) window.clearTimeout(busyTimeoutRef.current);
    // Safety: never leave the UI disabled forever if a request hangs.
    busyTimeoutRef.current = window.setTimeout(() => setBusy(false), 5 * 60 * 1000);
  }

  function endBusy() {
    if (busyTimeoutRef.current) {
      window.clearTimeout(busyTimeoutRef.current);
      busyTimeoutRef.current = null;
    }
    setBusy(false);
  }

  async function setDefault(key: keyof AppConfig, value: unknown) {
    beginBusy();
    try {
      await apiPost<{ ok: boolean }>("/api/config/set-default", { key, value });
    } catch (e) {
      setLogs((prev) => prev.concat({ ts: Date.now(), text: `error: ${(e as Error).message}` }));
    } finally {
      endBusy();
    }
  }

  async function runStep8() {
    if (!canRunStep8) return;
    beginBusy();
    try {
      await apiPost<{ ok: boolean }>("/api/step/8", {
        folder_name: cfg.folder_name,
        local_path: cfg.local_path,
      });
    } catch (e) {
      setLogs((prev) => prev.concat({ ts: Date.now(), text: `error: ${(e as Error).message}` }));
    } finally {
      endBusy();
    }
  }

  async function runStep2() {
    if (!canRunStep2) return;
    beginBusy();
    try {
      await apiPost<{ ok: boolean }>("/api/step/2", {
        folder_name: cfg.folder_name,
        local_path: cfg.local_path,
        remote_path: cfg.remote_path,
      });
    } catch (e) {
      setLogs((prev) => prev.concat({ ts: Date.now(), text: `error: ${(e as Error).message}` }));
    } finally {
      endBusy();
    }
  }

  async function runStep6() {
    beginBusy();
    try {
      await apiPost<{ ok: boolean }>("/api/step/6", {});
    } catch (e) {
      setLogs((prev) => prev.concat({ ts: Date.now(), text: `error: ${(e as Error).message}` }));
    } finally {
      endBusy();
    }
  }

  async function runStep12() {
    beginBusy();
    try {
      await apiPost<{ ok: boolean }>("/api/step/12", {});
    } catch (e) {
      setLogs((prev) => prev.concat({ ts: Date.now(), text: `error: ${(e as Error).message}` }));
    } finally {
      endBusy();
    }
  }

  async function runStep13() {
    if (!canRunStep13) return;
    beginBusy();
    try {
      await apiPost<{ ok: boolean }>("/api/step/13", {
        folder_name: cfg.folder_name,
        local_path: cfg.local_path,
      });
    } catch (e) {
      setLogs((prev) => prev.concat({ ts: Date.now(), text: `error: ${(e as Error).message}` }));
    } finally {
      endBusy();
    }
  }

  async function runStep14() {
    if (!canRunStep14) return;
    beginBusy();
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
      endBusy();
    }
  }

  async function runStep14NoElements() {
    if (!(cfg.folder_name && cfg.local_path && cfg.remote_path)) return;
    beginBusy();
    try {
      await apiPost<{ ok: boolean }>("/api/step/14-no-elements", {
        folder_name: cfg.folder_name,
        local_path: cfg.local_path,
        remote_path: cfg.remote_path,
      });
    } catch (e) {
      setLogs((prev) => prev.concat({ ts: Date.now(), text: `error: ${(e as Error).message}` }));
    } finally {
      endBusy();
    }
  }

  async function runStep3(mode: "single" | "companion" | "elements") {
    beginBusy();
    try {
      await apiPost<{ ok: boolean }>("/api/step/3", {
        mode,
        single_count: cfg.single_count ? Number(cfg.single_count) : undefined,
        companion_count: cfg.companion_count ? Number(cfg.companion_count) : undefined,
        elements_count: cfg.elements_count ? Number(cfg.elements_count) : undefined,
      });
    } catch (e) {
      setLogs((prev) => prev.concat({ ts: Date.now(), text: `error: ${(e as Error).message}` }));
    } finally {
      endBusy();
    }
  }

  async function runStep4() {
    beginBusy();
    try {
      await apiPost<{ ok: boolean }>("/api/step/4", {});
    } catch (e) {
      setLogs((prev) => prev.concat({ ts: Date.now(), text: `error: ${(e as Error).message}` }));
    } finally {
      endBusy();
    }
  }

  async function runStep5() {
    beginBusy();
    try {
      await apiPost<{ ok: boolean }>("/api/step/5", {});
    } catch (e) {
      setLogs((prev) => prev.concat({ ts: Date.now(), text: `error: ${(e as Error).message}` }));
    } finally {
      endBusy();
    }
  }

  async function runStep7() {
    beginBusy();
    try {
      await apiPost<{ ok: boolean }>("/api/step/7", {});
    } catch (e) {
      setLogs((prev) => prev.concat({ ts: Date.now(), text: `error: ${(e as Error).message}` }));
    } finally {
      endBusy();
    }
  }

  async function runStep9() {
    if (!canRunStep9) return;
    beginBusy();
    try {
      await apiPost<{ ok: boolean }>("/api/step/9", {
        element_name: cfg.element_name,
        element_path: cfg.element_path,
      });
    } catch (e) {
      setLogs((prev) => prev.concat({ ts: Date.now(), text: `error: ${(e as Error).message}` }));
    } finally {
      endBusy();
    }
  }

  async function runStep10() {
    if (!canRunStep10) return;
    beginBusy();
    try {
      await apiPost<{ ok: boolean }>("/api/step/10", {
        folder_name: cfg.folder_name,
        local_path: cfg.local_path,
        watermark_path: cfg.watermark_path,
        first_preview_watermark_path: cfg.first_preview_watermark_path,
        element_name: cfg.element_name,
        element_path: cfg.element_path,
      });
    } catch (e) {
      setLogs((prev) => prev.concat({ ts: Date.now(), text: `error: ${(e as Error).message}` }));
    } finally {
      endBusy();
    }
  }

  async function runStep11() {
    beginBusy();
    try {
      await apiPost<{ ok: boolean }>("/api/step/11", {
        mode: "all",
        png_pages: cfg.png_pages,
        jpg_pages: cfg.jpg_pages,
        pdf_pages: cfg.pdf_pages,
        focus_tab: Boolean(cfg.focus_browser_tabs),
        canva_url_part: (cfg.canva_design_url_part || "").trim() || undefined,
      });
    } catch (e) {
      setLogs((prev) => prev.concat({ ts: Date.now(), text: `error: ${(e as Error).message}` }));
    } finally {
      endBusy();
    }
  }

  async function runStep11Mode(mode: "png" | "jpg" | "pdf") {
    beginBusy();
    try {
      await apiPost<{ ok: boolean }>("/api/step/11", {
        mode,
        png_pages: cfg.png_pages,
        jpg_pages: cfg.jpg_pages,
        pdf_pages: cfg.pdf_pages,
        focus_tab: Boolean(cfg.focus_browser_tabs),
        canva_url_part: (cfg.canva_design_url_part || "").trim() || undefined,
      });
    } catch (e) {
      setLogs((prev) => prev.concat({ ts: Date.now(), text: `error: ${(e as Error).message}` }));
    } finally {
      endBusy();
    }
  }

  async function runStep15() {
    if (!canRunStep15) return;
    beginBusy();
    try {
      await apiPost<{ ok: boolean }>("/api/step/15", {
        primary_color: cfg.primary_color,
        secondary_color: cfg.secondary_color,
      });
    } catch (e) {
      setLogs((prev) => prev.concat({ ts: Date.now(), text: `error: ${(e as Error).message}` }));
    } finally {
      endBusy();
    }
  }

  const header = useMemo(() => {
    const name = (cfg.folder_name || "").trim();
    if (!name) return "DDCM Workflow";
    return `DDCM Workflow: ${name}`;
  }, [cfg.folder_name]);

  const steps = [
        { n: 1, title: "Basic Info", desc: "ตั้งค่าโฟลเดอร์/พาธที่ใช้ในงาน", action: null },
        {
          n: 2,
          title: "Create Folders",
          desc: "สร้างโฟลเดอร์งานที่ Local และ Remote",
          action: {
            label: "Create Folders",
            onClick: runStep2,
            enabled: Boolean(cfg.folder_name && cfg.local_path && cfg.remote_path),
          },
        },
        { n: 3, title: "Gemini Gen", desc: "ดึงข้อมูลจาก DDCM ไปสร้างภาพใน Gemini", action: null },
        { n: 4, title: "Download Images", desc: "โหลดรูปภาพทั้งหมดไปไว้ที่ Downloads/images", action: { label: "Download images", onClick: runStep4, enabled: true } },
        { n: 5, title: "Remove Background", desc: "ตัดพื้นหลังใน Photoshop", action: { label: "Done", onClick: runStep5, enabled: true } },
        { n: 6, title: "Classify Resolution", desc: "แยกกลุ่มตามขนาดภาพ", action: { label: "Classify resolution", onClick: runStep6, enabled: true } },
        { n: 7, title: "Upscale", desc: "ขยายภาพด้วย Upscayl", action: { label: "Done", onClick: runStep7, enabled: true } },
        {
          n: 8,
          title: "Downloads/images to Local",
          desc: "ย้ายรูปในโฟลเดอร์ images ไปที่ Local/4000x4000 พร้อม rename เริ่ม (1)",
          action: { label: "Downloads/images to Local", onClick: runStep8, enabled: canRunStep8 },
        },
        { n: 9, title: "Element to Local", desc: "ย้าย Elements เข้าคลัง", action: { label: "Element to Local", onClick: runStep9, enabled: canRunStep9 } },
        { n: 10, title: "Create Preview Sheet", desc: "สร้าง Sticker Set และใส่ watermark ลง Preview", action: { label: "Create Preview Sheet", onClick: runStep10, enabled: canRunStep10 } },
        { n: 11, title: "Canva Export", desc: "Export PNG/JPG/PDF", action: null },
        { n: 12, title: "Unzip", desc: "แตกไฟล์ zip ที่ดาวน์โหลด", action: { label: "Unzip Downloads", onClick: runStep12, enabled: true } },
        {
          n: 13,
          title: "Download to Local",
          desc: "รวบรวมไฟล์เข้าโฟลเดอร์งาน",
          action: { label: "Download to Local", onClick: runStep13, enabled: Boolean(cfg.folder_name && cfg.local_path) },
        },
        {
          n: 14,
          title: "Local to Remote",
          desc: "คัดลอกไป Remote และ rename เริ่ม (1) (Elements rename เป็น element (n))",
          action: { label: "Local to Remote", onClick: runStep14, enabled: canRunStep14 },
        },
        { n: 15, title: "Etsy", desc: "สร้าง Listing บน Etsy", action: { label: "Create Listing", onClick: runStep15, enabled: canRunStep15 } },
      ] as const;

  return (
    <div className="page">
      <header className="topbar">
        <div className="topbarTitle">{header}</div>
      </header>

      <main className="grid">
        <section className="card leftSticky">
          <div className="cardTitle">1. Basic Info</div>
          <div className="muted">ตั้งค่าโฟลเดอร์/พาธที่ใช้ในงาน</div>
          <div className="form" style={{ marginTop: 12 }}>
            <label>
              <span>Folder Name</span>
              <div style={{ display: "flex", gap: 10 }}>
                <input
                  value={cfg.folder_name || ""}
                  onChange={(e) => setCfg((p) => ({ ...p, folder_name: e.target.value }))}
                  placeholder='e.g. "33 - Abyssinian in Songkran"'
                />
                <button className="btn" onClick={() => setDefault("folder_name", (cfg.folder_name || "").trim())} disabled={busy}>
                  Set Default
                </button>
              </div>
            </label>
            <label>
              <span>Element Name</span>
              <div style={{ display: "flex", gap: 10 }}>
                <input
                  value={cfg.element_name || ""}
                  onChange={(e) => setCfg((p) => ({ ...p, element_name: e.target.value }))}
                  placeholder="Songkran"
                />
                <button className="btn" onClick={() => setDefault("element_name", (cfg.element_name || "").trim())} disabled={busy}>
                  Set Default
                </button>
              </div>
            </label>
            <label>
              <span>Element Path</span>
              <div style={{ display: "flex", gap: 10 }}>
                <input
                  value={cfg.element_path || ""}
                  onChange={(e) => setCfg((p) => ({ ...p, element_path: e.target.value }))}
                  placeholder="/Users/.../Documents/DDCM/Elements"
                />
                <button className="btn" onClick={() => setDefault("element_path", (cfg.element_path || "").trim())} disabled={busy}>
                  Set Default
                </button>
              </div>
            </label>
            <label>
              <span>Local Path</span>
              <div style={{ display: "flex", gap: 10 }}>
                <input
                  value={cfg.local_path || ""}
                  onChange={(e) => setCfg((p) => ({ ...p, local_path: e.target.value }))}
                  placeholder="/Users/.../Documents/DDCM"
                />
                <button className="btn" onClick={() => setDefault("local_path", (cfg.local_path || "").trim())} disabled={busy}>
                  Set Default
                </button>
              </div>
            </label>
            <label>
              <span>Remote Path</span>
              <div style={{ display: "flex", gap: 10 }}>
                <input
                  value={cfg.remote_path || ""}
                  onChange={(e) => setCfg((p) => ({ ...p, remote_path: e.target.value }))}
                  placeholder="/Users/.../GoogleDrive/..."
                />
                <button className="btn" onClick={() => setDefault("remote_path", (cfg.remote_path || "").trim())} disabled={busy}>
                  Set Default
                </button>
              </div>
            </label>
            <label>
              <span>Watermark Path</span>
              <div style={{ display: "flex", gap: 10 }}>
                <input
                  value={cfg.watermark_path || ""}
                  onChange={(e) => setCfg((p) => ({ ...p, watermark_path: e.target.value }))}
                  placeholder="/Users/.../Documents/DDCM/Watermark.png"
                />
                <button className="btn" onClick={() => setDefault("watermark_path", (cfg.watermark_path || "").trim())} disabled={busy}>
                  Set Default
                </button>
              </div>
            </label>

            <label>
              <span>First Preview Watermark Path</span>
              <div style={{ display: "flex", gap: 10 }}>
                <input
                  value={cfg.first_preview_watermark_path || ""}
                  onChange={(e) => setCfg((p) => ({ ...p, first_preview_watermark_path: e.target.value }))}
                  placeholder="/Users/.../Documents/DDCM/Watermark_First.png"
                />
                <button
                  className="btn"
                  onClick={() =>
                    setDefault("first_preview_watermark_path", (cfg.first_preview_watermark_path || "").trim())
                  }
                  disabled={busy}
                >
                  Set Default
                </button>
              </div>
            </label>
          </div>
        </section>

        <section className="card">
          <div className="cardTitle">Steps (2-15)</div>
          <div className="actions">
            {steps.filter((s) => s.n !== 1).map((s) => (
              <div key={s.n} style={{ display: "grid", gap: 6, padding: "8px 0" }}>
                <div style={{ display: "flex", justifyContent: "space-between", gap: 10 }}>
                  <div style={{ fontWeight: 700 }}>{s.n}. {s.title}</div>
                  {s.n === 3 ? (
                    <div style={{ display: "flex", gap: 8, flexWrap: "wrap", justifyContent: "flex-end" }}>
                      <button className="btn primary" onClick={() => runStep3("single")} disabled={busy}>
                        Gen Single
                      </button>
                      <button className="btn primary" onClick={() => runStep3("companion")} disabled={busy}>
                        Gen Companion
                      </button>
                      <button className="btn primary" onClick={() => runStep3("elements")} disabled={busy}>
                        Gen Elements
                      </button>
                    </div>
                  ) : s.action ? (
                    s.n === 14 ? (
                      <div style={{ display: "flex", gap: 8, flexWrap: "wrap", justifyContent: "flex-end" }}>
                        <button className="btn primary" onClick={s.action.onClick} disabled={!s.action.enabled || busy}>
                          {s.action.label}
                        </button>
                        <button className="btn primary" onClick={runStep14NoElements} disabled={!canRunStep14NoElements || busy}>
                          Local to Remote (No Elements)
                        </button>
                      </div>
                    ) : (
                      <button className="btn primary" onClick={s.action.onClick} disabled={!s.action.enabled || busy}>
                        {s.action.label}
                      </button>
                    )
                  ) : (
                    <div />
                  )}
                </div>
                <div className="muted">{s.desc}</div>

                {s.n === 3 ? (
                  <div className="form" style={{ marginTop: 8, gridTemplateColumns: "repeat(3, minmax(0, 1fr))" }}>
                    <label>
                      <span>Single Count</span>
                      <div style={{ display: "flex", gap: 10 }}>
                        <input value={cfg.single_count || ""} onChange={(e) => setCfg((p) => ({ ...p, single_count: e.target.value }))} placeholder="12" />
                        <button className="btn" onClick={() => setDefault("single_count", (cfg.single_count || "").trim())} disabled={busy}>
                          Set Default
                        </button>
                      </div>
                    </label>
                    <label>
                      <span>Companion Count</span>
                      <div style={{ display: "flex", gap: 10 }}>
                        <input value={cfg.companion_count || ""} onChange={(e) => setCfg((p) => ({ ...p, companion_count: e.target.value }))} placeholder="12" />
                        <button className="btn" onClick={() => setDefault("companion_count", (cfg.companion_count || "").trim())} disabled={busy}>
                          Set Default
                        </button>
                      </div>
                    </label>
                    <label>
                      <span>Elements Count</span>
                      <div style={{ display: "flex", gap: 10 }}>
                        <input value={cfg.elements_count || ""} onChange={(e) => setCfg((p) => ({ ...p, elements_count: e.target.value }))} placeholder="5" />
                        <button className="btn" onClick={() => setDefault("elements_count", (cfg.elements_count || "").trim())} disabled={busy}>
                          Set Default
                        </button>
                      </div>
                    </label>
                  </div>
                ) : null}

                {s.n === 11 ? (
                  <div className="form" style={{ marginTop: 8, gridTemplateColumns: "repeat(3, minmax(0, 1fr))" }}>
                    <label>
                      <span>PNG Pages</span>
                      <div style={{ display: "flex", gap: 10 }}>
                        <input value={cfg.png_pages || ""} onChange={(e) => setCfg((p) => ({ ...p, png_pages: e.target.value }))} placeholder="1-4" />
                        <button className="btn" onClick={() => setDefault("png_pages", (cfg.png_pages || "").trim())} disabled={busy}>
                          Set Default
                        </button>
                      </div>
                    </label>
                    <label>
                      <span>JPG Pages</span>
                      <div style={{ display: "flex", gap: 10 }}>
                        <input value={cfg.jpg_pages || ""} onChange={(e) => setCfg((p) => ({ ...p, jpg_pages: e.target.value }))} placeholder="6-9" />
                        <button className="btn" onClick={() => setDefault("jpg_pages", (cfg.jpg_pages || "").trim())} disabled={busy}>
                          Set Default
                        </button>
                      </div>
                    </label>
                    <label>
                      <span>PDF Pages</span>
                      <div style={{ display: "flex", gap: 10 }}>
                        <input value={cfg.pdf_pages || ""} onChange={(e) => setCfg((p) => ({ ...p, pdf_pages: e.target.value }))} placeholder="10" />
                        <button className="btn" onClick={() => setDefault("pdf_pages", (cfg.pdf_pages || "").trim())} disabled={busy}>
                          Set Default
                        </button>
                      </div>
                    </label>
                    <label style={{ gridColumn: "1 / -1" }}>
                      <span>Canva Design URL Part</span>
                      <div style={{ display: "flex", gap: 10 }}>
                        <input
                          value={cfg.canva_design_url_part || ""}
                          onChange={(e) => setCfg((p) => ({ ...p, canva_design_url_part: e.target.value }))}
                          placeholder="https://www.canva.com/design/"
                        />
                        <button className="btn" onClick={() => setDefault("canva_design_url_part", (cfg.canva_design_url_part || "").trim())} disabled={busy}>
                          Set Default
                        </button>
                      </div>
                    </label>
                    <label style={{ gridColumn: "1 / -1" }}>
                      <span>Focus Browser Tabs</span>
                      <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
                        <input
                          type="checkbox"
                          checked={Boolean(cfg.focus_browser_tabs)}
                          onChange={(e) => setCfg((p) => ({ ...p, focus_browser_tabs: e.target.checked }))}
                        />
                        <button className="btn" onClick={() => setDefault("focus_browser_tabs", Boolean(cfg.focus_browser_tabs))} disabled={busy}>
                          Set Default
                        </button>
                      </div>
                    </label>
                    <div style={{ gridColumn: "1 / -1", display: "flex", gap: 10, flexWrap: "wrap" }}>
                      <button className="btn primary" onClick={() => runStep11Mode("png")} disabled={busy}>
                        Export PNG
                      </button>
                      <button className="btn primary" onClick={() => runStep11Mode("jpg")} disabled={busy}>
                        Export JPG
                      </button>
                      <button className="btn primary" onClick={() => runStep11Mode("pdf")} disabled={busy}>
                        Export PDF
                      </button>
                      <button className="btn primary" onClick={runStep11} disabled={busy}>
                        Export ALL
                      </button>
                    </div>
                  </div>
                ) : null}

                {s.n === 15 ? (
                  <div className="form" style={{ marginTop: 8, gridTemplateColumns: "repeat(2, minmax(0, 1fr))" }}>
                    <label>
                      <span>Primary Color</span>
                      <div style={{ display: "flex", gap: 10 }}>
                        <input value={cfg.primary_color || ""} onChange={(e) => setCfg((p) => ({ ...p, primary_color: e.target.value }))} placeholder="Red" />
                        <button className="btn" onClick={() => setDefault("primary_color", (cfg.primary_color || "").trim())} disabled={busy}>
                          Set Default
                        </button>
                      </div>
                    </label>
                    <label>
                      <span>Secondary Color</span>
                      <div style={{ display: "flex", gap: 10 }}>
                        <input value={cfg.secondary_color || ""} onChange={(e) => setCfg((p) => ({ ...p, secondary_color: e.target.value }))} placeholder="Gray" />
                        <button className="btn" onClick={() => setDefault("secondary_color", (cfg.secondary_color || "").trim())} disabled={busy}>
                          Set Default
                        </button>
                      </div>
                    </label>
                  </div>
                ) : null}
              </div>
            ))}
            <div className="muted">Keep Chrome debug profile running on port 9222.</div>
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
