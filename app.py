import streamlit as st
import pandas as pd
import base64
import numpy as np
import requests
from bs4 import BeautifulSoup
import pandas as pd 

st.title('Chevening Data Scraper')

st.markdown("""
Scrapes Chevening Site for courses

Field in the Relevant Fields you'd like to know
""")

#Naively created input fields for people to scrape
field1 = st.text_input('Field 1',value ='Cloud')
field2 = st.text_input('Field 2')
field3 = st.text_input('Field 3')
field4 = st.text_input('Field 4')
field5 = st.text_input('Field 5')


fields = [field1,field2,field3,field4,field5]
fields = list(filter(None, fields))


st.write(fields)
print(fields)
# need to build list of cities
# iterate each cities with get requests

#takes input list of a BeautifulSoup sections element
def dataFramer(sections):
    unis = []
    courses = []
    chevenings = []
    links = []
    for section in sections:

        uni = section.find('div', class_='search_dept-head')
        #Try to find unis that is are chevening
        try :
            chevening = uni.find('a', class_='tag tag-tick').text
            uni.find('a', class_='tag tag-tick').text
            chevening = 'True'
            uni = uni.find_all('a')
            uni = uni[1].text

        except:
            chevening = 'False'
            uni = uni.find('a').text 

        #Try to find unis with more than one course

        course_list = section.find_all('li')
        for course in course_list:
            link = course.find('a', class_= 'course-name')
            link = link.get('href') 
            link = 'https://www.postgrad.com' + link
            links.append(link)
            course  = course.find('a', class_= 'course-name').text
            courses.append(course)
            unis.append(uni)
            chevenings.append(chevening)
        #courses.append(course.find('a', class_= 'course-name').text)

    df = pd.DataFrame(list(zip(unis, courses,chevenings,links)),
                columns =['University', 'Courses','Chevening','Links'])
    return df

def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="playerstats.csv">Download CSV File</a>'
    return href

soups = []

# need a way to check pagination container for list length, thats how we know how long it is
for field in fields:
    URL = 'https://www.postgrad.com/search/chevening/?q='+ field + '&uk_location='
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    soups.append(soup)
    print(field)

#use the initial html soup scraped to figure out how many pages each query has
pages_list = []

for soup in soups:
    page_container = soup.find('div', class_='pagination-container')
    pages = page_container.find_all('li')
    #number of of <li> indicates number of pages. -1 because 1 <li> represents the active page
    if len(pages) != 1:
        pages_list.append(len(pages)-1)
    else:
        pages_list.append(1)

field_page_dict = dict(zip(fields, pages_list))
new_soups = []
for field,pages in field_page_dict.items():
    for page in range(1,pages+1):
        URL = 'https://www.postgrad.com/search/chevening/?q='+ field + '&uk_location=&page=' + str(page)
        print(URL)
        page = requests.get(URL)
        new_soup = BeautifulSoup(page.content, 'html.parser')
        new_soups.append(new_soup)


sections_list =[]

for new_soup in new_soups:
    sections = new_soup.find_all('section', class_='search_dept')
    sections_list.append(sections)


#Using dataFramer function on all sections that and all data to be appended to dataframe
dataframe_list = []
for sections in sections_list:
    section_data = dataFramer(sections)
    dataframe_list.append(section_data)

all_data =pd.concat(dataframe_list)

st.dataframe(all_data)

st.markdown(filedownload(all_data), unsafe_allow_html=True)
#all_data.to_csv('chevening_university.csv',index=False)