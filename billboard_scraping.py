#!/usr/bin/env python
# coding: utf-8

# # Web Scraping: Python code

# ## Data Scraping functions
# 
# En esta primera parte del código se definen las funciones que se utilizarán posteriormente para la elaboración del web scraping. 
# 
# En primer lugar, se importarán las librerías necesarias así como se definirá el parámetro año.

# In[1]:


import requests
from bs4 import BeautifulSoup
import lxml
import html5lib
from datetime import datetime, date, timedelta

import pandas as pd
import datetime
import time


# Se debe seleccionar el año del que deseamos obtener información sobre la lista Hot 100 de Billboard. Los datos existen desde 1958 hasta el día actual.

# In[2]:


# Parameter

# Year of interest: you can choose to scrape the data from 1958 until the current year. 
year = 2020


# ### Acceso y parseo de la URL
# La primera función accederá al sitio web en el que deseamos hacer un *scraping* y parsear la URL en cuestión.

# In[3]:


# Function to get and parse the URL we are interested in
def get_parse_url(url):
    result = requests.get(url)
    soup = BeautifulSoup(result.text, 'html.parser')
    return soup


# ### Web Scraping
# Esta función servirá para extraer de la URL los datos que nos interesan: 
# - semana
# - posición
# - desplazamiento de posición
# - cantidad de desplazamiento
# - nombre de la canción
# - nombre del artista
# - posición en la semana anterior
# - mayor posición de la canción
# - número de semanas en la lista
# 
# Además, dentro de esta función todas estas listas que se crearán con los datos se añaden a un dataframe. 

# In[4]:


# Get the info of each song on the Billboard Chart 100
def get_song_info(url):
    soup = get_parse_url(url)

    # Which week are we taking the billboard chart from?
    week = soup.find("div", class_ = "date-selector container").button.next
    # Remove blank spaces at the beginning of the string
    week.strip()

    # Selecting the rank of each song
    rank = [x.next for x in soup.findAll("span", class_ = "chart-element__rank__number")]

    # Scraping the rise or fall of the song.
    # Was the song the week before on the chart? Is so, was it in a higher or lower rank?
    rise = [x.next for x in soup.findAll("span", class_="chart-element__trend")]

    # For loop to scrape the rise and fall song as well as the New ones and the re-entered ones
    for index, elemento in enumerate(rise):
        if elemento not in ('New', 'Re-Enter'):
            rise[index] = elemento.span.next

    # If the song rose last week, how many positions did it move?
    rise_nb = [x.next for x in soup.findAll("span", class_ = "chart-element__information__delta__text text--default")]

    # Scrape the data: name of the song and artist
    name = [x.next for x in soup.findAll("span", class_ = "chart-element__information__song")]
    artist = [x.next for x in soup.findAll("span", class_ = "chart-element__information__artist")]

    # Last week refers too what position was the song in last week
    last_week = [x.next for x in soup.findAll("span", class_ = "chart-element__meta text--center color--secondary text--last")]

    # Peak refers to the highest position on the chart that this song has reached in his history
    peak = [x.next for x in soup.findAll("span", class_ = "chart-element__meta text--center color--secondary text--peak")]

    # Week chart refers to the number os weeks this song has been on the list
    week_chart = [x.next for x in soup.findAll("span", class_ = "chart-element__meta text--center color--secondary text--week")]

    # Create dataframe with the scraped data
    scraped_data = pd.DataFrame({'week': week, 'rank': rank, 'rise': rise, 'rise_nb': rise_nb, 'name': name,
                                      'artist': artist, 'last_week': last_week, 'peak': peak, 'week_chart': week_chart})

    return scraped_data


# ### Función para recoger todos los sábados del año
# Las nuevas listas de Billboard Hot 100 salen cada sábado, por lo que la URL contiene la fecha del sábado correspondiente a la semana.

# In[5]:


# Function to get all saturdays of a year
def all_saturday(year):
    # Get this saturday's date
    today = datetime.date.today()
    idx = (today.weekday() + 1) % 7
    this_saturday = today + datetime.timedelta(7 + idx - 5)

    # January 1st of the given year
    dt = date(year, 1, 1)
    # First saturday of the given year
    dt += timedelta(days=5 - dt.weekday())

    # Create list to store all the dates
    day_list = []
    while dt.year == year and dt <= this_saturday:
        # Transform datetime.date to string type
        day = dt.strftime("%Y-%m-%d")
        # Append date as string to the list
        day_list.append(day)
        # Get next saturday
        dt += timedelta(days=7)
    return day_list


# ## Main code to run
# Debemos primero definir la url a la que más tarde le debemos añadir la fecha del sábado de la semana de interés.

# In[6]:


# URL for last saturday's Billboard Hot 100 Chart
hot_100_chart = "https://www.billboard.com/charts/hot-100"


# Debemos entonces crear una lista vacía en la que se almacenarán las url a las que queremos aplicar el web scraping. 
# 
# A continuación deberemos crear también una lista con todos los sábados del año que hemos escogido al principio como parámetro.
# De esta manera, podremos crear todas las url que necesitamos añadiendo "/" y el elemento de la lista de sábados. 

# In[7]:


# Create empty list to append the urls of the hot 100 Billboard charts of the year of interest
pages_urls = []

# Get all saturdays of the year of interest
saturday_list = all_saturday(year)

# Create the urls for all the urls of the hot 100 Billboard charts of the year of interest
for i in saturday_list:
    # Let's make sure that the url exists
    if requests.get(hot_100_chart).status_code == 200:
        hot_100_chart_loop = hot_100_chart + "/" + i
        pages_urls.append(hot_100_chart_loop)

print(pages_urls[:5])


# Una vez que tenemos la lista con todas la url para realizar el web scraping debemos ejecutar la función que extrae la información que nos interesa de cada sitio web y finalmente guardarla en un dataframe para posteriormente exportarlo como archivo csv.
# 
# En primer lugar, crearemos un dataframe vacío para poder ir añadiendo los datos de cada url.
# En segundo lugar, generaremos un bucle for para que se añadan los datos almacenados en listas en el dataframe yearly_hot_100_chart. 

# In[8]:


# Creation of an empty dataframe
columns = ['week', 'rank', 'rise', 'rise_nb', 'name', 'artist', 'last_week', 'peak', 'week_chart']
yearly_hot_100_chart = pd.DataFrame(columns=columns)


# Creation of the final dataset
for page in pages_urls:
    scraped_data = get_song_info(page)
    time.sleep(5)
    yearly_hot_100_chart = yearly_hot_100_chart.append(pd.DataFrame(data=scraped_data), ignore_index=True)


# Finalmente almacenaremos el dataframe en un archivo csv.

# In[9]:


# Creation of dataset as a csv file
yearly_hot_100_chart.to_csv('yearly_hot_100_chart.csv', sep=';', index=False)

