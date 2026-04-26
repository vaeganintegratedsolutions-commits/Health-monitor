import requests
import smtplib
import os
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- Configuration (Pulled from GitHub Secrets) ---
SENDER_EMAIL = os.environ.get("EMAIL_USER")
SENDER_PASSWORD = os.environ.get("EMAIL_PASS")
RECEIVER_EMAIL = os.environ.get("EMAIL_RECEIVER")

websites = {
    "Mango_Meadows": "https://mangomeadows.vaeganapps.com",
    "RR_Enterprise": "https://rr-enterprise1.vercel.app",
    "Gitea": "https://git.vaeganapps.com",
}


def check_sites():
    results = []
    for name, url in websites.items():
        try:
            r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            if r.status_code == 200:
                status = "ONLINE"
                status_class = "online"
                badge = "✅git "
            else:
                status = f"CODE {r.status_code}"
                status_class = "warning"
                badge = "⚠️"
            response_time = round(r.elapsed.total_seconds() * 1000)
        except Exception:
            status = "DOWN"
            status_class = "down"
            badge = "❌"
            response_time = None

        results.append({
            "name": name.replace("_", " "),
            "url": url,
            "status": status,
            "status_class": status_class,
            "badge": badge,
            "response_time": f"{response_time} ms" if response_time is not None else "—",
        })
    return results


