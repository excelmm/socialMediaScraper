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
    # options.add_argument("--headless")
    remote1 = webdriver.Chrome(options = options)

    remote1.get("https://facebook.com")
    remote1.find_element_by_name("email").send_keys(USERNAME)
    remote1.find_element_by_name("pass").send_keys(PASSWORD)
    remote1.find_element_by_name("pass").send_keys(Keys.RETURN)

    time.sleep(3)    

    # Runs through companies and returns their facebook details
    # database = google(remote1, sys.argv[1])
    database = bing(remote1, sys.argv[1])
    
    end = time.perf_counter()

    print(f"Finished writing. Time elapsed: {end - start: 0.4f}s for {len(database)} entries.")


def facebook(remote1, site):

    # Start
    detail = dict.fromkeys(["Company", "Facebook Name", "Numbers", "Emails", "Website"])

    time.sleep(1)
    
    names = remote1.find_elements_by_id("seo_h1_tag")
    if len(names):
        name = names[0].text.replace("\n", " ").encode("utf-8")
        detail["Facebook Name"] = name

    info = remote1.find_elements_by_class_name("_4bl9")
    infoText = ""
    for i in info:
        infoText += (i.text + " ")

    number = re.findall(r"[\+\(]?[0-9][0-9 .\-\(\)]{7,}[0-9]", infoText)
    website = re.findall(r"\b((?:https?://)?(?:(?:www\.)?(?:[\da-z\.-]+)\.(?:[a-z]{2,6})))\b", infoText)

    time.sleep(1)
    currentURL = remote1.current_url
    if currentURL[-1] == "/":
        nextURL = currentURL + "about"
    else:
        nextURL = currentURL + "/about"
    remote1.get(nextURL)

    try:
        WebDriverWait(remote1, LOAD_BUFFER_TIME).until(EC.presence_of_element_located((By.CLASS_NAME, "_4bl9")))
    except:
        print("Page unable to load.")

    email = remote1.find_elements_by_class_name("_4bl9")
    emailText = ""
    for i in email:
        emailText += (i.text + " ")

    email = re.findall(r"[\w\.-]+@[\w\.-]+\.\w+", emailText)

    for item in email:
        item = item.encode("utf-8")
    for item in website:
        item = item.encode("utf-8")

    detail["Company"] = site
    detail["Numbers"] = number
    detail["Emails"] = email
    detail["Website"] = website

    print(detail)

    return detail

