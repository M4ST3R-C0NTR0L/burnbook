"""
BurnBook Formatters - How the carnage is presented.
Console, JSON, and HTML output renderers.
"""

import json
import math
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path

import click


# Score band definitions
SCORE_BANDS = [
    (0,  20,  "🔥", "This code is a war crime",              "red",     "#ff1744"),
    (21, 40,  "😬", "Did a ChatGPT free tier write this?",   "magenta", "#ff6d00"),
    (41, 60,  "😐", "Mid. Like gas station sushi.",           "yellow",  "#ffd600"),
    (61, 80,  "👍", "Okay, not bad. Your mom would be proud.","cyan",    "#00e5ff"),
    (81, 100, "🏆", "Chef's kiss. Ship it.",                   "green",   "#00e676"),
]

CATEGORY_ICONS = {
    "complexity":    "🧠",
    "naming":        "🏷️",
    "security":      "🔐",
    "duplication":   "📋",
    "documentation": "📝",
    "dead_code":     "💀",
    "style":         "✨",
    "testing":       "🧪",
}

SEVERITY_COLORS = {
    "critical": "red",
    "high":     "magenta",
    "medium":   "yellow",
    "low":      "white",
    "info":     "cyan",
}

SEVERITY_ICONS = {
    "critical": "💥",
    "high":     "🔴",
    "medium":   "🟡",
    "low":      "🔵",
    "info":     "ℹ️",
}


def get_score_band(score: int):
    for low, high, emoji, label, color, hex_color in SCORE_BANDS:
        if low <= score <= high:
            return emoji, label, color, hex_color
    return "🔥", "This code is a war crime", "red", "#ff1744"


def get_score_badge(score: int) -> str:
    emoji, _, _, _ = get_score_band(score)
    return emoji


def get_score_label(score: int) -> str:
    _, label, _, _ = get_score_band(score)
    return label


def get_score_color(score: int) -> str:
    _, _, color, _ = get_score_band(score)
    return color