def build_html_report(results):
    ist_now = datetime.utcnow() + timedelta(hours=5, minutes=30)
    now = ist_now.strftime("%B %d, %Y  •  %H:%M IST")
    total = len(results)
    online = sum(1 for r in results if r["status_class"] == "online")
    down = sum(1 for r in results if r["status_class"] == "down")
    warn = total - online - down

    rows = ""
    for r in results:
        rows += f"""
        <tr>
          <td class="site-name">{r['name']}</td>
          <td class="site-url"><a href="{r['url']}">{r['url']}</a></td>
          <td><span class="badge {r['status_class']}">{r['status']}</span></td>
          <td class="response-time">{r['response_time']}</td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Website Status Report</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600;700&display=swap');

  * {{ margin: 0; padding: 0; box-sizing: border-box; }}

  body {{
    background: #0d1117;
    color: #c9d1d9;
    font-family: 'IBM Plex Sans', sans-serif;
    padding: 32px 16px;
  }}

  .wrapper {{
    max-width: 680px;
    margin: 0 auto;
  }}

  /* ── Header ── */
  .header {{
    background: linear-gradient(135deg, #161b22 0%, #0d1117 100%);
    border: 1px solid #30363d;
    border-radius: 12px 12px 0 0;
    padding: 32px 36px 28px;
    border-bottom: 2px solid #21262d;
  }}

  .header-top {{
    display: flex;
    align-items: center;
    margin-bottom: 6px;
  }}

  h1 {{
    font-size: 20px;
    font-weight: 700;
    color: #f0f6fc;
    letter-spacing: -0.3px;
  }}

  .subtitle {{
    font-size: 12px;
    color: #8b949e;
    font-family: 'IBM Plex Mono', monospace;
    margin-left: 0px;
  }}

  /* ── Summary cards ── */
  .summary {{
    background: #161b22;
    border: 1px solid #30363d;
    border-top: none;
    padding: 20px 0;
    display: flex;
    border-bottom: 1px solid #21262d;
  }}

  .stat {{ text-align: center; flex: 1; padding: 0 24px; }}

  .stat-value {{
    font-size: 28px;
    font-weight: 700;
    font-family: 'IBM Plex Mono', monospace;
    line-height: 1;
  }}

  .stat-label {{
    font-size: 11px;
    color: #8b949e;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 4px;
  }}

  .stat-value.green  {{ color: #3fb950; }}
  .stat-value.red    {{ color: #f85149; }}
  .stat-value.yellow {{ color: #d29922; }}
  .stat-value.muted  {{ color: #8b949e; }}

  .divider {{ width: 1px; background: #30363d; }}

  /* ── Table ── */
  .table-wrap {{
    background: #161b22;
    border: 1px solid #30363d;
    border-top: none;
    border-radius: 0 0 12px 12px;
    overflow: hidden;
  }}

  table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 13.5px;
  }}

  thead tr {{
    background: #0d1117;
    border-bottom: 1px solid #30363d;
  }}

  thead th {{
    padding: 12px 20px;
    text-align: left;
    font-size: 11px;
    font-weight: 600;
    color: #8b949e;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    font-family: 'IBM Plex Mono', monospace;
  }}

  tbody tr {{
    border-bottom: 1px solid #21262d;
    transition: background 0.15s;
  }}

  tbody tr:last-child {{ border-bottom: none; }}
  tbody tr:hover {{ background: #1c2128; }}

  td {{
    padding: 14px 20px;
    vertical-align: middle;
  }}

  .site-name {{
    font-weight: 600;
    color: #f0f6fc;
    white-space: nowrap;
  }}

  .site-url a {{
    color: #58a6ff;
    text-decoration: none;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12px;
  }}

  .site-url a:hover {{ text-decoration: underline; }}

  .response-time {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12px;
    color: #8b949e;
    white-space: nowrap;
  }}

  /* ── Status badges ── */
  .badge {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 11.5px;
    font-weight: 600;
    letter-spacing: 0.3px;
    white-space: nowrap;
  }}

  .badge.online  {{ background: rgba(63,185,80,.15);  color: #3fb950; border: 1px solid rgba(63,185,80,.3);  }}
  .badge.warning {{ background: rgba(210,153,34,.15); color: #d29922; border: 1px solid rgba(210,153,34,.3); }}
  .badge.down    {{ background: rgba(248,81,73,.15);  color: #f85149; border: 1px solid rgba(248,81,73,.3);  }}

  /* ── Footer ── */
  .footer {{
    margin-top: 20px;
    text-align: center;
    font-size: 11px;
    color: #484f58;
    font-family: 'IBM Plex Mono', monospace;
  }}
</style>
</head>
<body>
<div class="wrapper">

  <div class="header">
    <div class="header-top">

      <h1>Website Status Report</h1>
    </div>
    <div class="subtitle">Generated {now}</div>
  </div>

  <div class="summary">
    <div class="stat">
      <div class="stat-value muted">{total}</div>
      <div class="stat-label">Total</div>
    </div>
    <div class="divider"></div>
    <div class="stat">
      <div class="stat-value green">{online}</div>
      <div class="stat-label">Online</div>
    </div>
    <div class="divider"></div>
    <div class="stat">
      <div class="stat-value yellow">{warn}</div>
      <div class="stat-label">Warning</div>
    </div>
    <div class="divider"></div>
    <div class="stat">
      <div class="stat-value red">{down}</div>
      <div class="stat-label">Down</div>
    </div>
  </div>

  <div class="table-wrap">
    <table>
      <thead>
        <tr>
          <th>Site</th>
          <th>URL</th>
          <th>Status</th>
          <th>Response</th>
        </tr>
      </thead>
      <tbody>{rows}
      </tbody>
    </table>
  </div>

  <div class="footer">Automated monitor · Runs daily via GitHub Actions</div>

</div>
</body>
</html>"""
    return html


def send_email(html_content):
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        print("Missing credentials! Check your GitHub Secrets.")
        return

    msg = MIMEMultipart("alternative")
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL
    msg["Subject"] = "Daily Website Status Report"

    # Fallback plain-text part
    plain = "Website Status Report\nCheck your email client for the full HTML report."
    msg.attach(MIMEText(plain, "plain"))
    msg.attach(MIMEText(html_content, "html"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")


if __name__ == "__main__":
    results = check_sites()
    html_report = build_html_report(results)
    send_email(html_report)
