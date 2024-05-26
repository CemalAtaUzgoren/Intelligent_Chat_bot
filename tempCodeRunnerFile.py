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
        
    def test_extraction_delay_time_single_time(self):
        """
        Test case to verify the extraction of delay time from a single time input.

        This test case checks if the `extraction_time` method of the chatbot correctly extracts the time from the given text.
        It provides different input texts with time information and verifies if the extracted time matches the expected output.

        Test inputs:
        - text: "I want to book a ticket for the 10:30am train"
        - expected_output: "10:30"

        - text: "Please find me a train ticket for 3:00pm"
        - expected_output: "15:00"

        - text: "Please find me a train ticket for 14:47pm"
        - expected_output: "14:45"

        Expected output:
        - The extracted time from the first text should be "10:30".
        - The extracted time from the second text should be "15:00".
        - The extracted time from the third text should be "14:45".
        """
        
        text = "I want to book a ticket for the 10:30am train"
        expected_output = "10:30"

        self.assertEqual(self.chatbot.extraction_time(text), expected_output)
        
        
        text = "Please find me a train ticket for 3:00pm"
        expected_output = "15:00"

        self.assertEqual(self.chatbot.extraction_time(text), expected_output)
        
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

    def test_lemmatise(self):
        try:
            text1 = "I am going to the park."
            expected_output1 = "going to park"
            self.assertEqual(self.chatbot.lemmatise_and_clean(text1), expected_output1)
        except Exception as e:
            self.fail(f"{e}")

        try:
            text3 = "I have 5 apples and 3 oranges."
            expected_output3 = "5 apples 3 oranges"
            self.assertEqual(self.chatbot.lemmatise_and_clean(text3), expected_output3)
        
        except Exception as e:
            self.fail(f"{e}")

        try:
            text4 = "I am going from New York to Los Angeles."
            expected_output4 = "going from to"
            self.assertEqual(self.chatbot.lemmatise_and_clean(text4), expected_output4)
        
        except Exception as e:
            self.fail(f"{e}")
            
        try:
            # Test case 2: Text with special characters
            text2 = "Hello, @world! How are you?"
            expected_output2 = "hello world"
            self.assertEqual(self.chatbot.lemmatise_and_clean(text2), expected_output2)
        
        except Exception as e:
            self.fail(f"{e}")