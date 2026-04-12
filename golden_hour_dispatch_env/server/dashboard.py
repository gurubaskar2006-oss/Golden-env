from __future__ import annotations


def render_dashboard() -> str:
    return """
    <html>
      <head>
        <title>Golden Hour Ambulance Dispatch Command Center</title>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <style>
          :root {
            --bg: #edf4ff;
            --bg-2: #fff8f3;
            --panel: rgba(255,255,255,0.82);
            --panel-soft: rgba(27,56,102,0.05);
            --ink: #14233b;
            --muted: #5f7395;
            --accent: #ea5b2c;
            --accent-2: #ff8f4d;
            --critical: #d93f3f;
            --urgent: #c78117;
            --safe: #16986b;
            --edge: rgba(86, 112, 154, 0.34);
            --shadow: 0 20px 48px rgba(28, 46, 86, 0.12);
            --radius: 22px;
          }

          * { box-sizing: border-box; }
          body {
            margin: 0;
            font-family: "Trebuchet MS", "Segoe UI", sans-serif;
            color: var(--ink);
            background:
              radial-gradient(circle at 16% 12%, rgba(255,124,84,0.20), transparent 18rem),
              radial-gradient(circle at 84% 0%, rgba(88,164,231,0.20), transparent 20rem),
              linear-gradient(180deg, #f6f9ff 0%, var(--bg) 48%, var(--bg-2) 100%);
          }

          .shell {
            max-width: 1560px;
            margin: 0 auto;
            padding: 20px;
          }

          .hero {
            display: grid;
            grid-template-columns: 1.25fr 0.75fr;
            gap: 16px;
            align-items: stretch;
            margin-bottom: 14px;
          }

          .hero-services {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 12px;
            margin-top: 18px;
          }

          .hero-service-card {
            padding: 14px 16px;
            border-radius: 16px;
            background: var(--panel-soft);
            border: 1px solid rgba(45,84,140,0.10);
          }

          .hero-service-card strong {
            display: block;
            font-size: 0.8rem;
            color: var(--muted);
            margin-bottom: 6px;
            text-transform: uppercase;
            letter-spacing: 0.06em;
          }

          .hero-service-value {
            font-size: 1.25rem;
            font-weight: 700;
          }

          .panel {
            background: var(--panel);
            backdrop-filter: blur(14px);
            border: 1px solid rgba(45,84,140,0.10);
            border-radius: var(--radius);
            box-shadow: var(--shadow);
          }

          .hero-copy {
            padding: 28px;
            position: relative;
            overflow: hidden;
          }

          .hero-copy::after {
            content: "";
            position: absolute;
            right: -60px;
            top: -60px;
            width: 220px;
            height: 220px;
            background: radial-gradient(circle, rgba(255,107,61,0.16), rgba(255,107,61,0));
          }

          h1 {
            margin: 0 0 10px 0;
            font-size: clamp(2rem, 4vw, 3.5rem);
            line-height: 0.95;
            color: var(--accent);
          }

          .subhead {
            margin: 0;
            max-width: 62ch;
            color: var(--muted);
            font-size: 1rem;
            line-height: 1.6;
          }

          .controls {
            padding: 24px;
            display: grid;
            gap: 14px;
          }

          .control-row {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            align-items: center;
          }

          .api-links {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 2px;
          }

          .link-button {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            padding: 10px 14px;
            border-radius: 14px;
            font: inherit;
            font-weight: 700;
            text-decoration: none;
            background: rgba(255,255,255,0.86);
            color: var(--ink);
            box-shadow: inset 0 0 0 1px rgba(45,84,140,0.10);
            transition: transform 120ms ease, box-shadow 120ms ease, opacity 120ms ease;
          }

          .link-button:hover {
            transform: translateY(-1px);
            box-shadow: 0 10px 24px rgba(33,68,127,0.12);
          }

          select, button {
            border-radius: 14px;
            border: none;
            font: inherit;
          }

          select {
            padding: 12px 14px;
            min-width: 240px;
            background: rgba(255,255,255,0.96);
            color: var(--ink);
            box-shadow: inset 0 0 0 1px rgba(45,84,140,0.16);
            color-scheme: light;
            font-weight: 600;
          }

          select:focus {
            outline: 2px solid rgba(88,164,231,0.28);
            outline-offset: 2px;
          }

          select option,
          select optgroup {
            background: #f9fbff;
            color: #14233b;
          }

          button {
            padding: 12px 16px;
            cursor: pointer;
            transition: transform 120ms ease, box-shadow 120ms ease, opacity 120ms ease;
          }

          button:hover:not(:disabled) {
            transform: translateY(-1px);
            box-shadow: 0 10px 24px rgba(234,91,44,0.18);
          }

          button:disabled { opacity: 0.55; cursor: wait; }

          .primary { background: linear-gradient(135deg, var(--accent), #cf4c1e); color: white; }
          .secondary { background: rgba(255,255,255,0.86); color: var(--accent); box-shadow: inset 0 0 0 1px rgba(234,91,44,0.16); }
          .ghost { background: rgba(255,255,255,0.86); color: var(--ink); }

          .status-pill {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 8px 12px;
            border-radius: 999px;
            background: rgba(82,214,163,0.12);
            color: var(--safe);
            font-weight: 700;
          }

          .ticker {
            margin-bottom: 14px;
            padding: 12px 16px;
            overflow: hidden;
          }

          .ticker-track {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
          }

          .ticker-chip {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 8px 12px;
            border-radius: 999px;
            background: rgba(255,255,255,0.74);
            border: 1px solid rgba(45,84,140,0.10);
            font-size: 0.84rem;
            color: var(--muted);
          }

          .wall {
            display: grid;
            grid-template-columns: minmax(0, 1fr) 380px;
            gap: 16px;
            align-items: start;
          }

          .main-wall {
            display: grid;
            gap: 16px;
            min-width: 0;
          }

          .main-grid {
            display: grid;
            grid-template-columns: 320px minmax(0, 1fr);
            gap: 16px;
            align-items: start;
            min-width: 0;
          }

          .center-stage {
            display: grid;
            gap: 16px;
            min-width: 0;
          }

          .map-panel {
            padding: 18px;
          }

          .map-frame {
            position: relative;
            min-height: 560px;
            border-radius: 18px;
            overflow: hidden;
            background:
              radial-gradient(circle at 16% 14%, rgba(255,145,92,0.18), transparent 18rem),
              radial-gradient(circle at 84% 16%, rgba(116,188,244,0.18), transparent 14rem),
              linear-gradient(180deg, rgba(255,251,247,0.99) 0%, rgba(245,249,255,0.99) 48%, rgba(233,241,253,0.99) 100%);
            border: 1px solid rgba(45,84,140,0.14);
          }

          .coast-label {
            position: absolute;
            right: 20px;
            bottom: 14px;
            z-index: 4;
            color: rgba(33,102,189,0.82);
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
          }

          .map-overlay {
            position: absolute;
            z-index: 4;
            backdrop-filter: blur(10px);
            background: rgba(255,255,255,0.90);
            border: 1px solid rgba(45,84,140,0.14);
            border-radius: 16px;
            box-shadow: 0 14px 28px rgba(34, 65, 120, 0.10);
          }

          .map-feed {
            left: 16px;
            top: 16px;
            padding: 12px 14px;
            min-width: 230px;
          }

          .map-legend {
            right: 16px;
            top: 16px;
            padding: 12px 14px;
            min-width: 220px;
          }

          .legend-row {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-top: 8px;
            color: #486280;
            font-size: 0.8rem;
          }

          .legend-swatch {
            width: 12px;
            height: 12px;
            border-radius: 999px;
            flex: 0 0 auto;
          }

          svg {
            width: 100%;
            height: 560px;
            display: block;
            position: relative;
            z-index: 2;
          }

          .sidebar {
            display: grid;
            gap: 16px;
            align-content: start;
          }

          .left-sidebar,
          .right-sidebar {
            min-width: 0;
          }

          .right-sidebar {
            position: sticky;
            top: 18px;
          }

          .support-grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 16px;
          }

          .operations-grid {
            display: grid;
            grid-template-columns: minmax(0, 1.08fr) minmax(320px, 0.92fr);
            gap: 16px;
          }

          .metrics {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 12px;
            padding: 18px;
          }

          .metric {
            padding: 14px;
            border-radius: 16px;
            background: rgba(255,255,255,0.72);
            border: 1px solid rgba(45,84,140,0.10);
            min-height: 102px;
          }

          .metric-label {
            font-size: 0.8rem;
            color: var(--muted);
            text-transform: uppercase;
            letter-spacing: 0.08em;
          }

          .metric-value {
            margin-top: 8px;
            font-size: 1.6rem;
            font-weight: 700;
          }

          .stack {
            padding: 16px;
            display: grid;
            gap: 10px;
            align-content: start;
          }

          .stack h2 {
            margin: 0;
            font-size: 1rem;
            color: var(--accent);
          }

          .section-kicker {
            font-size: 0.76rem;
            color: var(--muted);
            text-transform: uppercase;
            letter-spacing: 0.08em;
            font-weight: 700;
          }

          .candidate-list, .log-list, .hospital-board {
            display: grid;
            gap: 10px;
            max-height: 360px;
            overflow: auto;
          }

          .queue-list, .fleet-board {
            max-height: 360px;
            overflow: auto;
            padding-right: 4px;
          }

          .candidate-list, .log-list, .hospital-board, .queue-list, .fleet-board {
            scrollbar-width: thin;
            scrollbar-color: rgba(255,107,61,0.40) rgba(255,255,255,0.06);
          }

          .intel-list {
            display: grid;
            gap: 10px;
          }

          .intel-card {
            padding: 12px 14px;
            border-radius: 14px;
            background: rgba(255,255,255,0.72);
            border: 1px solid rgba(45,84,140,0.10);
          }

          .intel-card strong {
            display: block;
            font-size: 0.82rem;
            color: var(--muted);
            margin-bottom: 6px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
          }

          .card {
            padding: 14px;
            border-radius: 16px;
            background: rgba(255,255,255,0.72);
            border: 1px solid rgba(45,84,140,0.10);
          }

          .service-board, .queue-list, .fleet-board {
            display: grid;
            gap: 10px;
          }

          .service-card {
            padding: 14px;
            border-radius: 16px;
            background: rgba(255,255,255,0.72);
            border: 1px solid rgba(45,84,140,0.10);
          }

          .fleet-card {
            padding: 14px;
            border-radius: 16px;
            background: rgba(255,255,255,0.72);
            border: 1px solid rgba(45,84,140,0.10);
            cursor: pointer;
            transition: transform 120ms ease, border-color 120ms ease, box-shadow 120ms ease;
          }

          .fleet-card:hover {
            transform: translateY(-1px);
            border-color: rgba(234,91,44,0.20);
            box-shadow: 0 14px 28px rgba(41, 74, 134, 0.12);
          }

          .fleet-card.is-selected {
            border-color: rgba(234,91,44,0.28);
            box-shadow: inset 0 0 0 1px rgba(234,91,44,0.14);
          }

          .fleet-head {
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 12px;
          }

          .fleet-name {
            font-weight: 800;
            line-height: 1.2;
          }

          .fleet-subline {
            margin-top: 6px;
            color: var(--muted);
            font-size: 0.88rem;
            line-height: 1.45;
          }

          .fleet-grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 10px;
            margin-top: 12px;
          }

          .fleet-stat {
            padding: 10px 12px;
            border-radius: 12px;
            background: rgba(243,247,255,0.92);
            border: 1px solid rgba(45,84,140,0.10);
          }

          .fleet-stat strong {
            display: block;
            font-size: 0.78rem;
            color: var(--muted);
            margin-bottom: 4px;
          }

          .fleet-footnote {
            margin-top: 10px;
            padding: 10px 12px;
            border-radius: 12px;
            background: rgba(243,247,255,0.88);
            border: 1px dashed rgba(45,84,140,0.16);
            color: var(--muted);
            font-size: 0.86rem;
            line-height: 1.45;
          }

          .service-title {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
            font-weight: 700;
          }

          .service-chip {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 5px 10px;
            border-radius: 999px;
            font-size: 0.74rem;
            font-weight: 700;
          }

          .service-emergency {
            background: rgba(198,40,40,0.12);
            color: var(--critical);
          }

          .service-maternal {
            background: rgba(140,90,230,0.16);
            color: #b896ff;
          }

          .service-grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 10px;
            margin-top: 12px;
          }

          .service-stat {
            padding: 10px 12px;
            border-radius: 12px;
            background: rgba(243,247,255,0.92);
            border: 1px solid rgba(45,84,140,0.10);
          }

          .service-stat strong {
            display: block;
            font-size: 0.78rem;
            color: var(--muted);
            margin-bottom: 4px;
          }

          .queue-card {
            padding: 12px 14px;
            border-radius: 14px;
            background: rgba(255,255,255,0.72);
            border: 1px solid rgba(45,84,140,0.10);
          }

          .focus-card {
            padding: 14px;
            border-radius: 16px;
            background: rgba(255,255,255,0.72);
            border: 1px solid rgba(45,84,140,0.10);
          }

          .hospital-card {
            padding: 14px;
            border-radius: 16px;
            background: rgba(255,255,255,0.72);
            border: 1px solid rgba(45,84,140,0.10);
          }

          .hospital-meta {
            margin-top: 8px;
            color: var(--muted);
            line-height: 1.5;
            font-size: 0.9rem;
          }

          .capacity-track {
            margin-top: 12px;
            width: 100%;
            height: 9px;
            border-radius: 999px;
            background: rgba(45,84,140,0.10);
            overflow: hidden;
          }

          .capacity-fill {
            height: 100%;
            border-radius: inherit;
          }

          .focus-grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 10px;
            margin-top: 12px;
          }

          .focus-stat {
            padding: 10px 12px;
            border-radius: 12px;
            background: rgba(243,247,255,0.92);
            border: 1px solid rgba(45,84,140,0.10);
          }

          .focus-stat strong {
            display: block;
            font-size: 0.78rem;
            color: var(--muted);
            margin-bottom: 4px;
          }

          .reward-bursts {
            position: absolute;
            inset: 0;
            pointer-events: none;
            z-index: 5;
          }

          .reward-burst {
            position: absolute;
            transform: translate(-50%, -50%);
            padding: 8px 10px;
            border-radius: 999px;
            font-size: 0.82rem;
            font-weight: 700;
            animation: reward-float 1.8s ease forwards;
            box-shadow: 0 14px 28px rgba(29, 29, 31, 0.18);
          }

          .reward-burst-positive {
            background: rgba(47,133,90,0.94);
            color: white;
          }

          .reward-burst-negative {
            background: rgba(198,40,40,0.94);
            color: white;
          }

          @keyframes reward-float {
            0% { opacity: 0; transform: translate(-50%, -10%); }
            15% { opacity: 1; transform: translate(-50%, -50%); }
            100% { opacity: 0; transform: translate(-50%, -150%); }
          }

          .candidate-head, .log-head {
            display: flex;
            justify-content: space-between;
            gap: 10px;
            align-items: baseline;
          }

          .candidate-title {
            font-weight: 700;
          }

          .badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 5px 10px;
            border-radius: 999px;
            font-size: 0.77rem;
            font-weight: 700;
          }

          .critical { background: rgba(198,40,40,0.12); color: var(--critical); }
          .urgent { background: rgba(255,180,84,0.16); color: var(--urgent); }
          .maternal { background: rgba(140,90,230,0.16); color: #b896ff; }
          .safe { background: rgba(47,133,90,0.12); color: var(--safe); }

          .reward-grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 10px;
          }

          .reward-item {
            padding: 10px 12px;
            border-radius: 14px;
            background: rgba(243,247,255,0.92);
            border: 1px solid rgba(45,84,140,0.10);
          }

          .reward-item strong {
            display: block;
            font-size: 0.8rem;
            color: var(--muted);
            margin-bottom: 4px;
          }

          .summary {
            padding: 14px 16px;
            line-height: 1.6;
          }

          .summary-head {
            display: flex;
            justify-content: space-between;
            gap: 16px;
            align-items: flex-start;
          }

          .summary-copy {
            min-width: 0;
          }

          .summary-title {
            display: block;
            font-size: 1.04rem;
            font-weight: 800;
            color: var(--ink);
          }

          .summary-chips {
            display: flex;
            flex-wrap: wrap;
            justify-content: flex-end;
            gap: 8px;
            max-width: 360px;
          }

          .summary-chip {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 7px 10px;
            border-radius: 999px;
            background: rgba(255,255,255,0.86);
            border: 1px solid rgba(45,84,140,0.10);
            font-size: 0.78rem;
            font-weight: 700;
            color: var(--muted);
          }

          .summary-note {
            margin-top: 10px;
            color: var(--muted);
            font-size: 0.92rem;
          }

          .map-node-label {
            font-size: 12px;
            fill: #61789a;
            font-weight: 800;
          }

          .map-chip {
            paint-order: stroke;
            stroke: rgba(255,255,255,0.98);
            stroke-width: 4.5px;
            stroke-linejoin: round;
          }

          .map-inline-label {
            font-size: 11px;
            font-weight: 700;
          }

          .empty {
            color: var(--muted);
            padding: 8px 0;
          }

          @media (max-width: 1280px) {
            .wall,
            .main-grid,
            .operations-grid,
            .support-grid {
              grid-template-columns: 1fr;
            }

            .right-sidebar {
              position: static;
            }
          }

          @media (max-width: 1100px) {
            .hero,
            .wall,
            .main-grid,
            .operations-grid {
              grid-template-columns: 1fr;
            }
          }
        </style>
      </head>
      <body>
        <div class="shell">
          <section class="hero">
            <div class="hero-copy panel">
              <div class="status-pill">Mission Control Live</div>
              <h1>Golden Hour Ambulance Dispatch Command Center</h1>
              <p class="subhead">
                Operate a Chennai control room for Tamil Nadu's 108 emergency and 102 mother-and-child ambulance services.
                You can dispatch manually or let the built-in policy coordinate the fleet in real time, always clearing active
                108 emergencies before maternal and newborn 102 cases when resources allow.
              </p>
              <div id="hero-services" class="hero-services"></div>
            </div>
            <div class="controls panel">
              <div>
                <div style="font-size:0.78rem; color:var(--muted); text-transform:uppercase; letter-spacing:0.08em; margin-bottom:8px;">Scenario</div>
                <div class="control-row">
                  <select id="task-select"></select>
                </div>
              </div>
              <div class="control-row">
                <button class="primary" id="reset-btn">Reset Scenario</button>
                <button class="secondary" id="auto-step-btn">Auto Dispatch Wave</button>
                <button class="secondary" id="auto-run-btn">Auto Run Shift</button>
              </div>
              <div class="api-links">
                <a class="link-button" href="/docs" target="_blank" rel="noreferrer">OpenEnv Docs</a>
                <a class="link-button" href="/schema" target="_blank" rel="noreferrer">Schema JSON</a>
                <a class="link-button" href="/state" target="_blank" rel="noreferrer">Live State</a>
              </div>
              <div id="ui-status" class="empty">Loading dashboard...</div>
            </div>
          </section>

          <section class="ticker panel">
            <div id="event-ticker" class="ticker-track"></div>
          </section>

          <section class="wall">
            <section class="main-wall">
              <section class="main-grid">
                <aside class="sidebar left-sidebar">
                  <section class="stack panel">
                    <h2>Service Split</h2>
                    <div id="service-board" class="service-board"></div>
                  </section>
                  <section class="stack panel">
                    <h2>Live Queue</h2>
                    <div id="queue-list" class="queue-list"></div>
                  </section>
                </aside>

                <section class="center-stage">
                  <div class="map-panel panel">
                    <div class="summary">
                      <div class="summary-head">
                        <div class="summary-copy">
                          <strong id="task-title" class="summary-title">Scenario loading...</strong>
                          <div id="task-objective" style="color:var(--muted); margin-top:6px;"></div>
                        </div>
                        <div id="map-summary-chips" class="summary-chips"></div>
                      </div>
                      <div id="map-summary-note" class="summary-note"></div>
                    </div>
                    <div class="map-frame">
                      <div id="map-feed" class="map-overlay map-feed"></div>
                      <div class="map-overlay map-legend">
                        <div style="font-size:0.76rem; font-weight:700; color:var(--accent);">Field Legend</div>
                        <div class="legend-row"><span class="legend-swatch" style="background:#b42318;"></span><span>108 emergency ambulance</span></div>
                        <div class="legend-row"><span class="legend-swatch" style="background:#8c5ae6;"></span><span>102 maternal/newborn ambulance</span></div>
                        <div class="legend-row"><span class="legend-swatch" style="background:#2563eb;"></span><span>Government and specialty hospitals</span></div>
                        <div class="legend-row"><span class="legend-swatch" style="background:#c62828;"></span><span>Active 108 incident</span></div>
                        <div class="legend-row"><span class="legend-swatch" style="background:#8c5ae6;"></span><span>Active 102 incident</span></div>
                      </div>
                      <div id="reward-bursts" class="reward-bursts"></div>
                      <div class="coast-label">Bay of Bengal</div>
                      <svg id="dispatch-map" viewBox="0 0 960 560" aria-label="Dispatch map"></svg>
                    </div>
                  </div>
                </section>
              </section>

              <section class="operations-grid">
                <section class="stack panel">
                  <h2>Fleet Board</h2>
                  <div id="fleet-board" class="fleet-board"></div>
                </section>
                <section class="stack panel">
                  <h2>Hospital Watch</h2>
                  <div id="hospital-board" class="hospital-board"></div>
                </section>
                <section class="stack panel">
                  <h2>Available Dispatches</h2>
                  <div id="candidate-list" class="candidate-list"></div>
                </section>
                <section class="stack panel">
                  <h2>Decision Log</h2>
                  <div id="log-list" class="log-list"></div>
                </section>
              </section>
            </section>

            <aside class="sidebar right-sidebar">
              <section class="metrics panel" id="metrics"></section>
              <section class="stack panel">
                <div class="section-kicker">AI Copilot</div>
                <h2>Decision Intelligence</h2>
                <div id="decision-intel" class="intel-list"></div>
              </section>
              <section class="stack panel">
                <h2>Unit Focus</h2>
                <div id="unit-focus"></div>
              </section>
              <section class="stack panel">
                <h2>Reward Breakdown</h2>
                <div id="reward-grid" class="reward-grid"></div>
              </section>
            </aside>
          </section>
        </div>

        <script>
          const state = {
            config: null,
            observation: null,
            envState: null,
            demoContext: null,
            busy: false,
            selectedAmbulance: null,
            rewardBursts: [],
          };

          const palette = {
            advanced: "#b42318",
            basic: "#ef6c2f",
            maternal: "#8c5ae6",
            hospital: "#2563eb",
            critical: "#c62828",
            urgent: "#f59e0b",
            maternalIncident: "#8c5ae6",
          };

          async function fetchJson(url, options = undefined) {
            const response = await fetch(url, options);
            if (!response.ok) {
              throw new Error(`Request failed: ${response.status}`);
            }
            return response.json();
          }

          function shortAmbulanceLabel(ambulance) {
            if (ambulance.support_level === "maternal") return "102";
            if (ambulance.support_level === "advanced") return "108";
            return "BLS";
          }

          function ambulanceFillForSupport(supportLevel) {
            return palette[supportLevel] || palette.basic;
          }

          function ambulanceIconMarkup({ ambulanceId = "", label = "", serviceLabel = "", x = 0, y = 0, fill = palette.advanced, selected = false, opacity = 0.92, showLabel = true }) {
            const halo = selected
              ? `<circle cx="0" cy="0" r="20" fill="${fill}" fill-opacity="0.14" stroke="#1d1d1f" stroke-opacity="0.12" stroke-width="2"></circle>`
              : "";
            const labelMarkup = showLabel
              ? `<text x="21" y="4" class="map-chip map-inline-label" fill="${fill}">${label}</text>`
              : "";
            return `
              <g class="ambulance-mark" data-ambulance-id="${ambulanceId}" transform="translate(${x} ${y})" style="cursor:pointer;">
                ${halo}
                <g opacity="${opacity}">
                  <rect x="-17" y="-9" width="24" height="14" rx="3.6" fill="${fill}" stroke="white" stroke-width="2"></rect>
                  <rect x="6" y="-6" width="10" height="11" rx="2.6" fill="${fill}" stroke="white" stroke-width="2"></rect>
                  <rect x="-12.5" y="-6.2" width="7.6" height="4.2" rx="1.2" fill="rgba(255,255,255,0.7)"></rect>
                  <rect x="8.2" y="-4.2" width="4.4" height="3.4" rx="0.8" fill="rgba(255,255,255,0.7)"></rect>
                  <rect x="-9.1" y="-2.2" width="7.2" height="4.4" rx="1" fill="white" opacity="0.95"></rect>
                  <rect x="-6.6" y="-4.6" width="2.2" height="9.2" rx="0.8" fill="white" opacity="0.95"></rect>
                  <circle cx="-9.5" cy="8" r="3.7" fill="#1d1d1f" stroke="white" stroke-width="1.5"></circle>
                  <circle cx="8.5" cy="8" r="3.7" fill="#1d1d1f" stroke="white" stroke-width="1.5"></circle>
                  <circle cx="-9.5" cy="8" r="1.25" fill="white" opacity="0.9"></circle>
                  <circle cx="8.5" cy="8" r="1.25" fill="white" opacity="0.9"></circle>
                  <text x="-1.5" y="1.5" text-anchor="middle" style="font-size:8px; font-weight:800; fill:#ffffff;">${serviceLabel}</text>
                </g>
                ${labelMarkup}
              </g>
            `;
          }

          function incidentStatusTone(status) {
            if (status === "resolved") return "safe";
            if (status === "missed") return "critical";
            return "urgent";
          }

          function hospitalNameById(hospitalId) {
            const hospital = (state.observation?.hospitals || []).find(item => item.hospital_id === hospitalId);
            return hospital ? hospital.label : hospitalId;
          }

          function ambulanceNameById(ambulanceId) {
            const ambulance = (state.observation?.ambulances || []).find(item => item.ambulance_id === ambulanceId);
            return ambulance ? ambulance.label : ambulanceId;
          }

          function incidentNameById(incidentId) {
            const incident = (state.observation?.incidents || []).find(item => item.incident_id === incidentId);
            return incident ? incident.label : incidentId;
          }

          function selectAmbulance(ambulanceId) {
            state.selectedAmbulance = ambulanceId;
            renderUnitFocus();
            renderMapFeed();
            renderMap();
          }

          function spawnRewardBurst(candidate, rewardValue) {
            if (!state.config || !candidate || !candidate.route_node_ids || !candidate.route_node_ids.length) return;
            const nodeId = candidate.route_node_ids[candidate.route_node_ids.length - 1];
            const node = state.config.graph.nodes.find(item => item.node_id === nodeId);
            if (!node) return;
            const burst = {
              id: `${Date.now()}-${Math.random().toString(36).slice(2)}`,
              x: node.x,
              y: node.y,
              label: `${rewardValue >= 0 ? "+" : ""}${Number(rewardValue || 0).toFixed(2)}`,
              tone: rewardValue >= 0 ? "positive" : "negative",
            };
            state.rewardBursts.push(burst);
            renderRewardBursts();
            setTimeout(() => {
              state.rewardBursts = state.rewardBursts.filter(item => item.id !== burst.id);
              renderRewardBursts();
            }, 1700);
          }

          function setBusy(flag, message = "") {
            state.busy = flag;
            document.getElementById("reset-btn").disabled = flag;
            document.getElementById("auto-step-btn").disabled = flag;
            document.getElementById("auto-run-btn").disabled = flag;
            if (message) document.getElementById("ui-status").textContent = message;
          }

          async function loadConfig() {
            state.config = await fetchJson("/demo/config");
            const select = document.getElementById("task-select");
            const groups = state.config.tasks.reduce((acc, task) => {
              const group = task.group || "Scenarios";
              if (!acc[group]) acc[group] = [];
              acc[group].push(task);
              return acc;
            }, {});

            select.innerHTML = Object.entries(groups).map(([group, tasks]) => `
              <optgroup label="${group}">
                ${tasks.map(task => `<option value="${task.task_id}">${task.title} (${task.difficulty})</option>`).join("")}
              </optgroup>
            `).join("");

            select.value = state.config.default_task_id || state.config.tasks[0]?.task_id || "";
          }

          async function resetScenario() {
            try {
              setBusy(true, "Resetting scenario...");
              const taskId = document.getElementById("task-select").value;
              const payload = JSON.stringify({ task_id: taskId });
              const data = await fetchJson("/demo/reset", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: payload,
              });
              state.observation = data.observation;
              state.envState = data.state;
              state.demoContext = data.demo_context || null;
              state.selectedAmbulance = null;
              state.rewardBursts = [];
              renderAll();
              setBusy(false, `Scenario ready: ${state.observation.task.title}`);
            } catch (error) {
              setBusy(false, `Reset failed: ${error.message}`);
            }
          }

          function buildActionFromCandidate(candidate, rationale) {
            return {
              ambulance_id: candidate.ambulance_id,
              incident_id: candidate.incident_id,
              hospital_id: candidate.hospital_id,
              use_green_corridor: candidate.use_green_corridor,
              rationale,
            };
          }

          async function manualDispatch(candidate) {
            try {
              setBusy(true, "Dispatching selected ambulance...");
              const request = fetchJson("/demo/step", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ action: buildActionFromCandidate(candidate, "Selected manually from dashboard.") }),
              });
              await animateTrace([{ minute: state.observation.current_time_minute, candidate }]);
              const data = await request;
              state.observation = data.observation;
              state.envState = data.state;
              state.demoContext = data.demo_context || state.demoContext;
              state.selectedAmbulance = candidate.ambulance_id;
              spawnRewardBurst(candidate, data.observation.reward || 0);
              renderAll();
              setBusy(false, data.done ? "Episode complete." : "Dispatch applied.");
            } catch (error) {
              setBusy(false, `Dispatch failed: ${error.message}`);
            }
          }

          async function autoStep() {
            try {
              setBusy(true, "Auto agent is dispatching all priority cases for the current minute...");
              const data = await fetchJson("/demo/auto-wave", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
              });
              await animateTrace(data.trace || []);
              state.observation = data.observation;
              state.envState = data.state;
              state.demoContext = data.demo_context || state.demoContext;
              const trace = data.trace || [];
              if (trace.length) {
                state.selectedAmbulance = trace[trace.length - 1].candidate?.ambulance_id || state.selectedAmbulance;
              }
              trace.forEach(entry => spawnRewardBurst(entry.candidate, entry.reward || 0));
              renderAll();
              const count = data.steps_taken || 0;
              setBusy(false, data.done ? `Episode complete. Auto wave dispatched ${count} ambulance(s).` : `Auto wave dispatched ${count} ambulance(s) this minute.`);
            } catch (error) {
              setBusy(false, `Auto wave failed: ${error.message}`);
            }
          }

          async function autoRun() {
            try {
              setBusy(true, "Auto agent is resolving the whole scenario...");
              const data = await fetchJson("/demo/auto-run", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
              });
              await animateTrace(data.trace || []);
              state.observation = data.observation;
              state.envState = data.state;
              state.demoContext = data.demo_context || state.demoContext;
              const trace = data.trace || [];
              if (trace.length) {
                state.selectedAmbulance = trace[trace.length - 1].candidate?.ambulance_id || state.selectedAmbulance;
              }
              trace.forEach(entry => spawnRewardBurst(entry.candidate, entry.reward || 0));
              renderAll();
              setBusy(false, `Auto run finished in ${data.steps_taken} step(s) with task score ${formatScore(state.envState.task_score || 0)}.`);
            } catch (error) {
              setBusy(false, `Auto run failed: ${error.message}`);
            }
          }

          function renderAll() {
            renderHeader();
            renderHeroServices();
            renderTicker();
            renderMetrics();
            renderServiceBoard();
            renderFleetBoard();
            renderQueueList();
            renderUnitFocus();
            renderHospitalBoard();
            renderRewardBreakdown();
            renderDecisionIntel();
            renderCandidates();
            renderLogs();
            renderMapFeed();
            renderMap();
            renderRewardBursts();
          }

          function formatScore(value) {
            const numeric = Number(value || 0);
            if (!Number.isFinite(numeric)) {
              return "0.01";
            }
            if (numeric >= 0.99) {
              return "0.99";
            }
            if (numeric <= 0.01) {
              return "0.01";
            }
            return numeric.toFixed(4);
          }

          function renderHeader() {
            if (!state.observation) return;
            const suffix = state.demoContext?.mode === "live_ops"
              ? ` | Live Mix -> ${state.demoContext.resolved_title}`
              : state.demoContext?.mode === "showcase"
                ? " | Showcase Scenario"
                : "";
            const incidents = state.observation.incidents || [];
            const active108 = incidents.filter(item => item.status === "pending" && item.triage === "108").length;
            const active102 = incidents.filter(item => item.status === "pending" && item.triage === "102").length;
            const difficultyLabel = state.observation.task.difficulty.charAt(0).toUpperCase() + state.observation.task.difficulty.slice(1);
            document.getElementById("task-title").textContent = `${state.observation.task.title} | ${difficultyLabel}${suffix}`;
            document.getElementById("task-objective").textContent = state.observation.task.objective;
            document.getElementById("map-summary-note").textContent = state.observation.summary || "Dispatch view ready.";
            document.getElementById("map-summary-chips").innerHTML = [
              `<div class="summary-chip"><span style="color:var(--accent);">Mode</span><span>${difficultyLabel}</span></div>`,
              `<div class="summary-chip"><span style="color:var(--critical);">108</span><span>${active108} active</span></div>`,
              `<div class="summary-chip"><span style="color:#b896ff;">102</span><span>${active102} active</span></div>`,
              `<div class="summary-chip"><span style="color:var(--safe);">Corridors</span><span>${state.observation.green_corridors_remaining} left</span></div>`,
            ].join("");
          }

          function renderHeroServices() {
            const container = document.getElementById("hero-services");
            if (!state.observation || !container) return;
            const incidents = state.observation.incidents || [];
            const active108 = incidents.filter(item => item.triage === "108" && item.status === "pending").length;
            const active102 = incidents.filter(item => item.triage === "102" && item.status === "pending").length;
            const cleared108 = incidents.filter(item => item.triage === "108" && item.status === "resolved").length;
            const cleared102 = incidents.filter(item => item.triage === "102" && item.status === "resolved").length;
            container.innerHTML = `
              <div class="hero-service-card">
                <strong>108 Emergency Service</strong>
                <div class="hero-service-value" style="color:var(--critical);">${active108} active | ${cleared108} cleared</div>
              </div>
              <div class="hero-service-card">
                <strong>102 Mother & Child Service</strong>
                <div class="hero-service-value" style="color:#b896ff;">${active102} active | ${cleared102} cleared</div>
              </div>
            `;
          }

          function renderTicker() {
            const container = document.getElementById("event-ticker");
            if (!state.observation || !container) return;
            const incidents = state.observation.incidents || [];
            const pending = incidents.filter(item => item.status === "pending");
            const chips = [];

            pending
              .slice()
              .sort((left, right) => left.triage === right.triage ? 0 : left.triage === "108" ? -1 : 1)
              .forEach(incident => {
                chips.push(`<div class="ticker-chip"><strong style="color:${incident.triage === "108" ? "var(--critical)" : "#b896ff"};">${incident.triage}</strong><span>${incident.label}</span></div>`);
              });

            if (state.demoContext?.mode === "live_ops") {
              chips.unshift(`<div class="ticker-chip"><strong style="color:var(--accent);">Live Ops</strong><span>${state.demoContext.resolved_title} | bonus x${Number(state.demoContext.bonus_multiplier || 1).toFixed(2)}</span></div>`);
            } else if (state.demoContext?.mode === "showcase") {
              chips.unshift(`<div class="ticker-chip"><strong style="color:var(--accent);">Showcase</strong><span>${state.demoContext.resolved_title} | demo-only scenario</span></div>`);
            }

            (state.observation.decision_log || []).slice().reverse().slice(0, 3).forEach(entry => {
              chips.push(`<div class="ticker-chip"><strong style="color:${entry.reward_delta >= 0 ? "var(--safe)" : "var(--critical)"};">Dispatch Update</strong><span>${entry.action_label}</span></div>`);
            });

            if (!chips.length) {
              chips.push('<div class="ticker-chip"><strong style="color:var(--safe);">Shift Stable</strong><span>No active calls waiting for dispatch.</span></div>');
            }

            container.innerHTML = chips.join("");
          }

          function renderMetrics() {
            if (!state.observation || !state.envState) return;
            const incidents = state.observation.incidents || [];
            const pending = incidents.filter(item => item.status === "pending").length;
            const missed = incidents.filter(item => item.status === "missed").length;
            const criticalPending = incidents.filter(item => item.status === "pending" && item.triage === "108").length;
            const criticalResolved = incidents.filter(item => item.status === "resolved" && item.triage === "108").length;
            const criticalMissed = incidents.filter(item => item.status === "missed" && item.triage === "108").length;
            const resolved = incidents.filter(item => item.status === "resolved").length;
            const ambulances = state.observation.ambulances || [];
            const busyUnits = ambulances.filter(item => item.mode === "busy").length;
            const fleetUtilization = ambulances.length ? (busyUnits / ambulances.length) * 100 : 0;
            const metrics = [
              ["Control Minute", `${state.observation.current_time_minute} min`],
              ["Episode Reward", Number(state.envState.cumulative_reward || 0).toFixed(2)],
              ["Lives Saved Proxy", Number(state.envState.weighted_survival_gained || 0).toFixed(2)],
              ["Resolved", `${resolved}/${incidents.length}`],
              ["Missed Cases", `${missed}`],
              ["Critical Cleared", `${criticalResolved}`],
              ["Critical Missed", `${criticalMissed}`],
              ["Critical Pending", `${criticalPending}`],
              ["Fleet Utilization", `${fleetUtilization.toFixed(0)}%`],
              ["Step Reward", Number(state.observation.reward || 0).toFixed(2)],
              ["Ops Score", formatScore(state.demoContext?.ops_score || state.envState.task_score || 0)],
              ["Task Score", formatScore(state.envState.task_score || 0)],
              ["Pending Cases", `${pending}`],
              ["Invalid Moves", `${state.envState.invalid_actions}`],
              ["Green Corridors", `${state.observation.green_corridors_remaining}`],
            ];
            document.getElementById("metrics").innerHTML = metrics.map(([label, value]) => `
              <div class="metric">
                <div class="metric-label">${label}</div>
                <div class="metric-value">${value}</div>
              </div>
            `).join("");
          }

          function renderServiceBoard() {
            const container = document.getElementById("service-board");
            if (!state.observation) return;
            const incidents = state.observation.incidents || [];
            const ambulances = state.observation.ambulances || [];
            const emergencyUnits = ambulances.filter(item => item.support_level === "advanced");
            const maternalUnits = ambulances.filter(item => item.support_level === "maternal");
            const emergencyPending = incidents.filter(item => item.status === "pending" && item.triage === "108").length;
            const emergencyResolved = incidents.filter(item => item.status === "resolved" && item.triage === "108").length;
            const maternalPending = incidents.filter(item => item.status === "pending" && item.triage === "102").length;
            const maternalResolved = incidents.filter(item => item.status === "resolved" && item.triage === "102").length;

            container.innerHTML = `
              <div class="service-card">
                <div class="service-title">
                  <span>108 Emergency Network</span>
                  <span class="service-chip service-emergency">ALS priority</span>
                </div>
                <div class="service-grid">
                  <div class="service-stat"><strong>Available units</strong>${emergencyUnits.filter(item => item.mode === "available").length}/${emergencyUnits.length}</div>
                  <div class="service-stat"><strong>Critical pending</strong>${emergencyPending}</div>
                  <div class="service-stat"><strong>Critical cleared</strong>${emergencyResolved}</div>
                  <div class="service-stat"><strong>Corridors left</strong>${state.observation.green_corridors_remaining}</div>
                </div>
              </div>
              <div class="service-card">
                <div class="service-title">
                  <span>102 Mother & Child</span>
                  <span class="service-chip service-maternal">Maternal/newborn</span>
                </div>
                <div class="service-grid">
                  <div class="service-stat"><strong>Available units</strong>${maternalUnits.filter(item => item.mode === "available").length}/${maternalUnits.length}</div>
                  <div class="service-stat"><strong>Maternal pending</strong>${maternalPending}</div>
                  <div class="service-stat"><strong>Maternal cleared</strong>${maternalResolved}</div>
                  <div class="service-stat"><strong>Govt centers</strong>${(state.observation.hospitals || []).filter(item => item.specialties.includes("maternity")).length}</div>
                </div>
              </div>
            `;
          }

          function renderFleetBoard() {
            const container = document.getElementById("fleet-board");
            const ambulances = state.observation?.ambulances || [];
            if (!container) return;
            if (!ambulances.length) {
              container.innerHTML = '<div class="empty">No fleet data yet.</div>';
              return;
            }

            const maskedById = new Map(
              (state.observation.masked_actions || []).map(item => [item.subject_id, item.reason])
            );
            const candidateCounts = new Map();
            const candidateMix = new Map();

            (state.observation.available_dispatches || []).forEach(candidate => {
              candidateCounts.set(candidate.ambulance_id, (candidateCounts.get(candidate.ambulance_id) || 0) + 1);
              const mix = candidateMix.get(candidate.ambulance_id) || { critical: 0, maternal: 0 };
              if (candidate.incident_triage === "108") {
                mix.critical += 1;
              } else {
                mix.maternal += 1;
              }
              candidateMix.set(candidate.ambulance_id, mix);
            });

            const sorted = ambulances.slice().sort((left, right) => {
              if (left.support_level !== right.support_level) {
                if (left.support_level === "advanced") return -1;
                if (right.support_level === "advanced") return 1;
              }
              if (left.mode !== right.mode) {
                return left.mode === "available" ? -1 : 1;
              }
              return left.label.localeCompare(right.label);
            });

            container.innerHTML = sorted.map(ambulance => {
              const candidateCount = candidateCounts.get(ambulance.ambulance_id) || 0;
              const mix = candidateMix.get(ambulance.ambulance_id) || { critical: 0, maternal: 0 };
              const maskedReason = maskedById.get(ambulance.ambulance_id);
              const lastAssignment = ambulance.last_assignment ? incidentNameById(ambulance.last_assignment) : "Standby";
              let readiness;

              if (ambulance.mode === "busy") {
                readiness = `On mission until minute ${ambulance.available_from_minute}.`;
              } else if (candidateCount > 0) {
                readiness = `${candidateCount} valid dispatch option(s) available now: ${mix.critical} for 108 and ${mix.maternal} for 102.`;
              } else if (maskedReason) {
                readiness = maskedReason;
              } else {
                readiness = "Standing by with no current dispatch recommendation.";
              }

              return `
                <div class="fleet-card ${state.selectedAmbulance === ambulance.ambulance_id ? "is-selected" : ""}" data-ambulance-id="${ambulance.ambulance_id}">
                  <div class="fleet-head">
                    <div>
                      <div class="fleet-name">${ambulance.label}</div>
                      <div class="fleet-subline">
                        ${ambulance.location_name}<br />
                        Last assignment: <strong>${lastAssignment}</strong>
                      </div>
                    </div>
                    <span class="service-chip ${ambulance.support_level === "maternal" ? "service-maternal" : "service-emergency"}">${shortAmbulanceLabel(ambulance)}</span>
                  </div>
                  <div class="fleet-grid">
                    <div class="fleet-stat"><strong>Status</strong>${ambulance.mode}</div>
                    <div class="fleet-stat"><strong>Fuel</strong>${ambulance.fuel_pct.toFixed(1)}%</div>
                    <div class="fleet-stat"><strong>Available from</strong>${ambulance.available_from_minute} min</div>
                    <div class="fleet-stat"><strong>Support</strong>${ambulance.support_level}</div>
                  </div>
                  <div class="fleet-footnote">${readiness}</div>
                </div>
              `;
            }).join("");

            container.querySelectorAll("[data-ambulance-id]").forEach(element => {
              element.addEventListener("click", () => {
                const ambulanceId = element.getAttribute("data-ambulance-id");
                if (ambulanceId) selectAmbulance(ambulanceId);
              });
            });
          }

          function renderQueueList() {
            const container = document.getElementById("queue-list");
            const incidents = state.observation?.incidents || [];
            if (!incidents.length) {
              container.innerHTML = '<div class="empty">No incidents in this scenario.</div>';
              return;
            }
            const priorityOrder = { pending: 0, resolved: 1, missed: 2 };
            const sorted = incidents.slice().sort((left, right) => {
              if (left.triage !== right.triage) return left.triage === "108" ? -1 : 1;
              return (priorityOrder[left.status] ?? 9) - (priorityOrder[right.status] ?? 9);
            });
            container.innerHTML = sorted.map(incident => `
              <div class="queue-card">
                <div class="candidate-head">
                  <div class="candidate-title">${incident.label}</div>
                  <span class="badge ${incident.triage === "108" ? "critical" : "maternal"}">${incident.triage}</span>
                </div>
                <div style="margin-top:8px; color:var(--muted);">
                  ${incident.location_name}<br />
                  Status: <span class="badge ${incidentStatusTone(incident.status)}">${incident.status}</span><br />
                  ${incident.status === "pending"
                    ? `Current wait: ${incident.wait_minutes.toFixed(1)}m | Support: ${incident.required_support}`
                    : `Required support: ${incident.required_support} | Outcome recorded for this shift`}
                </div>
                <div style="margin-top:8px; color:var(--muted);">${incident.description}</div>
              </div>
            `).join("");
          }

          function renderUnitFocus() {
            const container = document.getElementById("unit-focus");
            const ambulances = state.observation?.ambulances || [];
            if (!ambulances.length) {
              container.innerHTML = '<div class="empty">No fleet data yet.</div>';
              return;
            }
            const selected =
              ambulances.find(item => item.ambulance_id === state.selectedAmbulance) ||
              ambulances.find(item => item.mode === "busy") ||
              ambulances[0];
            state.selectedAmbulance = selected.ambulance_id;
            container.innerHTML = `
              <div class="focus-card">
                <div class="service-title">
                  <span>${selected.label}</span>
                  <span class="service-chip ${selected.support_level === "maternal" ? "service-maternal" : "service-emergency"}">${shortAmbulanceLabel(selected)}</span>
                </div>
                <div style="margin-top:10px; color:var(--muted);">
                  Current node: <strong>${selected.location_name}</strong><br />
                  Last assignment: <strong>${selected.last_assignment ? incidentNameById(selected.last_assignment) : "Standby"}</strong>
                </div>
                <div class="focus-grid">
                  <div class="focus-stat"><strong>Status</strong><span>${selected.mode}</span></div>
                  <div class="focus-stat"><strong>Fuel</strong><span>${selected.fuel_pct.toFixed(1)}%</span></div>
                  <div class="focus-stat"><strong>Available from</strong><span>${selected.available_from_minute} min</span></div>
                  <div class="focus-stat"><strong>Support</strong><span>${selected.support_level}</span></div>
                </div>
              </div>
            `;
          }

          function renderHospitalBoard() {
            const container = document.getElementById("hospital-board");
            const hospitals = state.observation?.hospitals || [];
            if (!container) return;
            if (!hospitals.length) {
              container.innerHTML = '<div class="empty">No hospital capacity data yet.</div>';
              return;
            }

            const sorted = hospitals.slice().sort((left, right) => {
              const leftRatio = left.bed_capacity ? left.current_load / left.bed_capacity : 0;
              const rightRatio = right.bed_capacity ? right.current_load / right.bed_capacity : 0;
              if (leftRatio !== rightRatio) return rightRatio - leftRatio;
              return left.label.localeCompare(right.label);
            });

            container.innerHTML = sorted.map(hospital => {
              const ratio = hospital.bed_capacity ? hospital.current_load / hospital.bed_capacity : 0;
              const loadPct = Math.min(ratio * 100, 100);
              const tone = ratio >= 1 ? "var(--critical)" : ratio >= 0.82 ? "var(--urgent)" : "var(--safe)";
              return `
                <div class="hospital-card">
                  <div class="service-title">
                    <span>${hospital.label}</span>
                    <span class="badge ${ratio >= 1 ? "critical" : ratio >= 0.82 ? "urgent" : "safe"}">L${hospital.trauma_level}</span>
                  </div>
                  <div class="hospital-meta">
                    ${hospital.location_name}<br />
                    Occupancy: <strong>${hospital.current_load}/${hospital.bed_capacity}</strong><br />
                    Services: ${hospital.specialties.join(", ")}
                  </div>
                  <div class="capacity-track">
                    <div class="capacity-fill" style="width:${loadPct}%; background:${tone};"></div>
                  </div>
                </div>
              `;
            }).join("");
          }

          function renderMapFeed() {
            const container = document.getElementById("map-feed");
            if (!state.observation || !container) return;
            const incidents = state.observation.incidents || [];
            const pending108 = incidents.filter(item => item.status === "pending" && item.triage === "108").length;
            const pending102 = incidents.filter(item => item.status === "pending" && item.triage === "102").length;
            const focus = (state.observation.ambulances || []).find(item => item.ambulance_id === state.selectedAmbulance);
            container.innerHTML = `
              <div style="font-size:0.76rem; font-weight:700; color:var(--accent);">Live Feed</div>
              <div style="margin-top:6px; color:var(--muted); font-size:0.86rem;">
                Active 108: <strong>${pending108}</strong> | Active 102: <strong>${pending102}</strong><br />
                ${focus ? `Tracking: <strong>${focus.label}</strong>` : "Tracking: <strong>Auto focus</strong>"}
              </div>
            `;
          }

          function renderRewardBursts() {
            const container = document.getElementById("reward-bursts");
            if (!container || !state.rewardBursts) return;
            container.innerHTML = state.rewardBursts.map(burst => `
              <div class="reward-burst reward-burst-${burst.tone}" style="left:${(burst.x / 960) * 100}%; top:${(burst.y / 560) * 100}%;">
                ${burst.label}
              </div>
            `).join("");
          }

          function renderRewardBreakdown() {
            if (!state.observation) return;
            const breakdown = state.observation.reward_breakdown || {};
            const items = [
              ["Survival Gain", breakdown.survival_gain || 0],
              ["Backlog Pressure", -(breakdown.backlog_pressure_penalty || 0)],
              ["Invalid Penalty", -(breakdown.invalid_action_penalty || 0)],
              ["Corridor Cost", -(breakdown.corridor_cost || 0)],
              ["Missed Penalty", -(breakdown.missed_incident_penalty || 0)],
              ["Total Reward", breakdown.total_reward || 0],
            ];
            document.getElementById("reward-grid").innerHTML = items.map(([label, value]) => `
              <div class="reward-item">
                <strong>${label}</strong>
                <span>${Number(value).toFixed(2)}</span>
              </div>
            `).join("");
          }

          function renderDecisionIntel() {
            const container = document.getElementById("decision-intel");
            if (!container || !state.observation || !state.envState) return;

            const candidates = (state.observation.available_dispatches || []).slice().sort((left, right) => (
              right.weighted_survival - left.weighted_survival
            ));
            const incidents = state.observation.incidents || [];
            const top = candidates[0];
            const runnerUp = candidates[1];
            const criticalPending = incidents.filter(item => item.status === "pending" && item.triage === "108").length;
            const maternalPending = incidents.filter(item => item.status === "pending" && item.triage === "102").length;
            const advancedAvailable = (state.observation.ambulances || []).filter(item => item.support_level === "advanced" && item.mode === "available").length;
            const maternalAvailable = (state.observation.ambulances || []).filter(item => item.support_level === "maternal" && item.mode === "available").length;
            const criticalCoverage = Number(state.envState.score_breakdown?.critical_coverage || 0);

            const cards = [];

            if (top) {
              const gap = runnerUp ? top.weighted_survival - runnerUp.weighted_survival : top.weighted_survival;
              cards.push(`
                <div class="intel-card">
                  <strong>Preferred Next Dispatch</strong>
                  ${ambulanceNameById(top.ambulance_id)} -> ${incidentNameById(top.incident_id)} -> ${hospitalNameById(top.hospital_id)}<br />
                  ${top.why_it_is_valid}<br />
                  ${runnerUp
                    ? `It leads the next-best option by ${gap.toFixed(2)} weighted-survival points.`
                    : `It is the only valid dispatch remaining at this moment.`}
                </div>
              `);
            } else {
              cards.push(`
                <div class="intel-card">
                  <strong>Preferred Next Dispatch</strong>
                  No valid dispatch remains. This usually means the shift has ended or all remaining cases were missed because no compatible resource could be assigned in time.
                </div>
              `);
            }

            cards.push(`
              <div class="intel-card">
                <strong>Service Pressure</strong>
                ${criticalPending} active 108 case(s), ${maternalPending} active 102 case(s).<br />
                Available fleet right now: ${advancedAvailable} advanced unit(s), ${maternalAvailable} maternal unit(s).<br />
                ${criticalPending > 0 && maternalAvailable > 0
                  ? `Advanced units are being protected for 108 emergencies while maternal units cover 102 transfers.`
                  : `Fleet pressure is currently low enough that the policy can focus on direct survival gain.`}
              </div>
            `);

            cards.push(`
              <div class="intel-card">
                <strong>Score Guardrail</strong>
                Critical-case coverage is ${criticalCoverage.toFixed(2)} and current task score is ${formatScore(state.envState.task_score || 0)}.<br />
                ${criticalCoverage < 1
                  ? `Missing a 108 case now hurts the final grade much more than before, so the policy cannot look successful while dropping a critical emergency.`
                  : `All critical 108 cases cleared so far, which keeps the final score credible for judges.`}
              </div>
            `);

            container.innerHTML = cards.join("");
          }

          function renderCandidates() {
            const container = document.getElementById("candidate-list");
            const candidates = state.observation?.available_dispatches || [];
            if (!candidates.length) {
              container.innerHTML = '<div class="empty">No valid dispatches remain.</div>';
              return;
            }
            container.innerHTML = candidates.slice(0, 8).map(candidate => `
              <div class="card">
                <div class="candidate-head">
                  <div class="candidate-title">${ambulanceNameById(candidate.ambulance_id)} -> ${incidentNameById(candidate.incident_id)}</div>
                  <span class="badge ${candidate.incident_triage === "108" ? 'critical' : 'maternal'}">
                    ${candidate.incident_triage === "108" ? '108 Emergency' : '102 Maternal/Newborn'}
                  </span>
                </div>
                <div style="margin-top:8px; color:var(--muted);">
                  Hospital: <strong>${hospitalNameById(candidate.hospital_id)}</strong><br />
                  ETA: ${candidate.scene_eta_minutes.toFixed(1)}m scene + ${candidate.transport_eta_minutes.toFixed(1)}m transport<br />
                  Weighted survival: <strong>${candidate.weighted_survival.toFixed(2)}</strong><br />
                  Fuel after trip: ${candidate.fuel_after_pct.toFixed(1)}%
                </div>
                <div style="margin-top:10px; color:var(--muted); line-height:1.45;">${candidate.why_it_is_valid}</div>
                <div style="margin-top:6px; color:var(--muted); line-height:1.45;">Route: ${candidate.route_summary}</div>
                <div style="margin-top:12px;">
                  <button class="primary" data-candidate="${candidate.candidate_id}">Dispatch This Unit</button>
                </div>
              </div>
            `).join("");

            const buttons = container.querySelectorAll("button[data-candidate]");
            buttons.forEach((button, index) => {
              button.onclick = () => {
                const candidate = candidates[index];
                manualDispatch(candidate);
              };
            });
          }

          function renderLogs() {
            const logs = state.observation?.decision_log || [];
            const container = document.getElementById("log-list");
            if (!logs.length) {
              container.innerHTML = '<div class="empty">No dispatch decisions yet.</div>';
              return;
            }
            container.innerHTML = logs.slice().reverse().map(entry => `
              <div class="card">
                <div class="log-head">
                  <strong>${entry.action_label}</strong>
                  <span class="badge ${entry.reward_delta >= 0 ? 'safe' : 'critical'}">${Number(entry.reward_delta).toFixed(2)}</span>
                </div>
                <div style="margin-top:8px; color:var(--muted);">Minute ${entry.minute}</div>
                <div style="margin-top:8px; line-height:1.55;">${entry.explanation}</div>
              </div>
            `).join("");
          }

          function shortHospitalLabel(hospital) {
            const known = {
              "Rajiv Gandhi GH": "RGGH L1",
              "Apollo Greams": "Apollo L1",
              "Kilpauk Medical": "KMC L2",
              "Institute of Obstetrics": "IOG L2",
              "KC General": "KC L2",
              "Vani Vilas": "Vani L2",
            };
            return known[hospital.label] || `${hospital.label.split(" ")[0]} L${hospital.trauma_level}`;
          }

          function shortIncidentLabel(incident) {
            if (incident.triage === "108") {
              return incident.label
                .replace("Cardiac arrest at ", "Cardiac: ")
                .replace("Cardiac arrest on ", "Cardiac: ")
                .replace("Heart attack at ", "Heart: ")
                .replace("Heart attack near ", "Heart: ")
                .replace("Major trauma on ", "Trauma: ")
                .replace("Severe trauma on ", "Trauma: ");
            }
            return incident.label
              .replace("Urgent maternity case in ", "Maternity: ")
              .replace("Urgent maternity transfer near ", "Maternity: ")
              .replace("High-risk pregnancy transfer at ", "Pregnancy: ")
              .replace("Newborn referral from ", "Newborn: ");
          }

          function routePointsFromIds(nodeMap, ids) {
            return ids
              .map(nodeId => nodeMap[nodeId])
              .filter(Boolean)
              .map(node => `${node.x},${node.y}`)
              .join(" ");
          }

          function renderMapBackdrop(nodeMap) {
            const seaPath = `
              <path
                d="M 926 0 L 960 0 L 960 560 L 934 560 Q 922 486 924 404 Q 926 312 940 226 Q 950 152 946 0 Z"
                fill="rgba(163,214,248,0.82)">
              </path>
              <path
                d="M 906 10 Q 900 98 902 178 Q 904 266 910 344 Q 916 456 928 560"
                fill="none"
                stroke="rgba(62,136,216,0.88)"
                stroke-width="4.5"
                stroke-linecap="round">
              </path>
            `;

            const corridorBands = [
              {
                nodeIds: ["anna_nagar", "koyambedu", "egmore", "greams_road", "marina"],
                color: "rgba(255,107,61,0.13)",
                stroke: "rgba(234,91,44,0.36)",
                width: 16,
                label: "Central Spine",
                x: 424,
                y: 146,
              },
              {
                nodeIds: ["greams_road", "t_nagar", "guindy", "velachery", "omr"],
                color: "rgba(88,164,231,0.16)",
                stroke: "rgba(88,164,231,0.40)",
                width: 15,
                label: "OMR Tech Corridor",
                x: 706,
                y: 414,
              },
              {
                nodeIds: ["guindy", "tambaram"],
                color: "rgba(234,91,44,0.12)",
                stroke: "rgba(234,91,44,0.32)",
                width: 14,
                label: "GST Road",
                x: 692,
                y: 454,
              },
            ].map(corridor => `
              <g>
                <polyline
                  points="${routePointsFromIds(nodeMap, corridor.nodeIds)}"
                  fill="none"
                  stroke="${corridor.color}"
                  stroke-width="${corridor.width}"
                  stroke-linecap="round"
                  stroke-linejoin="round">
                </polyline>
                <polyline
                  points="${routePointsFromIds(nodeMap, corridor.nodeIds)}"
                  fill="none"
                  stroke="${corridor.stroke}"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-dasharray="8 8">
                </polyline>
                <text x="${corridor.x}" y="${corridor.y}" fill="rgba(70,98,143,0.74)" style="font-size:11px; font-weight:700; letter-spacing:0.05em;">
                  ${corridor.label}
                </text>
              </g>
            `).join("");

            const districtLabels = [
              ["Anna Nagar", 150, 66],
              ["Medical Core", 372, 102],
              ["CBD / Marina", 644, 198],
              ["South Chennai", 612, 316],
              ["Tambaram Belt", 680, 528],
            ].map(([label, x, y]) => `
              <text x="${x}" y="${y}" fill="rgba(74,97,133,0.42)" style="font-size:15px; font-weight:700; letter-spacing:0.08em; text-transform:uppercase;">
                ${label}
              </text>
            `).join("");

            return `${seaPath}${corridorBands}${districtLabels}`;
          }

          function renderMap() {
            const svg = document.getElementById("dispatch-map");
            if (!state.config || !state.observation) return;

            const nodeMap = Object.fromEntries(state.config.graph.nodes.map(node => [node.node_id, node]));
            const ambulanceNodeOffsets = {};
            const incidentNodeOffsets = {};
            const nodeLabelOffsets = {
              anna_nagar: [18, 3],
              koyambedu: [16, 4],
              kilpauk: [16, -6],
              egmore: [16, 4],
              greams_road: [16, 4],
              marina: [14, 2],
              t_nagar: [14, 6],
              porur: [14, 6],
              guindy: [14, 6],
              velachery: [14, 2],
              omr: [14, 4],
              tambaram: [14, 6],
            };
            const backdrop = renderMapBackdrop(nodeMap);
            const edges = state.config.graph.edges.map(edge => {
              const source = nodeMap[edge.source];
              const target = nodeMap[edge.target];
              const congested = edge.congestion_multiplier >= 1.3;
              const stroke = congested ? "rgba(228,118,74,0.52)" : "rgba(92,120,163,0.44)";
              const width = congested ? 3.4 : 2.9;
              return `<line x1="${source.x}" y1="${source.y}" x2="${target.x}" y2="${target.y}" stroke="${stroke}" stroke-width="${width}" stroke-linecap="round" stroke-dasharray="${congested ? "10 7" : "none"}" />`;
            }).join("");

            const nodes = state.config.graph.nodes.map(node => `
              <g>
                <circle cx="${node.x}" cy="${node.y}" r="14" fill="rgba(255,255,255,0.98)" stroke="rgba(204,110,74,0.52)" stroke-width="3.2"></circle>
                <text x="${node.x + (nodeLabelOffsets[node.node_id]?.[0] || 18)}" y="${node.y + (nodeLabelOffsets[node.node_id]?.[1] || 5)}" class="map-node-label">${node.label}</text>
              </g>
            `).join("");

            const hospitalMarks = (state.observation.hospitals || []).map((hospital, index) => {
              const node = nodeMap[hospital.node_id];
              const sameNodeIndex = (state.observation.hospitals || [])
                .slice(0, index)
                .filter(item => item.node_id === hospital.node_id)
                .length;
              const loadRatio = hospital.bed_capacity ? hospital.current_load / hospital.bed_capacity : 0;
              const hospitalTone = loadRatio >= 1 ? palette.critical : loadRatio >= 0.82 ? palette.urgent : palette.hospital;
              const yOffset = 18 + sameNodeIndex * 16;
              return `
                <g>
                  <circle cx="${node.x}" cy="${node.y}" r="${18 + sameNodeIndex * 2}" fill="none" stroke="${hospitalTone}" stroke-opacity="0.30" stroke-width="5"></circle>
                  <text x="${node.x - 22}" y="${node.y - yOffset}" class="map-chip map-inline-label" fill="${hospitalTone}">${shortHospitalLabel(hospital)}</text>
                </g>
              `;
            }).join("");

            const ambulanceMarks = (state.observation.ambulances || []).map((ambulance) => {
              const node = nodeMap[ambulance.node_id];
              const sameNodeIndex = ambulanceNodeOffsets[ambulance.node_id] || 0;
              ambulanceNodeOffsets[ambulance.node_id] = sameNodeIndex + 1;
              const y = node.y + 30 + sameNodeIndex * 22;
              const selected = state.selectedAmbulance === ambulance.ambulance_id;
              return ambulanceIconMarkup({
                ambulanceId: ambulance.ambulance_id,
                label: ambulance.label,
                serviceLabel: shortAmbulanceLabel(ambulance),
                x: node.x - 4,
                y: y - 6,
                fill: ambulanceFillForSupport(ambulance.support_level),
                selected,
                opacity: selected ? 0.98 : 0.9,
              });
            }).join("");

            const incidentMarks = (state.observation.incidents || [])
              .filter(incident => incident.status === "pending")
              .map((incident) => {
                const node = nodeMap[incident.node_id];
                const sameNodeIndex = incidentNodeOffsets[incident.node_id] || 0;
                incidentNodeOffsets[incident.node_id] = sameNodeIndex + 1;
                const y = node.y - 30 - sameNodeIndex * 16;
                const cls = incident.triage === "108" ? palette.critical : palette.maternalIncident;
                const label = shortIncidentLabel(incident);
                return `
                  <g>
                    <circle cx="${node.x - 6}" cy="${y - 5}" r="10" fill="${cls}" opacity="0.92" stroke="white" stroke-width="2"></circle>
                    <text x="${node.x - 14}" y="${y - 1}" style="font-size:9px; font-weight:700; fill:white;">${incident.triage}</text>
                    <text x="${node.x + 10}" y="${y}" class="map-chip map-inline-label" fill="${cls}">${label}</text>
                  </g>
                `;
              }).join("");

            svg.innerHTML = `${backdrop}${edges}${nodes}${hospitalMarks}${ambulanceMarks}${incidentMarks}<g id="animation-layer"></g>`;
            svg.querySelectorAll(".ambulance-mark").forEach(element => {
              element.addEventListener("click", () => {
                const ambulanceId = element.getAttribute("data-ambulance-id");
                if (ambulanceId) selectAmbulance(ambulanceId);
              });
            });
          }

          function wait(ms) {
            return new Promise(resolve => setTimeout(resolve, ms));
          }

          async function animateTrace(trace) {
            if (!trace || !trace.length || !state.config) return;
            const groups = new Map();
            trace.forEach(entry => {
              const key = String(entry.minute ?? entry.step ?? 0);
              if (!groups.has(key)) groups.set(key, []);
              groups.get(key).push(entry);
            });

            for (const group of groups.values()) {
              await Promise.all(group.map((entry, index) => animateCandidate(entry.candidate, index)));
              await wait(140);
            }
          }

          function animateCandidate(candidate, index = 0) {
            return new Promise(resolve => {
              if (!candidate || !candidate.route_node_ids || candidate.route_node_ids.length < 2) {
                resolve();
                return;
              }

              const svg = document.getElementById("dispatch-map");
              const layer = svg.querySelector("#animation-layer");
              if (!svg || !layer) {
                resolve();
                return;
              }

              const nodeMap = Object.fromEntries(state.config.graph.nodes.map(node => [node.node_id, node]));
              const points = candidate.route_node_ids
                .map(nodeId => nodeMap[nodeId])
                .filter(Boolean)
                .map(node => ({ x: node.x, y: node.y }));

              if (points.length < 2) {
                resolve();
                return;
              }

              const namespace = "http://www.w3.org/2000/svg";
              const group = document.createElementNS(namespace, "g");
              const missionColor = candidate.incident_triage === "108" ? palette.critical : palette.maternalIncident;
              const vehicleLabel = candidate.incident_triage === "108" ? "108" : "102";
              const path = document.createElementNS(namespace, "polyline");
              path.setAttribute("fill", "none");
              path.setAttribute("stroke", missionColor);
              path.setAttribute("stroke-opacity", "0.22");
              path.setAttribute("stroke-width", candidate.incident_triage === "108" ? "6" : "5");
              path.setAttribute("stroke-linecap", "round");
              path.setAttribute("stroke-linejoin", "round");
              path.setAttribute("stroke-dasharray", candidate.incident_triage === "108" ? "10 7" : "5 8");
              path.setAttribute("points", points.map(point => `${point.x},${point.y}`).join(" "));

              const startPulse = document.createElementNS(namespace, "circle");
              startPulse.setAttribute("cx", points[0].x);
              startPulse.setAttribute("cy", points[0].y);
              startPulse.setAttribute("r", "8");
              startPulse.setAttribute("fill", missionColor);
              startPulse.setAttribute("fill-opacity", "0.18");
              startPulse.setAttribute("stroke", missionColor);
              startPulse.setAttribute("stroke-opacity", "0.45");
              startPulse.setAttribute("stroke-width", "2");

              const vehicle = document.createElementNS(namespace, "g");
              vehicle.innerHTML = `
                <circle cx="0" cy="0" r="18" fill="${missionColor}" fill-opacity="0.10"></circle>
                <rect x="-17" y="-9" width="24" height="14" rx="3.6" fill="${missionColor}" stroke="white" stroke-width="2"></rect>
                <rect x="6" y="-6" width="10" height="11" rx="2.6" fill="${missionColor}" stroke="white" stroke-width="2"></rect>
                <rect x="-12.5" y="-6.2" width="7.6" height="4.2" rx="1.2" fill="rgba(255,255,255,0.7)"></rect>
                <rect x="8.2" y="-4.2" width="4.4" height="3.4" rx="0.8" fill="rgba(255,255,255,0.7)"></rect>
                <rect x="-9.1" y="-2.2" width="7.2" height="4.4" rx="1" fill="white" opacity="0.95"></rect>
                <rect x="-6.6" y="-4.6" width="2.2" height="9.2" rx="0.8" fill="white" opacity="0.95"></rect>
                <circle cx="-9.5" cy="8" r="3.7" fill="#1d1d1f" stroke="white" stroke-width="1.5"></circle>
                <circle cx="8.5" cy="8" r="3.7" fill="#1d1d1f" stroke="white" stroke-width="1.5"></circle>
                <circle cx="-9.5" cy="8" r="1.25" fill="white" opacity="0.9"></circle>
                <circle cx="8.5" cy="8" r="1.25" fill="white" opacity="0.9"></circle>
                <text x="-1.5" y="1.5" text-anchor="middle" style="font-size:8px; font-weight:800; fill:#ffffff;">${vehicleLabel}</text>
                <text x="21" y="4" class="map-chip" style="font-size:11px; font-weight:700; fill:${missionColor};">${ambulanceNameById(candidate.ambulance_id)}</text>
              `;

              const destinationPulse = document.createElementNS(namespace, "circle");
              destinationPulse.setAttribute("cx", points[points.length - 1].x);
              destinationPulse.setAttribute("cy", points[points.length - 1].y);
              destinationPulse.setAttribute("r", "10");
              destinationPulse.setAttribute("fill", "none");
              destinationPulse.setAttribute("stroke", missionColor);
              destinationPulse.setAttribute("stroke-opacity", "0.0");
              destinationPulse.setAttribute("stroke-width", "2");

              group.appendChild(startPulse);
              group.appendChild(path);
              group.appendChild(destinationPulse);
              group.appendChild(vehicle);
              layer.appendChild(group);

              const segments = [];
              let totalLength = 0;
              for (let i = 1; i < points.length; i += 1) {
                const length = Math.hypot(points[i].x - points[i - 1].x, points[i].y - points[i - 1].y);
                segments.push(length);
                totalLength += length;
              }

              const duration = Math.max(1400, (candidate.scene_eta_minutes + candidate.transport_eta_minutes) * 95);
              const startDelay = index * 120;
              const startedAt = performance.now() + startDelay;

              function draw(now) {
                if (now < startedAt) {
                  requestAnimationFrame(draw);
                  return;
                }

                const elapsed = now - startedAt;
                const progress = Math.min(elapsed / duration, 1);
                let remaining = totalLength * progress;
                let x = points[0].x;
                let y = points[0].y;

                for (let i = 1; i < points.length; i += 1) {
                  const segment = segments[i - 1];
                  if (remaining <= segment) {
                    const ratio = segment === 0 ? 0 : remaining / segment;
                    x = points[i - 1].x + (points[i].x - points[i - 1].x) * ratio;
                    y = points[i - 1].y + (points[i].y - points[i - 1].y) * ratio;
                    break;
                  }
                  remaining -= segment;
                  x = points[i].x;
                  y = points[i].y;
                }

                vehicle.setAttribute("transform", `translate(${x} ${y})`);
                const pulseRadius = 8 + 5 * Math.abs(Math.sin(progress * Math.PI * 4));
                startPulse.setAttribute("r", `${pulseRadius}`);

                if (progress < 1) {
                  requestAnimationFrame(draw);
                } else {
                  destinationPulse.setAttribute("stroke-opacity", "0.65");
                  destinationPulse.setAttribute("r", "18");
                  setTimeout(() => {
                    group.remove();
                    resolve();
                  }, 120);
                }
              }

              requestAnimationFrame(draw);
            });
          }

          async function boot() {
            try {
              await loadConfig();
              document.getElementById("reset-btn").addEventListener("click", resetScenario);
              document.getElementById("auto-step-btn").addEventListener("click", autoStep);
              document.getElementById("auto-run-btn").addEventListener("click", autoRun);
              await resetScenario();
            } catch (error) {
              document.getElementById("ui-status").textContent = `Dashboard failed to load: ${error.message}`;
            }
          }

          window.manualDispatch = manualDispatch;
          window.addEventListener("load", boot);
        </script>
      </body>
    </html>
    """
