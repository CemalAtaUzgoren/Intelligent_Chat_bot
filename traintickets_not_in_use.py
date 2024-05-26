import requests
from requests_html import HTMLSession
import json
import re
from datetime import datetime
from pprint import pprint
import os
import re
import sys
#generating headrs to prevent from being detected by the website
def trainTicketCom_scraper(journey_origin , destination ,departure_time, date  , adults=1 , children=0  ):

    headers  = {
        'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'accept-Language' : 'en-GB,en;q=0.5',
        'Referer':'https://www.traintickets.com/?/',
        'DNT' : '1'
    }
# geting the location codes form the api.
    journey = [journey_origin,destination]
    code_dict ={}
    for loc in journey:
        loc_encode_url=f'https://www.traintickets.com/api/v1/autocomplete?query={loc}&limit=20'
        city_Info=requests.get(loc_encode_url,headers=headers).text
        parsed_city_Info = json.loads(city_Info)
        id_value = str(parsed_city_Info['data'][0]['id']) 
        code_dict[loc] = id_value

 # date and time format handling.
    date_obj = datetime.strptime(date, "%d/%m/%Y")
    new_date_str = str(date_obj.strftime("%Y-%m-%d"))
         
#render the dynamic html    
    print(f'https://www.traintickets.com/search/?/results/{code_dict[journey_origin]}/{code_dict[destination]}?departdate={new_date_str}T{departure_time}:00&adults={adults}&children={children}')
    session = HTMLSession()
    r = session.get(f'https://www.traintickets.com/search/?/results/{code_dict[journey_origin]}/{code_dict[destination]}?departdate={new_date_str}T{departure_time}:00&adults={adults}&children={children}',headers=headers)
    r.html.render(sleep=20,keep_page=True,scrolldown=1)
    
    Tickets = r.html.find('.delay-anim')

    #determinig the cheapst ticket in the page
    try:
        Ticket_costs = r.html.find('.cost')
        costs =[]
        prices = re.findall(r'[:£](\d+\.\d+)', Ticket_costs[0].text)
        costs.append(float(prices[0]))
        index_ = costs.index(min(costs))
        original_ticket = (Tickets[index_].text.split('\n'))
        if (Tickets[index_].text.split('\n'))[1] =='FASTEST' or (Tickets[index_].text.split('\n'))[1] =='CHEAPEST':
                original_ticket.pop(1)
    
        #extracting departure time  
        #print(original_ticket)          
        dep_time = original_ticket[1][:5] 
        arrival_time =  original_ticket[1][-5:]  
        duration = original_ticket[1][5:-5]     
        
        #number of changes
        number_of_changes = (original_ticket[3].split(' '))[0]
        
        #ticket type
        ticket_type = r.html.find(' .fare-ticket-name')[index_].text
    
        #stops
        stopsList = []
        tst = Tickets[index_].find('.city')
        for stop in tst:
            stopsList.append(stop.text)
        stopsList.pop(0)
        stopsList.pop(0)  

        details_of_cheapest_ticket = {
            'price' : str(min(costs)),
            'departure time' : dep_time,
            'arrival_time' : arrival_time,
            'duration' : duration,
            'number of changes' : number_of_changes,
            'ticket type' : ticket_type,
            'stops' :stopsList
        }
          
        price = details_of_cheapest_ticket['price']
        try:
            pattern = r"\d+\.\d+"
            find_actual_price = re.findall(pattern, price)
            price_dict = {"price": find_actual_price[0], 'url':f'https://www.traintickets.com/search/?/results/{code_dict[journey_origin]}/{code_dict[destination]}?departdate={new_date_str}T{departure_time}:00&adults={adults}&children={children}'}
        except IndexError:
            # When there is no decimal in the amount
            pattern = r"\d+"
            find_actual_price = re.findall(pattern, price)
            price_dict = {"price": find_actual_price[0], 'url':f'https://www.traintickets.com/search/?/results/{code_dict[journey_origin]}/{code_dict[destination]}?departdate={new_date_str}T{departure_time}:00&adults={adults}&children={children}'}

        with open("traintickets.json", "w") as f:
            json.dump(price_dict, f, ensure_ascii=False, indent=4)
        
        return details_of_cheapest_ticket
    except(IndexError):
         print('Ticket not found')
'''
fo = open("current_journey_info.csv", "r")
data = fo.readlines()
for line in data[1:]:
    line = line.split(",")
    origin, destination, date, time = line[0], line[1], line[2], line[3]
fo.close() 

origin = origin
destination = destination
input_date = date
input_time = time
'''
#pprint(trainTicketCom_scraper(origin.lower(), destination.lower(), input_time.rstrip() , input_date))
pprint(trainTicketCom_scraper('norwich' , 'london liverpool street' , '11:00', '14/05/2024'))