class ConsoleFormatter:
    """Rich console output — the full experience."""

    def __init__(self, severity: str = "brutal"):
        self.severity = severity

    def render(self, results: Dict[str, Any]) -> None:
        score = results.get("score", 0)
        emoji, label, color, _ = get_score_band(score)
        metrics = results.get("metrics", {})
        issues = results.get("issues", [])
        category_scores = results.get("category_scores", {})
        ai_roast = results.get("ai_roast")
        language = results.get("language", "unknown")
        elapsed = results.get("elapsed_seconds", 0)

        # ── Header ────────────────────────────────────────────────────────────
        click.echo("\n" + "═" * 60)
        click.echo(click.style(f"  {emoji}  VERDICT: {label}", fg=color, bold=True))
        click.echo(click.style(f"  Score: {score}/100", fg=color, bold=True))
        click.echo("═" * 60)

        # ── Summary ───────────────────────────────────────────────────────────
        click.echo(click.style("\n📊 ANALYSIS SUMMARY", fg="white", bold=True))
        click.echo(f"  Language    : {language}")
        click.echo(f"  Files       : {metrics.get('files_analyzed', 0)}")
        click.echo(f"  Lines       : {metrics.get('total_lines', 0):,}")
        click.echo(f"  Issues      : {metrics.get('total_issues', 0)}")
        click.echo(f"  Per file    : {metrics.get('issues_per_file', 0)}")
        click.echo(f"  Elapsed     : {elapsed}s")

        # ── Score bar ─────────────────────────────────────────────────────────
        click.echo(click.style("\n🎯 SCORE", fg="white", bold=True))
        self._render_score_bar(score, color)

        # ── Category breakdown ────────────────────────────────────────────────
        if category_scores:
            click.echo(click.style("\n📋 CATEGORY BREAKDOWN", fg="white", bold=True))
            for cat, cat_score in sorted(category_scores.items(), key=lambda x: x[1]):
                icon = CATEGORY_ICONS.get(cat, "•")
                cat_color = get_score_color(cat_score)
                bar = self._mini_bar(cat_score)
                click.echo(
                    f"  {icon} {cat:<15} {click.style(bar, fg=cat_color)} "
                    f"{click.style(str(cat_score), fg=cat_color, bold=True)}/100"
                )

        # ── Severity breakdown ────────────────────────────────────────────────
        sev_counts = metrics.get("severity_counts", {})
        if any(sev_counts.values()):
            click.echo(click.style("\n⚠️  SEVERITY BREAKDOWN", fg="white", bold=True))
            for sev in ["critical", "high", "medium", "low", "info"]:
                count = sev_counts.get(sev, 0)
                if count > 0:
                    icon = SEVERITY_ICONS.get(sev, "•")
                    sev_color = SEVERITY_COLORS.get(sev, "white")
                    styled_sev = click.style(sev.upper().ljust(10), fg=sev_color, bold=True)
                    click.echo(
                        f"  {icon} {styled_sev} "
                        f"{count} issue{'s' if count != 1 else ''}"
                    )

        # ── Top Issues ────────────────────────────────────────────────────────
        if issues:
            click.echo(click.style("\n🚨 TOP ISSUES", fg="white", bold=True))
            severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
            sorted_issues = sorted(
                issues,
                key=lambda x: severity_order.get(x.get("severity", "low"), 3)
            )[:15]

            for issue in sorted_issues:
                sev = issue.get("severity", "low")
                cat = issue.get("category", "style")
                msg = issue.get("message", "")
                file_path = issue.get("file", "")
                line_num = issue.get("line")
                icon = SEVERITY_ICONS.get(sev, "•")
                sev_color = SEVERITY_COLORS.get(sev, "white")

                location = ""
                if file_path:
                    fname = Path(file_path).name
                    location = f" [{fname}"
                    if line_num:
                        location += f":{line_num}"
                    location += "]"

                styled_sev = click.style(sev.upper().ljust(8), fg=sev_color, bold=True)
                click.echo(
                    f"  {icon} "
                    f"{styled_sev} "
                    f"{click.style(f'({cat})', fg='cyan')} "
                    f"{msg[:70]}{'...' if len(msg) > 70 else ''}"
                    f"{click.style(location, fg='bright_black')}"
                )

        # ── AI Roast ──────────────────────────────────────────────────────────
        if ai_roast and not ai_roast.get("error"):
            click.echo("\n" + "═" * 60)
            click.echo(click.style("  🤖 AI ROAST MASTER SPEAKS", fg="magenta", bold=True))
            click.echo("═" * 60)

            overall = ai_roast.get("overall", "")
            if overall:
                click.echo(click.style(f"\n  {overall}", fg="magenta"))

            sections = ai_roast.get("sections", [])
            for section in sections:
                cat = section.get("category", "")
                roast = section.get("roast", "")
                tip = section.get("tip", "")

                if roast:
                    cat_icon = CATEGORY_ICONS.get(cat.lower(), "•")
                    click.echo(f"\n  {cat_icon} {click.style(cat.upper(), fg='cyan', bold=True)}")
                    click.echo(f"    💬 {roast}")
                    if tip:
                        click.echo(click.style(f"    💡 FIX: {tip}", fg="green"))

            closing = ai_roast.get("closing", "")
            if closing:
                click.echo(f"\n  {click.style('🎤 MIC DROP:', fg='red', bold=True)} {closing}")

            verdict = ai_roast.get("verdict", "")
            if verdict:
                click.echo(click.style(f"\n  Verdict: \"{verdict}\"", fg="yellow", italic=True))

        elif ai_roast and ai_roast.get("error"):
            # Fallback static roasts
            click.echo("\n" + click.style("  📴 OFFLINE ROAST (Static Mode)", fg="cyan", bold=True))
            from burnbook.roaster import Roaster
            roaster = Roaster.__new__(Roaster)
            fallback = roaster._fallback_roast(score)
            click.echo(click.style(f"\n  {fallback}", fg="yellow"))
        else:
            # No AI roast available
            click.echo("\n" + click.style("  📴 STATIC ROAST MODE", fg="cyan", bold=True))
            from burnbook.roaster import Roaster
            roaster = Roaster.__new__(Roaster)
            fallback = roaster._fallback_roast(score)
            click.echo(click.style(f"\n  {fallback}", fg="yellow"))

        # ── Footer ────────────────────────────────────────────────────────────
        click.echo("\n" + "═" * 60)
        click.echo(click.style(
            f"  Generated by BurnBook 🔥 | {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            fg="bright_black"
        ))
        if not results.get("ai_roast"):
            click.echo(click.style(
                "  💡 Add OPENROUTER_API_KEY for AI-powered roasting",
                fg="bright_black"
            ))
        click.echo("═" * 60 + "\n")

    def _render_score_bar(self, score: int, color: str) -> None:
        """Render a visual score bar."""
        width = 40
        filled = int(score / 100 * width)
        empty = width - filled
        bar = click.style("█" * filled, fg=color) + click.style("░" * empty, fg="bright_black")
        click.echo(f"  [{bar}] {click.style(str(score), fg=color, bold=True)}/100")

    def _mini_bar(self, score: int, width: int = 15) -> str:
        """Render a mini score bar."""
        filled = int(score / 100 * width)
        empty = width - filled
        return "█" * filled + "░" * empty


