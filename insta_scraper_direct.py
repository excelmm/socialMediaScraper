import selenium
import csv
import re
import time
import sys
import random
import openpyxl as excel
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

USERNAME = "" # Enter username here
PASSWORD = "" # Enter password here
PAGES_PER_SEARCH = 3 
LOAD_BUFFER_TIME = 10

def main():

    if len(sys.argv) != 3:
        print("Usage: python", sys.argv[0], "company_names.txt result.csv")
        exit()

    start = time.perf_counter()

    # Initialise headless chrome
    options = Options()
    options.add_argument("--headless")
    remote1 = webdriver.Chrome(options = options)

    time.sleep(1)
    login(remote1)
    logout(remote1)
    time.sleep(1)    

    # Runs a google search and obtains the Instagram links
    database = google(remote1, sys.argv[1])

    # instagram(remote1, links)
    

    end = time.perf_counter()

    print(f"Finished writing. Time elapsed: {end - start: 0.4f}s for {len(database)} entries.")


def instagram(remote1, site):

    # Start
    detail = dict.fromkeys(["Company", "Instagram Handle", "Instagram Name", "Numbers", "Emails", "Website"])

    numbers = []
    emails = []

    time.sleep(1)

    instaHandle = remote1.find_elements_by_tag_name("h2")
    if len(instaHandle) != 0:
        detail["Instagram Handle"] = instaHandle[0].text.encode("utf-8")

    instaName = remote1.find_elements_by_tag_name("h1")
    if len(instaName) != 0:
        detail["Instagram Name"] = instaName[0].text.encode("utf-8")

    website = remote1.find_elements_by_class_name("yLUwa")
    if len(website) != 0:
        detail["Website"] = website[0].text.encode("utf-8")

    info = remote1.find_elements_by_class_name("-vDIg")
    if len(info) != 0:
        number = re.findall(r'[\+\(]?[0-9][0-9 .\-\(\)]{7,}[0-9]', info[0].text)
        numbers.append(number)
        email = re.findall(r"[\w\.-]+@[\w\.-]+\.\w+", info[0].text)
        for item in email:
            item = item.encode("utf-8")
        emails.append(email)

    detail["Company"] = site
    detail["Numbers"] = numbers
    detail["Emails"] = emails

    print(detail)

    return detail

def google(driver, filename):

    database = []
    # Initialise list of links

    sites = []
    # file = excel.load_workbook(filename)
    # sheet = file.active
    # firstCol = sheet['A']
    # for cell in range(len(firstCol)):
    #     contact = str(firstCol[cell].value)
    #     sites.append(contact)

    with open(filename, encoding = "utf-8") as f:
        sites = f.read().splitlines()
    with open(sys.argv[2], "a", newline = "") as f:
        fieldnames = ["Company", "Instagram Handle", "Instagram Name", "Numbers", "Emails", "Website"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        start = time.perf_counter()
        count = 0

        for site in sites:
        
            time.sleep(0.4)
            driver.get("https://www.instagram.com/" + site)

            detail = instagram(driver, site)
            try:
                writer.writerow({"Company": detail["Company"], "Instagram Handle": detail["Instagram Handle"],\
                    "Instagram Name":detail["Instagram Name"], "Numbers": detail["Numbers"],\
                        "Emails": detail["Emails"], "Website":detail["Website"]})
            except:
                pass

            database.append(detail)
            
            # delay = random.randomint(5,10)

            time.sleep(2)
            
            count += 1
            end = time.perf_counter()
            print(f"Company number {count}/{len(sites)} finished. Time elapsed: {end - start:0.2f} seconds. Average time per company: {(end - start) / count:0.2f} seconds.")
            print(f"ETA: {((end - start) / count) * (len(sites) - count):0.1f} seconds")

    return database


def login(remote1):
    
    # Initialise
    remote1.get('https://instagram.com/')
    
    # Login
    time.sleep(2)
    if len(remote1.find_elements_by_name("username")) != 0:
        remote1.find_element_by_name("username").send_keys(USERNAME)
        remote1.find_element_by_name("password").send_keys(PASSWORD)
        remote1.find_element_by_name("password").send_keys(Keys.RETURN)
        return 1
    else:
        return 0   

def logout(remote1):
    
    remote1.get("https://instagram.com/accounts/logout")
    time.sleep(1)

if __name__ == "__main__":
    main()