import unittest
from datetime import datetime
from chatbot_conversation import *
from contiegencies import *
import regression_model_functions
from HtmlTestRunner import HTMLTestRunner
import os
import sys
from scrapers_runner import *
import pandas as pd
from datetime import date,timedelta
import time


class TestCreate(unittest.TestCase):
    def setUp(self):
        self.chatbot = ChatbotConversation()

class TestChatbotConversation(TestCreate):       
    def test_convert_date_value(self):
        """
        Test case for the convert_date method of the Chatbot class.
        It checks if the method correctly converts a date string to the expected output format.

        Parameters:
        - self: The instance of the unit test class.

        Returns:
        - None
        """
        
        date_string = '15th October'
        expected_output = ('15/10/2024')
        
        self.assertEqual(self.chatbot.convert_date(date_string), expected_output)
    
    def test_convert_date_type(self):
        """
        Test case to verify the data type of the converted date.

        This test case checks if the data type of the converted date is as expected.
        It converts a given date string and compares the data type of the converted date
        with the expected data type.

        Inputs:
        - date_string: A string representing a date.

        Expected output:
        - expected_output_dtype: The expected data type of the converted date.

        Returns:
        - None

        Raises:
        - AssertionError: If the data type of the converted date is not equal to the expected data type.
        """
        
        date_string = '15th October'
        expected_output_dtype = str

        self.assertEqual(type(self.chatbot.convert_date(date_string)), expected_output_dtype)
        
    def test_extraction_delay_time_single_time1(self):
        
        text = "I want to book a ticket for the 10:30am train"
        expected_output = "10:30"
        self.assertEqual(self.chatbot.extraction_time(text), expected_output)
        
    def test_extraction_delay_time_single_time2(self):   
        text = "Please find me a train ticket for 3:00pm"
        expected_output = "15:00"
        self.assertEqual(self.chatbot.extraction_time(text), expected_output)

    def test_extraction_delay_time_single_time3(self):    
        text = "Please find me a train ticket for 14:47pm"
        expected_output = "14:45"

        self.assertEqual(self.chatbot.extraction_time(text), expected_output)
    
    # def test_extraction_delay_time_multiple_times(self):
    #     text = "I want to book a ticket for the 10:30am train and the 11:45am train"
    #     expected_output = {"current_depart_station_time": "10:30", "origin_depart_station_time": "11:45"}
    #     print(f"******* {self.chatbot.extraction_time(text)} *******")
    #     self.assertEqual(self.chatbot.extraction_time(text), expected_output)

    def test_extraction_delay_time_invalid_time_format(self):
        text = "I want to book a ticket for the 25:00 pm train"
        expected_output = False
        self.assertEqual(self.chatbot.extraction_time(text), expected_output)

    def test_extraction_delay_time_no_time_found(self):
        text = "I want to book a ticket"
        expected_output = None
        self.assertEqual(self.chatbot.extraction_time(text), expected_output)
        
    def test_extract_location_single(self):
        text = "Find me the cheapest train ticket to Exeter Central"
        expected_result = {"arrival_station": "Exeter Central".upper()}
        result = self.chatbot.extract_location(text)
    
        self.assertEqual(result, expected_result)

    def test_extract_location_multiple_matches(self):
        text = "Find me the cheapest train ticket from London Liverpool Street station to Norwich"
        expected_result = {"depart_station": "London Liverpool Street".upper(), 
                           "arrival_station": "Norwich".upper()}
        result = self.chatbot.extract_location(text)
    
        self.assertEqual(result, expected_result)
    
    
    def test_lemmatise_1(self):
        text1 = "I am going to the park."
        expected_output1 = "going to park"
        self.assertEqual(self.chatbot.lemmatise_and_clean(text1), expected_output1)

    def test_lemmatise_2(self):
        text3 = "I have 5 apples and 3 oranges."
        expected_output3 = "5 apples 3 oranges"
        self.assertEqual(self.chatbot.lemmatise_and_clean(text3), expected_output3)
    
    def test_lemmatise_3(self):
        text4 = "I am going from New York to Los Angeles."
        expected_output4 = "going from new york to los angeles"
        self.assertEqual(self.chatbot.lemmatise_and_clean(text4), expected_output4)

    def test_lemmatise_4(self):
         text2 = "Hello, @world! How are you?"
         expected_output2 = "hello world"
         self.assertTrue(self.chatbot.lemmatise_and_clean(text2) == expected_output2,"First value and second value are not equal !")
    
    def test_predictions(self):
        """
        Test the predictions made by the regression model.

        This method creates a test input data frame and calls the `make_delay_prediction` function
        from the `regression_model_functions` module to make a delay prediction. It then checks if
        the prediction falls within 5 minutes before and after the true time.
        Returns:
            None
        """
        _input_data = {"tpl" : 25,
                      "depart_from_LDN" : ["17:49"],
                      "depart_from_current_station" : ["19:02"]}
        
        input_data = pd.DataFrame(_input_data)
        # expected_output = "19:43"
        
        lower_band = regression_model_functions.convert_string_to_seconds("19:38")
        upper_band = regression_model_functions.convert_string_to_seconds("19:48")
        predictions = regression_model_functions.make_delay_prediction(input=input_data)
                
        self.assertTrue(((lower_band <= predictions[0]) & (predictions[0] <= upper_band)).all(), f"{predictions} not in range {lower_band}-{upper_band}")
        predictions = regression_model_functions.make_delay_prediction(input=input_data, output_type= str)
        self.assertTrue(isinstance(predictions, str))

    def test_predictions(self):
        _input_data = {"tpl" : 25,
                      "depart_from_LDN" : ["17:49"],
                      "depart_from_current_station" : ["19:02"]}
        
        input_data = pd.DataFrame(_input_data)
        # expected_output = "19:43"
        
        predictions = regression_model_functions.make_delay_prediction(input=input_data, output_type= str)
        self.assertTrue(isinstance(predictions, str))
    
    def test_predictions_2(self):
        _input_data = {"tpl" : 25,
                      "depart_from_LDN" : ["17:49"],
                      "depart_from_current_station" : ["19:02"]}
        
        input_data = pd.DataFrame(_input_data)
        # expected_output = "19:43"
        
        predictions = regression_model_functions.make_delay_prediction(input=input_data)
        self.assertTrue(isinstance(predictions, pd.DataFrame))

