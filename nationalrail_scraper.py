from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import os
import datetime
import re
import json
import sys

class NationalRail(object):
    def __init__(self):
        url = 'https://www.nationalrail.co.uk/'
        if sys.platform.startswith('win'):
            s = Service(os.getcwd() + "/chromedriver.exe")
        elif sys.platform.startswith('darwin'):
            s = Service(os.getcwd() + "/chromedriver")
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--headless")  # Run Chrome in headless mode
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-dev-shm-usage')
        # Creating a fake user agent since national rail was detecting the headless access attempts on their website
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36")
        # chrome_options.add_experimental_option("detach", True)
        self.driver = webdriver.Chrome(service=s, options=chrome_options)
        self.driver.implicitly_wait(30)
        self.driver.maximize_window()
        self.driver.get(url)
        self.wait = WebDriverWait(self.driver, 10)
        
        fo = open("current_journey_info.csv", "r")
        data = fo.readlines()
        for line in data[1:]:
            line = line.split(",")
            origin, destination, date, time = line[0], line[1], line[2], line[3]
        fo.close()
        
        self.origin = origin
        self.destination = destination
        self.input_date = date
        self.input_time = time

    def click_ele(self, locator, element):
        if locator.upper() in ["CSS"]:
            self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, element))).click()
        elif locator.upper() in ["XPATH"]:
            self.wait.until(EC.element_to_be_clickable((By.XPATH, element))).click()
        else:
            self.wait.until(EC.element_to_be_clickable((By.ID, element))).click()

    def time_delay_while_send_keys(self, element, word, delay):
        for w in word:
            self.driver.find_element(By.CSS_SELECTOR, element).send_keys(w)
            time.sleep(delay)

    def await_for_element_presence(self, locator, element, get_text=False):
        if locator.upper() in ["CSS"]:
            ele = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, element)))
            if get_text:
                return ele.text
        elif locator.upper() in ["XPATH"]:
            ele = self.wait.until(EC.presence_of_element_located((By.XPATH, element)))
            if get_text:
                return ele.text
        else:
            ele = self.wait.until(EC.presence_of_element_located((By.ID, element)))
            if get_text:
                return ele.text

    def submit_button(self, locator, element):
        if locator.upper() in ["CSS"]:
            self.driver.find_element(By.CSS_SELECTOR, element).click()
        elif locator.upper() in ["XPATH"]:
            self.driver.find_element(By.XPATH, element).click()
        else:
            self.driver.find_element(By.ID, element).click()

    def accept_cookies(self):
        # Accept Cookies
        self.click_ele("css", "#onetrust-accept-btn-handler")
        time.sleep(1)

    def click_depart_text_box(self):
        # Click departing from text field to open journey form
        self.click_ele('xpath', '//*[@id="jp-form-preview"]/section/div/button')

    def journey_details(self):
        # Enter from location
        self.time_delay_while_send_keys('[id^="jp-origin"]', self.origin.lower(), 0.2)
        time.sleep(1)
        self.click_ele(locator='css', element='[id^="sp-jp-origin-result-0"]')
        # Enter to location
        self.time_delay_while_send_keys('[id^="jp-destination"]', self.destination.lower(), 0.2)
        time.sleep(1)
        self.click_ele(locator='css', element='[id^="sp-jp-destination-result-0"]')
        # Click Calendar Icon
        self.click_ele(locator='css', element='[id^="leaving-date"]')

        # Parsing input date
        month_mapping = {}
        day, month = "", ""
        if "/" in self.input_date:
            get_date = self.input_date.split("/")
            day, month = get_date[0], get_date[1]
            if day.startswith("0"):
                day = day.replace("0", "")
            if month.startswith("0"):
                month = month.replace("0", "")
        elif "-" in self.input_date:
            get_date = self.input_date.split("-")
            day, month = get_date[0], get_date[1]
            if day.startswith("0"):
                day = day.replace("0", "")
            if month.startswith("0"):
                month = month.replace("0", "")
        else:
            month_mapping = {"1": "January", "2": "February", "3": "March", "4": "April", "5": "May", "6": "June",
                             "7": "July", "8": "August", "9": "September", "10": "October", "11": "November",
                             "12": "December"}
        if self.input_date in month_mapping.values():
            month = month_mapping['input_date']

        # Fetch current date
        calculate_date = datetime.date.today()
        cur_year, cur_month, cur_day = calculate_date.year, calculate_date.month, calculate_date.day
        date_list = []
        if str(cur_month) == month:
            for table in range(2, 3):
                for row in range(1, 6):
                    for col in range(1, 8):
                        date_element = f'//*[@id="arrowbox-leaving"]/div[2]/div/div[{table}]/div[2]/div[{row}]/div[{col}]'
                        get_cal_date = self.await_for_element_presence(locator="xpath",
                                                                       element=date_element, get_text=True)
                        if get_cal_date == day:
                            date_list.append(date_element)
            self.click_ele(locator='xpath', element=date_list[-1])

        elif int(month) > int(cur_month):
            diff = int(month) - int(cur_month)
            for i in range(diff):
                if i == 0:
                    self.click_ele("xpath", '//*[@id="arrowbox-leaving"]/div[2]/div/button')
                elif i > 0:
                    self.click_ele("xpath", '//*[@id="arrowbox-leaving"]/div[2]/div/button[2]')
                print(f"click counter: {i}")
                time.sleep(1)
            for table in range(2, 3):
                for row in range(1, 6):
                    for col in range(1, 8):
                        date_element = f'//*[@id="arrowbox-leaving"]/div[2]/div/div[{table}]/div[2]/div[{row}]/div[{col}]'
                        get_cal_date = self.await_for_element_presence(locator="xpath",
                                                                       element=date_element, get_text=True)
                        if get_cal_date == day:
                            date_list.append(date_element)
            self.click_ele(locator='xpath', element=date_list[-1])

        # Set Time
        # Click Hour dropdown
        self.click_ele(locator='css', element='[id^="leaving-hour"]')
        # Hour option mapping
        hour_option_mapping = {
            1: "00", 2: "01", 3: "02", 4: "03", 5: "04", 6: "05", 7: "06", 8: "07", 9: "08", 10: "09", 11: "10",
            12: "11", 13: "12", 14: "13", 15: "14", 16: "15", 17: "16", 18: "17", 19: "18", 20: "19", 21: "20",
            22: "21", 23: "22", 24: "23"
        }
        t = self.input_time.split(":")

        hour, minutes = t[0], t[1]
        minutes = minutes.rstrip()

        # Find hour element as per input
        get_hour = 0
        if hour in hour_option_mapping.values():
            get_hour = list(hour_option_mapping.keys())[list(hour_option_mapping.values()).index(hour)]
        self.click_ele(locator="xpath", element=f'//*[@id="leaving-hour"]/option[{get_hour}]')

        # Click Minutes dropdown
        self.click_ele(locator='css', element='[id^="leaving-min"]')
        # Minutes option mapping
        min_option_mapping = {1: "00", 2: "15", 3: "30", 4: "45"}

        # Find minutes element as per input
        get_min = 0
        if minutes in min_option_mapping.values():
            get_min = list(min_option_mapping.keys())[list(min_option_mapping.values()).index(minutes)]
        self.click_ele(locator="xpath", element=f'//*[@id="leaving-min"]/option[{get_min}]')

    def find_ticket_submit(self):
        self.submit_button("xpath", '//*[@id="button-jp"]/span[1]/span')

    def decline_feedback(self):
        self.click_ele(locator="xpath", element='//*[@id="fsrInvite"]/section[3]/button[2]')

    def find_cheapest_ticket(self):
        time.sleep(2)
        price = self.await_for_element_presence(locator="xpath", element='//*[@id="grid-jp-results"]/div/div/div[1]/fieldset/div/div[1]/label/span[2]/span[3]', get_text=True)
        print(f"Cheapest Ticket at National Rail on {self.input_date} {self.input_time} is " + price)
        url = str(self.driver.current_url)
        return price, url

    def result(self):
        price, url = self.find_cheapest_ticket()
        try:
            pattern = r"\d+\.\d+"
            find_actual_price = re.findall(pattern, price)
            price_dict = {"price": find_actual_price[0], "url": url}
        except IndexError:
            # When there is no decimal in the amount
            pattern = r"\d+"
            find_actual_price = re.findall(pattern, price)
            price_dict = {"price": find_actual_price[0], "url": url}

        with open("nationalrail.json", "w") as f:
            json.dump(price_dict, f, ensure_ascii=False, indent=4)
        f.close()
        
    def clear_json_file(self):
        fo = open("nationalrail.json", "w")
        fo.write("")
        fo.close()
        
    def quit_driver(self):
        self.driver.quit()


if __name__ == "__main__":
    obj = NationalRail()
    # Before anything, clear the existing json file containing old price
    obj.clear_json_file()
    obj.accept_cookies()
    obj.click_depart_text_box()
    obj.journey_details()
    obj.find_ticket_submit()
    try:
        obj.decline_feedback()
    except TimeoutException:
        print("Feedback pop did not appear this time. Proceeding.")
    obj.result()
    obj.quit_driver()
