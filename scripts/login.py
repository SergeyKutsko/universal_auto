import requests
import json
from selenium import webdriver
import time
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pathlib import Path
from selenium.webdriver.common.keys import Keys
from datetime import date
import os
import time
from app.models import PaymentsOrder
import csv
import datetime

def save_report_to_db(file_name):
    with open(file_name) as file:
        reader = csv.reader(file)
        next(reader)  # Advance past the header

        for row in reader:
            print(row)
            film = PaymentsOrder(transaction_uuid = row[0],
                                 driver_uuid = row[1],
                                 drievr_name = row[2],
                                 drievr_second_name = row[3],
                                 trip_uuid = row[4],
                                 trip_description = row[5],
                                 organization_name = row[6],
                                 organization_nickname = row[7],
                                 transaction_time = datetime.datetime.strptime(row[8], "%Y-%m-%d %H:%M:%S.%f %z EEST"),
                                 paid_to_you = row[9],
                                 your_earnings = row[10],
                                 cash = row[11],
                                 fare = row[12],
                                 tax = row[13],
                                 fare2 = row[14],
                                 service_tax = row[15],
                                 wait_time = row[16],
                                 out_of_city = row[17],
                                 tips = row[18],
                                 transfered_to_bank = row[19],
                                 ajustment_payment =row[20],
                                 cancel_payment = row[21])
            film.save()

def retry(fun, max_tries=2):
    for i in range(max_tries):
        try:
           time.sleep(0.3)
           return fun()
        except Exception:
            os.remove(SELENIUM_SESSION_FILE)
            continue

SELENIUM_SESSION_FILE = './selenium_session1'
SELENIUM_PORT=9514

def build_driver():
    options = Options()
    options = webdriver.ChromeOptions();
    prefs = {"download.default_directory": os.getcwd()}
    options.add_experimental_option("prefs", prefs);
    options.add_argument("--disable-infobars")
    options.add_argument("--enable-file-cookies")

    if os.path.isfile(SELENIUM_SESSION_FILE):
        session_file = open(SELENIUM_SESSION_FILE)
        session_info = session_file.readlines()
        session_file.close()

        executor_url = session_info[0].strip()
        session_id = session_info[1].strip()

        capabilities = options.to_capabilities()
        driver = webdriver.Remote(command_executor=executor_url, desired_capabilities=capabilities)
        # prevent annoying empty chrome windows
        driver.close()
        driver.quit()

        # attach to existing session
        driver.session_id = session_id
        return driver

    driver = webdriver.Chrome(options=options, port=SELENIUM_PORT)

    session_file = open(SELENIUM_SESSION_FILE, 'w')
    session_file.writelines([
        driver.command_executor._url,
        "\n",
        driver.session_id,
        "\n",
    ])
    session_file.close()

    return driver

def login(driver):
    driver.get("https://m.uber.com/")
    element = driver.find_element_by_name('phoneNumber')
    number = input("Enter your Phone Number: ")
    print(number)
    element.send_keys(number)
    driver.find_element_by_id("next-button").click()

    element = WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.ID, "password"))
    )
    password = input("Enter your password: ")
    print(password)
    element.send_keys(password)
    driver.find_element_by_id("next-button").click()


def generate_report(driver):
    driver.get("https://supplier.uber.com/orgs/49dffc54-e8d9-47bd-a1e5-52ce16241cb6/reports")
    driver.find_element_by_class_name('_css-jYsWkC').click()
    driver.find_element_by_xpath('//ul/li/div[text()[contains(.,"Payments transaction")]]').click()
    start = driver.find_element_by_xpath('//div[@data-testid="start-date-picker"]/div/div/div/input')
    start.send_keys(Keys.NULL)
    driver.find_element_by_xpath('//div[@aria-roledescription="button"]/div[text()="1"]').click()
    end = driver.find_element_by_xpath('//div[@data-testid="end-date-picker"]/div/div/div/input')
    end.send_keys(Keys.NULL)
    today = date.today()
    d, y, m  = today.strftime("%d"), today.strftime("%Y"), today.strftime("%m")
    driver.find_element_by_xpath(f'//div[@aria-roledescription="button"]/div[text()="{d}"]').click()
    driver.find_element_by_xpath('//button[@data-testid="generate-report-button"]').click()

    return f'{y}{m}01-{y}{m}{d}-payments_order-___.csv'

def download_report(driver):
    b = driver.find_element_by_xpath('//div[1][@data-testid="payment-reporting-table-row"]/div/div/div/div/button')
    driver.execute_script("arguments[0].click();", b)


def run():
    driver = retry(build_driver)
    #login(driver)
    report_name = generate_report(driver)
    download_report(driver)
    save_report_to_db(report_name)
    time.sleep(2000)

 