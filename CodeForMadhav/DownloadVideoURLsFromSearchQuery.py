import time
from selenium import webdriver
import random
from csv import writer
import pandas as pd
from pyvirtualdisplay import Display
import pickle
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service


def scroll_to_end(driver):
    start_time = time.time()
    prev_ht=driver.execute_script("return document.documentElement.scrollHeight")
    i = 0
    sleep_time = 2
    while True:
        i+=1
        print(i)
        if i == 50:
            return driver
        if i % 100 == 0:
            print(i, "scrolls executed")
            current_time = time.time()
            if current_time - start_time > (3600 * 5.5):
                print("5 hours elapsed; breaking at i = ", i)
                break
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
        time.sleep(sleep_time + random.uniform(0, 1))
        ht=driver.execute_script("return document.documentElement.scrollHeight")
        if prev_ht == ht:
            time.sleep(2)
            print("Entered same height condition at i = ", i)
            sleep_time += 0
            print("Increased sleep time to ", sleep_time)
            
            if sleep_time >= 20:
                print("Sleep time hit 20s; breaking")
                break
            
        prev_ht = ht
    return driver

def write_to_csv(driver):    
    time_start = time.time()
    out_dict = driver.execute_script("var result = []; " +
    "var all = document.getElementsByTagName('a'); " +
    "for (var i=0, max=all.length; i < max; i++) { " +
    "    if(all[i].getAttribute('id') ==  'video-title')" +                    
    "        result.push([all[i].getAttribute('title'), all[i].getAttribute('href')]); " +
    "} " +
    " return result; ")
    #print(out_dict)
    
    with open('Djokovic.CSV', 'w', newline='', encoding='utf-16', errors ='ignore') as csvfile: #change this line if you want to save the results in the different CSV.
        csv_writer = writer(csvfile)
        csv_writer.writerows(out_dict)
    
    time_end = time.time()
    
    print("written in ", (time_end - time_start) / 60)
    
if __name__ == "__main__": 

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    
    driver.get("https://www.youtube.com/results?search_query=novak+djokovic+deportation") #change this line if you want to use a new search query.

    driver = scroll_to_end(driver)
    write_to_csv(driver)
