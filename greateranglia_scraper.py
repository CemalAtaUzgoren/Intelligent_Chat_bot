from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
import time
import os
import datetime
import json
import sys
import re



class GreaterAnglia(object):
    def __init__(self):
        url = 'https://www.greateranglia.co.uk/'
        if sys.platform.startswith('win'):
            s = Service(os.getcwd() + "/chromedriver.exe")
        elif sys.platform.startswith('darwin'):
            s = Service(os.getcwd() + "/chromedriver")
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--headless")  # Run Chrome in headless mode
        # chrome_options.add_experimental_option("detach", True)
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-dev-shm-usage')
        # Creating a fake user agent since greater anglia was detecting the headless access attempts on their website
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36")
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

    def time_delay_while_send_keys(self, element, word, delay):
        for w in word:
            self.driver.find_element(By.CSS_SELECTOR, element).send_keys(w)
            time.sleep(delay)

    def submit_button(self, element):
        submit = self.driver.find_element(By.CSS_SELECTOR, element)
        submit.click()

    def click_ele(self, locator, element, retries=3):
        for attempt in range(retries):
            try:
                if locator.upper() in ["CSS"]:
                    self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, element))).click()
                elif locator.upper() in ["XPATH"]:
                    self.wait.until(EC.element_to_be_clickable((By.XPATH, element))).click()
                else:
                    self.wait.until(EC.element_to_be_clickable((By.ID, element))).click()
                return
            except StaleElementReferenceException:
                if attempt < retries - 1:
                    print(f"StaleElementReferenceException caught. Retrying {attempt + 1}/{retries}...")
                    time.sleep(1)
                else:
                    raise
            
    def await_for_element_visibility(self, locator, element, get_text=False):
        if locator.upper() in ["CSS"]:
            ele = self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, element)))
            if get_text:
                return ele.text
        elif locator.upper() in ["XPATH"]:
            ele = self.wait.until(EC.visibility_of_element_located((By.XPATH, element)))
            if get_text:
                return ele.text
        else:
            ele = self.wait.until(EC.visibility_of_element_located((By.ID, element)))
            if get_text:
                return ele.text

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

    def quit_driver(self):
        self.driver.quit()

    # Input journey details i.e. destinations, date & time
    def journey_details(self):
        # Input details as per chatbot input
        # Accept cookies
        self.click_ele(locator='css', element='#CybotCookiebotDialogBodyButtonDecline')
        # Enter from location
        self.time_delay_while_send_keys('[id^="from-buytlbf"]', self.origin.lower(), 0.2)
        self.click_ele(locator='css', element='#listbox_from-buytlbf_container li a[role="option"]')
        
        # Enter to location
        self.time_delay_while_send_keys('[id^="totlbf"]', self.destination.lower(), 0.2)
        self.click_ele(locator='css', element='#listbox_totlbf_container li a[role="option"]')
        
        # Calendar date time selection
        self.click_ele(locator='id', element="from-buytlbf")
        self.click_ele(locator='xpath', element="(//a[@class='dpg-btn p-0'])[1]")
        self.await_for_element_presence(locator='css', element='#outbounddatetlbf')

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
        if str(cur_month) == month:
            print("Current month")
            #self.await_for_element_visibility(locator='xpath', element=f"(//span[@class='ui-datepicker-month'])[{month}]",
            #                                  get_text=True)
        elif int(month) > int(cur_month):
            diff = int(month) - int(cur_month)
            for i in range(diff):
                self.click_ele("xpath", "(//a[@class='ui-datepicker-next ui-corner-all'])[2]")
                self.click_ele("css", "#outbounddatetlbf")
                print(f"click counter: {i}")
                time.sleep(1)
        # Select day
        try:
            self.click_ele("xpath", f"(//a[text()='{day}'])[3]")
        except TimeoutException:
            self.click_ele("xpath", f"(//a[text()='{day}'])[4]")

        # Click Time range Drop Down arrow
        self.click_ele("css", "#out_time_modaltlbf_chosen")

        # Select time near to input
        hour_min_map = {
            0: "00:00", 1: "00:15", 2: "00:30", 3: "00:45", 4: "01:00", 5: "01:15", 6: "01:30", 7: "01:45",
            8: "02:00", 9: "02:15", 10: "02:30", 11: "02:45", 12: "03:00", 13: "03:15", 14: "03:30", 15: "03:45",
            16: "04:00", 17: "04:15", 18: "04:30", 19: "04:45", 20: "05:00", 21: "05:15", 22: "05:30", 23: "05:45",
            24: "06:00", 25: "06:15", 26: "06:30", 27: "06:45", 28: "07:00", 29: "07:15", 30: "07:30", 31: "07:45",
            32: "08:00", 33: "08:15", 34: "08:30", 35: "08:45", 36: "09:00", 37: "09:15", 38: "09:30", 39: "09:45",
            40: "10:00", 41: "10:15", 42: "10:30", 43: "10:45", 44: "11:00", 45: "11:15", 46: "11:30", 47: "11:45",
            48: "12:00", 49: "12:15", 50: "12:30", 51: "12:45", 52: "13:00", 53: "13:15", 54: "13:30", 55: "13:45",
            56: "14:00", 57: "14:15", 58: "14:30", 59: "14:45", 60: "15:00", 61: "15:15", 62: "15:30", 63: "15:45",
            64: "16:00", 65: "16:15", 66: "16:30", 67: "16:45", 68: "17:00", 69: "17:15", 70: "17:30", 71: "17:45",
            72: "18:00", 73: "18:15", 74: "18:30", 75: "18:45", 76: "19:00", 77: "19:15", 78: "19:30", 79: "19:45",
            80: "20:00", 81: "20:15", 82: "20:30", 83: "20:45", 84: "21:00", 85: "21:15", 86: "21:30", 87: "21:45",
            88: "22:00", 89: "22:15", 90: "22:30", 91: "22:45", 92: "23:00", 93: "23:15", 94: "23:30", 95: "23:45"
        }

        get_key = 0
        if self.input_time in hour_min_map.values():
            get_key = list(hour_min_map.keys())[list(hour_min_map.values()).index(self.input_time)]

        self.click_ele("css", f"#out_time_modaltlbf_chosen > div > ul > li:nth-child({str(get_key + 1)})")

        # Click set date button
        self.click_ele("css", "#buytickets-modal > div > div > div.modal-body > button")

    def find_ticket_submit(self):
        self.submit_button('.submit.btn.btn-outline-default.btn-md.mb-0.p-2.px-3.rounded-3.w-100')
        self.click_ele(locator='css', element='#CybotCookiebotDialogBodyButtonDecline')

    def find_cheapest_ticket(self):
        price = self.await_for_element_presence(locator="css", element="#app > div > div > div._1ef9ip7 > div > div._1ktkzxu > div > div > h4 > span._1w9rlv9 > span > span",
                                                get_text=True)
        print(f"Cheapest Ticket at Greater Anglia on {self.input_date} {self.input_time} is " + price)
        url = str(self.driver.current_url)
        return price, url

    def clear_json_file(self):
        fo = open("greateranglia.json", "w")
        fo.write("")
        fo.close()
        
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

        with open("greateranglia.json", "w") as f:
            json.dump(price_dict, f, ensure_ascii=False, indent=4)
        f.close()

if __name__ == "__main__":
    obj = GreaterAnglia()
    # Before anything, clear the existing json file containing old price
    obj.clear_json_file()
    obj.journey_details()
    obj.find_ticket_submit()
    obj.result()
    obj.quit_driver()
