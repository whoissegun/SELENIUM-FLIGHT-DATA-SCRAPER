from backend_scrape import *

correct_spellings = ["January","February","March","April","May","June","July","August","September","October","November","December"]


def main():
    months_days = {
    "January": 31,
    "February": 28,
    "March": 31,
    "April": 30,
    "May": 31,
    "June": 30,
    "July": 31,
    "August": 31,
    "September": 30,
    "October": 31,
    "November": 30,
    "December": 31
    }
    
    while True:
        departure = input("Where are you departing from: ").title().strip()
        destination = input("Where is your destination: ").title().strip()
        dept_month =  input("What month would you like to depart: ").title()
        if dept_month not in correct_spellings:
            print("Please spell month correctly")
            continue
        else:
            ret_month =  input("What month would you like to return: ").title()
            if ret_month not in correct_spellings:
                print("Please spell month correctly")
                continue
            
            break
    
    dept_range_of_days = months_days[dept_month]
    ret_range_of_days = months_days[ret_month]
    while True:
        try:
            dept_day = int(input("What day would you like to depart: "))
            ret_day = int(input("What day would you like to return: "))
            
            if dept_day not in range(1,dept_range_of_days+1):
                print(f"That day does not exist in {dept_month}")
                continue
            if ret_day not in range(1,ret_range_of_days+1):
                print(f"That day does not exist in {dept_month}")
                continue
            
        except ValueError:
            print("Please type a number")
        
        except:
            print("Something went wrong. Please type again")
            continue
        
        break
    res = format_date(dept_month,dept_day,ret_month,ret_day)
    if res == "Incorrect date was inputted":
            return "Didn't work"
    elif res == "Return date cannot be before departure":
            return "Didn't work"
    else:
        dept_date,ret_date = res
        dept_iata_code, dest_iata_code = get_iata(departure,destination)
        url = build_url(dept_iata_code,dest_iata_code,dept_date,ret_date)
        scrape_data(url)


if __name__ == '__main__':
    print(main())