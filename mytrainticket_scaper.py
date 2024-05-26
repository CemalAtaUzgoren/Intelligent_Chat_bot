import requests
from bs4 import BeautifulSoup
from datetime import date
import json
import re

fo = open("current_journey_info.csv", "r")
data = fo.readlines()
for line in data[1:]:
    line = line.split(",")
    origin, destination, in_date, in_time = line[0], line[1], line[2], line[3]
fo.close()

origin = origin
destination = destination
input_date = in_date
input_time = in_time
input_time = input_time.rstrip()
input_time = input_time.split(":")
hour, min = input_time[0], input_time[1]

def ticket_scrape(departing_city_value, arriving_city_value, return_type='oneway', out_date=input_date, out_arrive_depart='departing', out_hour=hour, out_minute=min, return_date=input_date, return_arrive_depart='departing', return_hour='09', return_minute='00', adult_quantity='1', child_quantity='0', railcard_quantity_one='1', railcard_quantity_two='1', railcard_quantity_three='1', via_avoid='via'):
    global response_url

    payload = {'origin'         : departing_city_value, 
               'destination'    : arriving_city_value, 
               'return_type'    : return_type, 
               'out_date'       : out_date, 
               'out_arrive_depart'  : out_arrive_depart, 
               'out_hour'       : out_hour, 
               'out_minute'     : out_minute, 
               'return_date'    : return_date, 
               'return_arrive_depart': return_arrive_depart, 
               'return_hour'    : return_hour, 
               'return_minute'  : return_minute, 
               'adult_quantity' : adult_quantity, 
               'child_quantity' : child_quantity, 
               'railcard_quantity_one': railcard_quantity_one, 
               'railcard_quantity_two': railcard_quantity_two, 
               'railcard_quantity_three': railcard_quantity_three, 
               'via_avoid'      : via_avoid
               }
    
    # The target URL you provided
    target_url = 'https://bookings.mytrainticket.co.uk/journey_query?' 

    # Send the GET request with your search data
    response = requests.get(target_url, params=payload)

    # Check if the request was successful
    response.raise_for_status()
    
    response_url = response.url

    soup = BeautifulSoup(response.content, 'html.parser')
    response_url = response.url

    data = []
    train_data = {}

    # Find 'out-column' divs
    out_column_divs = soup.find_all('div', class_='out-column')

    console_output = ""

    for out_column_div in out_column_divs:
        table = out_column_div.find('table', class_="table is-striped is-hoverable is-fullwidth")

        if table:  # Check if the table exists
            tbodies = table.find_all('tbody')

            if tbodies:  # Check if at least one tbody exists
                for tbody in tbodies:
                    for row in tbody.find_all('tr'):
                        cells = row.find_all('td')
                        for cell in cells:
                            cell_text = cell.text.strip()
                            console_output = console_output + cell_text + ' '
            else:
                pass
        else:
            pass

    console_output_clean = console_output.replace("✠", "").replace('Overtaken','').strip().split()
    return console_output_clean, departing_city_value, arriving_city_value, out_date
#     return [console_output_clean, departing_city_value, arriving_city_value, out_date]


def list_to_dict(console_output_clean, departing_date='DATE-OUT', departing_city='CITY-OUT', arriving_city='CITY-IN'):    
    train_data = {}
    i = 0
    train_number = 1

    while i < len(console_output_clean):
        train_no = 'Train number ' + str(train_number)

        for line in console_output_clean:

            train_data[train_no] = {
                'departing city': departing_city,
                'departing date': departing_date,
                'departing time': line[i],
                'arriving city': arriving_city,
                'arrival time': line[i + 1],
                'duration': line[i + 2] + ' ' + line[i + 3],
                'number of changes': line[i + 4],
                'standard price': line[i + 6],
                'first class price': line[i + 7] if '£' in line[i + 7] else 'N/A'
            }
            if '£' not in line[i + 7]:
                i -= 1
            i += 8
            train_number += 1

            price_for_json = train_data[train_no]['standard price']
            price_for_json = re.sub(r'£', '', price_for_json)
            price_dict = {"price": price_for_json,
                          "url": response_url}
            
            # Write JSON data to a file
            with open('mytrainticket.json', 'w') as file:
                json.dump(price_dict, file, ensure_ascii=False, indent=4)
            file.close()

            print(f'\n***DEBUG: {train_data}\n')
            if train_number >=2:
                break

    return train_data

if __name__ == '__main__':
    train_data = list_to_dict(ticket_scrape('Bristol','London', out_date='12/06/2024'))
    for key in train_data.keys():
        print(key)
        for _ in train_data[key]:
            print(f"{_}: {train_data[key][_]}")
        print('\n')