class TestScrapers(TestCreate):

    def  test_LNER_scraper(self):
        with open(os.getcwd() + '/LNER.json', 'r') as file:
            try:
                data = json.load(file)
                # Check if the JSON object is empty
                self.assertTrue(data)
            except:
                self.assertTrue(False,'Scraper could not find any ticket.')

    def test_greateranglia_scraper(self):
        with open(os.getcwd() + '/greateranglia.json', 'r') as file:
            try:
                data = json.load(file)
                # Check if the JSON object is empty
                self.assertTrue(data)
            except:
                self.assertTrue(False,'Scraper could not find any ticket.')
    
    def test_myTrainTicket_scraper(self):
        with open(os.getcwd() + '/mytrainticket.json', 'r') as file:
            try:
                data = json.load(file)
                # Check if the JSON object is empty
                self.assertTrue(data)
            except:
                self.assertTrue(False,'Scraper could not find any ticket.')

    def test_nationalrail_scraper(self):
        with open(os.getcwd() + '/nationalrail.json', 'r') as file:
            try:
                data = json.load(file)
                # Check if the JSON object is empty
                self.assertTrue(data)
            except:
                self.assertTrue(False,'Scraper could not find any ticket.')

    def test_southernRailways_scraper(self):
        with open(os.getcwd() + '/southernRailways.json', 'r') as file:
            try:
                data = json.load(file)
                # Check if the JSON object is empty
                self.assertTrue(data)
            except:
                self.assertTrue(False,'Scraper could not find any ticket.')

    def test_trainpal_scraper(self):
        with open(os.getcwd() + '/trainpal.json', 'r') as file:
            try:
                data = json.load(file)
                # Check if the JSON object is empty
                self.assertTrue(data)
            except:
                self.assertTrue(False,'Scraper could not find any ticket.')
    
    def test_traintickets_scraper(self):
        with open(os.getcwd() + '/traintickets.json', 'r') as file:
            try:
                data = json.load(file)
                # Check if the JSON object is empty
                self.assertTrue(data)
            except:
                self.assertTrue(False,'Scraper could not find any ticket.')

class TestContingencies(TestCreate):
     def test_contingencyPlans(self):
         input_sent = "can you tell me the contingency plan as there is full blockage between train station diss and norwich?"
         objCont = ContingencyPlan()
         outcome = objCont.contigency_chatbot_response(input_sent)
         self.assertTrue(outcome!=False)
        

# TODO: add test for part C
# TODO: add scraper test Part A (done)

if __name__ == '__main__':
    #Creating temporary date for scraper testing
    journey_info = pd.read_csv(os.getcwd() + '/current_journey_info.csv')

    journey_info.at[0, 'date'] = (date.today()+timedelta(days=1)).strftime("%d/%m/%Y")
    journey_info.at[0, 'time'] = '10:30'
    journey_info.at[0, 'origin'] = 'NORWICH'
    journey_info.at[0, 'destination'] = 'LONDON LIVERPOOL STREET'
    journey_info.to_csv(os.getcwd() + '/current_journey_info.csv', index=False) 

    time.sleep(5)

    #run the scrapers
    runnerOBJ = ScrapersRunner()
    runnerOBJ.main()

    #run the test cases.
    loader = unittest.TestLoader()
    suite = (loader.loadTestsFromTestCase(TestChatbotConversation))
    suite2 = (loader.loadTestsFromTestCase(TestScrapers))
    suite3 = (loader.loadTestsFromTestCase(TestContingencies))
    
    mergedTests = unittest.TestSuite([suite,suite2,suite3])
    if sys.platform.startswith('win'):
        if os.path.isdir(os.getcwd() + "/Tests"):
            dir_name =os.getcwd() +  "/Tests"
        else:
            dir_name =os.getcwd() +  "../Tests"
    elif sys.platform.startswith('darwin'):
        if os.path.isdir("../../chatbot/Tests"):
            dir_name = "../../chatbot/Tests"
        else:
            dir_name = "../chatbot/Tests"

    with open(f'{dir_name}/test_report.html', 'w') as f:
     
        runner = HTMLTestRunner(stream=f, combine_reports=True, open_in_browser=True, output=dir_name)
        result = runner.run(mergedTests)

    #delete the temporary date from the '/current_journey_info.csv' file. 
    fo = open(os.getcwd() + '/current_journey_info.csv', "w")
    fo.write("")
    fo.write("origin,destination,date,time")
    fo.close()

    #create contingency data
    fo = open(os.getcwd() + '/contingencies_details.csv', "w")
    fo.write("")
    fo.write("Station1,Station2,BlockageType")
    fo.close()

    #crear scraper data
    scraper_files = ["greateranglia.json", "LNER.json", "nationalrail.json", "trainpal.json", 
                               "southernRailways.json" , "mytrainticket.json"]
    
    for file in scraper_files:
            fo = open(os.getcwd() + "/" + file, "w")
            fo.write("")
            fo.close()
   