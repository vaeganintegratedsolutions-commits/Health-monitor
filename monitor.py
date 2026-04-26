import requests
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- Configuration (Pulled from GitHub Secrets) ---
SENDER_EMAIL = os.environ.get("EMAIL_USER")
SENDER_PASSWORD = os.environ.get("EMAIL_PASS")
RECEIVER_EMAIL = os.environ.get("EMAIL_RECEIVER")

websites = {
    "Mango_Meadows": "https://mangomeadows.vaeganapps.com",
    "RR_Enterprise": "https://rr-enterprise1.vercel.app",
    "Mahesh_Saravanan": "https://mahesh-saravanan.com",
    "Gitea": "https://git.vaeganapps.com"
}

def get_status_report():
    report = "🚀 Website Status Report\n"
    report += "=" * 40 + "\n"
    report += f"{'Site Name':<20} | {'Status'}\n"
    report += "-" * 40 + "\n"
    for name, url in websites.items():
        try:
            # Added a user agent so sites don't block the GitHub Action bot
            r = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            status = "✅ ONLINE" if r.status_code == 200 else f"⚠️ CODE {r.status_code}"
        except:
            status = "❌ DOWN"
        report += f"{name:<20} | {status}\n"
    report += "=" * 40
    return report

def send_email(content):
    # Guard clause to ensure secrets are actually loaded
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        print("Missing credentials! Check your GitHub Secrets.")
        return

    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL
    msg['Subject'] = "Daily Website Monitoring Report"
    msg.attach(MIMEText(content, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

if __name__ == "__main__":
    report_text = get_status_report()
    send_email(report_text)