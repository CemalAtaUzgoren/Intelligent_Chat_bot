import random
import json
import spacy
import re
import os
import sys
import csv
import warnings
import pandas as pd
warnings.filterwarnings('ignore')
from random import choice
from datetime import datetime
from scrapers_runner import ScrapersRunner
from cheapest_price_finder import PriceFinder
from fuzzywuzzy import fuzz
from collections import OrderedDict
from contiegencies import ContingencyPlan
import regression_model_functions


class ChatbotConversation(object):
    def __init__(self):
        """
        Initializes the ChatbotConversation class.

        This method sets up the required file paths, initializes necessary objects, and loads the language model.

        Args:
            None

        Returns:
            None
        """
        
        # Paths of required files 
        # Set file paths based on the operating system
        if sys.platform.startswith('win'):
            self.intentions_path = os.getcwd() + "/intentions.json"  # Path to intentions file
            self.sentences_path = os.getcwd() + "/sentences.txt"  # Path to sentences file
            self.list_of_stations_dir = os.getcwd() + '/stations.csv'  # Path to stations file
            self.current_journey_info = os.getcwd() + '/current_journey_info.csv'  # Path to current journey info file
            self.return_request_path = os.getcwd() + '/return_confirmation.txt'  # Path to return confirmation file
            self.return_counter_path = os.getcwd() + '/return_counter.txt'  # Path to return counter file
            self.delay_request_path = os.getcwd() + '/delay_confirmation.txt'  # Path to delay confirmation file
            self.delay_info_data = os.getcwd() + "/delay_info.csv"  # Path to delay info file
            self.list_of_delay_stations_dir = os.getcwd() + '/delay_stations.csv'  # Path to delay stations file
            self.delay_stations_info = os.getcwd() + "/delay_concatenate_train_dataset.csv"  # Path to delay stations info file
            self.xg_boost_model_path = os.getcwd() + '/xgboost_model.json'  # Path to XGBoost model file
            self.contingency_request_path = os.getcwd() + '/contingency_confirmation.txt'  # Path to contingency confirmation file
            self.train_fare_scraper_counter = os.getcwd() + '/train_fare_scraper_counter.txt'  # Path to train fare scraper counter file
            self.contingency_details_path = os.getcwd() + '/contingencies_details.csv'  # Path to contingency details file
        elif sys.platform.startswith('darwin'):
            self.intentions_path = os.getcwd() + "/intentions.json"  # Path to intentions file
            self.sentences_path = os.getcwd() + "/sentences.txt"  # Path to sentences file
            self.list_of_stations_dir = os.getcwd() + '/stations.csv'  # Path to stations file
            self.current_journey_info = os.getcwd() + '/current_journey_info.csv'  # Path to current journey info file
            self.return_request_path = os.getcwd() + '/return_confirmation.txt'  # Path to return confirmation file
            self.return_counter_path = os.getcwd() + '/return_counter.txt'  # Path to return counter file
            self.delay_request_path = os.getcwd() + '/delay_confirmation.txt'  # Path to delay confirmation file
            self.delay_info_data = os.getcwd() + "/delay_info.csv"  # Path to delay info file
            self.list_of_delay_stations_dir = os.getcwd() + '/delay_stations.csv'  # Path to delay stations file
            self.delay_stations_info = os.getcwd() + "/delay_concatenate_train_dataset.csv"  # Path to delay stations info file
            self.xg_boost_model_path = os.getcwd() + '/xgboost_model.json'  # Path to XGBoost model file
            self.contingency_request_path = os.getcwd() + '/contingency_confirmation.txt'  # Path to contingency confirmation file
            self.train_fare_scraper_counter = os.getcwd() + '/train_fare_scraper_counter.txt'  # Path to train fare scraper counter file
            self.contingency_details_path = os.getcwd() + '/contingencies_details.csv'  # Path to contingency details file
        
        # Open output.txt file for writing
        self.fo = open("output.txt", "w")
        self.fo.write("")
        
        # Load the language model
        self.nlp = spacy.load('en_core_web_lg')
        
        self.final_chatbot = False
        
        # Open output.txt file for appending
        self.fo = open("output.txt", "a")  # Writing the response to the output.txt file to send the response to the node:js app.
        
        # Create objects for scraper runner, price finder, and contingency plan
        self.scraper = ScrapersRunner()  # Scraper runner object
        self.cheapest_price_finder = PriceFinder()  # Price finder object
        self.contingency = ContingencyPlan()  # Contingencies object
        
        # List of scraper files
        self.scraper_files = ["greateranglia.json", "LNER.json", "nationalrail.json", "trainpal.json", 
                       "southernRailways.json" , "mytrainticket.json"]

    def load_intentions(self):
            """
            Loads the intentions from the specified file path.

            Returns:
                intentions (dict): A dictionary containing the loaded intentions.
            """
            with open(self.intentions_path) as f:
                intentions = json.load(f)
            return intentions

    def load_sentences(self):
        """
        Load sentences from a file and categorize them based on their type.

        Returns:
            A tuple containing the categorized sentences:
            - time_sentences: Sentences related to time.
            - date_sentences: Sentences related to date.
            - location_sentences: Sentences related to location.
            - weather_sentences: Sentences related to weather.
            - train_sentences: Sentences related to train.
            - issue_sentences: Sentences related to help.
            - reset_sentences: Sentences related to reset.
            - return_sentences: Sentences related to return.
            - delay_sentences: Sentences related to delay.
            - contingency_sentences: Sentences related to contingency.
        """
        # Initialize empty variables for different types of sentences
        time_sentences = ''
        date_sentences = ''
        location_sentences = ''
        weather_sentences = ''
        train_sentences = ''
        issue_sentences = ''
        reset_sentences = ''
        return_sentences = ''
        delay_sentences = ''
        contingency_sentences = ''

        # Read the sentences from the file and categorize them based on their type
        with open(self.sentences_path) as file:
            for line in file:
                parts = line.split(' | ')
                if parts[0] == 'time':
                    time_sentences = time_sentences + ' ' + parts[1].strip()
                elif parts[0] == 'date':
                    date_sentences = date_sentences + ' ' + parts[1].strip()
                elif parts[0] == 'location':
                    location_sentences = location_sentences + ' ' + parts[1].strip()
                elif parts[0] == 'weather':
                    weather_sentences = weather_sentences + ' ' + parts[1].strip()
                elif parts[0] == 'train':
                    train_sentences = train_sentences + ' ' + parts[1].strip()
                elif parts[0] == 'help':
                    issue_sentences = issue_sentences + ' ' + parts[1].strip()
                elif parts[0] == 'reset':
                    reset_sentences = reset_sentences + ' ' + parts[1].strip()
                elif parts[0] == "return":
                    return_sentences = return_sentences + ' ' + parts[1].strip()
                elif parts[0] == "delay":
                    delay_sentences = delay_sentences + ' ' + parts[1].strip()
                elif parts[0] == "contingency":
                    contingency_sentences = contingency_sentences + ' ' + parts[1].strip()

        # Return the categorized sentences
        return time_sentences, date_sentences, location_sentences, weather_sentences, train_sentences, issue_sentences, reset_sentences, return_sentences, delay_sentences, contingency_sentences
    
    def match_sentences(self):
        """
        Extracts sentences from different categories and assigns labels to them.

        Returns:
        - labels: A list of labels corresponding to each sentence.
        - sentences: A list of sentences extracted from different categories.
        """
        # Load sentences from different categories
        time_sentences, date_sentences, location_sentences, weather_sentences, train_sentences, issue_sentences, reset_instances, return_instances, delay_instances, contingency_instances = self.load_sentences()

        # Initialize empty lists for labels and sentences
        labels = []
        sentences = []

        # Extract sentences and assign labels for time category
        doc = self.nlp(time_sentences)
        for sentence in doc.sents:
            if sentence.text == ' ':
                continue
            labels.append("time")
            sentences.append(sentence.text.lower().strip())

        # Extract sentences and assign labels for date category
        doc = self.nlp(date_sentences)
        for sentence in doc.sents:
            if sentence.text == ' ':
                continue
            labels.append("date")
            sentences.append(sentence.text.lower().strip())

        # Extract sentences and assign labels for location category
        doc = self.nlp(location_sentences)
        for sentence in doc.sents:
            if sentence.text == ' ':
                continue
            labels.append("location")
            sentences.append(sentence.text.lower().strip())

        # Extract sentences and assign labels for weather category
        doc = self.nlp(weather_sentences)
        for sentence in doc.sents:
            if sentence.text == ' ':
                continue
            labels.append("weather")
            sentences.append(sentence.text.lower().strip())

        # Extract sentences and assign labels for train category
        doc = self.nlp(train_sentences)
        for sentence in doc.sents:
            if sentence.text == ' ':
                continue
            labels.append("train")
            sentences.append(sentence.text.lower().strip())

        # Extract sentences and assign labels for help category
        doc = self.nlp(issue_sentences)
        for sentence in doc.sents:
            if sentence.text == ' ':
                continue
            labels.append("help")
            sentences.append(sentence.text.lower().strip())

        # Extract sentences and assign labels for reset category
        doc = self.nlp(reset_instances)
        for sentence in doc.sents:
            if sentence.text == ' ':
                continue
            labels.append("reset")
            sentences.append(sentence.text.lower().strip())
        
        # Extract sentences and assign labels for return category
        doc = self.nlp(return_instances)
        for sentence in doc.sents:
            if sentence.text == ' ':
                continue
            labels.append("return")
            sentences.append(sentence.text.lower().strip())
        
        # Extract sentences and assign labels for delay category
        doc = self.nlp(delay_instances)
        for sentence in doc.sents:
            if sentence.text == ' ':
                continue
            labels.append("delay")
            sentences.append(sentence.text.lower().strip())

        # Extract sentences and assign labels for contingency category
        doc = self.nlp(contingency_instances)
        for sentence in doc.sents:
            if sentence.text == ' ':
                continue
            labels.append("contingency")
            sentences.append(sentence.text.lower().strip())

        return labels, sentences

    # Function to lemmatise the text and remove stop words and punctuations, and then return the cleaned text
    def lemmatise_and_clean(self, text):
        """
        Lemmatizes and cleans the given text.

        Args:
            text (str): The text to be lemmatized and cleaned.

        Returns:
            str: The lemmatized and cleaned text.
        """
        
        doc = self.nlp(text.lower())
        out = ""
        for token in doc:
            if not token.is_punct and not token.is_stop:
                out = out + token.text + " "
            elif token.text == 'to' or token.text == 'from' or token.text == 'last' or token.text == 'first':
                out = out + token.text + " "
        return out.strip()
    
    def check_current_journey_data(self):
        """
        Retrieves the current journey data from a CSV file and returns it as a dictionary.

        Returns:
            dict: A dictionary containing the current journey data with keys 'origin', 'destination', 'date', and 'time'.
        """
        current_journey_dict = {}
        with open(self.current_journey_info, newline='')as csvfile:
            reader = csv.DictReader(csvfile)
            for journey in reader:
                origin, destination, date, time = journey['origin'], journey['destination'], journey['date'], journey['time']
                current_journey_dict['origin'] = origin
                current_journey_dict['destination'] = destination
                current_journey_dict['date'] = date
                current_journey_dict['time'] = time
        csvfile.close()    
        return current_journey_dict
    
    def check_delay_info(self):
        """
        Retrieves delay information from a CSV file and returns it as a dictionary.

        Returns:
            dict: A dictionary containing the delay information for the current journey.
                  The dictionary has the following keys:
                  - 'current_station': The current station of the journey.
                  - 'dept_time_curr_st': The departure time from the current station.
                  - 'dept_time_origin': The departure time from the origin station.
        """
        current_journey_dict = {}
        with open(self.delay_info_data, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for journey in reader:
                current_station = journey['current_station']
                dept_time_curr_st = journey['dept_time_curr_st']
                dept_time_london = journey['dept_time_origin']
                current_journey_dict['current_station'] = current_station
                current_journey_dict['dept_time_curr_st'] = dept_time_curr_st
                current_journey_dict['dept_time_origin'] = dept_time_london
        csvfile.close()
        return current_journey_dict
    
    def check_return_request(self):
        """
        Checks the return request status from a file and returns it.

        Returns:
            str: The return request status.
        """
        fo = open(self.return_request_path, "r")
        data = fo.readlines()
        for line in data[1:]:
            line = line.split()
            return_req = line[0]
        fo.close()
        return return_req.lower()
    
    def update_return_request(self, status):
        """
        Updates the return request status in a file.

        Args:
            status (str): The status of the return request.

        Returns:
            None
        """
        fo = open(self.return_request_path, "w")
        fo.write("RETURN_REQUESTED\n")
        fo.write(status.lower())
        fo.close()
    
    def check_delay_request(self):
        """
        Reads the delay request file and returns the delay request value.

        Returns:
            str: The delay request value in lowercase.

        """
        fo = open(self.delay_request_path, "r")
        data = fo.readlines()
        for line in data[1:]:
            line = line.split()
            return_req = line[0]
        fo.close()
        return return_req.lower()
    
    def update_delay_request(self, status):
        """
        Update the delay request status.

        This method updates the delay request status by writing the status to a file.

        Parameters:
        - status (str): The delay request status to be written.

        Returns:
        None
        """
        fo = open(self.delay_request_path, "w")
        fo.write("DELAY_REQUESTED\n")
        fo.write(status.lower())
        fo.close()

    def check_return_counter(self):
        """
        Reads the return counter from a file and returns its value.

        Returns:
            int: The value of the return counter.
        """
        fo = open(self.return_counter_path, "r")
        data = fo.readlines()
        for line in data:
            line = line.split()
            return_counter = line[0]
        fo.close()
        return int(return_counter)

    def update_return_counter(self, counter):
        """
        Updates the return counter with the given value.

        Parameters:
        counter (int): The new value for the return counter.

        Returns:
        None
        """
        fo = open(self.return_counter_path, "w")
        fo.write(counter)
        fo.close()

    def check_train_fare_counter(self):
        """
        Reads the train fare scraper counter file and returns the value of the train fare counter.

        Returns:
            int: The value of the train fare counter.

        """
        fo = open(self.train_fare_scraper_counter, "r")
        data = fo.readlines()
        for line in data:
            line = line.split()
            train_fare_counter = line[0]
        fo.close()
        return int(train_fare_counter)

    def update_train_fare_counter(self, counter):
        """
        Update the train fare counter with the given value.

        Parameters:
        - counter: The new value for the train fare counter.

        Returns:
        None
        """
        fo = open(self.train_fare_scraper_counter, "w")
        fo.write(counter)
        fo.close()

    def clear_journey_data(self):
        """
        Clears the journey data by deleting the contents of the current_journey_info file and resetting it with the header.

        This method is called once the ticket is returned for the user.

        Parameters:
        None

        Returns:
        None
        """
        # clear csv data once ticket is returned for the user
        fo = open(self.current_journey_info, "w")
        fo.write("")
        fo.write("origin,destination,date,time")
        fo.close()
    
    def clear_delay_data(self):
        """
        Clears the delay information data file.

        This method opens the delay information data file in write mode and clears its contents.
        It then writes the header line to the file, which includes the column names.
        Finally, it closes the file.

        Parameters:
        None

        Returns:
        None
        """
        fo = open(self.delay_info_data, "w")
        fo.write("")
        fo.write("current_station,dept_time_curr_st,dept_time_origin")
        fo.close()
    
    def clear_scrapers_data(self):
            """
            Clears the data in the scraper files.

            This method iterates over the list of scraper files and clears the contents of each file.

            Args:
                None

            Returns:
                None
            """
            for file in self.scraper_files:
                fo = open(os.getcwd() + "/" + file, "w")
                fo.write("")
                fo.close()
    
    def fetch_delay_stations(self):
        """
        Fetches the delay stations and their corresponding codes and delays.

        Returns:
            station_code_map (dict): A dictionary mapping station names to a list containing the station code and delay.
        """
        station_code_map = {}
        fo = open(self.delay_stations_info, "r")
        data = fo.readlines()
        all_stations_list = []
        for lines in data[1:]:
            lines = lines.split(",")
            all_stations_list.append(lines[2])
        unique_stations = list(set(all_stations_list))
        fo.close()

        all_stations_fo = open(self.list_of_delay_stations_dir, "r")
        stations_data = all_stations_fo.readlines()
        for all_st in stations_data[1:]:
            all_st = all_st.split(",")
            name, code = all_st[0], all_st[4]
            name = name.strip().rstrip('"').lstrip('"')
            code = code.strip().rstrip('"').lstrip('"')
            if code in unique_stations:
                if code == "BTHNLGR":
                    station_code_map[name] = [code, 3]
                elif code == "BRTWOOD":
                    station_code_map[name] = [code, 2]
                elif code == "BROXBRN":
                    station_code_map[name] = [code, 1]
                elif code == "CHDWLHT":
                    station_code_map[name] = [code, 4]
                elif code == "CHLMSFD":
                    station_code_map[name] = [code, 6]
                elif code == "CHESHNT":
                    station_code_map[name] = [code, 5]
                elif code == "CLCHSTR":
                    station_code_map[name] = [code, 7]
                elif code == "DISS":
                    station_code_map[name] = [code, 8]
                elif code == "FRSTGT":
                    station_code_map[name] = [code, 9]
                elif code == "FRSTGTJ":
                    station_code_map[name] = [code, 10]
                elif code == "GIDEAPK":
                    station_code_map[name] = [code, 11]
                elif code == "GODMAYS":
                    station_code_map[name] = [code, 13]
                elif code == "HAKNYNM":
                    station_code_map[name] = [code, 15]
                elif code == "HRLDWOD":
                    station_code_map[name] = [code, 17]
                elif code == "HFLPEVL":
                    station_code_map[name] = [code, 16]
                elif code == "HAGHLYJ":
                    station_code_map[name] = [code, 14]
                elif code == "ILFORD":
                    station_code_map[name] = [code, 19]
                elif code == "INGTSTN":
                    station_code_map[name] = [code, 21]
                elif code == "IPSWICH":
                    station_code_map[name] = [code, 25]
                elif code == "KELVEDN":
                    station_code_map[name] = [code, 26]
                elif code == "LIVST":
                    station_code_map[name] = [code, 27]
                elif code == "MANNGTR":
                    station_code_map[name] = [code, 28]
                elif code == "MANRPK":
                    station_code_map[name] = [code, 29]
                elif code == "MRKSTEY":
                    station_code_map[name] = [code, 30]
                elif code == "MRYLAND":
                    station_code_map[name] = [code, 31]
                elif code == "NEEDHAM":
                    station_code_map[name] = [code, 32]
                elif code == "NRCH":
                    station_code_map[name] = [code, 33]
                elif code == "ROMFORD":
                    station_code_map[name] = [code, 35]
                elif code == "SVNKNGS":
                    station_code_map[name] = [code, 41]
                elif code == "SEVNSIS":
                    station_code_map[name] = [code, 36]
                elif code == "SHENFLD":
                    station_code_map[name] = [code, 37]
                elif code == "STWMRKT":
                    station_code_map[name] = [code, 40]
                elif code == "STFD":
                    station_code_map[name] = [code, 38]
                elif code == "WARE":
                    station_code_map[name] = [code, 45]
                elif code == "WITHAME":
                    station_code_map[name] = [code, 46]
                
        all_stations_fo.close()
        station_code_map.pop('LIVERPOOL STREET LONDON')
        station_code_map['LONDON LIVERPOOL STREET'] = ['LIVST', 27]
        return station_code_map
    
    def check_contigency_status(self):
        """
        Reads the contingency request file and returns the status.

        Returns:
            str: The contingency status, converted to lowercase.

        Raises:
            FileNotFoundError: If the contingency request file is not found.
        """
        fo = open(self.contingency_request_path, "r")
        data = fo.readlines()
        for line in data[1:]:
            line = line.split()
            contingency_req = line[0]
        fo.close()
        return contingency_req.lower()
    
    def update_contingency_status(self, status):
        """
        Updates the contingency status by writing it to a file.

        Args:
            status (str): The new contingency status.

        Returns:
            None
        """
        fo = open(self.contingency_request_path, "w")
        fo.write("CONTINGENCY_REQUESTED\n")
        fo.write(status.lower())
        fo.close()
    
    def clear_contingency_details(self):
        """
        Clears the contingency details stored in a CSV file.

        This method opens the CSV file specified by `self.contingency_details_path` and clears its contents.
        It then writes a header row to the file to indicate the column names.

        Parameters:
        - None

        Returns:
        - None
        """
        # clear csv data once contingency plan is returned for the user
        fo = open(self.contingency_details_path, "w")
        fo.write("")
        fo.write("Station1,Station2,BlockageType")
        fo.close()
    
    # This function is to convert minutes within range 00, 15, 30 or 45 only
    def manage_minutes_mechanism(self, input_time):
        """
        Converts the minutes within the minute range 00, 15, 30, 45.

        Args:
            input_time (str): The input time in the format "HH:MM".

        Returns:
            str: The converted time in the format "HH:MM".

        """
        print("Converting minutes within the minute range 00, 15, 30, 45.")
        input_time = input_time.split(":")
        min = input_time[1]
        min = str(min)
        if min in ["55", "56", "57", "58", "59", "00", "01", "02", "03", "04", "05", "06", "07"]:
            min = "00"
        elif min in ["08", "09", "10", "11", "12", "13", "14", "15"
                     "16", "17", "18", "19", "20"]:
            min = "15"
        elif min in ["21", "22", "23", "24", "25", "26", "27", "28", "29", "30",
                     "31", "32", "33", "34", "35", "36", "37", "38", "39"]:
            min = "30"
        elif min in ["40", "41", "42", "43", "44", "45", "46", "47", "48", "49", "50",
                     "51", "52", "53", "54"]:
            min = "45"
        
        time_formed = f"{input_time[0]}:{min}"
        print(f"Acceptable time formed as per input: {time_formed}")
        self.fo.write(f"CMP_7028BTime:CMP_7028B{time_formed}")
        return time_formed
    
    def extraction_delay_time(self, text):
        """
        Extracts the time from the given text and performs further processing.

        Args:
            text (str): The text from which the time needs to be extracted.

        Returns:
            dict: A dictionary containing the extracted time and other relevant information.

        Raises:
            ValueError: If the time format is invalid.

        """
        time_extracted_dict = {}
        times_list = []
        # Regular expression pattern to match time in the format "hour[:minute] am/pm"
        time_pattern = r'\b(\d{1,2})(?::(\d{2}))?\s*(?:am|pm)\b'
        # Find all matches
        matches = re.findall(time_pattern, text, re.IGNORECASE)

        # If matches are found, print the first match (assuming only one time is present)
        if matches:
            for m in range(len(matches)):
                hour, minute = matches[m]
                # Check if hour and minute fall within valid ranges
                try:
                    if 0 <= int(hour) <= 23 and 0 <= int(minute) <= 59:
                        # Add leading zero if hour is a single digit
                        hour = hour.zfill(2)
                        if 'pm' in text.lower() and int(hour) < 12:
                            hour = str(int(hour) + 12)
                        if not minute:
                            minute = '00'  # If minute part is not present
                        # Add leading zero if minute is a single digit
                        minute = minute.zfill(2)
                        time_string = hour + ':' + minute
                        print(f"Time found:", time_string)
                        final_time = time_string
                        times_list.append(final_time)
                    else:
                        print("Invalid time format. Time hours should be in the range 0 to 12 and minutes in the range between 00 to 59 only")
                        return False
                except ValueError:
                        print("I am not that intelligent yet that I can assume time. Please give time properly. Hint: 10:00 am or 5:45 pm")
                        return False
        else:
            # Regular expression pattern to match time in the format "hour[:minute] [am/pm]"
            time_pattern = r'\b(\d{1,2})(?::(\d{2}))?(?:\s*(?:am|pm))?\b'
            # Find all matches
            matches = re.findall(time_pattern, text, re.IGNORECASE)

            # If matches are found, print the first match (assuming only one time is present)
            if matches:
                for m in range(len(matches)):
                    hour, minute = matches[m]
                    # Check if hour and minute fall within valid ranges
                    try:
                        if 0 <= int(hour) <= 23 and 0 <= int(minute) <= 59:
                            # Add leading zero if hour is a single digit
                            hour = hour.zfill(2)
                            if 'pm' in text.lower() and int(hour) < 12:
                                hour = str(int(hour) + 12)
                            if not minute:
                                minute = '00'  # If minute part is not present
                            # Add leading zero if minute is a single digit
                            minute = minute.zfill(2)
                            time_string = hour + ':' + minute
                            print("Time found:", time_string)
                            final_time = time_string
                            times_list.append(final_time)
                        else:
                            print("Invalid time format. Time hours should be in the range 0 to 12 and minutes in the range between 00 to 59 only")
                            return False
                    except ValueError:
                        print("I am not that intelligent yet that I can assume time. Please give time properly. Hint: 10:00 am or 5:45 pm.")
                        return False
            else:
                print("Unable to extract time. Please give time properly. Hint: 10:00 am or 5:45 pm")

        text = text.upper()
        sent = text.split()
        
        if len(times_list) == 0:
            return time_extracted_dict
            
        elif len(times_list) == 1:
            time_type_found_list = []
            print(f"Found only one exact matching time: {times_list[0]}")
            self.fo.write(f"CMP_7028BexactMatching:CMP_7028B{times_list[0]}")

            filtered_words_list = ["want", "city", "&", "ticket", "book", "travel", "station", "will", "departing", "is", "time"]
            for _ in range(0, len(sent)):
                for w in filtered_words_list:
                    if w.upper() in sent:
                        sent.remove(w.upper())

            target_words = ["current", "present", "origin", "starting", "start", "previous", "last", "original", "first"]
            closest_words = {}
            # Create an index map of the words in text for faster lookup
            word_indices = {word: index for index, word in enumerate(sent)}
            # Loop through each target word to find the closest words
            for target in target_words:
                if target.upper() in word_indices:
                    target_index = word_indices[target.upper()]
                    # Identify the word before the target if it exists
                    before_word = sent[target_index - 1] if target_index > 0 else None
                    # Identify the word after the target if it exists
                    after_word = sent[target_index + 1] if target_index < len(sent) - 1 else None
                    closest_words[target.upper()] = (before_word, after_word)
            
            matched_time = times_list[0]
            for k, v in closest_words.items():
                if k.lower() in target_words and matched_time in v:
                    if k.lower() in ["current", "present", "previous", "last"]:
                        depart_current_station_time = matched_time
                        print(f"Departing Current Station time is: {depart_current_station_time}")
                        time_type_found_list.append("current")
                        break
                    elif k.lower() in ["origin", "starting", "start", "first", "original"]:
                        depart_origin_station_time = matched_time
                        print(f"Departing Origin Station time is: {depart_origin_station_time}")
                        time_type_found_list.append("origin")
                        break
                else:
                    if k.lower() in target_words: 
                        for st in v:
                            if st == None:
                                continue
                            if st in matched_time:
                                if k.lower() in ["current", "present", "previous", "last"]:
                                    depart_current_station_time = matched_time
                                    print(f"Departing Current Station time is: {depart_current_station_time}")
                                    time_type_found_list.append("current")
                                    break
                                elif k.lower() in ["origin", "starting", "start", "first", "original"]:
                                    depart_origin_station_time = matched_time
                                    print(f"Departing Origin Station time is: {depart_origin_station_time}")
                                    time_type_found_list.append("origin")
                                    break
                        if time_type_found_list:
                            break

        elif len(times_list) == 2:
            # predict delay from sevent kings departing time from london 10:00 from current station 11:00
            filtered_words_list = ["want", "city", "&", "ticket", "book", "travel", "station", "will"]
            target_words = ["current", "present", "origin", "starting", "start", "previous", "last", "first", "original"]
            for _ in range(0, len(sent)):
                for w in filtered_words_list:
                    if w.upper() in sent:
                        sent.remove(w.upper())
        
            for ma in times_list:
                find_index = sent.index(ma)
                act_index = find_index + 1
                sent.insert(act_index, None)
            
            closest_words = {}
            time_type_found_list= []
            # Create an index map of the words in text for faster lookup
            word_indices = {word: index for index, word in enumerate(sent)}
            # Loop through each target word to find the closest words
            for target in target_words:
                if target.upper() in word_indices:
                    target_index = word_indices[target.upper()]
                    # Identify the word before the target if it exists
                    before_word = sent[target_index - 1] if target_index > 0 else None
                    # Identify the word after the target if it exists
                    after_word = sent[target_index + 1] if target_index < len(sent) - 1 else None
                    closest_words[target.upper()] = (before_word, after_word)
            
            # Loop through each matched time
            for matched_time in times_list:
                # Loop through each target word and its closest words
                for k, v in closest_words.items():
                    # Check if the target word and matched time are in the closest words
                    if k.lower() in target_words and matched_time in v:
                        # Check if the target word is related to "current" time
                        if k.lower() in ["current", "present", "previous", "last"]:
                            depart_current_station_time = matched_time
                            print(f"Departing Current Station time is: {depart_current_station_time}")
                            time_type_found_list.append("current")
                            times_list.remove(matched_time)
                            del closest_words[k]
                            break
                        # Check if the target word is related to "origin" time
                        elif k.lower() in ["origin", "starting", "start", "first", "original"]:
                            depart_origin_station_time = matched_time
                            print(f"Departing Origin Station time is: {depart_origin_station_time}")
                            time_type_found_list.append("origin")
                            times_list.remove(matched_time)
                            del closest_words[k]
                            break 
                    else:
                        # Check if the target word is in the target words list
                        if k.lower() in target_words: 
                            # Loop through each closest word
                            for st in v:
                                # Skip if the closest word is None
                                if st == None:
                                    continue
                                # Check if the closest word is in the matched time
                                if st in matched_time:
                                    # Check if the target word is related to "current" time
                                    if k.lower() in ["current", "present", "previous", "last"]:
                                        depart_current_station_time = matched_time
                                        print(f"Departing Current Station time is: {depart_current_station_time}")
                                        time_type_found_list.append("current")
                                        times_list.remove(matched_time)
                                        break
                                    # Check if the target word is related to "origin" time
                                    elif k.lower() in ["origin", "starting", "start", "first", "original"]:
                                        depart_origin_station_time = matched_time
                                        print(f"Departing Origin Station time is: {depart_origin_station_time}")
                                        time_type_found_list.append("origin")
                                        times_list.remove(matched_time)
                                        break
                            if time_type_found_list:
                                break
            
            # Loop through each matched time
            remaining_matched_times = times_list[0]
            for k, v in closest_words.items():
            # Check if the target word and remaining matched time are in the closest words
                if k.lower() in target_words and remaining_matched_times in v:
                    # Check if the target word is related to "current" time
                    if k.lower() in ["current", "present", "previous", "last"]:
                        depart_current_station_time = remaining_matched_times
                        print(f"Departing Current Station time is: {depart_current_station_time}")
                        time_type_found_list.append("current")
                        break
                    # Check if the target word is related to "origin" time
                    elif k.lower() in ["origin", "starting", "start", "first", "original"]:
                        depart_origin_station_time = remaining_matched_times
                        print(f"Departing Origin Station time is: {depart_origin_station_time}")
                        time_type_found_list.append("origin")
                        break
                else:
                    # Check if the target word is in the target words list
                    if k.lower() in target_words:
                        # Remove None values from the closest words list
                        v = list(v)
                        v = [i for i in v if i is not None]
                        v = tuple(v)
                        # Check if any of the closest words are in the remaining matched time
                        is_match = any(c in remaining_matched_times for c in v)
                        if is_match:
                            # Check if the target word is related to "current" time
                            if k.lower() in ["current", "present", "previous", "last"]:
                                depart_current_station_time = remaining_matched_times
                                print(f"Departing Current Station time is: {depart_current_station_time}")
                                time_type_found_list.append("current")
                                break
                            # Check if the target word is related to "origin" time
                            elif k.lower() in ["origin", "starting", "start", "first", "original"]:
                                depart_origin_station_time = remaining_matched_times
                                print(f"Departing Origin Station time is: {depart_origin_station_time}")
                                time_type_found_list.append("origin")
                                break
        
        # Check if only one time type is found and it is "current"
        if len(time_type_found_list) == 1 and time_type_found_list[0] == "current":
            print(f"Departing Current Station Time Detected: {depart_current_station_time}. But Origin Station Departing Time not found. Please provide the origin station time of departure as well.")
            self.fo.write(f"CMP_7028BDepartingCurrentTime:CMP_7028B{depart_current_station_time}")
            time_extracted_dict["current_depart_station_time"] = depart_current_station_time
            return time_extracted_dict
        # Check if only one time type is found and it is "origin"
        elif len(time_type_found_list) == 1 and time_type_found_list[0] == "origin":
            print(f"Departing Origin Station Time detected: {depart_origin_station_time}. But Current Station Departing Time not found. Please provide the current station time of departure as well.")
            self.fo.write(f"CMP_7028BDepartingOriginTime:CMP_7028B{depart_origin_station_time}")
            time_extracted_dict["origin_depart_station_time"] = depart_origin_station_time
            return time_extracted_dict
        # Check if both "current" and "origin" time types are found
        elif len(time_type_found_list) == 2:
            print(f"Departing Current Station Time detected: {depart_current_station_time}. Departing Origin Station Time detected: {depart_origin_station_time}.")
            self.fo.write(f"CMP_7028BDepartingCurrentTime:CMP_7028B{depart_current_station_time}CMP_7028BDepartingOriginTime:CMP_7028B{depart_origin_station_time}")
            time_extracted_dict = {"current_depart_station_time": depart_current_station_time, "origin_depart_station_time": depart_origin_station_time}
            return time_extracted_dict
    
    def extraction_time(self, text):
        """
        Extracts time from the given text.

        Args:
            text (str): The text from which to extract the time.

        Returns:
            str: The extracted time in the format "HH:MM" (24-hour format).

        Raises:
            ValueError: If the time format is invalid.

        """
        if ":" in text:
            # Regular expression pattern to match time in the format "hour[:minute] am/pm"
            time_pattern = r'\b(\d{1,2})(?::(\d{2}))?\s*(am|a\.m\.?|pm|p\.m\.?)\b'
            # Find all matches
            matches = re.findall(time_pattern, text, re.IGNORECASE)
            # If matches are found, print the first match (assuming only one time is present)
            if matches:
                hour, minute, period = matches[0]
                # Check if hour and minute fall within valid ranges
                try:
                    if 0 <= int(hour) <= 12 and (minute == "" or 0 <= int(minute) <= 59):
                        # Add leading zero if hour is a single digit
                        hour = hour.zfill(2)
                        if not minute:
                            minute = '00'
                        else:
                            # Add leading zero if minute is a single digit
                            minute = minute.zfill(2)
                        # Convert to 24-hour format
                        period = period.replace('.', '').lower()
                        if period == 'pm' and hour != '12':
                            hour = str(int(hour) + 12)
                        elif period == 'am' and hour == '12':
                            hour = '00'
                        time_string = hour + ':' + minute
                        print(f"Time found:", time_string)
                        final_time = self.manage_minutes_mechanism(time_string)
                        return final_time
                    else:
                        print("Invalid time format. Time hours should be in the range 0 to 12 and minutes in the range between 00 to 59 only")
                        return False
                except ValueError:
                        print("I am not that intelligent yet that I can assume time. Please give time properly. Hint: 10:00 am or 5:45 pm")
                        return False
            else:
                # Regular expression pattern to match time in the format "hour[:minute] [am/pm]"
                time_pattern = r'\b(\d{1,2})(?::(\d{2}))?\s*(am|a\.m\.|pm|p\.m\.)\b'
                # Find all matches
                matches = re.findall(time_pattern, text, re.IGNORECASE)

                # If matches are found, print the first match (assuming only one time is present)
                if matches:
                    hour, minute = matches[0]
                    # Check if hour and minute fall within valid ranges
                    try:
                        if 0 <= int(hour) <= 23 and 0 <= int(minute) <= 59:
                            # Add leading zero if hour is a single digit
                            hour = hour.zfill(2)
                            # Convert to 24-hour format
                            if hour == '12':
                                hour = '00'
                            if 'pm' in text.lower() and int(hour) < 12:
                                hour = str(int(hour) + 12)
                            if not minute:
                                minute = '00'  # If minute part is not present
                            # Add leading zero if minute is a single digit
                            minute = minute.zfill(2)
                            time_string = hour + ':' + minute
                            print("Time found:", time_string)
                            final_time = self.manage_minutes_mechanism(time_string)
                            return final_time
                        else:
                            print("Invalid time format. Time hours should be in the range 0 to 12 and minutes in the range between 00 to 59 only")
                            return False
                    except ValueError:
                        print("I am not that intelligent yet that I can assume time. Please give time properly. Hint: 10:00 am or 5:45 pm.")
                        return False
                else:
                    print("Unable to extract time. Please give time properly. Hint: 10:00 am or 5:45 pm")
                    self.fo.write("CMP_7028BUnable to extract time. Please give time properly. Hint: 10:00 am or 5:45 pm. ")

        else:
            time_pattern = r'\b(\d{1,2})\s*(?::?(\d{2}))?\s*(am|a\.m\.?|pm|p\.m\.?)?\b'
    
            # Find all matches
            matches = re.findall(time_pattern, text, re.IGNORECASE)
            
            # If matches are found, process each match
            for match in matches:
                hour, minute, period = match
                # Check if the minute part is present and if hour is valid
                try:
                    if (0 <= int(hour) <= 12 if period else 0 <= int(hour) <= 23) and (minute == "" or 0 <= int(minute) <= 59):
                        # Add leading zero if hour is a single digit
                        hour = hour.zfill(2)
                        
                        # Default minute to '00' if not provided
                        if not minute:
                            minute = '00'
                        else:
                            # Add leading zero if minute is a single digit
                            minute = minute.zfill(2)
                        
                        # Convert to 24-hour format if period is provided
                        if period:
                            period = period.replace('.', '').lower()
                            if period == 'pm' and hour != '12':
                                hour = str(int(hour) + 12)
                            elif period == 'am' and hour == '12':
                                hour = '00'
                        
                        time_string = f"{hour}:{minute}"
                        print(f"Time found: {time_string}")
                        # Replace self.manage_minutes_mechanism with actual processing function
                        final_time = time_string  # Replace with your processing function
                        final_time = self.manage_minutes_mechanism(time_string)
                        return final_time
                    else:
                         print("Invalid time format. Time hours should be in the range 0 to 12 and minutes in the range between 00 to 59 only")
                         return False
                except ValueError:
                    print("I am not that intelligent yet that I can assume time. Please give time properly. Hint: 10:00 am or 5:45 pm.")
                    return False
            print("Unable to extract time. Please give time properly. Hint: 10:00 am or 5:45 pm")
            self.fo.write("CMP_7028BUnable to extract time. Please give time properly. Hint: 10:00 am or 5:45 pm. ")

    def convert_date(self, date_string):
        """
        Converts a date string in the format 'ddth Month' to 'dd/mm/yyyy' format.

        Args:
            date_string (str): The date string to be converted.

        Returns:
            str: The converted date string in 'dd/mm/yyyy' format.
        """
        # Remove 'date' from the string
        date_string = date_string.replace('date ', '')
        date = datetime.strptime(date_string, '%dth %B')
        date = date.replace(year=datetime.now().year)
        return date.strftime('%d/%m/%Y')
    
    def date_extraction_via_regex(self, text):
        """
        Extracts dates from the given text using regular expressions.

        Args:
            text (str): The text from which dates need to be extracted.

        Returns:
            list: A list of extracted dates in the format 'dd/mm/yyyy'.

        Raises:
            None

        """
        final_date_list = []
        date_pattern_1 = r'\b(\d{1,2})(st|nd|rd|th)?\s+of\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})\b'
        matches_1 = re.findall(date_pattern_1, text, re.IGNORECASE)
        if matches_1:
            date_tuple = matches_1[0]
            day_no = date_tuple[0]
            if int(day_no) / 10 < 1:
                day_no = f"0{str(day_no)}"
            month_number = datetime.strptime(date_tuple[2], '%B').month
            if int(month_number) / 10 < 1:
                month_number = f"0{str(month_number)}"
            formatted_date = f"{day_no}/{month_number}/{date_tuple[3]}"
            print(f"Extracted date is: {formatted_date}.")
            self.fo.write(f"CMP_7028BDate:CMP_7028B{formatted_date}. ")
            final_date_list.append(formatted_date)
            return final_date_list
        else:
            date_pattern_2 = r'\b(\d{1,2}(?:st|nd|rd|th)?)\s*(?:of\s+)?(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})\b|\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}(?:st|nd|rd|th)?)\s+(\d{4})\b'
            matches_2 = re.findall(date_pattern_2, text, re.IGNORECASE)
            if matches_2:
                date_tuple = matches_2[0]
                try:
                    day_no = re.findall(r'[0-9]+', date_tuple[0])[0]
                    if int(day_no) / 10 < 1:
                        day_no = f"0{str(day_no)}"
                    
                    month_name = date_tuple[1].split()[0]
                    month_number = datetime.strptime(month_name, '%B').month
                    if int(month_number) / 10 < 1:
                        month_number = f"0{str(month_number)}" 

                    formatted_date = f"{day_no}/{month_number}/{date_tuple[2]}"
                    print(f"date: {formatted_date}.")
                    self.fo.write(f"CMP_7028BDate:CMP_7028B{formatted_date}. ")
                    final_date_list.append(formatted_date)
                    return final_date_list
                except IndexError:
                    day_no = re.findall(r'[0-9]+', date_tuple[4])[0]
                    if int(day_no) / 10 < 1:
                        day_no = f"0{str(day_no)}"
                    month_name = date_tuple[3].split()[0]
                    month_number = datetime.strptime(month_name, '%B').month
                    if int(month_number) / 10 < 1:
                        month_number = f"0{str(month_number)}" 

                    formatted_date = f"{day_no}/{month_number}/{date_tuple[5]}"
                    print(f"date: {formatted_date}.")
                    self.fo.write(f"CMP_7028BDate:CMP_7028B{formatted_date}. ")
                    final_date_list.append(formatted_date)
                    return final_date_list
            else:
                date_pattern_3 = r'\b(\d{1,2})(?:st|nd|rd|th)?\s*(?:of\s+)?(january|february|march|april|may|june|july|august|september|october|november|december)\b'
                matches_3 = re.findall(date_pattern_3, text, re.IGNORECASE)
                if matches_3:
                    date_str = matches_3[0]
                    print(f"No year specified. Assuming it's current year by default.")
                    self.fo.write(f"CMP_7028BNo year specified. Assuming it's current year by default. ")
                    current_year = datetime.now().year
                    date_tuple = (date_str, str(current_year))
                    try:
                        date_str = date_tuple[0][0] + ' ' +  date_tuple[0][1] + ' ' + date_tuple[1]
                        date_obj = datetime.strptime(date_str, '%d %B %Y')
                        formatted_date = date_obj.strftime('%d/%m/%Y')
                        print(f"Extracted date is: {formatted_date}")
                        self.fo.write(f"CMP_7028BDate:CMP_7028B{formatted_date}. ")
                        final_date_list.append(formatted_date)
                        return final_date_list
                    except ValueError:
                        date_str = date_tuple[0] + ' ' + date_tuple[1]
                        try:
                            date_obj = datetime.strptime(date_str, '%dth %B %Y')
                        except ValueError:
                            try:
                                date_obj = datetime.strptime(date_str, '%dnd %B %Y')
                            except ValueError:
                                try:
                                    date_obj = datetime.strptime(date_str, '%dst %B %Y')
                                except ValueError:
                                    date_obj = datetime.strptime(date_str, '%drd %B %Y')
                        formatted_date = date_obj.strftime('%d/%m/%Y')
                        print(f"Extracted date is: {formatted_date}.")
                        self.fo.write(f"CMP_7028BDate:CMP_7028B{formatted_date}")
                        final_date_list.append(formatted_date)
                        return final_date_list
                else:
                    date_pattern_4 =  r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+of\s+(\d{1,2}(?:st|nd|rd|th)?)\s+(\d{4})\b'

                    matches_4 = re.findall(date_pattern_4, text, re.IGNORECASE)
                    if matches_4:
                        date_tuple = matches_4[0]
                        day_no = re.findall(r'[0-9]+', date_tuple[1])[0]
                        if int(day_no) / 10 < 1:
                            day_no = f"0{str(day_no)}"
                    
                        month_name = date_tuple[0].split()[0]
                        month_number = datetime.strptime(month_name, '%B').month
                        if int(month_number) / 10 < 1:
                            month_number = f"0{str(month_number)}" 

                        formatted_date = f"{day_no}/{month_number}/{date_tuple[2]}"
                        print(f"date: {formatted_date}.")
                        self.fo.write(f"CMP_7028BDate:CMP_7028B{formatted_date}. ")
                        final_date_list.append(formatted_date)
                        return final_date_list
                    else:
                        date_pattern_5 = r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s*(?:of\s+)?(\d{1,2}(?:st|nd|rd|th)?)?\s*(\d{1,2}:\d{2}\s*(?:am|pm))?\b'
                        matches_5 = re.findall(date_pattern_5, text, re.IGNORECASE)
                        if matches_5:
                            date_str = matches_5[0]
                            print(f"No year specified. Assuming it's current year by default.")
                            self.fo.write(f"CMP_7028BNo year specified. Assuming it's current year by default. ")
                            current_year = datetime.now().year
                            date_tuple = (date_str, str(current_year))
                            try:
                                date_str = date_tuple[0][1] + ' ' +  date_tuple[0][0] + ' ' + date_tuple[1]
                                date_obj = datetime.strptime(date_str, '%d %B %Y')
                                formatted_date = date_obj.strftime('%d/%m/%Y')
                                print(f"Extracted date is: {formatted_date}")
                                self.fo.write(f"CMP_7028BDate:CMP_7028B{formatted_date}. ")
                                final_date_list.append(formatted_date)
                                return final_date_list
                            except ValueError or TypeError:
                                date_str = date_tuple[0][1] + ' ' +  date_tuple[0][0] + ' ' + date_tuple[1]
                                try:
                                    date_obj = datetime.strptime(date_str, '%dth %B %Y')
                                except ValueError or TypeError:
                                    try:
                                        date_obj = datetime.strptime(date_str, '%dnd %B %Y')
                                    except ValueError or TypeError:
                                        try:
                                            date_obj = datetime.strptime(date_str, '%dst %B %Y')
                                        except ValueError or TypeError:
                                            date_obj = datetime.strptime(date_str, '%drd %B %Y')
                                formatted_date = date_obj.strftime('%d/%m/%Y')
                                print(f"Extracted date is: {formatted_date}.")
                                self.fo.write(f"CMP_7028BDate:CMP_7028B{formatted_date}")
                                final_date_list.append(formatted_date)
                                return final_date_list
                        else:
                            print("Date not found. Hint: Try giving 8 june 2024 or 8th june 2024 or check for any spelling mistakes")
                            self.fo.write("CMP_7028BDate not found. Hint: Try giving 8 june 2024 or 8th june 2024. ")
                            return final_date_list
    
    def extract_date_via_nlp(self, text):
        lemma_text = self.lemmatise_and_clean(text)
        try:
            doc = self.nlp(lemma_text)
            dates = []
            for ent in doc.ents:
                if ent.label_ == 'DATE':
                    _ = self.convert_date(ent.text)
                    dates.append(_)            
            print(f'DATES EXTRACTED BY NLP: {dates}')
            if not dates:
                dates = self.date_extraction_via_regex(text)
                if dates:
                    input_date = datetime.strptime(dates[0], "%d/%m/%Y")
                    today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
                    if input_date >= today:
                        return dates
                    else:
                        print("Date can't be of previous day.")
                        self.fo.write("CMP_7028BPastDateCMP_7028BDate can't be of previous day")
                        return False
                else:
                    return False
        except ValueError:  
            dates = self.date_extraction_via_regex(text) 
            if dates:
                input_date = datetime.strptime(dates[0], "%d/%m/%Y")
                today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
                if input_date >= today:
                    return dates
                else:
                    print("Date can't be of previous day.")
                    self.fo.write("CMP_7028BPastDateCMP_7028BDate can't be of previous day")
                    return False
            else:
                return False
    
    def extract_delay_location(self, user_input):
        """
        Extracts the delay location from the user input.

        Args:
            user_input (str): The user input containing the location information.

        Returns:
            dict: A dictionary containing the extracted delay location.

        """
        station_extracted_dict = {}
        matches, stations_name_list = [], []
        get_stations_dict = self.fetch_delay_stations()
        for k, _ in get_stations_dict.items():
            stations_name_list.append(k)
        
        for stations in stations_name_list:
            if stations.upper() in user_input.upper():
                matches.append(stations.upper())

        def sub_function():
            multiple_matches = []
            # temporarily remove to, from and other words related to departure or arrival
            irrelevant_words_1 = ["to", "arrive", "arrival", "arriving", "book"]
            irrelevant_words_2 = ["ticket", "train", "from", "norwich", "delay", "predict"]
            # Convert text to lowercase for case-insensitive matching
            text_lower = user_input.lower()
            # Split the text into words
            words = text_lower.split()
            # Filter out words related to departure and arrival
            filtered_words = [word for word in words if word not in irrelevant_words_1 and word not in irrelevant_words_2]
            # Join the remaining words back into a string
            cleaned_text = ' '.join(filtered_words)
            #from fuzzywuzzy import fuzz
            # Set your desired threshold for similarity
            threshold = 75
            # Iterate through the stations_name_list
            cleaned_text = cleaned_text.split()
            for cleaned in cleaned_text:
                for station in stations_name_list:
                    # Calculate similarity score using token_set_ratio
                    similarity = fuzz.token_set_ratio(station.upper(), cleaned.upper())
                    # Check if similarity score is above the threshold
                    if similarity >= threshold:
                        multiple_matches.append(station)
            
            if multiple_matches:
                print(f"Multiple Matches found: {multiple_matches}")
                self.fo.write(f"CMP_7028BMultipleMatches:CMP_7028B{multiple_matches}")
                print("Please select from the top matches found or be specific with the search. ")
        
        if len(matches) == 0:
            sub_function()
            return station_extracted_dict      
        if len(matches) == 1:
            print(f"Found exact matching current departing station: {matches[0]}")  
            self.fo.write(f"CMP_7028BDelayStation:CMP_7028B{matches[0]}")
            station_extracted_dict["current_depart_station"] = matches[0]
            return station_extracted_dict
    
    def extract_location(self, _text):
        """
        Extracts the location from the given text.

        Args:
            _text (str): The text from which the location needs to be extracted.

        Returns:
            dict: A dictionary containing the extracted location information.
        """
        station_extracted_dict = {}
        # Rest of the code...
    def extract_location(self, _text):
        station_extracted_dict = {}
        text = self.lemmatise_and_clean(_text)
        text = text.upper()
    
        # Check if the station name exists in stations.csv
        stations_name_list = []
        fo = open(self.list_of_stations_dir)
        stations_data = fo.readlines()
        for lines in stations_data[1:]:
            lines = lines.split(",")
            stations_name_list.append(lines[0])   
        
        matches = []
        for stations in stations_name_list:
            if stations.upper() in text.upper():
                matches.append(stations.upper())
        
        sent = text.split()
        new_match = []
        for st in matches:
            st = st.split()
            new_match.extend(st)
        for s in new_match:
            if s not in sent:
                matches.remove(s)
        
        def sub_function():
            multiple_matches = []
            # temporarily remove to, from and other words related to departure or arrival
            departure_words = ["from", "depart", "departure", "departing", "city", "visiting"]
            arrival_words = ["to", "arrive", "arrival", "arriving", "book", "ticket", "train"]
            # Convert text to lowercase for case-insensitive matching
            text_lower = text.lower()
            try:
                text_lower = text_lower.replace(matched_city.lower(), "")
            except NameError:
                pass
            # Split the text into words
            words = text_lower.split()
            # Filter out words related to departure and arrival
            filtered_words = [word for word in words if word not in departure_words and word not in arrival_words]
            # Join the remaining words back into a string
            cleaned_text = ' '.join(filtered_words)
            #from fuzzywuzzy import fuzz
            # Set your desired threshold for similarity
            threshold = 75
            # Iterate through the stations_name_list
            cleaned_text = cleaned_text.split()
            for cleaned in cleaned_text:
                for station in stations_name_list:
                    # Calculate similarity score using token_set_ratio
                    similarity = fuzz.token_set_ratio(station.upper(), cleaned.upper())
                    # Check if similarity score is above the threshold
                    if similarity >= threshold:
                        multiple_matches.append(station)
            
            if multiple_matches:
                print(f"Multiple Matches found: {multiple_matches}")
                # rand_multi = ["Multiple Matches found", "There are multiple matches", "Hang on! There are multiple stations to that name"]
                self.fo.write(f"CMP_7028BMultipleMatches:CMP_7028B{multiple_matches}")
                print("Please select from the top matches found or be specific with the search. Hint: Find me the cheapest train ticket from London Liverpool Street station to Norwich. ")
                #self.fo.write("Please select from the top matches found or be specific with the search. Hint: Find me the cheapest train ticket from London Liverpool Street station to Norwich. ")
            
        if len(matches) == 0:
            sub_function()
            return station_extracted_dict
        
        elif len(matches) == 1:
            station_type_found_list = []
            print(f"Found only one exact matching station: {matches}")
            self.fo.write(f"CMP_7028BexactMatching:CMP_7028B{matches}")

            filtered_words_list = ["want", "city", "&", "ticket", "book", "travel", "station", "will"]
            for _ in range(0, len(sent)):
                for w in filtered_words_list:
                    if w.upper() in sent:
                        sent.remove(w.upper())

            target_words = ["departure", "arrival", "depart", "arrive", "departing", "arriving", "stop", "origin", "from", "to"]
            closest_words = {}
            # Create an index map of the words in text for faster lookup
            word_indices = {word: index for index, word in enumerate(sent)}
            # Loop through each target word to find the closest words
            for target in target_words:
                if target.upper() in word_indices:
                    target_index = word_indices[target.upper()]
                    # Identify the word before the target if it exists
                    before_word = sent[target_index - 1] if target_index > 0 else None
                    # Identify the word after the target if it exists
                    after_word = sent[target_index + 1] if target_index < len(sent) - 1 else None
                    closest_words[target.upper()] = (before_word, after_word)
            
            matched_city = matches[0]
            for k, v in closest_words.items():
                if k.lower() in target_words and matched_city in v:
                    if k.lower() in ["departure", "depart", "departing", "origin", "start", "starting", "from"]:
                        depart_station_name = matched_city
                        print(f"Departing station is: {depart_station_name}")
                        station_type_found_list.append("departing")
                        break
                    elif k.lower() in ["arrival", "arrive", "arriving", "stop", "end", "ending", "to"]:
                        arrive_station_name = matched_city
                        print(f"Arriving station is: {arrive_station_name}")
                        station_type_found_list.append("arriving")
                        break
                else:
                    if k.lower() in target_words: 
                        for st in v:
                            if st == None:
                                continue
                            if st in matched_city:
                                if k.lower() in ["departure", "depart", "departing", "origin", "start", "starting", "from"]:
                                    depart_station_name = matched_city
                                    print(f"Departing station is: {depart_station_name}")
                                    station_type_found_list.append("departing")
                                    break
                                elif k.lower() in ["arrival", "arrive", "arriving", "stop", "end", "ending", "to"]:
                                    arrive_station_name = matched_city
                                    print(f"Arriving station is: {arrive_station_name}")
                                    station_type_found_list.append("arriving")
                                    break
                        if station_type_found_list:
                            break

        elif len(matches) == 2:
            print(f"Found exact matching stations: {matches}")
            self.fo.write(f"CMP_7028BexactMatching:CMP_7028B{matches}")
            print("Figuring out the destination and arrival stations")
            #self.fo.write("Figuring out the destination and arrival stations. ")

            filtered_words_list = ["want", "city", "&", "ticket", "book", "travel", "station", "will"]
            target_words = ["departure", "arrival", "depart", "arrive", "departing", "arriving", "stop", "origin", "from", "to"]
            for _ in range(0, len(sent)):
                for w in filtered_words_list:
                    if w.upper() in sent:
                        sent.remove(w.upper())

            get_s_index = []
            for m in matches:
                m = m.split()
                if len(m) > 1:
                    get_s_index.append(m[0])
                    m = m[1:]
                    # Clean sent even more
                    for c in m:
                        sent.remove(c)

            if get_s_index:
                find_index = sent.index(get_s_index[0])
                act_index = find_index + 1
                sent.insert(act_index, None)
            
            closest_words = {}
            station_type_found_list= []
            # Create an index map of the words in text for faster lookup
            word_indices = {word: index for index, word in enumerate(sent)}
    
            # Loop through each target word to find the closest words
            for target in target_words:
                if target.upper() in word_indices:
                    target_index = word_indices[target.upper()]
                    # Identify the word before the target if it exists
                    before_word = sent[target_index - 1] if target_index > 0 else None
                    # Identify the word after the target if it exists
                    after_word = sent[target_index + 1] if target_index < len(sent) - 1 else None
                    closest_words[target.upper()] = (before_word, after_word)
        
            for matched_city in matches:
                for k, v in closest_words.items():
                    if k.lower() in target_words and matched_city in v:
                        if k.lower() in ["departure", "depart", "departing", "origin", "start", "starting", "from"]:
                            depart_station_name = matched_city
                            print(f"Departing station is: {depart_station_name}")
                            station_type_found_list.append("departing")
                            matches.remove(matched_city)
                            del closest_words[k]
                            break
                        elif k.lower() in ["arrival", "arrive", "arriving", "stop", "end", "ending", "to"]:
                            arrive_station_name = matched_city
                            print(f"Arriving station is: {arrive_station_name}")
                            station_type_found_list.append("arriving")
                            matches.remove(matched_city)
                            del closest_words[k]
                            break 
                    else:
                        if k.lower() in target_words: 
                            for st in v:
                                if st == None:
                                    continue
                                if st in matched_city:
                                    if k.lower() in ["departure", "depart", "departing", "origin", "start", "starting", "from"]:
                                        depart_station_name = matched_city
                                        print(f"Departing station is: {depart_station_name}")
                                        station_type_found_list.append("departing")
                                        matches.remove(matched_city)
                                        break
                                    elif k.lower() in ["arrival", "arrive", "arriving", "stop", "end", "ending", "to"]:
                                        arrive_station_name = matched_city
                                        print(f"Arriving station is: {arrive_station_name}")
                                        station_type_found_list.append("arriving")
                                        matches.remove(matched_city)
                                        break
                            if station_type_found_list:
                                break
            
            remaining_matched_city = matches[0]
            for k, v in closest_words.items():
                if k.lower() in target_words and remaining_matched_city in v:
                    if k.lower() in ["departure", "depart", "departing", "origin", "start", "starting", "from"]:
                        depart_station_name = remaining_matched_city
                        print(f"Departing station is: {depart_station_name}")
                        station_type_found_list.append("departing")
                        break
                    elif k.lower() in ["arrival", "arrive", "arriving", "stop", "end", "ending", "to"]:
                        arrive_station_name = remaining_matched_city
                        print(f"Arriving station is: {arrive_station_name}")
                        station_type_found_list.append("arriving")
                        break
                else:
                    if k.lower() in target_words:
                        v = list(v)
                        v = [i for i in v if i is not None]
                        v = tuple(v)
                        is_match = any(c in remaining_matched_city for c in v)
                        if is_match:
                            if k.lower() in ["departure", "depart", "departing", "origin", "start", "starting", "from"]:
                                    depart_station_name = remaining_matched_city
                                    print(f"Departing station is: {depart_station_name}")
                                    station_type_found_list.append("departing")
                                    break
                            elif k.lower() in ["arrival", "arrive", "arriving", "stop", "end", "ending", "to"]:
                                arrive_station_name = remaining_matched_city
                                print(f"Arriving station is: {arrive_station_name}")
                                station_type_found_list.append("arriving")
                                break                
        
        if len(station_type_found_list) == 1 and station_type_found_list[0] == "departing":
            print(f"Departing Station detected: {depart_station_name}. But arriving station not found. Please provide the station of arrival as well.")
            self.fo.write(f"CMP_7028BDeparting Station:CMP_7028B{depart_station_name}")
            station_extracted_dict["depart_station"] = depart_station_name
            sub_function()
            return station_extracted_dict
        elif len(station_type_found_list) == 1 and station_type_found_list[0] == "arriving":
            print(f"Arriving Station detected: {arrive_station_name}. But departing station not found. Please provide the station of departure as well.")
            self.fo.write(f"CMP_7028BArriving Station:CMP_7028B{arrive_station_name}")
            station_extracted_dict["arrival_station"] = arrive_station_name
            sub_function()
            return station_extracted_dict
        elif len(station_type_found_list) == 2:
            print(f"Departing Station detected: {depart_station_name}. Arriving Station detected: {arrive_station_name}.")
            self.fo.write(f"CMP_7028BDeparting Station:CMP_7028B{depart_station_name}CMP_7028BArriving Station:CMP_7028B{arrive_station_name}")
            station_extracted_dict = {"depart_station": depart_station_name, "arrival_station": arrive_station_name}
            return station_extracted_dict
        
    def return_ticket_mechanism(self, sentence):
        """
        This method handles the process of finding a return ticket for the user's journey.

        Args:
            sentence (str): The user's input sentence.

        Returns:
            bool: True if the return ticket is found, False otherwise.
        """
        get_return_counter = self.check_return_counter()
        get_return_counter += 1
        self.update_return_counter(str(get_return_counter))

        current_info_dict = self.check_current_journey_data()
        if not current_info_dict:
            print("Please perform the one-way search first in order to get return fares.")
            self.fo.write("Please perform the one-way search first in order to get return fares. ")
            self.update_return_request("no")
            self.update_return_counter("0")
            return False
        else:
            sentence = sentence.upper()
            not_words = ["not", "would not", "do not", "no", "no thanks", "no thank you", "dont", "don't"]
            do_not_want_list = []
            for word in not_words:
                if word.upper() in sentence:
                    do_not_want_list.append(word)
            if do_not_want_list:
                print("Very well. I hope you have a nice day.")
                self.fo.write("CMP_7028BRetunRejectCMP_7028BVery well. I hope you have a nice day. ")
                self.clear_journey_data()
                self.update_return_request("no")
                self.update_return_counter("0")
                self.update_train_fare_counter("0")
                self.clear_scrapers_data()
            else:
                if get_return_counter <= 1:
                    print("Initiating process to find return ticket.")
                    self.fo.write("Initiating process to find return ticket. ")
                    # switching locations
                    origin = current_info_dict['destination']
                    destination = current_info_dict['origin']
                    # Clear CSV before writing return values
                    self.clear_journey_data()
                    
                    journey_info = pd.read_csv(self.current_journey_info)
                    journey_info.at[0, 'origin'] = origin
                    journey_info.at[0, 'destination'] = destination
                    journey_info.to_csv(self.current_journey_info, index=False)

                return_info_dict = self.check_current_journey_data()
                if return_info_dict['date'] in ['', None] and return_info_dict['time'] in ['', None]:
                    self.information_extraction_mechanism(sentence, extraction_type="date")
                    self.information_extraction_mechanism(sentence, extraction_type="time")
                elif return_info_dict['date'] not in ['', None] and return_info_dict['time'] in ['', None]:
                    self.information_extraction_mechanism(sentence, extraction_type="time")
                elif return_info_dict['time'] not in ['', None] and return_info_dict['date'] in ['', None]:
                    self.information_extraction_mechanism(sentence, extraction_type="date")
                
            final_info_dict = self.check_current_journey_data()
            if ('origin' in final_info_dict.keys() and final_info_dict['origin'] not in ['', None]) and ('destination' in final_info_dict.keys() and final_info_dict['destination'] not in ['', None]) and ('date' in final_info_dict.keys() and final_info_dict['date'] not in ['', None]) and ('time' in final_info_dict.keys() and final_info_dict
            ['time'] not in ['', None]):
                print("Received all required information. Thank you. Proceeding to find cheapest train ticket for your return journey.")
                self.scraper_run()

    def check_intention_by_keyword(self, sentence):
        """
        Checks the intention of the user's sentence based on keywords.

        Args:
            sentence (str): The user's input sentence.

        Returns:
            bool or None: Returns True if the intention is met, None otherwise.
        """
        intentions_met = False
        intentions = self.load_intentions()
        for word in sentence.split():
            for type_of_intention in intentions:
                if type(intentions[type_of_intention]) == list:
                    pass
                else:
                    if word.lower() in intentions[type_of_intention]["patterns"]:
                        intentions_met = True
                        if intentions_met:
                            if type_of_intention in ["greeting", "thanks", "apologies", "help"]:
                                print(random.choice(intentions[type_of_intention]["responses"]))
                                self.fo.write(random.choice(intentions[type_of_intention]["responses"]))
                            if type_of_intention == 'return':
                                self.fo.write("CMP_7028BTrainBookCMP_7028B")
                                print(random.choice(intentions[type_of_intention]["responses"]))
                                self.fo.write(random.choice(intentions[type_of_intention]["responses"]))
                                self.return_ticket_mechanism(sentence)
                                check_current_info = self.check_current_journey_data()
                                if check_current_info['date'] in ['', None] or check_current_info['time'] in ['', None]:
                                    self.progress_check(sentence)
                                else:
                                    self.update_return_request("no")
                                    self.update_return_counter("0")
                                    self.clear_journey_data()
                                    self.clear_scrapers_data()
                            if type_of_intention == "time":
                                self.fo.write("CMP_7028BTrainBookCMP_7028B")
                                print(random.choice(intentions[type_of_intention]["responses"]))
                                self.information_extraction_mechanism(sentence, extraction_type="time")
                                self.progress_check(sentence)
                                self.scraper_run()
                            if type_of_intention == "date":
                                self.fo.write("CMP_7028BTrainBookCMP_7028B")
                                print(random.choice(intentions[type_of_intention]["responses"]))
                                self.information_extraction_mechanism(sentence, extraction_type="date")
                                self.progress_check(sentence)
                                self.scraper_run()
                            if type_of_intention == "contingency":
                                self.fo.write('CMP_7028BContingencyCMP_7028B')
                                self.update_contingency_status("yes")
                                self.contingency.contigency_chatbot_response(sentence)
                            if type_of_intention == "goodbye":
                                get_current_info = self.check_current_journey_data()
                                if get_current_info:
                                    self.fo.write("You have an on-going search. You may choose to reset it.")
                                else:
                                    print(random.choice(intentions[type_of_intention]["responses"]))
                                    self.fo.write(random.choice(intentions[type_of_intention]["responses"]))
                            return True
        if not intentions_met:
            self.update_train_fare_counter("1")
            print(random.choice(intentions['default']))
            self.fo.write(random.choice(intentions['default']))
            return None
    
    def delay_information_extraction_mechanism(self, user_input, extraction_type):
        """
        Extracts delay information from user input based on the extraction type.

        Args:
            user_input (str): The user input containing delay information.
            extraction_type (str): The type of information to extract (e.g., "LOCATION", "TIME").

        Returns:
            bool: True if the extraction is successful and the information is saved, False otherwise.
        """
        journey_info = pd.read_csv(self.delay_info_data)
        user_input = self.lemmatise_and_clean(user_input)

        if extraction_type.upper() in ["LOCATION"]:
            # Locations / Stations extraction 
            locations_dict = self.extract_delay_location(user_input)
            if not locations_dict:
                print("Un-able to save location since no station detected from input yet.")
                return False
            elif "current_depart_station" in locations_dict:
                journey_info.at[0, 'current_station'] = locations_dict["current_depart_station"]
                journey_info.to_csv(self.delay_info_data, index=False)
                return True
        
        elif extraction_type.upper() in ["TIME"]:
            time_dict = self.extraction_delay_time(user_input)
            if time_dict == {}:
                print("No time found in the input. Please provide departing times of current and origin station.")
                return False
            else:
                if 'current_depart_station_time' in time_dict and 'origin_depart_station_time' not in time_dict:
                    journey_info.at[0, 'dept_time_curr_st'] = time_dict["current_depart_station_time"]
                    journey_info.to_csv(self.delay_info_data, index=False)
                    return False
                elif 'origin_depart_station_time' in time_dict and 'current_depart_station_time' not in time_dict:
                    journey_info.at[0, 'dept_time_origin'] = time_dict["origin_depart_station_time"]
                    journey_info.to_csv(self.delay_info_data, index=False)
                    return False
                else:
                    journey_info.at[0, 'dept_time_curr_st'] = time_dict["current_depart_station_time"]
                    journey_info.at[0, 'dept_time_origin'] = time_dict["origin_depart_station_time"]
                    journey_info.to_csv(self.delay_info_data, index=False)
                    return True
        else:
            print(f"Invalid Extraction Type given: {extraction_type}")
            return False
    
    # extract and write required information
    def information_extraction_mechanism(self, user_input, extraction_type):
        """
        Extracts information from user input based on the specified extraction type.

        Args:
            user_input (str): The user input from which information needs to be extracted.
            extraction_type (str): The type of information to be extracted. Valid values are "LOCATION", "DATE", and "TIME".

        Returns:
            bool: True if the information is successfully extracted and saved, False otherwise.
        """
        journey_info = pd.read_csv(self.current_journey_info)

        if extraction_type.upper() in ["LOCATION"]:
            # Locations / Stations extraction 
            locations_dict = self.extract_location(user_input)
            if not locations_dict:
                print("Un-able to save location/s since no stations detected from input yet.")
                return False
            elif "depart_station" in locations_dict and "arrival_station" in locations_dict:
                journey_info.at[0, 'origin'] = locations_dict["depart_station"]
                journey_info.at[0, 'destination'] = locations_dict["arrival_station"]
                journey_info.to_csv(self.current_journey_info, index=False)
                return True
            elif "depart_station" in locations_dict and "arrival_station" not in locations_dict:
                journey_info.at[0, 'origin'] = locations_dict["depart_station"]
                journey_info.to_csv(self.current_journey_info, index=False)
                return False
            elif "arrival_station" in locations_dict and "depart_station" not in locations_dict:
                journey_info.at[0, 'destination'] = locations_dict["arrival_station"]
                journey_info.to_csv(self.current_journey_info, index=False)
                return False      
        
        elif extraction_type.upper() in ["DATE"]:
            # Date extraction
            date_list = self.extract_date_via_nlp(user_input)
            if not date_list:
                print("Un-able to save date since no date detected from input yet.")
                return False
            else:
                journey_info.at[0, 'date'] = date_list[0]
                journey_info.to_csv(self.current_journey_info, index=False) 
        elif extraction_type.upper() in ["TIME"]:
            # Time --> Hour Minutes extraction
            get_time = self.extraction_time(user_input)
            if not get_time:
                print("Un-able to save time since no time detected from input yet")
                return False
            else:
                journey_info.at[0, 'time'] = get_time
                journey_info.to_csv(self.current_journey_info, index=False)
    
    def time_conversion_and_encoding(self):
        """
        Converts the time strings to datetime format and encodes the station name.
        
        Returns:
            df (pandas.DataFrame): A DataFrame containing the encoded station name and the converted time values.
        """
        get_info = self.check_delay_info()
        get_station_name = get_info['current_station']
        get_current_station_dept_time = get_info['dept_time_curr_st']
        get_origin_station_dept_time = get_info['dept_time_origin']

        try:
            # Try to convert the time string to datetime format with seconds
            curr_time_value = pd.to_datetime(get_current_station_dept_time, format='%H:%M:%S')
            origin_time_value = pd.to_datetime(get_origin_station_dept_time, format='%H:%M:%S')
            curr_seconds = curr_time_value.hour * 3600 + curr_time_value.minute * 60 + curr_time_value.second
            origin_seconds = origin_time_value.hour * 3600 + origin_time_value.minute * 60 + origin_time_value.second
        except:
            # If the conversion fails, try to convert the time string to datetime format without seconds
            curr_time_value = pd.to_datetime(get_current_station_dept_time, format='%H:%M')
            origin_time_value = pd.to_datetime(get_origin_station_dept_time, format='%H:%M')
            curr_seconds = curr_time_value.hour * 3600 + curr_time_value.minute * 60 + curr_time_value.second
            origin_seconds = origin_time_value.hour * 3600 + origin_time_value.minute * 60 + origin_time_value.second

        get_stations_dict = self.fetch_delay_stations()
        for k, v in get_stations_dict.items():
            if k == get_station_name:
                encoded_value = v[1]
        
        ordered_dict = OrderedDict([('tpl', encoded_value), ('depart_from_LDN', origin_seconds),('depart_from_current_station', curr_seconds)])
        df = pd.DataFrame([ordered_dict])
        return df
    
    def model_loading_and_prediction(self):
        """
        Loads the model, performs time conversion and encoding, and predicts the delay.

        Returns:
            float: The predicted delay time.
        """
        df = self.time_conversion_and_encoding()
        print("Predicting Delay..")
        final_delay_time = regression_model_functions.make_delay_prediction(df, str)
        print(final_delay_time)
        self.fo.write(f"CMP_7028BDelayPrediction:CMP_7028B{final_delay_time}")
        return final_delay_time
    
    def scraper_run(self):
        """
        Runs the scraper to find the cheapest train ticket for the given journey.

        This method checks if all the required information for the journey is received. If all the required information is
        available, it proceeds to run the scrapers via multi-processing. After running the scrapers, it compares the prices
        and finds the cheapest train ticket. It then writes the journey details, including the cheapest website, price, and
        link, to a file.

        Returns:
            None
        """
        # check required info dict again if all required information received or not
        current_info_dict = self.check_current_journey_data()
        if ('origin' in current_info_dict.keys() and current_info_dict['origin'] not in ['', None]) and ('destination' in current_info_dict.keys() and current_info_dict['destination'] not in ['', None]) and ('date' in current_info_dict.keys() and current_info_dict['date'] not in ['', None]) and ('time' in current_info_dict.keys() and current_info_dict['time'] not in ['', None]):
            print("Received all required information. Thank you. Proceeding to find cheapest train ticket for your journey")
            # Run scrapers via multi-processing once all info is received
            self.scraper.main()
            print("Scrapers ran successfully. Proceeding to find cheapest train ticket.")
            price_finder = self.cheapest_price_finder.compare_prices()
            cheapest_website, chepeast_price, wesbite_link = price_finder[0], price_finder[1][0], price_finder[1][1]
            if cheapest_website == "greateranglia.json":
                cheapest_website = "https://www.greateranglia.co.uk/"
            elif cheapest_website == "LNER.json":
                cheapest_website = "https://www.lner.co.uk/"
            elif cheapest_website == "nationalrail.json":
                cheapest_website = "https://www.nationalrail.co.uk/"
            elif cheapest_website == "trainpal.json":
                cheapest_website = "https://www.mytrainpal.com/"
            elif cheapest_website == "southernRailways.json":
                cheapest_website = "https://www.southernrailway.com/"
            elif cheapest_website == "mytrainticket.json":
                cheapest_website = "https://www.mytrainticket.co.uk/"
            read_csv=open(self.current_journey_info,'r')
            read_data = read_csv.readlines()
            for info in read_data[1:]:
                info = info.split(',')
                t = info[3]
                t = t.rstrip() 
            self.fo.write(f"CMP_7028BDeparting Station:CMP_7028B{info[0]}")  
            self.fo.write(f"CMP_7028BArriving Station:CMP_7028B{info[1]}")
            self.fo.write(f"CMP_7028BDate:CMP_7028B{info[2]}") 
            self.fo.write(f"CMP_7028BTime:CMP_7028B{info[3]}")     
            self.fo.write(f"CMP_7028BWebsite Name:CMP_7028B{cheapest_website}")
            self.fo.write(f"CMP_7028BPrice:CMP_7028B{chepeast_price}")
            self.fo.write(f"CMP_7028BLink:CMP_7028B{wesbite_link}")
            # return_status = self.check_return_request()
            return_counter = self.check_return_counter()
            print(f"RETURN COUNTER: {return_counter}")
            if int(return_counter) == 0:
                self.fo.write(f"CMP_7028BReturnCMP_7028B")
                  
    
    def delay_progress_check(self, user_input):
        """
        Check the progress of delay information extraction and update the data accordingly.

        Args:
            user_input (str): The user's input.

        Returns:
            None
        """
        current_info_dict = self.check_delay_info()
        if not current_info_dict:
            print("No saved info found. Extracting fresh delay information..")
            self.delay_information_extraction_mechanism(user_input, extraction_type="location")
            self.delay_information_extraction_mechanism(user_input, extraction_type="time")
        elif current_info_dict['current_station'] in ['', None] and current_info_dict['dept_time_curr_st'] in ['', None] and current_info_dict['dept_time_origin'] not in ['', None]:
            self.delay_information_extraction_mechanism(user_input, extraction_type="location")
            self.delay_information_extraction_mechanism(user_input, extraction_type="time")
        elif current_info_dict['current_station'] in ['', None] and current_info_dict['dept_time_curr_st'] not in ['', None] and current_info_dict['dept_time_origin'] in ['', None]:
            self.delay_information_extraction_mechanism(user_input, extraction_type="location")
            self.delay_information_extraction_mechanism(user_input, extraction_type="time")
        elif current_info_dict['current_station'] not in ['', None] and current_info_dict['dept_time_curr_st'] in ['', None] and current_info_dict['dept_time_origin'] in ['', None]:
            self.delay_information_extraction_mechanism(user_input, extraction_type="time")
        elif current_info_dict['current_station'] not in ['', None] and current_info_dict['dept_time_curr_st'] not in ['', None] and current_info_dict['dept_time_origin'] in ['', None]:
            self.delay_information_extraction_mechanism(user_input, extraction_type="time")
        elif current_info_dict['current_station'] not in ['', None] and current_info_dict['dept_time_curr_st'] in ['', None] and current_info_dict['dept_time_origin'] not in ['', None]:
            self.delay_information_extraction_mechanism(user_input, extraction_type="time")
        elif current_info_dict['current_station'] in ['', None] and current_info_dict['dept_time_curr_st'] not in ['', None] and current_info_dict['dept_time_origin'] not in ['', None]:
            self.delay_information_extraction_mechanism(user_input, extraction_type="location")
    
    def progress_check(self, user_input):
        """
        Checks the progress of the conversation and extracts information based on the current state.

        Args:
            user_input (str): The user's input.

        Returns:
            None
        """
        current_info_dict = self.check_current_journey_data()
        if not current_info_dict:
            self.fo.write("Happy to find the train tickets for you. ")
            print("No saved info found. Extracting fresh information..")
            self.information_extraction_mechanism(user_input, extraction_type="location")
            self.information_extraction_mechanism(user_input, extraction_type="date")
            self.information_extraction_mechanism(user_input, extraction_type="time")
        elif current_info_dict['origin'] in ['', None] and current_info_dict['destination'] in ['', None] and current_info_dict['date'] not in ['', None] and current_info_dict['time'] not in ['', None]:
            self.information_extraction_mechanism(user_input, extraction_type="location")
        elif current_info_dict['date'] in ['', None] and current_info_dict['time'] not in ['', None] and current_info_dict['origin'] not in ['', None] and current_info_dict['destination'] not in ['', None]:
            self.information_extraction_mechanism(user_input, extraction_type="date")
        elif current_info_dict['time'] in ['', None] and current_info_dict['date'] not in ['', None] and current_info_dict['origin'] not in ['', None] and current_info_dict['destination'] not in ['', None]:
            self.information_extraction_mechanism(user_input, extraction_type="time")
        elif current_info_dict['date'] in ['', None] and current_info_dict['time'] in ['', None] and current_info_dict['origin'] not in ['', None] and current_info_dict['destination'] not in ['', None]:
            self.information_extraction_mechanism(user_input, extraction_type="date")
            self.information_extraction_mechanism(user_input, extraction_type="time")
        elif current_info_dict['destination'] in ['', None] and current_info_dict['date'] in ['', None] and current_info_dict['time'] in ['', None] and current_info_dict['origin'] not in ['', None]:
            self.information_extraction_mechanism(user_input, extraction_type="location")
            self.information_extraction_mechanism(user_input, extraction_type="date")
            self.information_extraction_mechanism(user_input, extraction_type="time")
        elif current_info_dict['origin'] in ['', None] and current_info_dict['date'] in ['', None] and current_info_dict['time'] in ['', None] and current_info_dict['destination'] not in ['', None]:
            self.information_extraction_mechanism(user_input, extraction_type="location")
            self.information_extraction_mechanism(user_input, extraction_type="date")
            self.information_extraction_mechanism(user_input, extraction_type="time")
        elif current_info_dict['origin'] in ['', None] and current_info_dict['date'] not in ['', None] and current_info_dict['time'] not in ['', None] and current_info_dict['destination'] not in ['', None]:
            self.information_extraction_mechanism(user_input, extraction_type="location")
        elif current_info_dict['destination'] in ['', None] and current_info_dict['date'] not in ['', None] and current_info_dict['time'] not in ['', None] and current_info_dict['origin'] not in ['', None]:
            self.information_extraction_mechanism(user_input, extraction_type="location")
        elif current_info_dict['origin'] in ['', None] and current_info_dict['time'] in ['', None] and current_info_dict['destination'] not in ['', None] and current_info_dict['date'] not in ['', None]:
            self.information_extraction_mechanism(user_input, extraction_type="location")
            self.information_extraction_mechanism(user_input, extraction_type="time")
        elif current_info_dict['destination'] in ['', None] and current_info_dict['time'] in ['', None] and current_info_dict['origin'] not in ['', None] and current_info_dict['date'] not in ['', None]:
            self.information_extraction_mechanism(user_input, extraction_type="location")
            self.information_extraction_mechanism(user_input, extraction_type="time")
        elif current_info_dict['origin'] in ['', None] and current_info_dict['date'] in ['', None] and current_info_dict['time'] not in ['', None] and current_info_dict['destination'] not in ['', None]:
            self.information_extraction_mechanism(user_input, extraction_type="location")
            self.information_extraction_mechanism(user_input, extraction_type="date")
        elif current_info_dict['destination'] in ['', None] and current_info_dict['date'] in ['', None] and current_info_dict['origin'] not in ['', None] and current_info_dict['time'] not in ['', None]:
            self.information_extraction_mechanism(user_input, extraction_type="location")
            self.information_extraction_mechanism(user_input, extraction_type="date")
    
    def delay_chatbot_response(self, user_input):
        """
        This method handles the delay chatbot response. It writes the delay information to a file,
        checks the progress of the delay, retrieves the delay information, and calculates the delay prediction.

        Args:
            user_input (str): The user input.

        Returns:
            None
        """
        self.fo.write('CMP_7028B DELAY CMP_7028B')
        self.delay_progress_check(user_input)
        final_info_dict = self.check_delay_info()
        if ('current_station' in final_info_dict.keys() and final_info_dict['current_station'] not in ['', None]) and ('dept_time_curr_st' in final_info_dict.keys() and final_info_dict['dept_time_curr_st'] not in ['', None]) and ('dept_time_origin' in final_info_dict.keys() and final_info_dict['dept_time_origin'] not in ['', None]):
            print("Received all required information. Thank you. Proceeding to calculate delay prediction. ")
            model_prediction = self.model_loading_and_prediction()
            if model_prediction:
                check_delay_request = self.check_delay_request()
                if check_delay_request == "yes":
                    self.update_delay_request("no")
                    self.clear_delay_data()
            else:
                print("Un-able to calculate delay at the moment. Please try again later. ")
    
    def chat_response(self, user_input, min_similarity=0.60):
            cleaned_user_input = self.lemmatise_and_clean(user_input)
            doc_1 = self.nlp(cleaned_user_input)
            similarities = {}

            # Fetch labels and sentences
            labels, sentences = self.match_sentences()
            for idx, sentence in enumerate(sentences):
                cleaned_sentence = self.lemmatise_and_clean(sentence)
                doc_2 = self.nlp(cleaned_sentence)
                similarity = doc_2.similarity(doc_1)
                similarities[idx] = similarity
            current_info_dict = self.check_current_journey_data()
            max_similarity_idx = max(similarities, key=similarities.get)
            print(f'similarity : {labels[max_similarity_idx]}')
            print(f'similarity index : {[max_similarity_idx]}')
            print(f'similarity index : {similarities[max_similarity_idx]}')
            
            if similarities[max_similarity_idx] >= min_similarity:
                print(f'similarity : {labels[max_similarity_idx]}')
                if labels[max_similarity_idx] == 'train' or labels[max_similarity_idx] == "location" or labels[max_similarity_idx] == "date" or labels[max_similarity_idx] == "time":
                    self.update_train_fare_counter("0")
                    check_delay_request = self.check_delay_request()
                    check_contingency_request = self.check_contigency_status()
                    if "delay" in user_input or "predict" in user_input or "predict delay" in user_input:
                        check_current_info = self.check_current_journey_data()
                        if check_current_info:
                            print("You have an on-going cheapest fare search request. Please reset it first in order to proceed with the delay.")
                            self.fo.write("CMP_7028BOnGoingCMP_7028BYou have an on-going cheapest fare search request. Please reset it first in order to proceed with the delay.")
                            return False
                        else:
                            self.update_delay_request("yes")
                            self.delay_chatbot_response(user_input)
                    elif check_delay_request == "yes":
                        if "book" in user_input or "train" in user_input or "ticket" in user_input:
                            print("You have an on-going cheapest fare search request. Please reset it first in order to proceed with the delay.")
                            self.fo.write("CMP_7028BOnGoingCMP_7028BYou have an on-going delay search request. Please reset it first in order to proceed with the ticket search.")
                            return False
                        elif "contingencies" in user_input or "contingency" in user_input or "diversions" in user_input or "diversion" in user_input:
                            print("You have an on-going delay search request. Please reset it first in order to proceed with the contingencies.")
                            self.fo.write("CMP_7028BOnGoingCMP_7028BYou have an on-going delay search request. Please reset it first in order to proceed with the contingencies.")
                            return False
                        else:
                            self.delay_chatbot_response(user_input)
                    elif "contingency" in user_input or "blockage" in user_input or "partial blockage" in user_input or "full blockage" in user_input or "Contingency" in user_input or "Blockage" in user_input or "Partial" in user_input or "Full Blockage" in user_input or "contingencies" in user_input or "Contingencies" in user_input:
                        Check_current_journey = self.check_current_journey_data()
                        if Check_current_journey:
                            if (Check_current_journey['origin']!='' or Check_current_journey['destination']!='' or Check_current_journey['date']!='' or Check_current_journey['time']!=''):
                                print("You have an on-going cheapest fare search request. Please reset it first in order to proceed with the contingency plans.")
                                self.fo.write("CMP_7028BOnGoingCMP_7028BYou have an on-going cheapest fare search request. Please reset it first in order to proceed with the contingency plans.")
                                return False
                        else:
                            self.fo.write('CMP_7028BContingencyCMP_7028B')
                            print("Contingency plans are available for Greater Anglia's Great Eastern Tracks only between Colchester and Norwich")
                            self.update_contingency_status("yes")
                            self.contingency.contigency_chatbot_response(user_input)
                    elif check_contingency_request == "yes":
                        self.fo.write('CMP_7028BContingencyCMP_7028B')
                        check_current_info = self.check_current_journey_data()
                        if not check_current_info:
                            if "booking" in user_input or "book" in user_input or "ticket" in user_input or "fare" in user_input:
                                print("You have an on-going contingency plan request search. Please reset it first in order to proceed with the ticket search.")
                                self.fo.write("CMP_7028BOnGoingCMP_7028BYou have an on-going contingency plan request search. Please reset it first in order to proceed with the ticket search.")
                                return False
                            else:
                                self.contingency.contigency_chatbot_response(user_input)
                        else:
                            print("You have an on-going contingency plan request search. Please reset it first in order to proceed with the ticket search.")
                            self.fo.write("CMP_7028BOnGoingCMP_7028BYou have an on-going contingency plan request search. Please reset it first in order to proceed with the ticket search.")
                            return False
                    else:
                        self.fo.write("CMP_7028BTrainBookCMP_7028B")
                        return_status = self.check_return_request()
                        if return_status == "yes":
                            self.return_ticket_mechanism(user_input)
                            check_current_info = self.check_current_journey_data()
                            if check_current_info['date'] in ['', None] or check_current_info['time'] in ['', None]:
                                self.progress_check(user_input)
                            else:
                                self.update_return_request("no")
                                self.update_return_counter("0")
                                self.update_train_fare_counter("0")
                                self.clear_journey_data()
                                self.clear_scrapers_data()
                        else:
                            self.progress_check(user_input)            
                            
                elif labels[max_similarity_idx] == "return":
                    self.update_train_fare_counter("0")
                    check_delay_request = self.check_delay_request()
                    Check_current_journey = self.check_current_journey_data()
                    if check_delay_request == "yes":
                        print("You have an on-going delay search in place currently. Please reset it first in order to find cheapest return train fares. ")
                        self.fo.write("CMP_7028BOnGoingCMP_7028BYou have an on-going delay search in place currently. Please reset it first in order to find cheapest return train fares.")
                        return False

                    elif len(Check_current_journey)==0 or (Check_current_journey['origin']!='' and Check_current_journey['destination']!='' and Check_current_journey['date']!='' and Check_current_journey['time']!=''):
                        self.fo.write("CMP_7028BTrainBookCMP_7028B")
                        check_contingency_request = self.check_contigency_status()
                        if check_contingency_request == "yes":
                            print("You have an on-going contingency plan request search. Please reset it first in order to proceed with the return request.")
                            self.fo.write("CMP_7028BOnGoingCMP_7028BYou have an on-going contingency plan request search. Please reset it first in order to proceed with the return request.")
                            return False
                        
                        self.update_return_request("yes")
                        self.return_ticket_mechanism(user_input)
                        check_current_info = self.check_current_journey_data()
                        
                        if check_current_info['date'] in ['', None] or check_current_info['time'] in ['', None]:
                            self.progress_check(user_input)
                        else:
                            self.update_return_request("no")
                            self.update_return_counter("0")
                            self.update_train_fare_counter("0")
                            self.clear_journey_data()
                            self.clear_scrapers_data()
                    else:
                        print("You have an on-going outbound journey search. Please reset it first in order to proceed with your return ticket.")
                        self.fo.write("CMP_7028BOnGoingCMP_7028BYou have an on-going outbound journey search. Please reset it first in order to proceed with your return ticket.")
                        return False
                    
                elif labels[max_similarity_idx] == "reset":
                    current_delay_info = self.check_delay_info()
                    delay_confirmation_status = self.check_delay_request()
                    contingency_status = self.check_contigency_status()
                    if not current_info_dict and not current_delay_info and delay_confirmation_status == "no" and contingency_status =='no':
                        print("Nothing to reset at the moment.")
                        self.fo.write("CMP_7028BOnGoingCMP_7028BNothing to reset at the moment.")
                    else:
                        print("Initiating reset protocol.")
                        self.fo.write("CMP_7028BOnGoingCMP_7028BInitiating reset protocol.")
                        self.clear_journey_data()
                        self.update_delay_request("no")
                        self.update_return_request("no")
                        self.update_return_counter("0")
                        self.update_train_fare_counter("0")
                        self.update_contingency_status("no")
                        self.clear_delay_data()
                        self.clear_contingency_details()
                        self.clear_scrapers_data()
                        print("Existing journey search cleared.")
                        self.fo.write("CMP_7028BOnGoingCMP_7028BExisting journey search cleared.")
                elif labels[max_similarity_idx] == "delay":
                    current_info_dict = self.check_current_journey_data()
                    return_request = self.check_return_request()
                    print('dösfjhgdsckghv',current_info_dict)
                    if current_info_dict:
                            print("You have an on-going cheapest fare search going on. Please reset it first.")
                            self.fo.write("CMP_7028BOnGoingCMP_7028BYou have an on-going cheapest fare search going on. Please reset it first.")
                            if (current_info_dict['origin']!='' or current_info_dict['destination']!='' or current_info_dict['date']!='' or current_info_dict['time']!=''):
                                self.update_train_fare_counter("1")
                            return False
                    elif return_request == "yes":
                            print("You have an on-going return cheapest fare search. Please reset it first.")
                            self.fo.write("CMP_7028BOnGoingCMP_7028BYou have an on-going return cheapest fare search goung on. Please reset it first.")
                            return False
                    elif "contingency" in user_input or "blockage" in user_input or "partial blockage" in user_input or "full blockage" in user_input or "Contingency" in user_input or "Blockage" in user_input or "Partial" in user_input or "Full Blockage" in user_input or "contingencies" in user_input or "Contingencies" in user_input:
                        self.fo.write('CMP_7028BContingencyCMP_7028B')
                        print("Contingency plans are available for Greater Anglia's Great Eastern Tracks only between Colchester and Norwich")
                        self.update_contingency_status("yes")
                        self.contingency.contigency_chatbot_response(user_input)
                    else:
                        check_contingency_request = self.check_contigency_status()
                        if check_contingency_request == "yes":
                            self.fo.write('CMP_7028BContingencyCMP_7028B')
                            if "delay" in user_input or "ticket" in user_input:
                                print("You have on-going contingency request. Please reset it first in order to proceed with the delay.")
                                self.fo.write("CMP_7028BOnGoingCMP_7028BYou have on-going contingency request. Please reset it first in order to proceed with the delay.")
                                return False
                            else:
                                self.contingency.contigency_chatbot_response(user_input)
                        else:
                            self.update_delay_request("yes")
                            self.delay_chatbot_response(user_input)
                            check_current_info = self.check_current_journey_data()


                elif labels[max_similarity_idx] == "contingency":
                    self.fo.write('CMP_7028BContingencyCMP_7028B')
                    current_info_dict = self.check_current_journey_data()
                    return_request = self.check_return_request()
                    self.contingency.contigency_chatbot_response(user_input)
                    check_delay_request = self.check_delay_request()
                    
                    if current_info_dict:
                        print("You have an on-going cheapest fare search going on. Please reset it first in order to proceed with contingency.")
                        self.fo.write("CMP_7028BOnGoingCMP_7028BYou have an on-going cheapest fare search going on. Please reset it first in order to proceed with contingency.")
                        if (current_info_dict['origin']!='' or current_info_dict['destination']!='' or current_info_dict['date']!='' or current_info_dict['time']!=''):
                                self.update_train_fare_counter("1")
                        return False
                        
                    elif return_request == "yes":
                        print("You have an on-going return cheapest fare search. Please reset it first in order to proceed with the contingency.")
                        self.fo.write("CMP_7028BOnGoingCMP_7028BYou have an on-going return cheapest fare search goung on. Please reset it first in order to proceed with the contingency.")
                        return False
                        
                    elif check_delay_request == "yes":
                        print("You have on-going delay request. Please reset it first in order to proceed with the contingency.")
                        self.fo.write("CMP_7028BOnGoingCMP_7028BYou have on-going delay request. Please reset it first in order to proceed with the contingency.")
                        return False
            
                    else:
                        self.contingency.contigency_chatbot_response(user_input)
                
                check_delay_request = self.check_delay_request()
                check_contingency_request = self.check_contigency_status()
                check_current_info = self.check_current_journey_data()
                if check_delay_request == "no" and check_contingency_request == "no":
                    check_train_fare_counter = self.check_train_fare_counter()
                    check_train_fare_counter = int(check_train_fare_counter)
                    if check_train_fare_counter == 0:
                        self.scraper_run() 
                    else:
                        print("You have an on-going return cheapest fare search. Please reset it first in order to proceed with the new search with new details.")
                        self.fo.write("CMP_7028BOnGoingCMP_7028BYou have an on-going return cheapest fare search. Please reset it first in order to proceed with the new search with new details.")
                        return False
            else:  
                current_info_dict = self.check_current_journey_data()
                check = 0
                 
                if "contingency" in user_input or "blockage" in user_input or "partial blockage" in user_input or "full blockage" in user_input or "Contingency" in user_input or "Blockage" in user_input or "Partial" in user_input or "Full Blockage" in user_input or "contingencies" in user_input or "Contingencies" in user_input:

                    if (current_info_dict and (current_info_dict['origin']!='' or current_info_dict['destination']!='' or current_info_dict['date']!='' or current_info_dict['time']!='')):
                        print("You have an on-going cheapest fare search. Please reset it first in order to proceed with the new search with new details.")
                        self.fo.write("CMP_7028BOnGoingCMP_7028BYou have an on-going cheapest fare search. Please reset it first in order to proceed with the new search with new details.")
                        self.update_train_fare_counter("1")
                        check = 1
                        return False
                   

                elif  "delay" in user_input or "predict" in user_input or "predict delay" in user_input:

                    if (current_info_dict and (current_info_dict['origin']!='' or current_info_dict['destination']!='' or current_info_dict['date']!='' or current_info_dict['time']!='')):
                        print("You have an on-going cheapest fare search. Please reset it first in order to proceed with the new search with new details.")
                        self.fo.write("CMP_7028BOnGoingCMP_7028BYou have an on-going cheapest fare search. Please reset it first in order to proceed with the new search with new details.")
                        self.update_train_fare_counter("1")
                        check = 1
                        return False
                    
                   
                if check ==0:
                    self.check_intention_by_keyword(user_input)

                
    

if __name__ == "__main__":
    obj = ChatbotConversation()
    
    json_data = json.loads(sys.argv[1])#getting data from the server side
    obj.chat_response(json_data)

    # obj.chat_response("can you assist me in finding train ticket from norwich to london liverpool street for the date 5th june 2024 for 10:35 am?")
    # obj.chat_response("i want a return as well on 9th june at 11 am")
    # obj.chat_response("the date is 18th may")
    # obj.chat_response("please predict the possible delay")
    # obj.chat_response("I would like to find train tickets from norwich to london liverpool street")
    # obj.chat_response("arriving station is london liverpool street")
    # obj.chat_response("please predict a possible delay")
    # obj.chat_response("the current stations is diss. My departing time from origin is 13:00 and from current station is 14:00")
    # obj.chat_response("please reset my search")
    # obj.chat_response("can you predict the delay from diss. My departing time from origin is 12:00 and from current station is 14:00")
    # obj.chat_response("departing time from origin is 13:00 and from current station is 14:00")
    # obj.chat_response("hi there")
    # obj.chat_response("can you tell me the contingency plan?")
    # obj.chat_response("the location is Diss")
    # obj.chat_response("i want to find a train ticket from norwich")
    # obj.chat_response("the station is diss")
    # obj.chat_response("can you tell me the contingency plan as there is full blockage between train station diss and norwich?")
    
    # obj.chat_response("the station one is diss")
    # time.sleep(1)
    # obj.chat_response("the blockage type is full")
    # time.sleep(1)
    # obj.chat_response("the station two is norwich")
    # obj.chat_response("can you tell me the contingency plan ?")
    # obj.chat_response('the time will be 12:33 pm and the date will be 27th may')
    # obj.extract_date_via_nlp("can you assist me in finding train ticket from norwich to london liverpool street for the date 17th may 2024 for 10:35 am?")
    # obj.extraction_time("can you assist me in finding train ticket from norwich to london liverpool street for the date 24th may 2024 for 10:35 am?")
    # obj.date_extraction_via_regex("can you assist me in finding train ticket from norwich to london liverpool street for the date june 16 10:35 am?")
    # obj.date_extraction_via_regex("the date is june of 16th 2024")
    # obj.chat_response("the time will be 12:34 a.m")