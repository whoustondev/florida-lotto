
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# import time
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options


# url = "https://files.floridalottery.com/exptkt/l6.pdf?_gl=1*1kcikff*_ga*MTczOTQ0NDAxMC4xNzQwODAwOTk0*_ga_3E9WN4YVMF*MTc0MTUyOTExNC40LjEuMTc0MTUyOTEzMy40MS4wLjA."
# save_path = "florida_lottery_pdf_two.pdf"

# def download_pdf():
#     # Set up Chrome options to allow downloading
#     chrome_options = Options()
#     chrome_options.add_argument("--headless")  # Optional: Run in headless mode (without opening a browser window)
#     chrome_options.add_argument("--no-sandbox")
#     chrome_options.add_argument("--disable-dev-shm-usage")
    
#     # Specify the download directory
#     prefs = {
#         "download.default_directory": "/Users/whouston/Code/python/proj-fla-lotto"  # Replace with your desired download directory
#     }
#     chrome_options.add_experimental_option("prefs", prefs)

#     # Path to ChromeDriver (make sure it's correctly set in your system)
#     # driver = webdriver.Chrome(executable_path='/path/to/chromedriver', options=chrome_options)
#     driver = webdriver.Chrome(service=Service('/usr/local/bin/chromedriver'))
#     try:
#         # Open the URL
#         driver.get(url)

#         # Wait for a few seconds to ensure the page is loaded and the download link is ready
#         time.sleep(5)  # Adjust the sleep time if necessary

#         # Now that the browser is open, Selenium will automatically trigger the download
#         print(f"Downloading PDF to {save_path}")
#         # Use JavaScript to access the Shadow DOM and find the button

#         shadow_root_js = """
#         let host = document.querySelector('first-shadow-host');
#         let shadow = host.shadowRoot;
#         let button = shadow.querySelector('second-shadow-host').shadowRoot.querySelector('cr-icon-button#download');
#         return button;
#         """
#         download_button = driver.execute_script(shadow_root_js)

#         # Wait for download
#         # Wait a bit to make sure the file has been downloaded
#         time.sleep(10)  # Adjust the sleep time if necessary

#         print(f"PDF successfully downloaded to {save_path}")

#     except Exception as e:
#         print(f"Error downloading PDF: {str(e)}")

#     finally:
#         driver.quit()

# download_pdf()



from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

# PDF URL & Save Path
url = "https://files.floridalottery.com/exptkt/l6.pdf?_gl=1*1kcikff*_ga*MTczOTQ0NDAxMC4xNzQwODAwOTk0*_ga_3E9WN4YVMF*MTc0MTUyOTExNC40LjEuMTc0MTUyOTEzMy40MS4wLjA."
download_path = "/Users/whouston/Code/python/proj-fla-lotto"  # Adjust for your OS

def download_pdf():
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
        print("Opening URL...")
        driver.get(url)

        # Allow time for the download to complete
        time.sleep(10)

        print(f"PDF should be downloaded in: {download_path}")

    except Exception as e:
        print(f"Error downloading PDF: {str(e)}")

    finally:
        driver.quit()

download_pdf()
