import csv
import os.path
import matplotlib
import numpy as np
import pandas as pd  # with pandas you cannot use Python 3.9
import matplotlib.pyplot as plt
from urllib import request
from zipfile import ZipFile

''' Q1: What is the min, avg and max number of cars/capita. Show the results in a table (dataframe also ok).
        You are allowed to create supporting functions.'''

''' Q2: What municipality has the largest number of registered cars per capita. Show the 5 largest in a bar chart. 
        You are allowed to create supporting functions/methods '''

''' Q3: Optional statistics and optional graphics. 
        You are allowed to create supporting functions/methods and also change exsisting ones '''


def main():

    # extracts information about Finnish municipalities and vehicles and saves into variables
    municipalities = load_municipalities('finnish_municipalities.csv')
    vehicles = load_vehicles(
        'vehicles.zip', 'http://trafiopendata.97.fi/opendata/TieliikenneAvoinData_5_14.zip', 'TieliikenneAvoinData_5_14.csv')

    # creating dictionaries
    dict_mun = create_dictionary_municipalities(municipalities)
    dict_veih = create_dictionary_vehicles(vehicles)

    # creating dataframe
    dataFrame = create_dataframe(
        dict_numVehicles_in_municipality(dict_veih, dict_mun))

    # calling the functions that you should create
    Q1(dataFrame)
    Q2(dataFrame)
    Q3(dataFrame)


# ----------------------- stat & graph  ------------------------

def Q1(df: pd.DataFrame) -> None:
    ''' This is where you create the program code for Q1. \n
    Takes in dataframe as inparameter, now you have to change it \n\n

    Tip to look up: \n
     "dataframe divide column by another column" \n
     functions min(), mean(), max() \n
     how to create table/dataframe '''
    print("Inside Q1")
    series: pd.Series = df["Number of vehicles"]/df["Population"]
    max_ = series.max()
    min_ = series.min()
    mean_ = series.mean()

    my_dict = {"min": [min_], "max": [max_], "mean": [mean_]}
    my_df = pd.DataFrame.from_dict(my_dict)
    print(my_df)


def Q2(df: pd.DataFrame) -> None:
    ''' This is where you create the program code for Q2 \n
    Takes in dataframe as inparameter, now you have to change it \n\n

    Tip to look up: \n 
    "dataframe divide column by another column" \n
    functions: sort_values(), head(), df.plot.bar \n '''
    df["Result"] = df["Number of vehicles"]/df["Population"]
    df = df.sort_values("Result", ascending=False)
    df = df.head()
    df.plot(x="Municipality name", y="Result", kind="bar")
    plt.show()


def Q3(df: pd.DataFrame):
    ''' This is where you create the program code for Q3 \n
    You probably need to load more data from csv into a dataframe.
    Takes in dataframe as inparameter (for now), now you have to change it the function '''

    # Uppgift: Jämför antalet bilar i Åbo och Helsingfors.

    helsinki: pd.Series = None
    turku: pd.Series = None
    for value in df.iterrows():
        # value is a tuple containing an index and an entry
        entry = value[1]
        if entry["Municipality name"] == "Helsingfors":
            helsinki = entry
        elif entry["Municipality name"] == "Åbo":
            turku = entry
        else:
            if helsinki is not None and turku is not None:
                break

    vehicles_in_turku = turku["Number of vehicles"]
    vehicles_in_helsinki = helsinki["Number of vehicles"]
    as_percentage = (vehicles_in_turku/vehicles_in_helsinki)*100
    as_percentage = int(round(as_percentage, 0))
    if as_percentage == 100:
        print("There is an approximatly equal number of cars in turku and helsinki")
    elif as_percentage < 100:
        print(f"There are {as_percentage}% fewer cars in turku than helsinki")
    else:
        print(f"There are {as_percentage}% more cars in turku than helsinki")


# ---------------------   data structures   ---------------------

def create_dataframe(dict_all_keyValue):
    ''' creates Data Frame from inparameter dict_all_keyValye {City_num: (num_cars, city_name, population)} \n
    df = Municipality number, Municipality name, Population, Number of cars '''

    # creating dataframe
    df = pd.DataFrame.from_dict(
        dict_all_keyValue, orient="index").reset_index()
    df.columns = ['Municipality number', 'Number of vehicles',
                  'Municipality name', 'Population']   # Naming columns
    df = df[['Municipality number', 'Municipality name', 'Population',
             'Number of vehicles']]       # rearranging order of columns

    print(df, '\nThis is your given dataframe\n')

    return df


def dict_numVehicles_in_municipality(vehicles, municipalities):
    ''' Takes in dict 'vehicles' and dict ' municipalities' \nCounts how many vehicles in each municipality \n returns a dict merged from the two inparameters '''
    tuple_municipality_NoVehicles = (
    )                                      # creating a new tuple

    # looping through vehicles dict, sorting municipality number from low to high
    for k, v in vehicles.items():
        # finding how many vehicles in each municipality
        tuple_municipality_NoVehicles += (k, len(list(filter(None, v))))
        # creating tuple of even index (municipality number)
        even_index = (tuple_municipality_NoVehicles[::2])
        # creating tuple of odd index (number of vehicles)
        odd_index = (tuple_municipality_NoVehicles[1::2])

    # zipping tuples together to dictionary
    dict_num_vehicles = dict(zip(even_index, odd_index))
    # merging two dicts
    merged_dicts = (merge_dict(municipalities, dict_num_vehicles))

    return merged_dicts


