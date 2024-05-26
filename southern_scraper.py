import requests
from requests_html import HTMLSession
import json
import re
from datetime import datetime
from pprint import pprint
import os
import re
import sys
from urllib.parse import quote 
import time

def southernCom_scraper(journey_origin , destination ,departure_time, date , adults=1 , children=0  ):
    
#generating headers to prevent from being detected by the website
    headers  = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',
        'accept-Language' : 'en-GB,en;q=0.5',
        'Referer':'https://www.southernrailway.com/',
        'Origin':'https://www.southernrailway.com',
        'DNT' : '1',
        'authority': 'api.southernrailway.com',
        'X-Access-Token':'otrl|a6af56be1691ac2929898c9f68c4b49a0a2d930849770dba976be5d792a',
        'X-Trace-Token': 'booking-engine@/d97b32a0ecf011eea8d3b164b004af4b-13'

    }
    
    journey = [journey_origin,destination]
    loc_type = ['Origin' , 'Destination']
    counter =0
    for loc  in journey:
        
        loc_encode_url=f'https://api.southernrailway.com/config/stations?search={quote(loc,safe="")}&type={loc_type[counter]}'
        city_Info=requests.get(loc_encode_url,headers=headers).text
        parsed_city_Info = json.loads(city_Info)
        
        if counter == 0:
            id_value = str(parsed_city_Info['result'][0]['station'])
            crs_origin = str(parsed_city_Info['links'][id_value]['crs'])
            nlc_origin = str(parsed_city_Info['links'][id_value]['nlc']) 
            counter+=1
            print(crs_origin,nlc_origin , id_value)
        elif counter ==1:
            id_value_dest = str(parsed_city_Info['result'][0]['station'])
            nlc_dest = str(parsed_city_Info['links'][id_value_dest]['nlc']) 
            print(nlc_dest , id_value_dest)
    print(crs_origin , nlc_dest)

    dateObj = datetime.strptime(date,"%d/%m/%Y")
    compatForm = dateObj.strftime("%Y-%m-%d")
    print(compatForm)

    payload = {
        "adults": adults,
        "children": children,
        "destination": nlc_dest,
        "disableGroupSavings": False,
        "doRealTime": False,
        "filterFares": True,
        "isAmending": False,
        "keepAllZoneFares": False,
        "numJourneys": 5,
        "openReturn": False,
        "orderId": None,
        "origin": nlc_origin,
        "outward": {
            "arriveDepart": "Depart",
            "rangeEnd": f"{compatForm}T23:15:00",
            "rangeStart": f"{compatForm}T{departure_time}:00",
            
        },
        "showCheapest": False
    }
    #jsonPayload = json.dumps(payload ,indent=4)
    time.sleep(10)
    r = requests.post('https://api.southernrailway.com/jp/journey-plan',json=payload , headers=headers).text
    Tickets = json.loads(r)['result']['outward']

    intHour = int(departure_time.replace(":",""))
    
    diffFirst = int(Tickets[0]['journey'].split('%7C')[1]) - intHour
    desiredTicketIndex=0
    for i in range(1,len(Tickets)):
       
       diff = int(Tickets[i]['journey'].split('%7C')[1]) - intHour

       if diff < diffFirst:
           desiredTicketIndex = i
       diffFirst = diff
    
    print(desiredTicketIndex ,Tickets[desiredTicketIndex]['journey'].split('%7C')[1] )
    
    ticket_price = {
         
        'price' :str(Tickets[desiredTicketIndex]['fares']["cheapest"]["totalPrice"])[:-2] + "." + str(Tickets[desiredTicketIndex]['fares']["cheapest"]["totalPrice"])[-2:]
    }
    print(ticket_price['price'])

    price = ticket_price['price']
    try:
        pattern = r"\d+\.\d+"
        find_actual_price = re.findall(pattern, price)
        price_dict = {"price": find_actual_price[0], 'url':f'https://ticket.southernrailway.com/journeys-list/{crs_origin}/{nlc_dest}/{compatForm}T{departure_time}//{adults}/{children}/?departNow=no&realTime=no&searchPreferences=%2C%2C%2C&showAdditionalRoutes=no&showCheapest=no&tocSpecific=no'}
    except IndexError:
        # When there is no decimal in the amount
        pattern = r"\d+"
        find_actual_price = re.findall(pattern, price)
        price_dict = {"price": find_actual_price[0], 'url':f'https://ticket.southernrailway.com/journeys-list/{crs_origin}/{nlc_dest}/{compatForm}T{departure_time}//{adults}/{children}/?departNow=no&realTime=no&searchPreferences=%2C%2C%2C&showAdditionalRoutes=no&showCheapest=no&tocSpecific=no'}

    with open("southernRailways.json", "w") as f:
        json.dump(price_dict, f, ensure_ascii=False, indent=4)

fo = open("current_journey_info.csv", "r")
data = fo.readlines()
for line in data[1:]:
    line = line.split(",")
    origin, destination, date, in_time = line[0], line[1], line[2], line[3]
fo.close()

origin = origin
destination = destination
input_date = date
input_time = in_time
    
southernCom_scraper(origin.lower() , destination.lower() , input_time.rstrip(), input_date)