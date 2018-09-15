import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import os
from selenium.webdriver.common.keys import Keys
import re
import time
import validators 

def get_names(link):
    ## Given a url returns all the hyperlinks on that webpage which are in a list form
    try:
        if validators.url(link):
            page = requests.get(link)
            soup = BeautifulSoup(page.text, 'html.parser')
            names=[]
            for i in soup.find_all('li'): # This is better than using 'a' because we know that we are dealing with a list
                names.append(i.get_text())
            return names
        else:
            raise ValueError 
    except ValueError:
        print ("Oops! That was no valid url. Try again...")

def clean_names(l):
    ## Given a list with bad entries keeps on asking the user for start and end positions that are required to be deleted.
    ## Once the deletion is done returns the list with useful names
    clean_names = l
    condition = 1
    while condition==1:
        start = int(input("Enter the starting index for deletion: "))
        end = int(input("Enter the last index for deletion (not inclusive): "))
        try:
            if start >= 0 and start <= end and end  <= len(l):
                for name in l[start:end]:
                    clean_names.remove(name)
                print(clean_names)    
            else:
                raise ValueError
        except ValueError:
            print("The start end must be less than equal to the end index or the value of start index must be positive whereas the value of end index must be less than length of the list. Try again....")
        condition = int(input("Do you want to continue? (1 for yes and 0 for no): "))
        if condition !=1 and condition !=0:
            print("Enter either 1 or 0. Try again...." )
    return clean_names

def useful_names(clean_names,keywords,keywords_2):
    ## Given a list of clean_names and keywords, the function googles each name from the clean_names list, clicks on the first link, which is usually
    ## the link of the organization. Then it looks for the keywords in the website of the organization. If the keyword is present in the website then
    ## the hyperlink corresponding to that keyword is opened and a second set of keywords_2  is looked for in those pages. A dictionary called dic stores
    ## the name of the organization as key and all the subsidary links as values. In the end the keys of the the dictionary are printed which signify the
    ## useful names
    useful_dic = {}
    for name in clean_names:
        driver = webdriver.Chrome()
        driver.get("http://www.google.com")
        elem = driver.find_element_by_name("q")
        elem.clear()
        elem.send_keys(name)
        elem.send_keys(Keys.RETURN)

        soup = BeautifulSoup(driver.page_source,'html.parser')
        ## This is because we are considering the first link that appears on google search 
        raw_link = str(soup.h3.a) 
        ## This is for constructing the link of the first webpage as witnessed on google search
        raw_link = raw_link[9:]
        x = raw_link.find('"' )
        first_page_link = raw_link[:x]

        driver.get(first_page_link)
        soup = BeautifulSoup(driver.page_source,'html.parser')
        # The following list will contain the organizations whose webpage contains any of the words in keywords list
        org_links = [] 
        for link in soup.find_all('a'):
            m = str(link)
            for word in keywords:
                if word in m:
                    org_links.append(link.get('href'))
        if len(org_links)>0: # Otherwise the webpage does not contain the keyword and so it is useless
            loc = first_page_link[::-1].find('/')
            primary_link = first_page_link[:len(first_page_link)-loc-1]
            useful_dic[name] = primary_link
            for link in org_links:
                temp_link = ""
                if link[0]=='/': # To avoid some corner cases this need to be done 
                    temp_link = primary_link + link
                else:
                    temp_link = primary_link+'/'+link
                ## Just to be sure!
                if validators.url(temp_link):
                    driver.get(temp_link)
                    for word in keywords_2:
                        if word in soup.find_all():
                            print(link)
        #The following is done to maintain a reasonable crawl rate 
        time.sleep(10)
        driver.quit()
    print ("List of Useful Organizations")
    for keys in useful_dic:
        print (keys)
        

           