def merge_dict(dict1, dict2):
    ''' This function merges dict num_vehicle and dict municipality into one for creating a dataframe '''

    sorted_dict = {}                        # creating empty dict

    for key in dict2.keys():                # looping through dict2
        if (key in dict1):                  # if same key as in dict1
            sorted_dict[key] = dict1[key]   # save in sorted_dict
        # if not, just skip (there were some troubles with original csv columns)
        else:
            continue

    keys = dict2.keys()                     # save dict2 keys
    # zip dict2 values and sorted_dict values
    values = zip(dict2.values(), sorted_dict.values())
    values = [tuple([int(v[0]), v[1][0], v[1][1]])
              for v in values]  # make values into tuple

    # zip keys and values together into dict
    dictionary = dict(zip(keys, values))

    return dictionary


def create_dictionary_municipalities(input_data):
    '''creates dictionary for municipalities in Finland. \nK = municipality number, V = Swedish name for municipality and population \ne.g. {5: 'Alajärvi', 9: 'Alavieska', ... , 989: 'Etseri', 992: 'Äänekoski'} '''

    # creates dictionary. Key = minucupality number and values are Swedish name and population
    municipalities_dictionary = input_data.set_index(
        'Kommunnummer').transpose().to_dict(orient='list')
    return municipalities_dictionary


def create_dictionary_vehicles(input_list):
    '''Take in input_list and creates dictionary for vehicles registered in Finland by making index[0] Key and index[1] Value. \nK = municipality number, V = car brand \ne.g. {'091': 'BMW', '893': 'Sprite', '179': 'Ford', ... , '734': 'Omavalmiste', '761': 'Valtteri'}'''

    vehicles_dictionary = {}

    # looping through input_list zipping index 0 to Key and index 1 to Value
    for key, value in zip(input_list[0], input_list[1]):
        vehicles_dictionary.setdefault(key, []).append(
            value)       # appends k,v to vehicles_dictionary

    return dict(vehicles_dictionary)


# ------------------------ file loading ------------------------

def load_municipalities(file):
    '''reads csv, splits to columns at ; and returns it as parsed_data'''

    parsed_data = {}
    print("\nLoading " + file.split('.csv')[0] + " file...")

    # checks if file is in directory or file ir empty
    if (not os.path.isfile(file)) or isEmpty(file):
        # printing error message
        print("File: " + file.split('.csv')[0] + " not found or is empty")
    else:
        # reading and parsing csv file
        parsed_data = pd.read_csv(file, encoding='utf-8', delimiter=';')

    parsed_data = parsed_data.replace(" ", "", regex=True)
    parsed_data['Befolkningsmängd'] = parsed_data["Befolkningsmängd"].astype(
        int)

    return parsed_data


def load_vehicles(zipfolder, url, file_to_extract):
    '''Uses url to download and save zip in zipfolder. File_to_extract extracts given csv from zipfolder. \nCreates and returns two lists from two different columns'''

    # checks if file is in directory or file ir empty
    if (not os.path.isfile(zipfolder)) or isEmpty(zipfolder):

        print("\nDownloading vehicles zip-file....")
        # saves zip from url into directory
        request.urlretrieve(url, zipfolder)

        with ZipFile(zipfolder, 'r') as zipfile:                        # reading zip
            print("Unzipping " + zipfolder.split('.zip')[0] + " file....")
            # extracts csv from zip and saves into directory
            zipfile.extract(file_to_extract)

    # this is just for printing it nicely
    fileformat = file_to_extract.split('.')[-1]
    print("Loading " + file_to_extract.split('.' + fileformat)[0] + " file...")

    with open(file_to_extract, 'r') as f:                               # reading csv
        # two empty lists
        vechicle_list = []
        municipality_list = []
        counter = 0
        # reading each line of f
        reader = f.readlines()

    # looping through everything from csv file
    for item in reader:
        data = item.split(';')
        # appends everything from column 25 to vehicle_list
        vechicle_list.append(data[25])
        # appends everything from column -5 to municipality list
        municipality_list.append(data[-5])

        counter += 1

        # Use this if you don't want to loop through 5,2 million lines of csv:
        # counter == x, where x is as many rows you want from csv. Each row takes a little time. Up to 100 000 quite fast.
        if counter == 1000:
            break

    municipality_list = municipality_list[1:]
    new_city_list = []
    for i in municipality_list:
        if i != '':
            new_city_list.append(int(i))
        else:
            new_city_list.append(int(0))

    # returns the lists from index 1 forward (to cut out headline from list)
    return new_city_list, vechicle_list[1:]


def isEmpty(file):
    '''returns true if file is empty'''

    return os.stat(file).st_size == 0


if __name__ == "__main__":
    main()
