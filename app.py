import os
import re
import time
import datetime
import logging
import threading
import requests
import subprocess
import pdfplumber
from flask import Flask, render_template, request, jsonify
from threading import Lock
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.ssl_ import create_urllib3_context

# Flask setup
app = Flask(__name__)

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
app.logger = logging.getLogger(__name__)

# PDF source
URL = "https://files.floridalottery.com/exptkt/l6.pdf"
SAVE_PATH = "fla_lotto_results.pdf"
DOWNLOAD_DIR = os.getcwd()

# Global variables
winners = None
winners_lock = Lock()

# Regex to extract dates + numbers
PATTERN = re.compile(
    r'(\d{2}/\d{2}/\d{2})\s+(\d+)-\s*(\d+)-\s*(\d+)-\s*(\d+)-\s*(\d+)-\s*(\d+)\s*(LOTTO(?: DP)?|LOTTO)?'
)


class TLSAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        ctx = create_urllib3_context()
        ctx.set_ciphers('DEFAULT@SECLEVEL=1')  # Lower security level if server has weak ciphers
        kwargs['ssl_context'] = ctx
        return super().init_poolmanager(*args, **kwargs)

def download_pdf(refresh=False):
    if refresh and os.path.exists(SAVE_PATH):
        os.rename(SAVE_PATH, SAVE_PATH.replace(".pdf", "_backup.pdf"))
        app.logger.info("Existing PDF backed up.")

    app.logger.info("Downloading PDF via curl...")

    curl_command = [
        "curl",
        "-L",  # Follow redirects
        "-o", SAVE_PATH,
        "-H", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
              "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "-H", "Referer: https://www.floridalottery.com/",
        URL
    ]

    try:
        result = subprocess.run(curl_command, capture_output=True, text=True, check=True)
        app.logger.info("PDF downloaded successfully via curl.")
    except subprocess.CalledProcessError as e:
        app.logger.error(f"Failed to download PDF via curl: {e.stderr}")

    if refresh:
        backup = SAVE_PATH.replace(".pdf", "_backup.pdf")
        if os.path.exists(backup):
            os.remove(backup)
            app.logger.info("Backup file deleted.")

# ===== UTILS =====

# def download_pdf(refresh=False):
#     """Download the lotto PDF from URL."""
#     try:
#         if refresh and os.path.exists(SAVE_PATH):
#             os.rename(SAVE_PATH, SAVE_PATH.replace(".pdf", "_backup.pdf"))
#             app.logger.info("Existing PDF backed up.")

#         app.logger.info("Downloading PDF...")
#         r = requests.get(URL)
#         r.raise_for_status()
#         with open(SAVE_PATH, 'wb') as f:
#             f.write(r.content)
#         app.logger.info("PDF downloaded successfully.")

#         if refresh:
#             backup = SAVE_PATH.replace(".pdf", "_backup.pdf")
#             if os.path.exists(backup):
#                 os.remove(backup)
#                 app.logger.info("Backup file deleted.")

#     except Exception as e:
#         app.logger.error(f"Error downloading PDF: {e}")

def extract_numbers_from_pdf():
    """Extract numbers from PDF and return them as a nested list."""
    matches = []
    count = 0
    with pdfplumber.open(SAVE_PATH) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            page_matches = PATTERN.findall(text)
            matches.append(page_matches)
            count += len(page_matches)

    app.logger.info(f"Extracted {count} total matches from {len(matches)} pages.")
    return matches

def convert_to_datetime(date_str):
    return datetime.datetime.strptime(date_str, "%m/%d/%y")

# ===== ROUTES =====

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/lotto')
def lotto():
    return render_template('lotto.html')

@app.route('/single_position_winning_numbers')
def single_position_winning_numbers():
    return render_template('single_position_winning_numbers.html')

@app.route('/winning_numbers')
def winning_numbers():
    return render_template('winning_numbers.html')

@app.route('/get_numbers', methods=['GET'])
def get_numbers():
    position = int(request.args.get('position', 0)) - 1
    if position < 0 or position > 5:
        return "Invalid number, please select a number between 1 and 6."
    selected_numbers = []
    with winners_lock:
        for page in winners:
            for number in page:
                selected_numbers.append(number[1 + position])
    return jsonify({'numbers': selected_numbers})

@app.route('/get_winners', methods=['GET'])
def get_winners():
    refresh_flag = request.args.get('refresh', '0') == '1'

    global winners
    with winners_lock:
        if refresh_flag:
            app.logger.info("Manual refresh requested via URL param.")
            download_pdf(refresh=True)
            winners = extract_numbers_from_pdf()

        selected_numbers = [number for page in winners for number in page]
    return jsonify({'numbers': selected_numbers})

# ===== BACKGROUND REFRESH THREAD =====

def refresh_if_needed():
    global winners
    while True:
        try:
            with winners_lock:
                last_draw_date = convert_to_datetime(winners[0][0][0])
            days_since = (datetime.datetime.now() - last_draw_date).days
            app.logger.info(f"It has been {days_since} days since last lottery draw.")
            if days_since >= 3:
                app.logger.info("Refreshing lotto data automatically...")
                with winners_lock:
                    download_pdf(refresh=True)
                    winners = extract_numbers_from_pdf()
        except Exception as e:
            app.logger.error(f"Error in refresh thread: {e}")
        time.sleep(3600)

# ===== APP STARTUP =====

def init_app():
    global winners
    if not os.path.exists(SAVE_PATH):
        app.logger.info("No local PDF found, downloading now...")
        download_pdf()
    winners = extract_numbers_from_pdf()
    threading.Thread(target=refresh_if_needed, daemon=True).start()
    app.logger.info("Background refresh thread started.")

if __name__ == '__main__':
    init_app()
    app.run(debug=True, use_reloader=False)
else:
    init_app()
