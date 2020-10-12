#!/usr/bin/env python3
import os, datetime, requests
import pandas as pd
import matplotlib.pyplot as plt

TODAY = datetime.date.today()
PATH = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/'
MYPATH = './'
FILENAME_CASES = 'time_series_covid19_confirmed_global.csv'
FILENAME_DEATHS = 'time_series_covid19_deaths_global.csv'
FILENAME_RECOVERED = 'time_series_covid19_recovered_global.csv'
FILES = [FILENAME_CASES, FILENAME_DEATHS, FILENAME_RECOVERED]
MYPATH = './'

def update_local_files():
    print('Starting update...')
    for file in FILES:
        r = requests.get(PATH+file)
        if r.status_code != requests.codes.ok:
            print(f"Failed to fetch {file}")
            continue
        with open(MYPATH+file, "wb") as f:
            f.write(r.content)
        print(f'Saved {MYPATH + file}')
    print('All done. Last update made on', str(TODAY))

update_local_files()

cases_global = pd.read_csv(MYPATH + FILENAME_CASES)
deaths_global = pd.read_csv(MYPATH + FILENAME_DEATHS)
recovered_global = pd.read_csv(MYPATH + FILENAME_RECOVERED)

def transform_data(data_list):
    '''
    Преобразуем из каждую из time series в таблицу (индексы - даты, первая колонка - значения), вернем список таблиц
    '''
    result = []
    for data in data_list:
        data.drop(['Province/State', 'Country/Region', 'Lat', 'Long'], axis=1, inplace=True)
        data.columns = pd.to_datetime(data.columns)
        data = data.squeeze()
        result.append(data)
    return result

def process_data(country):
    '''
    Соберем в один dataframe из трех разных файлов данные по заданной стране (country)
    '''
    country_cases = cases_global[cases_global['Country/Region'] == country][:]
    country_deaths = deaths_global[deaths_global['Country/Region'] == country][:]
    country_recovered = recovered_global[recovered_global['Country/Region'] == country][:]
    country_cases, country_deaths, country_recovered = transform_data([country_cases, country_deaths, country_recovered])
    country_cases.name = f'Cases {country}'
    country_deaths.name = f'Deaths {country}'
    country_recovered.name = f'Recovered {country}'
    country_active = country_cases - country_deaths - country_recovered
    country_active.name = f'Active Cases {country}'
    result = pd.concat([country_cases, country_recovered, country_deaths, country_active], axis=1)
    return result

data_rus = process_data('Russia')
DAYS = 200
data_rus[-DAYS:].plot(legend=True, grid=True, title=f"Birds-eye view of COVID19 in Russia for {TODAY}", figsize=(10,5))
plt.savefig(f"{TODAY}_Overall_RU.jpeg") # сохраняем картинку


DAYS = 160 ## задает число дней, которые увидим на графике
data_rus["Active Cases Russia"][-DAYS:].plot(legend=True, grid=True, title=f"Active cases by date as of {TODAY}", figsize=(10,5))
plt.savefig(f"{TODAY}_Active_Cases_RU.jpeg") # сохраняем картинку

"""### Прирост активных случаев (активных случаев сегодня - активных случаев вчера)"""

DAYS = 170 # Число дней, за которые увидим динамику
active_cases_shift_one_day = pd.Series(data_rus["Active Cases Russia"][:-1])
active_cases_shift_one_day.index = data_rus["Active Cases Russia"].index[1:]
abs_growth_active_cases_ru = data_rus["Active Cases Russia"] - active_cases_shift_one_day
abs_growth_active_cases_ru[-DAYS:].plot(grid=True, title=f"Growth of number of active cases by date as of {TODAY}", figsize=(10,5))
plt.savefig(f"{TODAY}_Active_Cases_Growth_By_Day_RU.jpeg") # сохраняем картинку

"""### Прирост числа зарегистрированных случаев (зарегистрированных случаев сегодня минус зарегистрированных случаев вчера)"""

DAYS = 170
newcases_less_one_day = data_rus["Cases Russia"][:-1]
newcases_less_one_day.index = data_rus["Cases Russia"].index[1:]
abs_registered_cases_growth = data_rus["Cases Russia"] - newcases_less_one_day

abs_registered_cases_growth[-DAYS:].plot(legend=True, grid=True, title=f"New registered cases by date as of {TODAY}", figsize=(10,5))
plt.savefig(f"{TODAY}_New_Registered_Cases_RU.jpeg") # сохраняем картинку