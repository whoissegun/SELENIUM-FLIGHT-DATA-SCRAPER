from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
import time
import datetime

options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
driver = webdriver.Chrome(options=options)
def get_iata(departure,destination):
    url = "https://www.ccra.com/airport-codes/" #i used this url to scrape the airport iata code of the user-specified points of departure and return
    driver.get(url)
    main = WebDriverWait(driver,10)
    main.until(EC.presence_of_element_located((By.XPATH,"//input[@type='search']")))
    search_bar = driver.find_element(By.XPATH,"//input[@type='search']")
    search_bar.clear()
    search_bar.send_keys(departure)
    search_bar.send_keys(Keys.RETURN)
    parent = driver.find_element(By.CLASS_NAME,"row-hover")
    child = parent.find_element(By.CLASS_NAME,"column-3")
    dept_iata_code = child.text

    search_bar.clear()
    search_bar.send_keys(destination)
    search_bar.send_keys(Keys.RETURN)
    parent = driver.find_element(By.CLASS_NAME,"row-hover")
    child = parent.find_element(By.CLASS_NAME,"column-3")
    dest_iata_code = child.text
    return dept_iata_code,dest_iata_code


def format_date(dept_month,dept_day,ret_month,ret_day):
    months = {
    "January": 1,
    "February": 2,
    "March": 3,
    "April": 4,
    "May": 5,
    "June": 6,
    "July": 7,
    "August": 8,
    "September": 9,
    "October": 10,
    "November": 11,
    "December": 12
    }
    # Convert the month and day to integers
    dept_month = months[dept_month]
    dept_day = int(dept_day)
    ret_month = months[ret_month]
    ret_day = int(ret_day)
    # Get the current year
    year = datetime.datetime.now().year

    # Create a datetime object from the year, month, and day
    dept_date = datetime.datetime(year, dept_month, dept_day)
    ret_date = datetime.datetime(year, ret_month, ret_day)

    # Format the date as yyyy-mm-dd
    dept_date = dept_date.strftime("%Y-%m-%d")
    dept_date_obj = datetime.datetime.strptime(dept_date, "%Y-%m-%d")
    ret_date = ret_date.strftime("%Y-%m-%d")
    ret_date_obj = datetime.datetime.strptime(ret_date, "%Y-%m-%d")
    
    now = datetime.datetime.now()
    if dept_date_obj < now or ret_date_obj < now:
        return "Incorrect date was inputted"
    else:
        if ret_date_obj < dept_date_obj: #checking if the user typed a return date that is before the departure date
            
            return "Return date cannot be before departure"
        else:
            return dept_date, ret_date

  
def build_url(dept_iata_code,dest_iata_code,dept_date,ret_date):
    #building a valid kayak url that we will scrape from
    url = f'https://www.ca.kayak.com/flights/{dept_iata_code}-{dest_iata_code}/{dept_date}/{ret_date}' 
    return url
    
