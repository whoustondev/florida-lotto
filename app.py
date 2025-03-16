

import pdfplumber
import re
import sys
import os
import datetime
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

import threading
import os
os.environ['FLASK_ENV'] = 'development'

from flask import Flask, render_template, request, jsonify
import pdfplumber
import re

app = Flask(__name__)
# Global variable to store the extracted numbers
winners = None
# logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, 
#                     format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define the URL of the PDF to be downloaded
url = "https://files.floridalottery.com/exptkt/l6.pdf?_gl=1*1kcikff*_ga*MTczOTQ0NDAxMC4xNzQwODAwOTk0*_ga_3E9WN4YVMF*MTc0MTUyOTExNC40LjEuMTc0MTUyOTEzMy40MS4wLjA."
save_path = "fla_lotto_results.pdf"
# handler = logging.StreamHandler(stream=sys.stdout)
# handler.setFormatter(logging.Formatter('flask [%(levelname)s] %(message)s'))
# logger.addHandler(handler)

# app.logger.addHandler(handler)
# PDF URL & Save Path
download_path = os.getcwd() # Adjust for your OS

def rename_file(old_name, new_name):
    try:
        os.rename(old_name, new_name)
        logger.info(f"File renamed from {old_name} to {new_name}")
    except FileNotFoundError:
        logger.info("Error: File not found.")
    except PermissionError:
        logger.info("Error: Permission denied.")
    except Exception as e:
        logger.info(f"Error renaming file: {e}")
    except Exception as e:
            logger.info(f"Error downloading PDF: {str(e)}")

def download_pdf(refresh=False):
    # Set up Chrome options for headless downloading
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")  # Headless mode (Chrome 109+)
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Ensure Chrome auto-downloads PDFs instead of opening them
    prefs = {
        "download.default_directory": download_path,
        "plugins.always_open_pdf_externally": True,  # Force download instead of opening
        "download.prompt_for_download": False,
        "download.directory_upgrade": True
    }
    chrome_options.add_experimental_option("prefs", prefs)

    # Initialize WebDriver
    driver = webdriver.Chrome(service=Service('/usr/local/bin/chromedriver'), options=chrome_options)

    try:
        if refresh:
            # so we can download l6 and rename it 
            rename_file("fla_lotto_results.pdf", "fla_lotto_results_backup.pdf")
        logger.info("Opening URL...")
        driver.get(url)

        # Allow time for the download to complete
        time.sleep(10)

        logger.info(f"PDF should be downloaded in: {download_path}")

        rename_file("l6.pdf", "fla_lotto_results.pdf")

        if os.path.exists("fla_lotto_results_backup.pdf"):
            os.remove("fla_lotto_results_backup.pdf")
            logger.info("File deleted successfully")
        else:
            # This should never happen
            logger.info("File not found")

    finally:
        driver.quit()


# Function to extract and process the PDF data
def extract_numbers_from_pdf():
    numbers_data = []  # Will store lists of numbers
    # Regular expression to match the date and numbers
    pattern = r'(\d{2}/\d{2}/\d{2})\s(\d+)-\s(\d+)-\s(\d+)-\s(\d+)-\s(\d+)-\s(\d+)\s*(LOTTO(?: DP\s*)?$|LOTTO DP|LOTTO\s*)'
    # Find all matches in the text
    # Create a list of column names
    columns = ['Date', 'Number 1', 'Number 2', 'Number 3', 'Number 4', 'Number 5', 'Number 6', 'Play Type']
    matches = []
    count = 0
    # Open and extract text from the PDF
    with pdfplumber.open('fla_lotto_results.pdf') as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            matches.append(re.findall(pattern, text))
            count = count + len(matches)
    logger.info("Found {0} pages of data".format(str(len(pdf.pages))))
    logger.info("Found {0} matches".format(str(count)))
    return matches



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
    # Get the number index from the form
    position = int(request.args.get('position')) - 1  # Convert to zero-based index
    # Extract the corresponding number from all datasets
    if position < 0 or position > 5:
        return "Invalid number, please select a number between 1 and 6."
    selected_numbers = []
    for page in winners:
        for number in page:
            selected_numbers.append(number[1+position])
    #return render_template('index.html', numbers=selected_numbers, position=position + 1)
    return jsonify({'numbers': selected_numbers})


@app.route('/get_winners', methods=['GET'])
def get_winners():
    selected_numbers = []
    for page in winners:
        for number in page:
            selected_numbers.append(number)
    #return render_template('index.html', numbers=selected_numbers, position=position + 1)
    return jsonify({'numbers': selected_numbers})
    #return jsonify({"message": "You entered position", "position": position})



def convert_to_datetime(date_str):
    return datetime.datetime.strptime(date_str, "%m/%d/%y")


    
if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel("DEBUG")
    app.logger.critical("This is a CRITICAL message in the gunicorn logger")
    if os.path.exists(save_path):
        logger.info("File exists")
    else:
        logger.info("File not found. Downloading now...")
        download_pdf()
    app.logger.info("Extracting winners")
    winners = extract_numbers_from_pdf()
    def refresh_if_we_have_to():
        global winners
        app.logger.debug("Inside refresh func")
        # TODO: We can be more efficient here, but now we have bigger fish
        while True:
            logger.info("Refresh checker is running...")
            days_since = (datetime.datetime.now() - convert_to_datetime(winners[0][0][0])).days
            logger.info("It has been {0} days since last lottery draw".format(days_since))
            if days_since >=3:
                logger.info("Refreshing lotto data")
                # do refresh
                download_pdf(refresh=True)
                winners = extract_numbers_from_pdf()
            time.sleep(3600)

    # Create and start the thread
    
    thread = threading.Thread(target=refresh_if_we_have_to, daemon=True)  
    thread.start()
    app.logger.critical("Started Thread, now lets run the app")
    # app.run(debug=True, use_reloader=False)  # use_reloader=False to avoid starting multiple threads
    