class JSONFormatter:
    """JSON output — for machines and people who like to process data."""

    def render(self, results: Dict[str, Any]) -> str:
        output = {
            "burnbook_version": "1.0.0",
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "target": results.get("target"),
            "language": results.get("language"),
            "score": results.get("score"),
            "verdict": get_score_label(results.get("score", 0)),
            "files_analyzed": results.get("files_analyzed"),
            "elapsed_seconds": results.get("elapsed_seconds"),
            "metrics": results.get("metrics", {}),
            "category_scores": results.get("category_scores", {}),
            "issues": results.get("issues", []),
            "ai_roast": results.get("ai_roast"),
        }
        return json.dumps(output, indent=2, default=str)


class HTMLFormatter:
    """HTML report — pretty charts and brutal commentary."""

    def __init__(self, severity: str = "brutal"):
        self.severity = severity

    def render(self, results: Dict[str, Any]) -> str:
        score = results.get("score", 0)
        emoji, label, color, hex_color = get_score_band(score)
        metrics = results.get("metrics", {})
        issues = results.get("issues", [])
        category_scores = results.get("category_scores", {})
        ai_roast = results.get("ai_roast", {}) or {}
        language = results.get("language", "unknown")
        target = results.get("target", "")
        generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Build category chart data
        cat_labels = json.dumps(list(category_scores.keys()))
        cat_values = json.dumps(list(category_scores.values()))
        cat_colors = json.dumps([
            get_score_band(v)[3] for v in category_scores.values()
        ])

        # Build issues table
        issues_html = self._render_issues_table(issues)
        ai_section = self._render_ai_section(ai_roast)
        sev_counts = metrics.get("severity_counts", {})

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>BurnBook Report — {Path(target).name}</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
  <style>
    :root {{
      --bg: #0d1117;
      --surface: #161b22;
      --surface2: #21262d;
      --border: #30363d;
      --text: #c9d1d9;
      --text-muted: #8b949e;
      --accent: {hex_color};
      --red: #ff1744;
      --orange: #ff6d00;
      --yellow: #ffd600;
      --cyan: #00e5ff;
      --green: #00e676;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', monospace;
      background: var(--bg);
      color: var(--text);
      padding: 2rem;
      line-height: 1.6;
    }}
    .container {{ max-width: 1200px; margin: 0 auto; }}
    header {{
      text-align: center;
      margin-bottom: 2rem;
      padding: 2rem;
      background: var(--surface);
      border-radius: 12px;
      border: 1px solid var(--border);
    }}
    .logo {{ font-size: 3rem; font-weight: 900; color: var(--accent); letter-spacing: -2px; }}
    .subtitle {{ color: var(--text-muted); margin-top: 0.5rem; }}
    .score-hero {{
      margin: 2rem auto;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 1rem;
    }}
    .score-circle {{
      width: 180px;
      height: 180px;
      border-radius: 50%;
      border: 6px solid {hex_color};
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      background: var(--surface2);
      box-shadow: 0 0 40px {hex_color}44;
    }}
    .score-number {{ font-size: 3.5rem; font-weight: 900; color: {hex_color}; line-height: 1; }}
    .score-max {{ font-size: 1rem; color: var(--text-muted); }}
    .verdict {{ font-size: 1.4rem; font-weight: 700; color: {hex_color}; text-align: center; }}
    .emoji-verdict {{ font-size: 2.5rem; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.5rem; margin-bottom: 2rem; }}
    .card {{
      background: var(--surface);
      border-radius: 12px;
      border: 1px solid var(--border);
      padding: 1.5rem;
    }}
    .card h2 {{ font-size: 1rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 1rem; }}
    .stat-row {{ display: flex; justify-content: space-between; padding: 0.4rem 0; border-bottom: 1px solid var(--border); }}
    .stat-row:last-child {{ border-bottom: none; }}
    .stat-val {{ font-weight: 700; color: var(--text); }}
    .sev-badge {{
      display: inline-block;
      padding: 2px 8px;
      border-radius: 4px;
      font-size: 0.75rem;
      font-weight: 700;
      margin-right: 4px;
    }}
    .sev-critical {{ background: #ff174422; color: #ff1744; border: 1px solid #ff174444; }}
    .sev-high     {{ background: #ff6d0022; color: #ff6d00; border: 1px solid #ff6d0044; }}
    .sev-medium   {{ background: #ffd60022; color: #ffd600; border: 1px solid #ffd60044; }}
    .sev-low      {{ background: #00e5ff22; color: #00e5ff; border: 1px solid #00e5ff44; }}
    .sev-info     {{ background: #8b949e22; color: #8b949e; border: 1px solid #8b949e44; }}
    .chart-container {{ position: relative; height: 300px; }}
    .issues-table {{ width: 100%; border-collapse: collapse; font-size: 0.85rem; }}
    .issues-table th {{
      background: var(--surface2);
      color: var(--text-muted);
      padding: 0.75rem 1rem;
      text-align: left;
      border-bottom: 1px solid var(--border);
    }}
    .issues-table td {{ padding: 0.6rem 1rem; border-bottom: 1px solid var(--border); vertical-align: top; }}
    .issues-table tr:hover td {{ background: var(--surface2); }}
    .ai-roast {{
      background: linear-gradient(135deg, #1a0833, #0d1117);
      border: 1px solid #7b2fff44;
      border-radius: 12px;
      padding: 2rem;
      margin-bottom: 2rem;
    }}
    .ai-roast h2 {{ color: #bf5fff; font-size: 1.3rem; margin-bottom: 1.5rem; }}
    .ai-overall {{ font-size: 1.1rem; color: var(--text); font-style: italic; border-left: 3px solid #bf5fff; padding-left: 1rem; margin-bottom: 1.5rem; }}
    .ai-section {{ margin-bottom: 1rem; background: var(--surface2); border-radius: 8px; padding: 1rem; }}
    .ai-section h3 {{ color: #00e5ff; font-size: 0.9rem; margin-bottom: 0.5rem; }}
    .ai-tip {{ color: var(--green); font-size: 0.85rem; margin-top: 0.5rem; }}
    .closing {{ color: var(--red); font-weight: 700; font-size: 1.1rem; margin-top: 1.5rem; }}
    footer {{ text-align: center; color: var(--text-muted); padding: 2rem; font-size: 0.85rem; }}
    .category-bar {{ display: flex; align-items: center; gap: 1rem; margin-bottom: 0.6rem; }}
    .category-name {{ width: 120px; font-size: 0.85rem; color: var(--text-muted); }}
    .bar-track {{ flex: 1; height: 8px; background: var(--surface2); border-radius: 4px; overflow: hidden; }}
    .bar-fill {{ height: 100%; border-radius: 4px; transition: width 0.3s; }}
    .category-score {{ width: 40px; text-align: right; font-size: 0.85rem; font-weight: 700; }}
  </style>
</head>
<body>
<div class="container">
  <header>
    <div class="logo">🔥 BurnBook</div>
    <div class="subtitle">The code quality roaster that tells it like it is</div>
    <div class="subtitle" style="margin-top:0.5rem; font-size:0.85rem;">
      Target: <code style="color:{hex_color}">{target}</code> &nbsp;|&nbsp;
      Language: <code>{language}</code> &nbsp;|&nbsp;
      Generated: {generated_at}
    </div>
    <div class="score-hero">
      <div class="emoji-verdict">{emoji}</div>
      <div class="score-circle">
        <span class="score-number">{score}</span>
        <span class="score-max">/100</span>
      </div>
      <div class="verdict">{label}</div>
    </div>
  </header>

  <div class="grid">
    <!-- Stats card -->
    <div class="card">
      <h2>📊 Summary</h2>
      <div class="stat-row"><span>Files analyzed</span><span class="stat-val">{metrics.get('files_analyzed', 0)}</span></div>
      <div class="stat-row"><span>Total lines</span><span class="stat-val">{metrics.get('total_lines', 0):,}</span></div>
      <div class="stat-row"><span>Total issues</span><span class="stat-val">{metrics.get('total_issues', 0)}</span></div>
      <div class="stat-row"><span>Issues per file</span><span class="stat-val">{metrics.get('issues_per_file', 0)}</span></div>
      <div class="stat-row"><span>Elapsed</span><span class="stat-val">{results.get('elapsed_seconds', 0)}s</span></div>
    </div>

    <!-- Severity card -->
    <div class="card">
      <h2>⚠️ Severity Breakdown</h2>
      {"".join(
        f'<div class="stat-row"><span><span class="sev-badge sev-{sev}">{sev.upper()}</span></span><span class="stat-val">{sev_counts.get(sev, 0)}</span></div>'
        for sev in ["critical", "high", "medium", "low", "info"]
      )}
    </div>

    <!-- Category scores card -->
    <div class="card">
      <h2>🎯 Category Scores</h2>
      {"".join(
        f'''<div class="category-bar">
          <span class="category-name">{CATEGORY_ICONS.get(cat, "•")} {cat}</span>
          <div class="bar-track"><div class="bar-fill" style="width:{v}%; background:{get_score_band(v)[3]}"></div></div>
          <span class="category-score" style="color:{get_score_band(v)[3]}">{v}</span>
        </div>'''
        for cat, v in sorted(category_scores.items(), key=lambda x: x[1])
      )}
    </div>
  </div>

  <!-- Chart -->
  <div class="card" style="margin-bottom:2rem">
    <h2>📈 Category Score Radar</h2>
    <div class="chart-container">
      <canvas id="radarChart"></canvas>
    </div>
  </div>

  {ai_section}

  <!-- Issues Table -->
  <div class="card" style="margin-bottom:2rem; overflow-x:auto;">
    <h2>🚨 Issues ({len(issues)} total)</h2>
    {issues_html}
  </div>

  <footer>
    Generated by <strong>BurnBook</strong> 🔥 &nbsp;|&nbsp;
    <a href="https://github.com/burnbook/burnbook" style="color:#bf5fff">github.com/burnbook/burnbook</a>
    &nbsp;|&nbsp; MIT License
  </footer>
</div>

<script>
const ctx = document.getElementById('radarChart').getContext('2d');
new Chart(ctx, {{
  type: 'radar',
  data: {{
    labels: {cat_labels},
    datasets: [{{
      label: 'Score',
      data: {cat_values},
      backgroundColor: 'rgba(191, 95, 255, 0.15)',
      borderColor: '#bf5fff',
      pointBackgroundColor: {cat_colors},
      pointBorderColor: '#fff',
      pointRadius: 5,
    }}]
  }},
  options: {{
    responsive: true,
    maintainAspectRatio: false,
    scales: {{
      r: {{
        min: 0,
        max: 100,
        ticks: {{ color: '#8b949e', stepSize: 20 }},
        grid: {{ color: '#30363d' }},
        pointLabels: {{ color: '#c9d1d9', font: {{ size: 12 }} }},
        angleLines: {{ color: '#30363d' }},
      }}
    }},
    plugins: {{
      legend: {{ display: false }},
    }}
  }}
}});
</script>
</body>
</html>"""

    def _render_issues_table(self, issues: List[Dict]) -> str:
        if not issues:
            return "<p style='color:var(--green); padding:1rem'>🎉 No issues found!</p>"

        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
        sorted_issues = sorted(
            issues,
            key=lambda x: severity_order.get(x.get("severity", "low"), 3)
        )[:50]

        rows = ""
        for issue in sorted_issues:
            sev = issue.get("severity", "low")
            cat = issue.get("category", "style")
            msg = issue.get("message", "").replace("<", "&lt;").replace(">", "&gt;")
            file_path = issue.get("file", "")
            line_num = issue.get("line", "")
            rule_id = issue.get("rule_id", "")
            fname = Path(file_path).name if file_path else ""
            icon = SEVERITY_ICONS.get(sev, "•")

            rows += f"""
            <tr>
              <td><span class="sev-badge sev-{sev}">{icon} {sev.upper()}</span></td>
              <td><code style="color:var(--cyan)">{cat}</code></td>
              <td>{msg[:120]}{'…' if len(msg) > 120 else ''}</td>
              <td><code style="color:var(--text-muted)">{fname}{f':{line_num}' if line_num else ''}</code></td>
              <td><code style="color:var(--text-muted);font-size:0.75rem">{rule_id}</code></td>
            </tr>"""

        return f"""
        <table class="issues-table">
          <thead>
            <tr>
              <th>Severity</th>
              <th>Category</th>
              <th>Issue</th>
              <th>Location</th>
              <th>Rule</th>
            </tr>
          </thead>
          <tbody>{rows}</tbody>
        </table>
        {"<p style='color:var(--text-muted);padding:0.75rem;font-size:0.8rem'>Showing top 50 issues.</p>" if len(issues) > 50 else ""}
        """

    def _render_ai_section(self, ai_roast: Dict) -> str:
        if not ai_roast or ai_roast.get("error"):
            return ""

        overall = ai_roast.get("overall", "")
        sections = ai_roast.get("sections", [])
        closing = ai_roast.get("closing", "")
        verdict = ai_roast.get("verdict", "")

        sections_html = ""
        for section in sections:
            cat = section.get("category", "")
            roast = section.get("roast", "")
            tip = section.get("tip", "")
            icon = CATEGORY_ICONS.get(cat.lower(), "•")

            sections_html += f"""
            <div class="ai-section">
              <h3>{icon} {cat.upper()}</h3>
              <p>💬 {roast}</p>
              {f'<p class="ai-tip">💡 Fix: {tip}</p>' if tip else ''}
            </div>"""

        return f"""
        <div class="ai-roast">
          <h2>🤖 AI Roast Master</h2>
          {f'<div class="ai-overall">"{overall}"</div>' if overall else ''}
          {sections_html}
          {f'<div class="closing">🎤 {closing}</div>' if closing else ''}
          {f'<p style="color:#ffd600;margin-top:1rem;font-style:italic;">Verdict: "{verdict}"</p>' if verdict else ''}
        </div>
        """
