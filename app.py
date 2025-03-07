
from flask import Flask, render_template, request
import pdfplumber
import re

app = Flask(__name__)

from flask import Flask, render_template, request
import pdfplumber
import re
import re
import pandas as pd



app = Flask(__name__)

# Function to extract and process the PDF data
def extract_numbers_from_pdf():
    numbers_data = []  # Will store lists of numbers

    # Regular expression to match the date and numbers
    pattern = r'(\d{2}/\d{2}/\d{2})\s(\d+)-\s(\d+)-\s(\d+)-\s(\d+)-\s(\d+)-\s(\d+)\s*(LOTTO(?: DP)?$|LOTTO)'

    # Find all matches in the text
    

    # Create a list of column names
    columns = ['Date', 'Number 1', 'Number 2', 'Number 3', 'Number 4', 'Number 5', 'Number 6', 'Play Type']


    matches = []
    # Open and extract text from the PDF
    with pdfplumber.open('fla-lottery-results.pdf') as pdf:
        for page in pdf.pages:
            text = page.extract_text()

            matches.append(re.findall(pattern, text))
            
    print(matches)

    return matches

# Global variable to store the extracted numbers
winning_numbers = extract_numbers_from_pdf()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_numbers', methods=['POST'])
def get_numbers():
    # Get the number index from the form
    position = int(request.form.get('position')) - 1  # Convert to zero-based index
    # Extract the corresponding number from all datasets
    if position < 0 or position > 5:
        return "Invalid number, please select a number between 1 and 6."
    selected_numbers = []
    for page in winning_numbers:
        for number in page:
            selected_numbers.append(number[1+position])
    return render_template('index.html', numbers=selected_numbers, position=position + 1)

if __name__ == '__main__':
    app.run(debug=True)
