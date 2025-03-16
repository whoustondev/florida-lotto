
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Set up headless Chrome options
options = Options()
options.headless = True
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--remote-debugging-port=9222')  # Optional, for debugging

# Path to ChromeDriver
driver = webdriver.Chrome(options=options)

# Example: navigate to a webpage
driver.get('http://example.com')

# Perform your automation tasks here

driver.quit()

