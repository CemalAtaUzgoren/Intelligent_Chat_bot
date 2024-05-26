import requests
import json
import re
from datetime import datetime
from pprint import pprint
from urllib.parse import quote
import os
import sys
def LNERCom_scraper(journey_origin , destination ,departure_time, date , adults=1 , children=0  ):
    
#generating headers to prevent from being detected by the website
    headers  = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',
        'accept-Language' : 'en-GB,en;q=0.5',
        'Referer':'https://www.lner.co.uk/',
        'DNT' : '1',
        'authority': 'www.lner.co.uk'
    }
    
    journey = [journey_origin,destination]
    code_dict ={}
    Crs_dict ={}
    for loc in journey:
        loc_encode_url=f'https://www.lner.co.uk/api/cbereference/stationsAndMatchingPopularRoutes?term={loc}&includeGroups=true&includeLondonTerminals=false&eastCoastServicedStationsOnly=false'
        city_Info=requests.get(loc_encode_url,headers=headers).text
        parsed_city_Info = json.loads(city_Info)
        id_value = str(parsed_city_Info['data'][0]['Stations'][0]['NLC'])
        CRS_code = str(parsed_city_Info['data'][0]['Stations'][0]['CrsCode'])
        code_dict[loc] = id_value
        Crs_dict[loc] = CRS_code
    print(code_dict , Crs_dict)
    
    # date and time format handling.
    date_obj = datetime.strptime(date, "%d/%m/%Y")
    new_date_str = date_obj.strftime("%Y-%m-%d")
    new_date_str = str(date_obj.strftime("%d+%B%%2C+%Y"))
    
    date_array = date.split('/') 
    print (date_array)

    #time format handling
    new_time_str = departure_time.replace(":", "%3A")
    new_time_hour = new_time_str[:2]
    new_time_min = new_time_str[-2:] 

    print(new_time_hour  ,  new_time_min , new_date_str) 

    url = f"https://www.lner.co.uk/api/CbeService/GetFares?od={journey_origin}&onlc={code_dict[journey_origin]}&ocrs={Crs_dict[journey_origin]}&dd={destination}&dnlc={code_dict[destination]}&dcrs={Crs_dict[destination]}&JourneyType=singleJourney&DepartureDate={new_date_str}&ocffp=&ocffd=&outda=y&ReturnDate=&icffp=&icffd=&retda=y&DepartureTime={new_time_str}&ReturnTime=&outd={date_obj.day}&outm={date_obj.month}&outy={date_obj.year}&retd=&retm=&rety={date_obj.year}&outh={new_time_str[:2]}&outmi={new_time_str[-2:]}&reth=&retmi=&nad={adults}&nch={children}&totalPassengers={adults+children}&totalPassengersMinimum={adults+children}&RailCardCode=&rc=&rcn=&tto=0&pc=&cc=&tsc=0&Clearpromo=0&refC=&inToc=&orderId=&brandName=&shouldHideJourneyPicker=False&loggedin=false&referringpageurl=%2Fbuy-tickets%2Fbooking-engine%2F%3Fod%3D{journey_origin}%26onlc%3D{code_dict[journey_origin]}%26ocrs%3D{Crs_dict[journey_origin]}%26dd%3D{destination}%26dnlc%3D{code_dict[destination]}%26dcrs%3D{Crs_dict[destination]}%26JourneyType%3DsingleJourney%26DepartureDate%3D{quote(date, safe='')}%26ocffp%3D%26ocffd%3D%26outda%3Dy%26ReturnDate%3D%26icffp%3D%26icffd%3D%26retda%3Dy%26DepartureTime%3D{quote(departure_time, safe='')}%26ReturnTime%3D%26outd%3D{date_obj.day}%26outm%3D{date_obj.month}%26outy%3D{date_obj.year}%26retd%3D%26retm%3D%26rety%3D{date_obj.year}%26outh%3D{new_time_str[:2]}%26outmi%3D{new_time_str[-2:]}%26reth%3D%26retmi%3D%26nad%3D{adults}%26nch%3D{children}%26totalPassengers%3D{adults+children}%26totalPassengersMinimum%3D{adults+children}%26RailCardCode%3D%26rc%3D%26rcn%3D%26tto%3D0%26pc%3D%26cc%3D%26tsc%3D0%26Clearpromo%3D0%26refC%3D%26inToc%3D%26orderId%3D%26brandName%3D%26shouldHideJourneyPicker%3DFalse%26loggedin%3Dfalse%26shoppingCartId%3Dd0367278-bdb4-41b7-87e3-550747aa3857&shoppingCartId=d0367278-bdb4-41b7-87e3-550747aa3857"

    r = requests.get( url,headers=headers).text
    parsed_page_info = (json.loads(r))
    cheapest = parsed_page_info['FareQuickFinder']['Cheapest']

    details_of_cheapest_ticket = {
            'price' : cheapest['OutboundCost'].replace('£',""),
            'departure time': cheapest['OutwardJourneyDepartureTime'] ,
            'arrival_time' : cheapest['OutwardJourneyArrivalTime'] ,
            'duration' : cheapest['OutboundDuration'],
            'number of changes' : 'not present',
            'ticket type' : 'not present',
            'stops' :'notpresent'
        }
    
    
    price = details_of_cheapest_ticket['price']
    try:
        pattern = r"\d+\.\d+"
        find_actual_price = re.findall(pattern, price)
        price_dict = {"price": find_actual_price[0], "url":f"https://www.lner.co.uk/buy-tickets/booking-engine/?od={journey_origin}&onlc={code_dict[journey_origin]}&ocrs={Crs_dict[journey_origin]}&dd={destination}&dnlc={code_dict[destination]}&dcrs={Crs_dict[destination]}&JourneyType=singleJourney&DepartureDate={new_date_str}&ocffp=&ocffd=&outda=y&ReturnDate=&icffp=&icffd=&retda=y&DepartureTime={new_time_str}&ReturnTime=&outd={date_obj.day}&outm={date_obj.month}&outy={date_array[2]}&retd=&retm=&rety={date_array[2]}&outh={new_time_str[:2]}&outmi={new_time_str[-2:]}&reth=&retmi=&nad={adults}&nch={children}&totalPassengers={adults+children}&totalPassengersMinimum={adults+children}&RailCardCode=&rc=&rcn=&tto=0&pc=&cc=&tsc=0&Clearpromo=0&refC=&inToc=&orderId=&brandName=&shouldHideJourneyPicker=False"}
        print(price_dict['url'])
    except IndexError:
        # When there is no decimal in the amount
        pattern = r"\d+"
        find_actual_price = re.findall(pattern, price)
        price_dict = {"price": find_actual_price[0], "url":f"https://www.lner.co.uk/api/CbeService/GetFares?od={journey_origin}&onlc={code_dict[journey_origin]}&ocrs={Crs_dict[journey_origin]}&dd={destination}&dnlc={code_dict[destination]}&dcrs={Crs_dict[destination]}&JourneyType=singleJourney&DepartureDate={new_date_str}&ocffp=&ocffd=&outda=y&ReturnDate=&icffp=&icffd=&retda=y&DepartureTime={new_time_str}&ReturnTime=&outd={date_obj.day}&outm={date_obj.month}&outy={date_obj.year}&retd=&retm=&rety={date_obj.year}&outh={new_time_str[:2]}&outmi={new_time_str[-2:]}&reth=&retmi=&nad={adults}&nch={children}&totalPassengers={adults+children}&totalPassengersMinimum={adults+children}&RailCardCode=&rc=&rcn=&tto=0&pc=&cc=&tsc=0&Clearpromo=0&refC=&inToc=&orderId=&brandName=&shouldHideJourneyPicker=False"}

    with open("LNER.json", "w") as f:
        json.dump(price_dict, f, ensure_ascii=False, indent=4)
        
    return details_of_cheapest_ticket


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

pprint(LNERCom_scraper(origin.lower() , destination.lower() , input_time.rstrip(), input_date))
#pprint(LNERCom_scraper('norwich' , 'london liverpool street' , '11:00', '14/05/2024'))