def google(driver, filename):

    database = []

    # Sets headless Chrome
    options = Options()
    options.headless = True

    # Initialise list of links

    # sites = []
    # file = excel.load_workbook(filename)
    # sheet = file.active
    # firstCol = sheet['A']
    # for cell in range(len(firstCol)):
    #     contact = str(firstCol[cell].value)
    #     sites.append(contact)

    with open(filename, encoding = "utf-8") as f:
        sites = f.read().splitlines()
    with open(sys.argv[2], "a", newline = "") as f:
        fieldnames = ["Company", "Facebook Name", "Numbers", "Emails", "Website"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        count = 0
        start = time.perf_counter()

        for site in sites:

            time.sleep(0.4)
            driver.get("https://www.google.com/")

            try:
                element = WebDriverWait(driver, LOAD_BUFFER_TIME).until(
                    EC.presence_of_element_located((By.NAME, "q"))
                )
            except:
                print("Page unable to load")
                continue

            element = driver.find_element_by_name("q")
            searchText = site.replace("PT. ", "") + " facebook tour or travel \"home\""
            element.send_keys(searchText)
            element.send_keys(Keys.RETURN)

            for i in range(PAGES_PER_SEARCH):

                try:
                    WebDriverWait(driver, LOAD_BUFFER_TIME).until(EC.presence_of_element_located((By.TAG_NAME, "h3")))
                except:
                    driver.save_screenshot("test.png")
                    print("Page unable to load.")
                    continue

                linksList = driver.find_elements_by_xpath("//h3")
                if len(linksList) < PAGES_PER_SEARCH:
                    continue
                text = linksList[i].text
                if "Home | Facebook" not in text:
                    continue

                linksList[i].click()

                time.sleep(1)

                detail = facebook(driver, site)
                if True:
                    writer.writerow({"Company": detail["Company"], "Facebook Name":detail["Facebook Name"], "Numbers": detail["Numbers"],\
                            "Emails": detail["Emails"], "Website":detail["Website"]})

                database.append(detail)

                time.sleep(1)

                driver.back()
                time.sleep(1)
                driver.back()
                time.sleep(1)
            

            count += 1
            end = time.perf_counter()
            print(f"Company number {count}/{len(sites)} finished. Time elapsed: {end - start:0.2f} seconds. Average time per company: {(end - start) / count:0.2f} seconds.")
            print(f"ETA: {((end - start) / count) * (len(sites) - count):0.1f} seconds")

            # Introduce randomised delay
            # delay = random.randint(5, 10)
            # time.sleep(delay)
            

    return database


def bing(driver, filename):

    database = []

    # Sets headless Chrome
    options = Options()
    options.headless = True

    # Initialise list of links

    # sites = []
    # file = excel.load_workbook(filename)
    # sheet = file.active
    # firstCol = sheet['A']
    # for cell in range(len(firstCol)):
    #     contact = str(firstCol[cell].value)
    #     sites.append(contact)

    with open(filename, encoding = "utf-8") as f:
        sites = f.read().splitlines()
    with open(sys.argv[2], "a", newline = "") as f:
        fieldnames = ["Company", "Facebook Name", "Numbers", "Emails", "Website"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        count = 0
        start = time.perf_counter()

        for site in sites:

            time.sleep(0.4)
            driver.get("https://www.bing.com/")

            try:
                element = WebDriverWait(driver, LOAD_BUFFER_TIME).until(
                    EC.presence_of_element_located((By.NAME, "q"))
                )
            except:
                print("Page unable to load")
                continue

            element = driver.find_element_by_name("q")
            searchText = site.replace("PT. ", "") + " facebook tour \"home\""
            element.send_keys(searchText)
            element.send_keys(Keys.RETURN)

            for i in range(PAGES_PER_SEARCH):

                try:
                    WebDriverWait(driver, LOAD_BUFFER_TIME).until(EC.presence_of_element_located((By.TAG_NAME, "h2")))
                    WebDriverWait(driver, LOAD_BUFFER_TIME).until(EC.presence_of_element_located((By.TAG_NAME, "cite")))
                except:
                    driver.save_screenshot("test.png")
                    print("Page unable to load.")
                    continue

                linksList = driver.find_elements_by_xpath("//cite")
                pageList = driver.find_elements_by_xpath("//h2")
                
                if len(linksList) < PAGES_PER_SEARCH:
                    continue
                text = pageList[i].text
                
                if "Home | Facebook" not in text:
                    continue
                if " " in linksList[i].text:
                    continue

                driver.save_screenshot("test.png")
                print(linksList[i].text)

                if "http" not in linksList[i].text:
                    driver.get("https://" + linksList[i].text)
                else:
                    driver.get(linksList[i].text)

                # linksList[i].send_keys(Keys.RETURN)

                time.sleep(1)

                detail = facebook(driver, site)
                if True:
                    writer.writerow({"Company": detail["Company"], "Facebook Name":detail["Facebook Name"], "Numbers": detail["Numbers"],\
                            "Emails": detail["Emails"], "Website":detail["Website"]})

                database.append(detail)

                time.sleep(1)

                driver.back()
                time.sleep(1)
                driver.back()
                time.sleep(1)
            

            count += 1
            end = time.perf_counter()
            print(f"Company number {count}/{len(sites)} finished. Time elapsed: {end - start:0.2f} seconds. Average time per company: {(end - start) / count:0.2f} seconds.")
            print(f"ETA: {((end - start) / count) * (len(sites) - count):0.1f} seconds")

            # Introduce randomised delay
            # delay = random.randint(5, 10)
            # time.sleep(delay)
        
        return database


if __name__ == "__main__":
    main()