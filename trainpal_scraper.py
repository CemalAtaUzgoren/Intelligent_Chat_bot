from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import os
import datetime
import re
import json
import sys

class TrainPal(object):
    def __init__(self):
        url = 'https://www.mytrainpal.com/'
        if sys.platform.startswith('win'):
            s = Service(os.getcwd() + "/chromedriver.exe")
        elif sys.platform.startswith('darwin'):
            s = Service(os.getcwd() + "/chromedriver")
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run Chrome in headless mode
        chrome_options.add_argument("--no-sandbox")
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
        time.sleep(1)
        # Accept Cookies
        self.submit_button("css", '.c_btn._btn_outline.decline_eab38')

    def day_selection_mechanism(self, day):
        # Find un-ordered list element
        self.await_for_element_presence(locator="xpath", element='//*[@class="day-wrap_b500e"]')
        disable_dates = self.driver.find_elements(By.CSS_SELECTOR,
                                                  '.date-picker_d34d2>ul>li>span[class="disabled_c48e0"]')
        disabled_dates_list, all_dates_list = [], []
        for dis in disable_dates:
            disabled_dates_list.append(dis.text)
        all_dates = self.driver.find_elements(By.CSS_SELECTOR, '.date-picker_d34d2>ul>li>span[role="button"]')
        for d in all_dates:
            all_dates_list.append(d.text)
        # Remove previous disabled dates which are empty strings
        disabled_dates_list = list(filter(None, disabled_dates_list))
        get_valid_dates = list(set(all_dates_list) - set(disabled_dates_list))
        get_valid_dates = sorted(get_valid_dates)

        # Check validity of input day in valid dates of the input month
        get_overall_dates = self.driver.find_elements(By.CSS_SELECTOR, '.date-picker_d34d2>ul>li>span')
        over_all_list = []
        for over in get_overall_dates:
            over_all_list.append(over.text)
        if str(day) in get_valid_dates:
            get_index = over_all_list.index(str(day))
            self.click_ele(locator="css", element=f'.date-picker_d34d2>ul>li:nth-child({str(get_index + 1)})>span')

    def time_selection_mechanism(self, hour, minute):
        # Time Selection Mechanism
        # Click time text field
        self.click_ele(locator="css", element=".time-picker_e4ca4 .time-show_dc0e7")
        # Get valid hours
        self.await_for_element_presence(locator="xpath", element='//*[@class="hour-wrap"]')
        valid_hours = self.driver.find_elements(By.CSS_SELECTOR, '.hour-wrap>li>span[role="button"]')
        for hours in valid_hours:
            if hour == hours.text:
                # Click Hour
                form_ele = f'.hour-wrap>li:nth-child({str(int(hour)+1)})>span'
                self.click_ele(locator="css", element=form_ele)

        # Get valid minutes
        self.await_for_element_presence(locator="xpath", element='//*[@class="mins-wrap"]')
        valid_mins = self.driver.find_elements(By.CSS_SELECTOR, '.mins-wrap>li>span[role="button"]')
        mins_list = []
        for mins in valid_mins:
            mins_list.append(mins.text)
        get_index = mins_list.index(str(minute))
        # Click Minutes
        form_ele = f'.mins-wrap>li:nth-child({str(get_index + 1)})>span'
        self.click_ele(locator="css", element=form_ele)

    def find_ticket_submit(self):
        self.submit_button("css", '.search-btn_db7b7')

    def ack_pop_up(self):
        self.click_ele(locator="css", element=".c_btn._btn_filled.apply_a4915")

    def journey_details(self):
        # Enter from location
        if sys.platform.startswith('win'):
            self.driver.find_element(By.CSS_SELECTOR, '[id^="fromStation"]').send_keys(Keys.CONTROL, 'a')
        elif sys.platform.startswith('darwin'):
            self.driver.find_element(By.CSS_SELECTOR, '[id^="fromStation"]').send_keys(Keys.COMMAND, 'a')
        
        self.driver.find_element(By.CSS_SELECTOR, '[id^="fromStation"]').send_keys(Keys.BACKSPACE)
        self.time_delay_while_send_keys('[id^="fromStation"]', self.origin.lower(), 0.2)
        # Enter to location
        if sys.platform.startswith('win'):
            self.driver.find_element(By.CSS_SELECTOR, '[id^="toStation"]').send_keys(Keys.CONTROL, 'a')
        elif sys.platform.startswith('darwin'):
            self.driver.find_element(By.CSS_SELECTOR, '[id^="toStation"]').send_keys(Keys.COMMAND, 'a')
        self.driver.find_element(By.CSS_SELECTOR, '[id^="toStation"]').send_keys(Keys.BACKSPACE)
        self.time_delay_while_send_keys('[id^="toStation"]', self.destination.lower(), 0.2)

        # Click Calendar Text Field to open
        self.click_ele(locator="css", element='.outward-box_b6231.normal')
        self.await_for_element_presence(locator="css", element=".date-head_f1c3f>span", get_text=True)

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
        if str(cur_month) == month:
            self.day_selection_mechanism(day)
        elif int(month) > int(cur_month):
            diff = int(month) - int(cur_month)
            for i in range(diff):
                # Click forward arrow
                self.click_ele(locator="css", element='.right-btn_fca5f.iconfont')
            self.day_selection_mechanism(day)

        # Time selection
        t = self.input_time.split(":")
        hour, minutes = t[0], t[1]
        minutes = minutes.rstrip()
        if minutes == "00":
            minutes = "0"
        if hour.startswith("0"):
            hour = hour.replace("0", "")
        self.time_selection_mechanism(hour, minutes)

        # Click Done button after date & time selection
        self.click_ele(locator="css", element=".done-btn_c7058")

    def find_cheapest_ticket(self):
        time.sleep(2)
        price = self.await_for_element_presence(locator="css", element='.price_fef06', get_text=True)
        price = price.split(" ")
        print(f"Cheapest Ticket at Train Pal on {self.input_date} {self.input_time} is " + price[1])
        url = str(self.driver.current_url)
        return price[1], url

    def clear_json_file(self):
        fo = open("trainpal.json", "w")
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
        
        with open("trainpal.json", "w") as f:
            json.dump(price_dict, f, ensure_ascii=False, indent=4)
        f.close()
        
    def quit_driver(self):
        self.driver.quit()


if __name__ == "__main__":
    obj = TrainPal()
    # Before anything, clear the existing json file containing old price
    obj.clear_json_file()
    obj.accept_cookies()
    obj.journey_details()
    obj.find_ticket_submit()
    obj.ack_pop_up()
    obj.result()
    obj.quit_driver()