def scrape_data(url):
    driver.get(url)
    while True:
        #the Kayak site is dynamic,so I picked two common values of element's class for the program to handle if they ever appeared.
        #not sure how to comment the remaining part of the cpde, because you'd need to study and inspect the structure of the site to understand
        time.sleep(20)
        try:
            advice_col = driver.find_element(By.CLASS_NAME,"col-advice")
            advice = advice_col.find_element(By.CLASS_NAME,"value ").get_attribute("aria-busy")
        except NoSuchElementException:
            driver.refresh()
        
        if advice == 'true':
            driver.refresh()
            continue
        print("Done")
        time.sleep(5)
    
        flights = driver.find_elements(By.CLASS_NAME,"resultInner")
        if flights:
            for flight in flights:
                times = flight.find_elements(By.CLASS_NAME,"time-pair")
                dept_dept_time = times[0].text
                dept_arriv_time = times[1].text
                ret_dept_time = times[2].text
                ret_arriv_time = times[3].text

                no_of_stops = flight.find_elements(By.CLASS_NAME,"stops-text")
                dept_stop = no_of_stops[0].text
                ret_stop = no_of_stops[1].text

                dept_stop_lst = dept_stop.split()
                dept_stop_lst = dept_stop_lst[0]
                ret_stop_lst = ret_stop.split()[0]
                stops_section = flight.find_elements(By.CLASS_NAME,"stops")
                dept_stopovers = stops_section[0].find_elements(By.CLASS_NAME,"js-layover")
                ret_stopovers = stops_section[1].find_elements(By.CLASS_NAME,"js-layover")
                
                dept_flight_journey = ""
                ret_flight_journey = ""
                dept_stopovers_txt = ""
                ret_stopovers_txt = ""
                
                if dept_stop_lst != 'direct':
                    if int(dept_stop_lst) == 1:
                        dept_stopover1_iata = dept_stopovers[0].text 
                        dept_stopover1_ini = dept_stopovers[0].get_attribute('title')
                        dept_stopover1_ini = dept_stopover1_ini.replace(',','')
                        dept_stopover1_ini = dept_stopover1_ini.replace('<b>','at: ')
                        dept_stopover1_ini = dept_stopover1_ini.replace('</b>','.')
                        dept_stopover1 = dept_stopover1_ini.split("at:")[1]
                        dept_stopover1_time = dept_stopover1_ini.split("at:")[0]
                        dept_stopovers_txt = f"{dept_stopover1}({dept_stopover1_iata}) for {dept_stopover1_time}"
                        dept_flight_journey = f"Lagos - {dept_stopover1}({dept_stopover1_iata}) - Ottawa"

                    if int(dept_stop_lst) == 2:
                        dept_stopover1_iata = dept_stopovers[0].text 
                        dept_stopover1_ini = dept_stopovers[0].get_attribute('title')
                        dept_stopover1_ini = dept_stopover1_ini.replace(',','')
                        dept_stopover1_ini = dept_stopover1_ini.replace('<b>','at: ')
                        dept_stopover1_ini = dept_stopover1_ini.replace('</b>','.')
                        dept_stopover1 = dept_stopover1_ini.split("at:")[1]
                        dept_stopover1_time = dept_stopover1_ini.split("at:")[0]
                        
                        dept_stopover2_iata = dept_stopovers[1].text
                        dept_stopover2_ini = dept_stopovers[1].get_attribute("title")
                        dept_stopover2_ini = dept_stopover2_ini.replace(',','')
                        dept_stopover2_ini = dept_stopover2_ini.replace('<b>','at: ')
                        dept_stopover2_ini = dept_stopover2_ini.replace('</b>','.')
                        dept_stopover2 = dept_stopover2_ini.split("at:")[1]
                        dept_stopover2_time = dept_stopover2_ini.split("at:")[0]
                        dept_flight_journey = f"Murtal Muhammed Intl.(LOS) - {dept_stopover1}({dept_stopover1_iata}) - {dept_stopover2}({dept_stopover2_iata}) - Ottawa Airport(XYZ)"
                        dept_stopovers_txt = f"{dept_stopover1}({dept_stopover1_iata}) for {dept_stopover1_time} and {dept_stopover2}({dept_stopover2_iata}) for {dept_stopover2_time}"
                
                if ret_stop_lst != 'direct':
                    if int(ret_stop_lst) == 1:
                        ret_stopover1_iata = ret_stopovers[0].text 
                        ret_stopover1_ini = ret_stopovers[0].get_attribute('title')
                        ret_stopover1_ini = ret_stopover1_ini.replace(',','')
                        ret_stopover1_ini = ret_stopover1_ini.replace('<b>','at: ')
                        ret_stopover1_ini = ret_stopover1_ini.replace('</b>','.')
                        ret_stopover1 = ret_stopover1_ini.split("at:")[1]
                        ret_stopover1_time = ret_stopover1_ini.split("at:")[0]
                        ret_stopovers_txt = f"{ret_stopover1}({ret_stopover1_iata}) for {ret_stopover1_time}"
                        ret_flight_journey = f"Lagos - {ret_stopover1}({ret_stopover1_iata}) - Ottawa"

                    if int(ret_stop_lst) == 2:
                        if int(dept_stop_lst) == 2:
                            ret_stopover1_iata = ret_stopovers[0].text 
                            ret_stopover1_ini = ret_stopovers[0].get_attribute('title')
                            ret_stopover1_ini = ret_stopover1_ini.replace(',','')
                            ret_stopover1_ini = ret_stopover1_ini.replace('<b>','at: ')
                            ret_stopover1_ini = ret_stopover1_ini.replace('</b>','.')
                            ret_stopover1 = ret_stopover1_ini.split("at:")[1]
                            ret_stopover1_time = ret_stopover1_ini.split("at:")[0]
                            
                            ret_stopover2_iata = ret_stopovers[1].text
                            ret_stopover2_ini = ret_stopovers[1].get_attribute("title")
                            ret_stopover2_ini = ret_stopover2_ini.replace(',','')
                            ret_stopover2_ini = ret_stopover2_ini.replace('<b>','at: ')
                            ret_stopover2_ini = ret_stopover2_ini.replace('</b>','.')
                            ret_stopover2 = ret_stopover2_ini.split("at:")[1]
                            ret_stopover2_time = ret_stopover2_ini.split("at:")[0]
                            ret_flight_journey = f"Murtal Muhammed Intl.(LOS) - {ret_stopover1}({ret_stopover1_iata}) - {ret_stopover2}({ret_stopover2_iata}) - Ottawa Airport(XYZ)"
                            ret_stopovers_txt = f"{ret_stopover1}({ret_stopover1_iata}) for {ret_stopover1_time} and {ret_stopover2}({ret_stopover2_iata}) for {ret_stopover2_time}"
                    
                
                flight_duration_section = flight.find_elements(By.CLASS_NAME,"allow-multi-modal-icons")
                dept_flight_dur = flight_duration_section[0].find_element(By.CLASS_NAME,"top").text
                ret_flight_dur = flight_duration_section[1].find_element(By.CLASS_NAME,"top").text

                bags = flight.find_element(By.CLASS_NAME,"Flights-Results-FlightFeeIcons")
                no_carry_on = bags.find_elements(By.CLASS_NAME,"_h5")[0].text
                no_check_in = bags.find_elements(By.CLASS_NAME,"_h5")[1].text

                price = flight.find_element(By.CLASS_NAME,"price-text").text

                airline = flight.find_element(By.CLASS_NAME,"name-only-text").text

                with open("flight_information.txt","a") as f:
                    f.write(f"Airline: {airline} \n")
                    f.write(f"Price in Canadian Dollars: {price} \n")
                    f.write("Departure:\n")
                    f.write(f"{dept_dept_time} - {dept_arriv_time}\n")
                    f.write(f"Number of stopovers when departing: {dept_stop} \n")
                    f.write(f"Departure flight duration: {dept_flight_dur} \n")
                    f.write(f"This is the departure flight journey: {dept_flight_journey} \n")
                    f.write(f"Layovers at: {dept_stopovers_txt} \n")
                    f.write("_________________ \n")
                    f.write("Return: \n")
                    f.write(f"{ret_dept_time} - {ret_arriv_time} \n")
                    f.write(f"Number of stopovers when returning: {ret_stop} \n")
                    f.write(f"Return flight duration {ret_flight_dur} \n")
                    f.write(f"No. of carry-on bags allowed: {no_carry_on} \n")
                    f.write(f"No. of check-in bags allowed: {no_check_in} \n")
                    f.write(f"This is the return flight journey {ret_flight_journey} \n")
                    f.write(f"Layovers at: {ret_stopovers_txt} \n")
                    f.write("\n")
                
                     
        else:
            
            flights = driver.find_elements(By.CLASS_NAME,"nrc6-inner")
            for flight in flights:
                div_times = flight.find_elements(By.CLASS_NAME,"vmXl-mod-variant-large")
                dept_times = div_times[0].find_elements(By.TAG_NAME,"span")
                dept_dept_time = dept_times[0].text
                dept_arriv_time = dept_times[2].text

                ret_times = div_times[1].find_elements(By.TAG_NAME,"span")
                ret_dept_time = ret_times[0].text
                ret_arriv_time = ret_times[2].text

                no_of_stops = flight.find_elements(By.CLASS_NAME,"JWEO-stops-text")
                dept_stop = no_of_stops[0].text
                ret_stop = no_of_stops[1].text
                dept_stop_lst = dept_stop.split()
                dept_stop_lst = dept_stop_lst[0]
                ret_stop_lst = ret_stop.split()
                ret_stop_lst = ret_stop_lst[0]
                
                stops_section = flight.find_elements(By.CLASS_NAME,"JWEO")
                dept_stopovers = stops_section[0].find_element(By.CLASS_NAME,"c_cgF-mod-variant-full-airport")
                ret_stopovers = stops_section[1].find_element(By.CLASS_NAME,"c_cgF-mod-variant-full-airport")

                dept_flight_journey = ""
                ret_flight_journey = ""
                dept_stopovers_txt = ""
                ret_stopovers_txt = ""
                
                if dept_stop_lst != 'direct':
                    
                    if int(dept_stop_lst) == 1:
                        dept_stopover1_iata = dept_stopovers.find_elements(By.TAG_NAME,"span")[1].text 
                        dept_stopover1_ini = dept_stopovers.find_elements(By.TAG_NAME,"span")[1].get_attribute("title")
                        dept_stopover1_ini = dept_stopover1_ini.replace(',','')
                        dept_stopover1_ini = dept_stopover1_ini.replace('<b>','at: ')
                        dept_stopover1_ini = dept_stopover1_ini.replace('</b>','.')
                        dept_stopover1 = dept_stopover1_ini.split("at:")[1]
                        dept_stopover1_time = dept_stopover1_ini.split("at:")[0]
                        dept_stopovers_txt = f"{dept_stopover1}({dept_stopover1_iata}) for {dept_stopover1_time}"

                        dept_flight_journey = f"Lagos - {dept_stopover1} - Ottawa"
                        
                    
                    if int(dept_stop_lst) == 2:
                        dept_stopover1_iata = dept_stopovers.find_elements(By.TAG_NAME,"span")[1].text 
                        dept_stopover1_ini = dept_stopovers.find_elements(By.TAG_NAME,"span")[1].get_attribute("title")
                        dept_stopover1_ini = dept_stopover1_ini.replace(',','')
                        dept_stopover1_ini = dept_stopover1_ini.replace('<b>','at: ')
                        dept_stopover1_ini = dept_stopover1_ini.replace('</b>','.')
                        dept_stopover1 = dept_stopover1_ini.split("at:")[1]
                        dept_stopover1_time = dept_stopover1_ini.split("at:")[0]
                        
                        dept_stopover2_iata = dept_stopovers.find_elements(By.TAG_NAME,"span")[3].text 
                        dept_stopover2_ini = dept_stopovers.find_elements(By.TAG_NAME,"span")[3].get_attribute("title")
                        dept_stopover2_ini = dept_stopover2_ini.replace(',','')
                        dept_stopover2_ini = dept_stopover2_ini.replace('<b>','at: ')
                        dept_stopover2_ini = dept_stopover2_ini.replace('</b>','.')
                        dept_stopover2 = dept_stopover2_ini.split("at:")[1]
                        dept_stopover2_time = dept_stopover2_ini.split("at:")[0]

                        dept_stopovers_txt = f"{dept_stopover1}({dept_stopover1_iata}) for {dept_stopover1_time} and {dept_stopover2}({dept_stopover2_iata}) for {dept_stopover2_time}"

                        dept_flight_journey = f"Lagos Murtala Muhammed Intl.(LOS) - {dept_stopover1} - {dept_stopover2} - Ottawa Intl. Airport (XYZ)"
                if ret_stop_lst != 'direct':
                    if int(ret_stop_lst) == 1:
                        ret_stopover1_iata = ret_stopovers.find_elements(By.TAG_NAME,"span")[1].text 
                        ret_stopover1_ini = ret_stopovers.find_elements(By.TAG_NAME,"span")[1].get_attribute("title")
                        ret_stopover1_ini = ret_stopover1_ini.replace(',','')
                        ret_stopover1_ini = ret_stopover1_ini.replace('<b>','at: ')
                        ret_stopover1_ini = ret_stopover1_ini.replace('</b>','.')
                        ret_stopover1 = ret_stopover1_ini.split("at:")[1]
                        ret_stopover1_time = ret_stopover1_ini.split("at:")[0]
                        ret_flight_journey = f"Lagos - {ret_stopover1} - Ottawa"

                        ret_stopovers_txt = f"{ret_stopover1}({ret_stopover1_iata}) for {ret_stopover1_time}"

                    if int(ret_stop_lst) == 2:
                        ret_stopover1_iata = ret_stopovers.find_elements(By.TAG_NAME,"span")[1].text 
                        ret_stopover1_ini = ret_stopovers.find_elements(By.TAG_NAME,"span")[1].get_attribute("title")
                        ret_stopover1_ini = ret_stopover1_ini.replace(',','')
                        ret_stopover1_ini = ret_stopover1_ini.replace('<b>','at: ')
                        ret_stopover1_ini = ret_stopover1_ini.replace('</b>','.')
                        ret_stopover1 = ret_stopover1_ini.split("at:")[1]
                        ret_stopover1_time = ret_stopover1_ini.split("at:")[0]

                        ret_stopover2_iata = ret_stopovers.find_elements(By.TAG_NAME,"span")[3].text 
                        ret_stopover2_ini = ret_stopovers.find_elements(By.TAG_NAME,"span")[3].get_attribute("title")
                        ret_stopover2_ini = ret_stopover2_ini.replace(',','')
                        ret_stopover2_ini = ret_stopover2_ini.replace('<b>','at: ')
                        ret_stopover2_ini = ret_stopover2_ini.replace('</b>','.')
                        ret_stopover2 = ret_stopover2_ini.split("at:")[1]
                        ret_stopover2_time = ret_stopover2_ini.split("at:")[0]

                        ret_stopovers_txt = f"{ret_stopover1}({ret_stopover1_iata}) for {ret_stopover1_time} and {ret_stopover2}({ret_stopover2_iata}) for {ret_stopover2_time}"

                        ret_flight_journey = f"Lagos Murtala Muhammed Intl.(LOS) - {ret_stopover1} - {ret_stopover2} - Ottawa Intl. Airport (XYZ)"

                flight_duration_section = flight.find_elements(By.CLASS_NAME,"xdW8-mod-full-airport")
                dept_flight_dur = flight_duration_section[0].find_element(By.CLASS_NAME,"vmXl-mod-variant-default").text
                ret_flight_dur = flight_duration_section[1].find_element(By.CLASS_NAME,"vmXl-mod-variant-default").text

                bags = flight.find_elements(By.CLASS_NAME,"ac27-fee-box")

                no_carry_on = bags[0].find_elements(By.CLASS_NAME,"ac27-inner")[1].text
                no_check_in = bags[1].find_elements(By.CLASS_NAME,"ac27-inner")[1].text

                price = flight.find_element(By.CLASS_NAME,"f8F1-price-text").text

                airline = flight.find_element(By.CLASS_NAME,"M_JD-provider-name").text

                with open("flight_information.txt","w") as f:
                    f.write(f"Airline: {airline}\n")
                    f.write(f"Price in Canadian Dollars: {price}\n")
                    f.write("Departure:\n")
                    f.write(f"{dept_dept_time} - {dept_arriv_time}\n")
                    f.write(f"Number of stopovers when departing: {dept_stop}\n")
                    f.write(f"Departure flight duration: {dept_flight_dur}\n")
                    f.write(f"This is the departure flight journey: {dept_flight_journey}\n")
                    f.write(f"Layovers at: {dept_stopovers_txt}\n")
                    f.write("_________________\n")
                    f.write("Return:\n")
                    f.write(f"{ret_dept_time} - {ret_arriv_time}\n")
                    f.write(f"Number of stopovers when returning: {ret_stop}\n")
                    f.write(f"Return flight duration {ret_flight_dur}\n")
                    f.write(f"No. of carry-on bags allowed: {no_carry_on}\n")
                    f.write(f"No. of check-in bags allowed: {no_check_in}\n")
                    f.write(f"This is the return flight journey {ret_flight_journey}\n")
                    f.write(f"Layovers at: {ret_stopovers_txt}\n")
                    f.write("\n\n")
                
            print("Wahala")
        break
  