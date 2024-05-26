import os
import sys
import csv
import json
import spacy
import warnings
import pandas as pd
from fuzzywuzzy import fuzz
warnings.filterwarnings('ignore')


class ContingencyPlan(object):
    def __init__(self) -> None:
        if sys.platform.startswith('win'):
            self.contingencies_info_path = os.getcwd() + "/contingencies_info.json"
            self.contingency_details_path = os.getcwd() + "/contingencies_details.csv"
            self.contingency_request_path = os.getcwd() + '/contingency_confirmation.txt'
        elif sys.platform.startswith('darwin'):
            self.contingencies_info_path = os.getcwd() + "/contingencies_info.json"
            self.contingency_details_path = os.getcwd() + "/contingencies_details.csv"
            self.contingency_request_path = os.getcwd() + '/contingency_confirmation.txt'
        
        self.fo = open("output.txt", "a")#writing the response to the output.txt file to send the response to the node:js app.
        
        # Considering blockages on  occurring between Colchester and Norwich in Greater Anglia’s Great Eastern Tracks, specified in document D3, Sections 1 and 2 (as per Part C requirements)
        self.stations_name_list = ["Colchester", "Manningtree", "Ipswich", "Stowmarket", "Diss", "Norwich"]
        self.blockage_type = ["Partial", "Full"]

        # llm model
        self.nlp = spacy.load('en_core_web_lg')

    # Function to lemmatize the text and remove stop words and punctuations, and then return the cleaned text
    def lemmatise_and_clean_contingency(self, text):
        doc = self.nlp(text.lower())
        out = ""
        for token in doc:
            if not token.is_punct and not token.is_stop:
                out = out + token.text + " "
            elif token.text == 'full' or token.text == 'partial':
                out = out + token.text + " "
        return out.strip()
    
    def check_contingency_details(self):
        # check contingency data
        current_contingency_dict = {}
        with open(self.contingency_details_path, newline='')as csvfile:
            reader = csv.DictReader(csvfile)
            for contingency in reader:
                station_1, station_2, blockage_type = contingency['Station1'], contingency['Station2'], contingency['BlockageType']
                current_contingency_dict['Station1'] = station_1
                current_contingency_dict['Station2'] = station_2
                current_contingency_dict['BlockageType'] = blockage_type
        csvfile.close()    
        return current_contingency_dict
    
    def clear_contingency_details(self):
        # clear csv data once contigency plan is returned for the user
        fo = open(self.contingency_details_path, "w")
        fo.write("")
        fo.write("Station1,Station2,BlockageType")
        fo.close()
    
    def check_contigency_status(self):
        fo = open(self.contingency_request_path, "r")
        data = fo.readlines()
        for line in data[1:]:
            line = line.split()
            contingency_req = line[0]
        fo.close()
        return contingency_req.lower()
    
    def update_contingency_status(self, status):
        fo = open(self.contingency_request_path, "w")
        fo.write("CONTINGENCY_REQUESTED\n")
        fo.write(status.lower())
        fo.close()
    
    def view_contingency_plans(self):
        with open(self.contingencies_info_path) as f:
            contingency_plans = json.load(f)
        f.close()
        return contingency_plans
    
    def matched_contingency_plans(self, input_stations, blockage_type):
        plans = self.view_contingency_plans()
        stations_found = []
        for plan_type in plans:
            if plan_type == blockage_type:
                all_stations_dict = plans[plan_type]["Stations"]
        for stations, guidelines in all_stations_dict.items():
            if stations == input_stations:
                stations_found.append("found")
                return guidelines
            if not stations_found:
                input_stations = input_stations.split(",")
                first_station, second_station = input_stations[0], input_stations[1]
                input_stations = f"{second_station},{first_station}"
                if stations == input_stations:
                    return guidelines

    def contingency_type_extraction(self, user_input):
        type_dictionary = {}
        text = self.lemmatise_and_clean_contingency(user_input)
        text = text.upper()
        
        matches = []
        for type in self.blockage_type:
            if type.upper() in text.upper():
                matches.append(type.upper())
        
        sent = text.split()
        new_match = []
        for t in matches:
            t = t.split()
            new_match.extend(t)
        for s in new_match:
            if s not in sent:
                matches.remove(s)
        
        def sub_function():
            multiple_matches = []
            # temporarily remove to, from and other words related to departure or arrival
            departure_words = ["from", "depart", "departure", "departing", "city", "visiting"]
            arrival_words = ["to", "arrive", "arrival", "arriving", "book", "ticket", "train", "Colchester", "Manningtree", "Ipswich", "Stowmarket", "Diss", "Norwich"]
            # Convert text to lowercase for case-insensitive matching
            text_lower = text.lower()
            # Split the text into words
            words = text_lower.split()
            # Filter out words related to departure and arrival
            filtered_words = [word for word in words if word not in departure_words and word not in arrival_words]
            # Join the remaining words back into a string
            cleaned_text = ' '.join(filtered_words)
            #from fuzzywuzzy import fuzz
            # Set your desired threshold for similarity
            threshold = 75
            # Iterate through the blockage type
            cleaned_text = cleaned_text.split()
            for cleaned in cleaned_text:
                for station in self.blockage_type:
                    # Calculate similarity score using token_set_ratio
                    similarity = fuzz.token_set_ratio(station.upper(), cleaned.upper())
                    # Check if similarity score is above the threshold
                    if similarity >= threshold:
                        multiple_matches.append(station)
            
            if multiple_matches:
                print(f"Matches found: {multiple_matches}")
                self.fo.write(f"CMP_7028BMultipleMatches:CMP_7028B{multiple_matches}")
                print("Please select from the top matches found or be specific with the search.")
        
        
        if len(matches) == 0:
            print("Please provide blockage type on Greater Eastern track. Hint: Can you tell me the contigency plan as there is partial blockage between train station Diss and Norwich")
            sub_function()
            return type_dictionary
        
        elif len(matches) == 1:
            print(f"Blockage Type detected: {matches[0]}")
            type_dictionary["blockage_type"] =  matches[0]
            return type_dictionary
        else:
            print("Please give 1 blockage type only, either partial or full.")
            return False
    
    def contingency_extraction_location(self, user_input):
        stations_dictionary = {}
        text = self.lemmatise_and_clean_contingency(user_input)
        text = text.upper()
        
        matches = []
        for stations in self.stations_name_list:
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
                for station in self.stations_name_list:
                    # Calculate similarity score using token_set_ratio
                    similarity = fuzz.token_set_ratio(station.upper(), cleaned.upper())
                    # Check if similarity score is above the threshold
                    if similarity >= threshold:
                        multiple_matches.append(station)
            
            if multiple_matches:
                print(f"Multiple Matches found: {multiple_matches}")
                self.fo.write(f"CMP_7028BMultipleMatches:CMP_7028B{multiple_matches}")
                print("Please select from the top matches found or be specific with the search.")
        
        
        if len(matches) == 0:
            print("Please provide stations facing blockage on Greater Eastern track. Hint: Can you tell me the contigency plan as there is partial blockage between train station Diss and Norwich")
            sub_function()
            return stations_dictionary
        
        elif len(matches) == 1:
            print(f"One matching station detected: {matches[0]}")
            #self.fo.write(f"CMP_7028BexactMatching:CMP_7028B{matches}")
            print("Please provide another station facing blockage.")
            stations_dictionary["first_station"] =  matches[0]
            sub_function()
            return stations_dictionary

        elif len(matches) == 2:
            print(f"Stations detected: {matches[0], matches[1]}")
            #self.fo.write(f"CMP_7028BexactMatching:CMP_7028B{matches}")
            stations_dictionary["first_station"], stations_dictionary["second_station"] =  matches[0], matches[1]
            return stations_dictionary
        else:
            print("Please give 2 stations only.")
            return False

    def contingency_progress_check(self, user_input):
        # Extract as much information possible and write data progress accordingly
        current_info_dict = self.check_contingency_details()
        if not current_info_dict:
            print("No saved info found. Extracting fresh contigency information..")
            self.contingency_information_extraction(user_input, extraction_type="location")
            self.contingency_information_extraction(user_input, extraction_type="blockage")
        elif current_info_dict['Station1'] in ['', None] and current_info_dict['Station2'] in ['', None] and current_info_dict['BlockageType'] not in ['', None]:
            self.contingency_information_extraction(user_input, extraction_type="location")
        elif current_info_dict['Station1'] in ['', None] and current_info_dict['Station2'] not in ['', None] and current_info_dict['BlockageType'] in ['', None]:
            self.contingency_information_extraction(user_input, extraction_type="location")
            self.contingency_information_extraction(user_input, extraction_type="blockage")
        elif current_info_dict['Station1'] not in ['', None] and current_info_dict['Station2'] in ['', None] and current_info_dict['BlockageType'] in ['', None]:
            self.contingency_information_extraction(user_input, extraction_type="location")
            self.contingency_information_extraction(user_input, extraction_type="blockage")
        elif current_info_dict['Station1'] not in ['', None] and current_info_dict['Station2'] not in ['', None] and current_info_dict['BlockageType'] in ['', None]:
            self.contingency_information_extraction(user_input, extraction_type="blockage")
        elif current_info_dict['Station1'] not in ['', None] and current_info_dict['Station2'] in ['', None] and current_info_dict['BlockageType'] not in ['', None]:
            self.contingency_information_extraction(user_input, extraction_type="location")
        elif current_info_dict['Station1'] in ['', None] and current_info_dict['Station2'] not in ['', None] and current_info_dict['BlockageType'] not in ['', None]:
            self.contingency_information_extraction(user_input, extraction_type="location")
    
    def contingency_information_extraction(self, user_input, extraction_type):
        get_contingency_info = self.check_contingency_details()
        contingency_info = pd.read_csv(self.contingency_details_path)
        user_input = self.lemmatise_and_clean_contingency(user_input)

        if extraction_type.upper() in ["LOCATION"]:
            # Locations / Stations extraction 
            locations_dict = self.contingency_extraction_location(user_input)
    
            if not locations_dict:
                print("Un-able to save location since no station detected from input yet.")
                return False
            elif "first_station" in locations_dict and "second_station" in locations_dict:
                contingency_info.at[0, 'Station1'] = locations_dict["first_station"]
                contingency_info.at[0, 'Station2'] = locations_dict["second_station"]
                contingency_info.to_csv(self.contingency_details_path, index=False)
                return True
            elif "first_station" not in locations_dict:
                contingency_info.at[0, 'Station1'] = locations_dict["first_station"]
                contingency_info.to_csv(self.contingency_details_path, index=False)
                return False
            elif "first_station" in locations_dict and "Station1" not in get_contingency_info.keys():
                contingency_info.at[0, 'Station1'] = locations_dict["first_station"]
                contingency_info.to_csv(self.contingency_details_path, index=False)
                return False
            elif "first_station" in locations_dict and "Station1" in get_contingency_info.keys() and get_contingency_info["Station1"] in ['', None]:
                contingency_info.at[0, 'Station1'] = locations_dict["first_station"]
                contingency_info.to_csv(self.contingency_details_path, index=False)
                return False
            elif "first_station" in locations_dict and "Station2" in get_contingency_info.keys() and get_contingency_info["Station2"] in ['', None] and "Station1" in get_contingency_info.keys() and get_contingency_info["Station1"] not in ['', None]:
                contingency_info.at[0, 'Station2'] = locations_dict["first_station"]
                contingency_info.to_csv(self.contingency_details_path, index=False)
                return False
        
        elif extraction_type.upper() in ["BLOCKAGE"]:
            blockage_type_dict = self.contingency_type_extraction(user_input)
            if blockage_type_dict == {}:
                print("No blockage type found in the input. Please provide either partial or full blockage type.")
                return False
            else:
                if 'blockage_type' in blockage_type_dict:
                    contingency_info.at[0, 'BlockageType'] = blockage_type_dict["blockage_type"]
                    contingency_info.to_csv(self.contingency_details_path, index=False)
                    return True
                else:
                    return False
               
        else:
            print(f"Invalid Extraction Type given: {extraction_type}")
            return False
    
    def contigency_chatbot_response(self, user_input):
        self.contingency_progress_check(user_input)
        final_info_dict = self.check_contingency_details()
        if ('Station1' in final_info_dict.keys() and final_info_dict['Station1'] not in ['', None]) and ('Station2' in final_info_dict.keys() and final_info_dict['Station2'] not in ['', None]) and ('BlockageType' in final_info_dict.keys() and final_info_dict['BlockageType'] not in ['', None]):
                print("Received all required information. Thank you. Proceeding to find contingency plan. ")
                form_stations_key = f"{final_info_dict['Station1'].capitalize()},{final_info_dict['Station2'].capitalize()}"
                blockage_type = final_info_dict['BlockageType'].capitalize()
                print(form_stations_key, blockage_type)
                
                contigency_plan_list = self.matched_contingency_plans(form_stations_key, blockage_type)
                for plans in contigency_plan_list:
                    print(plans)
                    self.fo.write(f'CMP_7028BactionPlanCMP_7028B{plans}')
                
                self.update_contingency_status("no")
                

if __name__ == "__main__":
    obj = ContingencyPlan()
    # print(obj.check_contingency_details())
    # obj.contingency_information_extraction("can you tell me the contingency plan as there is full blockage between train station diss and norwich", extraction_type="location")
    # obj.contingency_information_extraction("can you tell me the contingency plan as there is partial blockage between train station diss and norwich", extraction_type="blockage")
    # obj.contigency_chatbot_response("can you tell me the contingency plan as there is full blockage between train station diss and norwich?")
    # obj.contigency_chatbot_response("can you tell me the contingency")
    # obj.clear_contingency_details()
    # obj.contigency_chatbot_response("can you tell me the contingency plan as there is full blockage between norwich?")
    # obj.contigency_chatbot_response("the station two is norwich")