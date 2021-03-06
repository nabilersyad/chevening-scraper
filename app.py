import streamlit as st
import pandas as pd
import base64
import numpy as np
import requests
from bs4 import BeautifulSoup
import pandas as pd 
import plotly.graph_objects as go


st.title('Chevening Find A Course List Compiler 2021')

st.markdown("""
[![Star](https://img.shields.io/github/stars/nabilersyad/chevening-scraper?style=social)](https://github.com/nabilersyad/chevening-scraper)
&nbsp[![Follow](https://img.shields.io/twitter/follow/NabilErsyad?style=social)](https://twitter.com/NabilErsyad)
&nbsp[![Buy me a coffee](https://img.shields.io/badge/Buy%20me%20a%20coffee--yellow.svg?logo=buy-me-a-coffee&logoColor=orange&style=social)](https://www.buymeacoffee.com/nabilersyad)


Scrapes Chevening Site for courses and universities on the Chevening website @ https://www.chevening.org/scholarships/find-a-course/ to get a list of courses and universities that may interest you

Just enter the fields or courses that you're want to look for and click the button below. The more you enter the longer it'll take!

""")

#Naively created input fields for people to scrape
field1 = st.text_input('Field 1',value ='Data Science')
field2 = st.text_input('Field 2', value='Biology')
field3 = st.text_input('Field 3')
field4 = st.text_input('Field 4')
field5 = st.text_input('Field 5')


fields = [field1,field2,field3,field4,field5]
fields = list(filter(None, fields))


st.write("You've entered the following field(s): "+ str(fields))
# need to build list of cities
# iterate each cities with get requests

#takes input list of a BeautifulSoup sections element
def dataFramer(sections):
    unis = []
    courses = []
    chevenings = []
    links = []
    fields = []
    field = sections[1]
    for section in sections[0]:
        uni = section.find('div', class_='search_dept-head')
        #Try to find unis that is are chevening
        try :
            chevening = uni.find('a', class_='tag tag-tick').text
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
            fields.append(field)
        #courses.append(course.find('a', class_= 'course-name').text)

    df = pd.DataFrame(list(zip(unis, courses,fields,chevenings,links)),
                columns =['University', 'Courses','Field','Chevening Partner','Links'])
    return df

def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="university-list.csv">Download CSV File</a>'
    return href

if st.button('Confirm Selection'):
    soups = []

    # need a way to check pagination container for list length, thats how we know how long it is
    for field in fields:
        URL = 'https://www.postgrad.com/search/chevening/?q='+ field + '&uk_location='
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, 'html.parser')
        soup = (soup, field)
        soups.append(soup)

    #use the initial html soup scraped to figure out how many pages each query has
    pages_list = []

    for soup,field in soups:
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
            page = requests.get(URL)
            new_soup = BeautifulSoup(page.content, 'html.parser')
            temp_tuple = (new_soup , field)
            new_soups.append(temp_tuple)


    sections_list =[]
    for new_soup , field in new_soups:
        sections = new_soup.find_all('section', class_='search_dept')
        temp_tup = (sections,field)
        sections_list.append(temp_tup)


    #Using dataFramer function on all sections that and all data to be appended to dataframe
    dataframe_list = []
    for sections in sections_list:
        section_data = dataFramer(sections)
        dataframe_list.append(section_data)

    all_data =pd.concat(dataframe_list)

    m1, m2, m3, m4= st.columns((1,1,1,1))
    
    courses_total =   len(all_data)
    universities_total = len(all_data['University'].unique())   
    
    m1.write('')
    m2.metric(label ='Total Available Courses',value = courses_total)
    m3.metric(label ='Total Universities',value = universities_total)
    m4.write('')


    # fig = go.Figure(data=[go.Table(
    #     header=dict(values=list(all_data.columns),
    #                 fill_color='paleturquoise',
    #                 align='left'),
    #     cells=dict(values=[all_data['University'], all_data['Courses'], all_data['Field'], all_data['Chevening Partner'],all_data['Links']],
    #             fill_color='lavender',
    #             align='left'))
    # ])

    # st.plotly_chart(fig)
    st.dataframe(all_data)

    st.write('Click the button below to download this list')
    st.markdown(filedownload(all_data), unsafe_allow_html=True)


