## Formula 1 data pit stop - 1950 to 2023

### Project idea

My son is a big F1 fan and I thought I might try to build on my recent Geospatial and Streamlit learning to create a simple app which allows him to choose a track, see it on a map, and provide some selective stats with visualizations - podium finishes, fastest lap, number of crashes etc. 

The first step as always was to source my data.

### Non-spatial data source

A quick internet search directed me to [Chris Newell](https://github.com/jcnewell) who administers an [f1-api](http://ergast.com/mrd/db/). 

The database can also be downloaded as a set of CSV files which can be imported into spreadsheets and other types of software:

[f1db_csv.zip](http://ergast.com/downloads/f1db_csv.zip)

### Data structure and schema

Each CSV file contains a single database table. The text encoding is UTF-8 and the first line of each file contains the column headers. The tables are described in the [User Guide](http://ergast.com/docs/f1db_user_guide.txt) also shown below :


```python
+----------------------------+
| Ergast Database User Guide |
+----------------------------+
| Version: 1.0               |
| Date: 31 January 2021      |
| Author: Chris Newell       |
+----------------------------+

+----------------------+          +------------------------------------------------------------------+
| List of Tables       |          | General Notes                                                    |
+----------------------+          +------------------------------------------------------------------|
| circuits             |          | Dates, times and durations are in ISO 8601 format                |
| constructorResults   |          | Dates and times are UTC                                          |
| constructorStandings |          | Strings use UTF-8 encoding                                       |
| constructors         |          | Primary keys are for internal use only                           |
| driverStandings      |          | Fields ending with "Ref" are unique identifiers for external use |
| drivers              |          | A grid position of '0' is used for starting from the pitlane     |
| lapTimes             |          | Labels used in the positionText fields:                          |
| pitStops             |          |   "D" - disqualified                                             |
| qualifying           |          |   "E" - excluded                                                 |
| races                |          |   "F" - failed to qualify                                        |
| results              |          |   "N" - not classified                                           |
| seasons              |          |   "R" - retired                                                  |
| status               |          |   "W" - withdrew                                                 |
+----------------------+          +------------------------------------------------------------------+

circuits table
+------------+--------------+------+-----+---------+----------------+---------------------------+
| Field      | Type         | Null | Key | Default | Extra          | Description               |
+------------+--------------+------+-----+---------+----------------+---------------------------+
| circuitId  | int(11)      | NO   | PRI | NULL    | auto_increment | Primary key               |
| circuitRef | varchar(255) | NO   |     |         |                | Unique circuit identifier |
| name       | varchar(255) | NO   |     |         |                | Circuit name              |
| location   | varchar(255) | YES  |     | NULL    |                | Location name             |
| country    | varchar(255) | YES  |     | NULL    |                | Country name              |
| lat        | float        | YES  |     | NULL    |                | Latitude                  |
| lng        | float        | YES  |     | NULL    |                | Longitude                 |
| alt        | int(11)      | YES  |     | NULL    |                | Altitude (metres)         |
| url        | varchar(255) | NO   | UNI |         |                | Circuit Wikipedia page    |
+------------+--------------+------+-----+---------+----------------+---------------------------+

constructor_results table
+----------------------+--------------+------+-----+---------+----------------+----------------------------------------+
| Field                | Type         | Null | Key | Default | Extra          | Description                            |
+----------------------+--------------+------+-----+---------+----------------+----------------------------------------+
| constructorResultsId | int(11)      | NO   | PRI | NULL    | auto_increment | Primary key                            |
| raceId               | int(11)      | NO   |     | 0       |                | Foreign key link to races table        |
| constructorId        | int(11)      | NO   |     | 0       |                | Foreign key link to constructors table |
| points               | float        | YES  |     | NULL    |                | Constructor points for race            |
| status               | varchar(255) | YES  |     | NULL    |                | "D" for disqualified (or null)         |
+----------------------+--------------+------+-----+---------+----------------+----------------------------------------+

constructor_standings table
+------------------------+--------------+------+-----+---------+----------------+------------------------------------------+
| Field                  | Type         | Null | Key | Default | Extra          | Description                              |
+------------------------+--------------+------+-----+---------+----------------+------------------------------------------+
| constructorStandingsId | int(11)      | NO   | PRI | NULL    | auto_increment | Primary key                              |
| raceId                 | int(11)      | NO   |     | 0       |                | Foreign key link to races table          |
| constructorId          | int(11)      | NO   |     | 0       |                | Foreign key link to constructors table   |
| points                 | float        | NO   |     | 0       |                | Constructor points for season            |
| position               | int(11)      | YES  |     | NULL    |                | Constructor standings position (integer) |
| positionText           | varchar(255) | YES  |     | NULL    |                | Constructor standings position (string)  |
| wins                   | int(11)      | NO   |     | 0       |                | Season win count                         |
+------------------------+--------------+------+-----+---------+----------------+------------------------------------------+

constructors table
+----------------+--------------+------+-----+---------+----------------+-------------------------------+
| Field          | Type         | Null | Key | Default | Extra          | Description                   |
+----------------+--------------+------+-----+---------+----------------+-------------------------------+
| constructorId  | int(11)      | NO   | PRI | NULL    | auto_increment | Primary key                   |
| constructorRef | varchar(255) | NO   |     |         |                | Unique constructor identifier |
| name           | varchar(255) | NO   | UNI |         |                | Constructor name              |
| nationality    | varchar(255) | YES  |     | NULL    |                | Constructor nationality       |
| url            | varchar(255) | NO   |     |         |                | Constructor Wikipedia page    |
+----------------+--------------+------+-----+---------+----------------+-------------------------------+

driver_standings table
+-------------------+--------------+------+-----+---------+----------------+-------------------------------------+
| Field             | Type         | Null | Key | Default | Extra          | Description                         |
+-------------------+--------------+------+-----+---------+----------------+-------------------------------------+
| driverStandingsId | int(11)      | NO   | PRI | NULL    | auto_increment | Primary key                         |
| raceId            | int(11)      | NO   |     | 0       |                | Foreign key link to races table     |
| driverId          | int(11)      | NO   |     | 0       |                | Foreign key link to drivers table   |
| points            | float        | NO   |     | 0       |                | Driver points for season            |
| position          | int(11)      | YES  |     | NULL    |                | Driver standings position (integer) |
| positionText      | varchar(255) | YES  |     | NULL    |                | Driver standings position (string)  |
| wins              | int(11)      | NO   |     | 0       |                | Season win count                    |
+-------------------+--------------+------+-----+---------+----------------+-------------------------------------+

drivers table
+-------------+--------------+------+-----+---------+----------------+--------------------------+
| Field       | Type         | Null | Key | Default | Extra          | Description              |
+-------------+--------------+------+-----+---------+----------------+--------------------------+
| driverId    | int(11)      | NO   | PRI | NULL    | auto_increment | Primary key              |
| driverRef   | varchar(255) | NO   |     |         |                | Unique driver identifier |
| number      | int(11)      | YES  |     | NULL    |                | Permanent driver number  |
| code        | varchar(3)   | YES  |     | NULL    |                | Driver code e.g. "ALO"   |     
| forename    | varchar(255) | NO   |     |         |                | Driver forename          |
| surname     | varchar(255) | NO   |     |         |                | Driver surname           |
| dob         | date         | YES  |     | NULL    |                | Driver date of birth     |
| nationality | varchar(255) | YES  |     | NULL    |                | Driver nationality       |
| url         | varchar(255) | NO   | UNI |         |                | Driver Wikipedia page    |
+-------------+--------------+------+-----+---------+----------------+--------------------------+

lap_times table
+--------------+--------------+------+-----+---------+-------+-----------------------------------+
| Field        | Type         | Null | Key | Default | Extra | Description                       |
+--------------+--------------+------+-----+---------+-------+-----------------------------------+
| raceId       | int(11)      | NO   | PRI | NULL    |       | Foreign key link to races table   |
| driverId     | int(11)      | NO   | PRI | NULL    |       | Foreign key link to drivers table |
| lap          | int(11)      | NO   | PRI | NULL    |       | Lap number                        |
| position     | int(11)      | YES  |     | NULL    |       | Driver race position              |
| time         | varchar(255) | YES  |     | NULL    |       | Lap time e.g. "1:43.762"          |
| milliseconds | int(11)      | YES  |     | NULL    |       | Lap time in milliseconds          |
+--------------+--------------+------+-----+---------+-------+-----------------------------------+

pit_stops table
+--------------+--------------+------+-----+---------+-------+-----------------------------------+
| Field        | Type         | Null | Key | Default | Extra | Description                       |
+--------------+--------------+------+-----+---------+-------+-----------------------------------+
| raceId       | int(11)      | NO   | PRI | NULL    |       | Foreign key link to races table   |
| driverId     | int(11)      | NO   | PRI | NULL    |       | Foreign key link to drivers table |
| stop         | int(11)      | NO   | PRI | NULL    |       | Stop number                       |
| lap          | int(11)      | NO   |     | NULL    |       | Lap number                        |
| time         | time         | NO   |     | NULL    |       | Time of stop e.g. "13:52:25"      |
| duration     | varchar(255) | YES  |     | NULL    |       | Duration of stop e.g. "21.783"    |
| milliseconds | int(11)      | YES  |     | NULL    |       | Duration of stop in milliseconds  |
+--------------+--------------+------+-----+---------+-------+-----------------------------------+

qualifying table
+---------------+--------------+------+-----+---------+----------------+----------------------------------------+
| Field         | Type         | Null | Key | Default | Extra          | Description                            |
+---------------+--------------+------+-----+---------+----------------+----------------------------------------+
| qualifyId     | int(11)      | NO   | PRI | NULL    | auto_increment | Primary key                            |
| raceId        | int(11)      | NO   |     | 0       |                | Foreign key link to races table        |
| driverId      | int(11)      | NO   |     | 0       |                | Foreign key link to drivers table      |
| constructorId | int(11)      | NO   |     | 0       |                | Foreign key link to constructors table |
| number        | int(11)      | NO   |     | 0       |                | Driver number                          |
| position      | int(11)      | YES  |     | NULL    |                | Qualifying position                    |
| q1            | varchar(255) | YES  |     | NULL    |                | Q1 lap time e.g. "1:21.374"            |
| q2            | varchar(255) | YES  |     | NULL    |                | Q2 lap time                            |
| q3            | varchar(255) | YES  |     | NULL    |                | Q3 lap time                            |
+---------------+--------------+------+-----+---------+----------------+----------------------------------------+

races table
+-------------+--------------+------+-----+------------+----------------+------------------------------------+
| Field       | Type         | Null | Key | Default    | Extra          | Description                        |
+-------------+--------------+------+-----+------------+----------------+------------------------------------+
| raceId      | int(11)      | NO   | PRI | NULL       | auto_increment | Primary key                        |
| year        | int(11)      | NO   |     | 0          |                | Foreign key link to seasons table  |
| round       | int(11)      | NO   |     | 0          |                | Round number                       |
| circuitId   | int(11)      | NO   |     | 0          |                | Foreign key link to circuits table |
| name        | varchar(255) | NO   |     |            |                | Race name                          | 
| date        | date         | NO   |     | 0000-00-00 |                | Race date e.g. "1950-05-13"        |
| time        | time         | YES  |     | NULL       |                | Race start time e.g."13:00:00"     |
| url         | varchar(255) | YES  | UNI | NULL       |                | Race Wikipedia page                |
| fp1_date    | date         | YES  |     | NULL       |                | FP1 date                           |
| fp1_time    | time         | YES  |     | NULL       |                | FP1 start time                     |
| fp2_date    | date         | YES  |     | NULL       |                | FP2 date                           |
| fp2_time    | time         | YES  |     | NULL       |                | FP2 start time                     |
| fp3_date    | date         | YES  |     | NULL       |                | FP3 date                           |
| fp3_time    | time         | YES  |     | NULL       |                | FP3 start time                     |
| quali_date  | date         | YES  |     | NULL       |                | Qualifying date                    |
| quali_time  | time         | YES  |     | NULL       |                | Qualifying start time              |
| sprint_date | date         | YES  |     | NULL       |                | Sprint date                        |
| sprint_time | time         | YES  |     | NULL       |                | Sprint start time                  |
+-------------+--------------+------+-----+------------+----------------+------------------------------------+

results table
+-----------------+--------------+------+-----+---------+----------------+---------------------------------------------+
| Field           | Type         | Null | Key | Default | Extra          | Description                                 |
+-----------------+--------------+------+-----+---------+----------------+---------------------------------------------+
| resultId        | int(11)      | NO   | PRI | NULL    | auto_increment | Primary key                                 |
| raceId          | int(11)      | NO   |     | 0       |                | Foreign key link to races table             |
| driverId        | int(11)      | NO   |     | 0       |                | Foreign key link to drivers table           |
| constructorId   | int(11)      | NO   |     | 0       |                | Foreign key link to constructors table      |
| number          | int(11)      | YES  |     | NULL    |                | Driver number                               |
| grid            | int(11)      | NO   |     | 0       |                | Starting grid position                      |
| position        | int(11)      | YES  |     | NULL    |                | Official classification, if applicable      |
| positionText    | varchar(255) | NO   |     |         |                | Driver position string e.g. "1" or "R"      |
| positionOrder   | int(11)      | NO   |     | 0       |                | Driver position for ordering purposes       |
| points          | float        | NO   |     | 0       |                | Driver points for race                      |
| laps            | int(11)      | NO   |     | 0       |                | Number of completed laps                    |
| time            | varchar(255) | YES  |     | NULL    |                | Finishing time or gap                       |
| milliseconds    | int(11)      | YES  |     | NULL    |                | Finishing time in milliseconds              |   
| fastestLap      | int(11)      | YES  |     | NULL    |                | Lap number of fastest lap                   |
| rank            | int(11)      | YES  |     | 0       |                | Fastest lap rank, compared to other drivers |
| fastestLapTime  | varchar(255) | YES  |     | NULL    |                | Fastest lap time e.g. "1:27.453"            |
| fastestLapSpeed | varchar(255) | YES  |     | NULL    |                | Fastest lap speed (km/h) e.g. "213.874"     |
| statusId        | int(11)      | NO   |     | 0       |                | Foreign key link to status table            |
+-----------------+--------------+------+-----+---------+----------------+---------------------------------------------+

sprint_results table
+-----------------+--------------+------+-----+---------+----------------+---------------------------------------------+
| Field           | Type         | Null | Key | Default | Extra          | Description                                 |
+-----------------+--------------+------+-----+---------+----------------+---------------------------------------------+
| sprintResultId  | int(11)      | NO   | PRI | NULL    | auto_increment | Primary key                                 |
| raceId          | int(11)      | NO   |     | 0       |                | Foreign key link to races table             |
| driverId        | int(11)      | NO   |     | 0       |                | Foreign key link to drivers table           |
| constructorId   | int(11)      | NO   |     | 0       |                | Foreign key link to constructors table      |
| number          | int(11)      | YES  |     | NULL    |                | Driver number                               |
| grid            | int(11)      | NO   |     | 0       |                | Starting grid position                      |
| position        | int(11)      | YES  |     | NULL    |                | Official classification, if applicable      |
| positionText    | varchar(255) | NO   |     |         |                | Driver position string e.g. "1" or "R"      |
| positionOrder   | int(11)      | NO   |     | 0       |                | Driver position for ordering purposes       |
| points          | float        | NO   |     | 0       |                | Driver points for race                      |
| laps            | int(11)      | NO   |     | 0       |                | Number of completed laps                    |
| time            | varchar(255) | YES  |     | NULL    |                | Finishing time or gap                       |
| milliseconds    | int(11)      | YES  |     | NULL    |                | Finishing time in milliseconds              |   
| fastestLap      | int(11)      | YES  |     | NULL    |                | Lap number of fastest lap                   |
| fastestLapTime  | varchar(255) | YES  |     | NULL    |                | Fastest lap time e.g. "1:27.453"            |
| statusId        | int(11)      | NO   |     | 0       |                | Foreign key link to status table            |
+-----------------+--------------+------+-----+---------+----------------+---------------------------------------------+

seasons table
+-------+--------------+------+-----+---------+-------+-----------------------+
| Field | Type         | Null | Key | Default | Extra | Description           |
+-------+--------------+------+-----+---------+-------+-----------------------+
| year  | int(11)      | NO   | PRI | 0       |       | Primary key e.g. 1950 |
| url   | varchar(255) | NO   | UNI |         |       | Season Wikipedia page |
+-------+--------------+------+-----+---------+-------+-----------------------+

status table
+----------+--------------+------+-----+---------+----------------+---------------------------------+
| Field    | Type         | Null | Key | Default | Extra          | Description                     |
+----------+--------------+------+-----+---------+----------------+---------------------------------+
| statusId | int(11)      | NO   | PRI | NULL    | auto_increment | Primary key                     |
| status   | varchar(255) | NO   |     |         |                | Finishing status e.g. "Retired" |
+----------+--------------+------+-----+---------+----------------+---------------------------------+

This work is licensed under a Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License
To view a copy of this license, visit: http://creativecommons.org/licenses/by-nc-sa/3.0/
```

## Spatial data source

Now I needed the maps. When I find the time, I will have a go at creating my own maps, but I was very grateful to find that [Tomislav Bacinger](https://github.com/bacinger) had already curated circuit [geojson files](https://github.com/bacinger/f1-circuits/blob/master/f1-circuits.geojson) for 35 tracks.

### Import required packages


```python
import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import Point
import leafmap.foliumap as leafmap
```

Before jumping in it is imperative that we spend a lot of time getting to know our data. It can sometimes feel a bit overwhelming with such a large volume of data, spread across a number of different tables (see the table schemas below) but by being methodical and making use of the pandas library in particular, we can start to take control of the wheel.

### Custom function to perform inital exploratory data analysis (EDA)

Let's create a custom function to automate some of our data wrangling :


```python
def initial_eda(df):
    if isinstance(df, pd.DataFrame):
        total_na = df.isna().sum().sum()
        print("Dimensions : %d rows, %d columns" % (df.shape[0], df.shape[1]))
        print("Total NA Values : %d " % (total_na))
        print("%38s %10s     %10s %10s" % ("Column Name", "Data Type", "#Distinct", "NA Values"))
        col_name = df.columns
        dtyp = df.dtypes
        uniq = df.nunique()
        na_val = df.isna().sum()
        for i in range(len(df.columns)):
            print("%38s %10s   %10s %10s" % (col_name[i], dtyp[i], uniq[i], na_val[i]))
        
    else:
        print("Expect a DataFrame but got a %15s" % (type(df)))
```

### Drivers


```python
# read in our data
drivers = pd.read_csv('formula_one/data/drivers.csv')
```

Now apply our custom function :


```python
initial_eda(drivers)
```

    Dimensions : 857 rows, 9 columns
    Total NA Values : 0 
                               Column Name  Data Type      #Distinct  NA Values
                                  driverId      int64          857          0
                                 driverRef     object          857          0
                                    number     object           45          0
                                      code     object           95          0
                                  forename     object          476          0
                                   surname     object          798          0
                                       dob     object          839          0
                               nationality     object           42          0
                                       url     object          857          0



```python
# preview first 5 rows
drivers.head()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>driverId</th>
      <th>driverRef</th>
      <th>number</th>
      <th>code</th>
      <th>forename</th>
      <th>surname</th>
      <th>dob</th>
      <th>nationality</th>
      <th>url</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>hamilton</td>
      <td>44</td>
      <td>HAM</td>
      <td>Lewis</td>
      <td>Hamilton</td>
      <td>1985-01-07</td>
      <td>British</td>
      <td>http://en.wikipedia.org/wiki/Lewis_Hamilton</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2</td>
      <td>heidfeld</td>
      <td>\N</td>
      <td>HEI</td>
      <td>Nick</td>
      <td>Heidfeld</td>
      <td>1977-05-10</td>
      <td>German</td>
      <td>http://en.wikipedia.org/wiki/Nick_Heidfeld</td>
    </tr>
    <tr>
      <th>2</th>
      <td>3</td>
      <td>rosberg</td>
      <td>6</td>
      <td>ROS</td>
      <td>Nico</td>
      <td>Rosberg</td>
      <td>1985-06-27</td>
      <td>German</td>
      <td>http://en.wikipedia.org/wiki/Nico_Rosberg</td>
    </tr>
    <tr>
      <th>3</th>
      <td>4</td>
      <td>alonso</td>
      <td>14</td>
      <td>ALO</td>
      <td>Fernando</td>
      <td>Alonso</td>
      <td>1981-07-29</td>
      <td>Spanish</td>
      <td>http://en.wikipedia.org/wiki/Fernando_Alonso</td>
    </tr>
    <tr>
      <th>4</th>
      <td>5</td>
      <td>kovalainen</td>
      <td>\N</td>
      <td>KOV</td>
      <td>Heikki</td>
      <td>Kovalainen</td>
      <td>1981-10-19</td>
      <td>Finnish</td>
      <td>http://en.wikipedia.org/wiki/Heikki_Kovalainen</td>
    </tr>
  </tbody>
</table>
</div>




```python
# concatenate driver names
drivers["name"] = drivers[["forename", "surname"]].apply(lambda x: " ".join(x), axis =1)
```


```python
# drop columns of no interest
drivers.drop(['driverRef', 'number', 'forename', 'surname', 'url', 'code'], axis=1, inplace=True)
```


```python
drivers.nationality.nunique()
```




    42




```python
drivers.nationality.unique()
```




    array(['British', 'German', 'Spanish', 'Finnish', 'Japanese', 'French',
           'Polish', 'Brazilian', 'Italian', 'Australian', 'Austrian',
           'American', 'Dutch', 'Colombian', 'Portuguese', 'Canadian',
           'Indian', 'Hungarian', 'Irish', 'Danish', 'Argentine', 'Czech',
           'Malaysian', 'Swiss', 'Belgian', 'Monegasque', 'Swedish',
           'Venezuelan', 'New Zealander', 'Chilean', 'Mexican',
           'South African', 'Liechtensteiner', 'Rhodesian',
           'American-Italian', 'Uruguayan', 'Argentine-Italian', 'Thai',
           'East German', 'Russian', 'Indonesian', 'Chinese'], dtype=object)




```python
drivers.describe()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>driverId</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>count</th>
      <td>857.000000</td>
    </tr>
    <tr>
      <th>mean</th>
      <td>429.057176</td>
    </tr>
    <tr>
      <th>std</th>
      <td>247.632402</td>
    </tr>
    <tr>
      <th>min</th>
      <td>1.000000</td>
    </tr>
    <tr>
      <th>25%</th>
      <td>215.000000</td>
    </tr>
    <tr>
      <th>50%</th>
      <td>429.000000</td>
    </tr>
    <tr>
      <th>75%</th>
      <td>643.000000</td>
    </tr>
    <tr>
      <th>max</th>
      <td>858.000000</td>
    </tr>
  </tbody>
</table>
</div>



So we have information on 857 drivers representing 42 different nationalities.

### Circuits


```python
# read in our data
circuits = pd.read_csv('formula_one/data/circuits.csv')
```


```python
initial_eda(circuits)
```

    Dimensions : 77 rows, 9 columns
    Total NA Values : 0 
                               Column Name  Data Type      #Distinct  NA Values
                                 circuitId      int64           77          0
                                circuitRef     object           77          0
                                      name     object           77          0
                                  location     object           75          0
                                   country     object           35          0
                                       lat    float64           77          0
                                       lng    float64           77          0
                                       alt     object           66          0
                                       url     object           77          0


Let's create a geometry column from the `lat` and `lng` values : 


```python
circuits.head()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>circuitId</th>
      <th>circuitRef</th>
      <th>name</th>
      <th>location</th>
      <th>country</th>
      <th>lat</th>
      <th>lng</th>
      <th>alt</th>
      <th>url</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>albert_park</td>
      <td>Albert Park Grand Prix Circuit</td>
      <td>Melbourne</td>
      <td>Australia</td>
      <td>-37.84970</td>
      <td>144.96800</td>
      <td>10</td>
      <td>http://en.wikipedia.org/wiki/Melbourne_Grand_P...</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2</td>
      <td>sepang</td>
      <td>Sepang International Circuit</td>
      <td>Kuala Lumpur</td>
      <td>Malaysia</td>
      <td>2.76083</td>
      <td>101.73800</td>
      <td>18</td>
      <td>http://en.wikipedia.org/wiki/Sepang_Internatio...</td>
    </tr>
    <tr>
      <th>2</th>
      <td>3</td>
      <td>bahrain</td>
      <td>Bahrain International Circuit</td>
      <td>Sakhir</td>
      <td>Bahrain</td>
      <td>26.03250</td>
      <td>50.51060</td>
      <td>7</td>
      <td>http://en.wikipedia.org/wiki/Bahrain_Internati...</td>
    </tr>
    <tr>
      <th>3</th>
      <td>4</td>
      <td>catalunya</td>
      <td>Circuit de Barcelona-Catalunya</td>
      <td>Montmeló</td>
      <td>Spain</td>
      <td>41.57000</td>
      <td>2.26111</td>
      <td>109</td>
      <td>http://en.wikipedia.org/wiki/Circuit_de_Barcel...</td>
    </tr>
    <tr>
      <th>4</th>
      <td>5</td>
      <td>istanbul</td>
      <td>Istanbul Park</td>
      <td>Istanbul</td>
      <td>Turkey</td>
      <td>40.95170</td>
      <td>29.40500</td>
      <td>130</td>
      <td>http://en.wikipedia.org/wiki/Istanbul_Park</td>
    </tr>
  </tbody>
</table>
</div>




```python
# Use a lambda function to create Point objects and assign them to the 'geometry' column
circuits['geometry'] = circuits.apply(lambda row: Point(row['lng'], row['lat']), axis=1)
```


```python
circuits.country.nunique()
```




    35




```python
circuits.country.unique()
```




    array(['Australia', 'Malaysia', 'Bahrain', 'Spain', 'Turkey', 'Monaco',
           'Canada', 'France', 'UK', 'Germany', 'Hungary', 'Belgium', 'Italy',
           'Singapore', 'Japan', 'China', 'Brazil', 'USA', 'United States',
           'UAE', 'Argentina', 'Portugal', 'South Africa', 'Mexico', 'Korea',
           'Netherlands', 'Sweden', 'Austria', 'Morocco', 'Switzerland',
           'India', 'Russia', 'Azerbaijan', 'Saudi Arabia', 'Qatar'],
          dtype=object)



So we have information on 77 race circuits across 35 different countries.


```python
# drop columns of no interest
circuits.drop(['alt', 'url', 'circuitRef'], axis=1, inplace=True)
circuits
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>circuitId</th>
      <th>name</th>
      <th>location</th>
      <th>country</th>
      <th>lat</th>
      <th>lng</th>
      <th>geometry</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>Albert Park Grand Prix Circuit</td>
      <td>Melbourne</td>
      <td>Australia</td>
      <td>-37.84970</td>
      <td>144.96800</td>
      <td>POINT (144.968 -37.8497)</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2</td>
      <td>Sepang International Circuit</td>
      <td>Kuala Lumpur</td>
      <td>Malaysia</td>
      <td>2.76083</td>
      <td>101.73800</td>
      <td>POINT (101.738 2.76083)</td>
    </tr>
    <tr>
      <th>2</th>
      <td>3</td>
      <td>Bahrain International Circuit</td>
      <td>Sakhir</td>
      <td>Bahrain</td>
      <td>26.03250</td>
      <td>50.51060</td>
      <td>POINT (50.5106 26.0325)</td>
    </tr>
    <tr>
      <th>3</th>
      <td>4</td>
      <td>Circuit de Barcelona-Catalunya</td>
      <td>Montmeló</td>
      <td>Spain</td>
      <td>41.57000</td>
      <td>2.26111</td>
      <td>POINT (2.26111 41.57)</td>
    </tr>
    <tr>
      <th>4</th>
      <td>5</td>
      <td>Istanbul Park</td>
      <td>Istanbul</td>
      <td>Turkey</td>
      <td>40.95170</td>
      <td>29.40500</td>
      <td>POINT (29.405 40.9517)</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>72</th>
      <td>75</td>
      <td>Autódromo Internacional do Algarve</td>
      <td>Portimão</td>
      <td>Portugal</td>
      <td>37.22700</td>
      <td>-8.62670</td>
      <td>POINT (-8.6267 37.227)</td>
    </tr>
    <tr>
      <th>73</th>
      <td>76</td>
      <td>Autodromo Internazionale del Mugello</td>
      <td>Mugello</td>
      <td>Italy</td>
      <td>43.99750</td>
      <td>11.37190</td>
      <td>POINT (11.3719 43.9975)</td>
    </tr>
    <tr>
      <th>74</th>
      <td>77</td>
      <td>Jeddah Corniche Circuit</td>
      <td>Jeddah</td>
      <td>Saudi Arabia</td>
      <td>21.63190</td>
      <td>39.10440</td>
      <td>POINT (39.1044 21.6319)</td>
    </tr>
    <tr>
      <th>75</th>
      <td>78</td>
      <td>Losail International Circuit</td>
      <td>Al Daayen</td>
      <td>Qatar</td>
      <td>25.49000</td>
      <td>51.45420</td>
      <td>POINT (51.4542 25.49)</td>
    </tr>
    <tr>
      <th>76</th>
      <td>79</td>
      <td>Miami International Autodrome</td>
      <td>Miami</td>
      <td>USA</td>
      <td>25.95810</td>
      <td>-80.23890</td>
      <td>POINT (-80.2389 25.9581)</td>
    </tr>
  </tbody>
</table>
<p>77 rows × 7 columns</p>
</div>




```python
circuits.describe()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>circuitId</th>
      <th>lat</th>
      <th>lng</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>count</th>
      <td>77.000000</td>
      <td>77.000000</td>
      <td>77.000000</td>
    </tr>
    <tr>
      <th>mean</th>
      <td>39.883117</td>
      <td>33.442925</td>
      <td>1.076683</td>
    </tr>
    <tr>
      <th>std</th>
      <td>23.001701</td>
      <td>22.808866</td>
      <td>65.516951</td>
    </tr>
    <tr>
      <th>min</th>
      <td>1.000000</td>
      <td>-37.849700</td>
      <td>-118.189000</td>
    </tr>
    <tr>
      <th>25%</th>
      <td>20.000000</td>
      <td>32.777400</td>
      <td>-9.394170</td>
    </tr>
    <tr>
      <th>50%</th>
      <td>40.000000</td>
      <td>40.951700</td>
      <td>3.930830</td>
    </tr>
    <tr>
      <th>75%</th>
      <td>59.000000</td>
      <td>46.958900</td>
      <td>19.248600</td>
    </tr>
    <tr>
      <th>max</th>
      <td>80.000000</td>
      <td>57.265300</td>
      <td>144.968000</td>
    </tr>
  </tbody>
</table>
</div>



### Circuit Maps


```python
# create a GeoPandas DataFrame of circuits from geojson file
circuits_gdf = gpd.read_file('https://raw.githubusercontent.com/Stephen137/formula_one/main/data/f1-circuits.geojson')
```


```python
print(type(circuits_gdf))
```

    <class 'geopandas.geodataframe.GeoDataFrame'>



```python
initial_eda(circuits_gdf)
```

    Dimensions : 35 rows, 8 columns
    Total NA Values : 0 
                               Column Name  Data Type      #Distinct  NA Values
                                        id     object           35          0
                                  Location     object           35          0
                                      Name     object           35          0
                                    opened      int64           29          0
                                   firstgp      int64           26          0
                                  length_m      int64           34          0
                                altitude_m      int64           33          0
                                  geometry   geometry           35          0


We only have maps for 35 circuits. So let's bear that in mind and filter our race stats to include only those that we have maps for.


```python
circuit_names = list(circuits_gdf.Name.values)
circuit_names
```




    ['Albert Park Grand Prix Circuit',
     'Bahrain International Circuit',
     'Shanghai International Circuit',
     'Baku City Circuit',
     'Circuit de Barcelona-Catalunya',
     'Circuit de Monaco',
     'Circuit Gilles Villeneuve',
     'Circuit Paul Ricard',
     'Red Bull Ring',
     'Silverstone Circuit',
     'Hockenheimring',
     'Hungaroring',
     'Circuit de Spa-Francorchamps',
     'Autodromo Nazionale di Monza',
     'Marina Bay Street Circuit',
     'Sochi Autodrom',
     'Suzuka Circuit',
     'Circuit of the Americas',
     'Autódromo Hermanos Rodríguez',
     'Autódromo José Carlos Pace',
     'Yas Marina Circuit',
     'Autodromo Enzo e Dino Ferrari',
     'Nürburgring',
     'Autódromo Internacional do Algarve',
     'Autodromo Internazionale del Mugello',
     'Sepang International Circuit',
     'Istanbul Park',
     'Circuit Park Zandvoort',
     'Circuit de Nevers Magny-Cours',
     'Autódromo do Estoril',
     'Autódromo Internacional Nelson Piquet',
     'Jeddah Corniche Circuit',
     'Miami International Autodrome',
     'Losail International Circuit',
     'Las Vegas Strip Street Circuit']



### Races


```python
# read in our data
races = pd.read_csv('formula_one/data/races.csv')
```


```python
initial_eda(races)
```

    Dimensions : 1101 rows, 18 columns
    Total NA Values : 0 
                               Column Name  Data Type      #Distinct  NA Values
                                    raceId      int64         1101          0
                                      year      int64           74          0
                                     round      int64           22          0
                                 circuitId      int64           77          0
                                      name     object           54          0
                                      date     object         1101          0
                                      time     object           34          0
                                       url     object         1101          0
                                  fp1_date     object           67          0
                                  fp1_time     object           19          0
                                  fp2_date     object           67          0
                                  fp2_time     object           16          0
                                  fp3_date     object           55          0
                                  fp3_time     object           17          0
                                quali_date     object           67          0
                                quali_time     object           13          0
                               sprint_date     object           13          0
                               sprint_time     object            6          0



```python
# drop columns of no interest
races = races [["raceId", "year", "circuitId", "name", "date"]]
races
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>raceId</th>
      <th>year</th>
      <th>circuitId</th>
      <th>name</th>
      <th>date</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>2009</td>
      <td>1</td>
      <td>Australian Grand Prix</td>
      <td>2009-03-29</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2</td>
      <td>2009</td>
      <td>2</td>
      <td>Malaysian Grand Prix</td>
      <td>2009-04-05</td>
    </tr>
    <tr>
      <th>2</th>
      <td>3</td>
      <td>2009</td>
      <td>17</td>
      <td>Chinese Grand Prix</td>
      <td>2009-04-19</td>
    </tr>
    <tr>
      <th>3</th>
      <td>4</td>
      <td>2009</td>
      <td>3</td>
      <td>Bahrain Grand Prix</td>
      <td>2009-04-26</td>
    </tr>
    <tr>
      <th>4</th>
      <td>5</td>
      <td>2009</td>
      <td>4</td>
      <td>Spanish Grand Prix</td>
      <td>2009-05-10</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>1096</th>
      <td>1116</td>
      <td>2023</td>
      <td>69</td>
      <td>United States Grand Prix</td>
      <td>2023-10-22</td>
    </tr>
    <tr>
      <th>1097</th>
      <td>1117</td>
      <td>2023</td>
      <td>32</td>
      <td>Mexico City Grand Prix</td>
      <td>2023-10-29</td>
    </tr>
    <tr>
      <th>1098</th>
      <td>1118</td>
      <td>2023</td>
      <td>18</td>
      <td>São Paulo Grand Prix</td>
      <td>2023-11-05</td>
    </tr>
    <tr>
      <th>1099</th>
      <td>1119</td>
      <td>2023</td>
      <td>80</td>
      <td>Las Vegas Grand Prix</td>
      <td>2023-11-19</td>
    </tr>
    <tr>
      <th>1100</th>
      <td>1120</td>
      <td>2023</td>
      <td>24</td>
      <td>Abu Dhabi Grand Prix</td>
      <td>2023-11-26</td>
    </tr>
  </tbody>
</table>
<p>1101 rows × 5 columns</p>
</div>




```python
races.describe()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>raceId</th>
      <th>year</th>
      <th>circuitId</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>count</th>
      <td>1101.000000</td>
      <td>1101.000000</td>
      <td>1101.000000</td>
    </tr>
    <tr>
      <th>mean</th>
      <td>553.355132</td>
      <td>1992.020890</td>
      <td>23.700272</td>
    </tr>
    <tr>
      <th>std</th>
      <td>321.425790</td>
      <td>20.296406</td>
      <td>19.346014</td>
    </tr>
    <tr>
      <th>min</th>
      <td>1.000000</td>
      <td>1950.000000</td>
      <td>1.000000</td>
    </tr>
    <tr>
      <th>25%</th>
      <td>276.000000</td>
      <td>1976.000000</td>
      <td>9.000000</td>
    </tr>
    <tr>
      <th>50%</th>
      <td>551.000000</td>
      <td>1994.000000</td>
      <td>18.000000</td>
    </tr>
    <tr>
      <th>75%</th>
      <td>826.000000</td>
      <td>2010.000000</td>
      <td>34.000000</td>
    </tr>
    <tr>
      <th>max</th>
      <td>1120.000000</td>
      <td>2023.000000</td>
      <td>80.000000</td>
    </tr>
  </tbody>
</table>
</div>



So we have information on 1,101 races taking place across 80 different circuits, spanning the 73 years between 1950 and 2023.

### Results


```python
# read in our data
results = pd.read_csv('formula_one/data/results.csv')
```


```python
initial_eda(results)
```

    Dimensions : 26080 rows, 18 columns
    Total NA Values : 0 
                               Column Name  Data Type      #Distinct  NA Values
                                  resultId      int64        26080          0
                                    raceId      int64         1091          0
                                  driverId      int64          857          0
                             constructorId      int64          210          0
                                    number     object          130          0
                                      grid      int64           35          0
                                  position     object           34          0
                              positionText     object           39          0
                             positionOrder      int64           39          0
                                    points    float64           39          0
                                      laps      int64          172          0
                                      time     object         7000          0
                              milliseconds     object         7213          0
                                fastestLap     object           80          0
                                      rank     object           26          0
                            fastestLapTime     object         6970          0
                           fastestLapSpeed     object         7145          0
                                  statusId      int64          137          0



```python
# Use a lambda function to Point objects and assign them to the 'geometry' column
results['positionDiff'] = results.apply(lambda row: (row['positionOrder'] - row['grid']), axis=1)
results.head()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>resultId</th>
      <th>raceId</th>
      <th>driverId</th>
      <th>constructorId</th>
      <th>number</th>
      <th>grid</th>
      <th>position</th>
      <th>positionText</th>
      <th>positionOrder</th>
      <th>points</th>
      <th>laps</th>
      <th>time</th>
      <th>milliseconds</th>
      <th>fastestLap</th>
      <th>rank</th>
      <th>fastestLapTime</th>
      <th>fastestLapSpeed</th>
      <th>statusId</th>
      <th>positionDiff</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>18</td>
      <td>1</td>
      <td>1</td>
      <td>22</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>10.0</td>
      <td>58</td>
      <td>1:34:50.616</td>
      <td>5690616</td>
      <td>39</td>
      <td>2</td>
      <td>1:27.452</td>
      <td>218.300</td>
      <td>1</td>
      <td>0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2</td>
      <td>18</td>
      <td>2</td>
      <td>2</td>
      <td>3</td>
      <td>5</td>
      <td>2</td>
      <td>2</td>
      <td>2</td>
      <td>8.0</td>
      <td>58</td>
      <td>+5.478</td>
      <td>5696094</td>
      <td>41</td>
      <td>3</td>
      <td>1:27.739</td>
      <td>217.586</td>
      <td>1</td>
      <td>-3</td>
    </tr>
    <tr>
      <th>2</th>
      <td>3</td>
      <td>18</td>
      <td>3</td>
      <td>3</td>
      <td>7</td>
      <td>7</td>
      <td>3</td>
      <td>3</td>
      <td>3</td>
      <td>6.0</td>
      <td>58</td>
      <td>+8.163</td>
      <td>5698779</td>
      <td>41</td>
      <td>5</td>
      <td>1:28.090</td>
      <td>216.719</td>
      <td>1</td>
      <td>-4</td>
    </tr>
    <tr>
      <th>3</th>
      <td>4</td>
      <td>18</td>
      <td>4</td>
      <td>4</td>
      <td>5</td>
      <td>11</td>
      <td>4</td>
      <td>4</td>
      <td>4</td>
      <td>5.0</td>
      <td>58</td>
      <td>+17.181</td>
      <td>5707797</td>
      <td>58</td>
      <td>7</td>
      <td>1:28.603</td>
      <td>215.464</td>
      <td>1</td>
      <td>-7</td>
    </tr>
    <tr>
      <th>4</th>
      <td>5</td>
      <td>18</td>
      <td>5</td>
      <td>1</td>
      <td>23</td>
      <td>3</td>
      <td>5</td>
      <td>5</td>
      <td>5</td>
      <td>4.0</td>
      <td>58</td>
      <td>+18.014</td>
      <td>5708630</td>
      <td>43</td>
      <td>1</td>
      <td>1:27.418</td>
      <td>218.385</td>
      <td>1</td>
      <td>2</td>
    </tr>
  </tbody>
</table>
</div>




```python
results.describe()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>resultId</th>
      <th>raceId</th>
      <th>driverId</th>
      <th>constructorId</th>
      <th>grid</th>
      <th>positionOrder</th>
      <th>points</th>
      <th>laps</th>
      <th>statusId</th>
      <th>positionDiff</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>count</th>
      <td>26080.000000</td>
      <td>26080.000000</td>
      <td>26080.000000</td>
      <td>26080.000000</td>
      <td>26080.000000</td>
      <td>26080.000000</td>
      <td>26080.000000</td>
      <td>26080.000000</td>
      <td>26080.000000</td>
      <td>26080.000000</td>
    </tr>
    <tr>
      <th>mean</th>
      <td>13041.372661</td>
      <td>536.695667</td>
      <td>266.277569</td>
      <td>49.059663</td>
      <td>11.167561</td>
      <td>12.854141</td>
      <td>1.906635</td>
      <td>46.076687</td>
      <td>17.476074</td>
      <td>1.686580</td>
    </tr>
    <tr>
      <th>std</th>
      <td>7530.008377</td>
      <td>303.034639</td>
      <td>272.581622</td>
      <td>60.221056</td>
      <td>7.232797</td>
      <td>7.700068</td>
      <td>4.219715</td>
      <td>29.726058</td>
      <td>26.129965</td>
      <td>9.699508</td>
    </tr>
    <tr>
      <th>min</th>
      <td>1.000000</td>
      <td>1.000000</td>
      <td>1.000000</td>
      <td>1.000000</td>
      <td>0.000000</td>
      <td>1.000000</td>
      <td>0.000000</td>
      <td>0.000000</td>
      <td>1.000000</td>
      <td>-30.000000</td>
    </tr>
    <tr>
      <th>25%</th>
      <td>6520.750000</td>
      <td>294.750000</td>
      <td>57.000000</td>
      <td>6.000000</td>
      <td>5.000000</td>
      <td>6.000000</td>
      <td>0.000000</td>
      <td>22.000000</td>
      <td>1.000000</td>
      <td>-4.000000</td>
    </tr>
    <tr>
      <th>50%</th>
      <td>13040.500000</td>
      <td>519.000000</td>
      <td>163.000000</td>
      <td>25.000000</td>
      <td>11.000000</td>
      <td>12.000000</td>
      <td>0.000000</td>
      <td>53.000000</td>
      <td>10.000000</td>
      <td>0.000000</td>
    </tr>
    <tr>
      <th>75%</th>
      <td>19560.250000</td>
      <td>791.000000</td>
      <td>364.000000</td>
      <td>58.250000</td>
      <td>17.000000</td>
      <td>18.000000</td>
      <td>2.000000</td>
      <td>66.000000</td>
      <td>14.000000</td>
      <td>5.000000</td>
    </tr>
    <tr>
      <th>max</th>
      <td>26085.000000</td>
      <td>1110.000000</td>
      <td>858.000000</td>
      <td>214.000000</td>
      <td>34.000000</td>
      <td>39.000000</td>
      <td>50.000000</td>
      <td>200.000000</td>
      <td>141.000000</td>
      <td>39.000000</td>
    </tr>
  </tbody>
</table>
</div>



So we have results information covering 1,110 races (the latest race being the Belgian Grand Prix on 30 July 2023), 858 drivers (slightly anomalous compared to those tables), and 214 constructors. 

### Constructors


```python
# read in our data
constructors = pd.read_csv('formula_one/data/constructors.csv')
```


```python
initial_eda(constructors)
```

    Dimensions : 211 rows, 5 columns
    Total NA Values : 0 
                               Column Name  Data Type      #Distinct  NA Values
                             constructorId      int64          211          0
                            constructorRef     object          211          0
                                      name     object          211          0
                               nationality     object           24          0
                                       url     object          174          0



```python
# drop columns of no interest
constructors.drop(['url', 'constructorRef'], axis=1, inplace=True)
constructors
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>constructorId</th>
      <th>name</th>
      <th>nationality</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>McLaren</td>
      <td>British</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2</td>
      <td>BMW Sauber</td>
      <td>German</td>
    </tr>
    <tr>
      <th>2</th>
      <td>3</td>
      <td>Williams</td>
      <td>British</td>
    </tr>
    <tr>
      <th>3</th>
      <td>4</td>
      <td>Renault</td>
      <td>French</td>
    </tr>
    <tr>
      <th>4</th>
      <td>5</td>
      <td>Toro Rosso</td>
      <td>Italian</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>206</th>
      <td>209</td>
      <td>Manor Marussia</td>
      <td>British</td>
    </tr>
    <tr>
      <th>207</th>
      <td>210</td>
      <td>Haas F1 Team</td>
      <td>American</td>
    </tr>
    <tr>
      <th>208</th>
      <td>211</td>
      <td>Racing Point</td>
      <td>British</td>
    </tr>
    <tr>
      <th>209</th>
      <td>213</td>
      <td>AlphaTauri</td>
      <td>Italian</td>
    </tr>
    <tr>
      <th>210</th>
      <td>214</td>
      <td>Alpine F1 Team</td>
      <td>French</td>
    </tr>
  </tbody>
</table>
<p>211 rows × 3 columns</p>
</div>




```python
constructors.nationality.nunique()
```




    24




```python
constructors.nationality.unique()
```




    array(['British', 'German', 'French', 'Italian', 'Japanese', 'Austrian',
           'Indian', 'Dutch', 'Russian', 'Swiss', 'Irish', 'Hong Kong',
           'Brazilian', 'Canadian', 'Mexican', 'American', 'Australian',
           'New Zealander', 'South African', 'Rhodesian', 'Belgian',
           'East German', 'Spanish', 'Malaysian'], dtype=object)




```python
constructors.describe()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>constructorId</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>count</th>
      <td>211.000000</td>
    </tr>
    <tr>
      <th>mean</th>
      <td>107.037915</td>
    </tr>
    <tr>
      <th>std</th>
      <td>61.653629</td>
    </tr>
    <tr>
      <th>min</th>
      <td>1.000000</td>
    </tr>
    <tr>
      <th>25%</th>
      <td>54.500000</td>
    </tr>
    <tr>
      <th>50%</th>
      <td>107.000000</td>
    </tr>
    <tr>
      <th>75%</th>
      <td>159.500000</td>
    </tr>
    <tr>
      <th>max</th>
      <td>214.000000</td>
    </tr>
  </tbody>
</table>
</div>



### Status


```python
# read in our data
status = pd.read_csv('formula_one/data/status.csv')
```


```python
initial_eda(status)
```

    Dimensions : 139 rows, 2 columns
    Total NA Values : 0 
                               Column Name  Data Type      #Distinct  NA Values
                                  statusId      int64          139          0
                                    status     object          139          0



```python
status.status.values
```




    array(['Finished', 'Disqualified', 'Accident', 'Collision', 'Engine',
           'Gearbox', 'Transmission', 'Clutch', 'Hydraulics', 'Electrical',
           '+1 Lap', '+2 Laps', '+3 Laps', '+4 Laps', '+5 Laps', '+6 Laps',
           '+7 Laps', '+8 Laps', '+9 Laps', 'Spun off', 'Radiator',
           'Suspension', 'Brakes', 'Differential', 'Overheating',
           'Mechanical', 'Tyre', 'Driver Seat', 'Puncture', 'Driveshaft',
           'Retired', 'Fuel pressure', 'Front wing', 'Water pressure',
           'Refuelling', 'Wheel', 'Throttle', 'Steering', 'Technical',
           'Electronics', 'Broken wing', 'Heat shield fire', 'Exhaust',
           'Oil leak', '+11 Laps', 'Wheel rim', 'Water leak', 'Fuel pump',
           'Track rod', '+17 Laps', 'Oil pressure', '+42 Laps', '+13 Laps',
           'Withdrew', '+12 Laps', 'Engine fire', 'Engine misfire',
           '+26 Laps', 'Tyre puncture', 'Out of fuel', 'Wheel nut',
           'Not classified', 'Pneumatics', 'Handling', 'Rear wing', 'Fire',
           'Wheel bearing', 'Physical', 'Fuel system', 'Oil line', 'Fuel rig',
           'Launch control', 'Injured', 'Fuel', 'Power loss', 'Vibrations',
           '107% Rule', 'Safety', 'Drivetrain', 'Ignition', 'Did not qualify',
           'Injury', 'Chassis', 'Battery', 'Stalled', 'Halfshaft',
           'Crankshaft', '+10 Laps', 'Safety concerns', 'Not restarted',
           'Alternator', 'Underweight', 'Safety belt', 'Oil pump',
           'Fuel leak', 'Excluded', 'Did not prequalify', 'Injection',
           'Distributor', 'Driver unwell', 'Turbo', 'CV joint', 'Water pump',
           'Fatal accident', 'Spark plugs', 'Fuel pipe', 'Eye injury',
           'Oil pipe', 'Axle', 'Water pipe', '+14 Laps', '+15 Laps',
           '+25 Laps', '+18 Laps', '+22 Laps', '+16 Laps', '+24 Laps',
           '+29 Laps', '+23 Laps', '+21 Laps', 'Magneto', '+44 Laps',
           '+30 Laps', '+19 Laps', '+46 Laps', 'Supercharger', '+20 Laps',
           'Collision damage', 'Power Unit', 'ERS', '+49 Laps', '+38 Laps',
           'Brake duct', 'Seat', 'Damage', 'Debris', 'Illness', 'Undertray',
           'Cooling system'], dtype=object)



I intend to use this data to perhaps guauge the safety of each of the circuits by charting the number of major incidents.

### Joining our races and circuits data


```python
races_circuits = races.merge(circuits,left_on='circuitId', right_on='circuitId')
races_circuits
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>raceId</th>
      <th>year</th>
      <th>circuitId</th>
      <th>name_x</th>
      <th>date</th>
      <th>name_y</th>
      <th>location</th>
      <th>country</th>
      <th>lat</th>
      <th>lng</th>
      <th>geometry</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>2009</td>
      <td>1</td>
      <td>Australian Grand Prix</td>
      <td>2009-03-29</td>
      <td>Albert Park Grand Prix Circuit</td>
      <td>Melbourne</td>
      <td>Australia</td>
      <td>-37.8497</td>
      <td>144.9680</td>
      <td>POINT (144.968 -37.8497)</td>
    </tr>
    <tr>
      <th>1</th>
      <td>18</td>
      <td>2008</td>
      <td>1</td>
      <td>Australian Grand Prix</td>
      <td>2008-03-16</td>
      <td>Albert Park Grand Prix Circuit</td>
      <td>Melbourne</td>
      <td>Australia</td>
      <td>-37.8497</td>
      <td>144.9680</td>
      <td>POINT (144.968 -37.8497)</td>
    </tr>
    <tr>
      <th>2</th>
      <td>36</td>
      <td>2007</td>
      <td>1</td>
      <td>Australian Grand Prix</td>
      <td>2007-03-18</td>
      <td>Albert Park Grand Prix Circuit</td>
      <td>Melbourne</td>
      <td>Australia</td>
      <td>-37.8497</td>
      <td>144.9680</td>
      <td>POINT (144.968 -37.8497)</td>
    </tr>
    <tr>
      <th>3</th>
      <td>55</td>
      <td>2006</td>
      <td>1</td>
      <td>Australian Grand Prix</td>
      <td>2006-04-02</td>
      <td>Albert Park Grand Prix Circuit</td>
      <td>Melbourne</td>
      <td>Australia</td>
      <td>-37.8497</td>
      <td>144.9680</td>
      <td>POINT (144.968 -37.8497)</td>
    </tr>
    <tr>
      <th>4</th>
      <td>71</td>
      <td>2005</td>
      <td>1</td>
      <td>Australian Grand Prix</td>
      <td>2005-03-06</td>
      <td>Albert Park Grand Prix Circuit</td>
      <td>Melbourne</td>
      <td>Australia</td>
      <td>-37.8497</td>
      <td>144.9680</td>
      <td>POINT (144.968 -37.8497)</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>1096</th>
      <td>1075</td>
      <td>2022</td>
      <td>77</td>
      <td>Saudi Arabian Grand Prix</td>
      <td>2022-03-27</td>
      <td>Jeddah Corniche Circuit</td>
      <td>Jeddah</td>
      <td>Saudi Arabia</td>
      <td>21.6319</td>
      <td>39.1044</td>
      <td>POINT (39.1044 21.6319)</td>
    </tr>
    <tr>
      <th>1097</th>
      <td>1099</td>
      <td>2023</td>
      <td>77</td>
      <td>Saudi Arabian Grand Prix</td>
      <td>2023-03-19</td>
      <td>Jeddah Corniche Circuit</td>
      <td>Jeddah</td>
      <td>Saudi Arabia</td>
      <td>21.6319</td>
      <td>39.1044</td>
      <td>POINT (39.1044 21.6319)</td>
    </tr>
    <tr>
      <th>1098</th>
      <td>1078</td>
      <td>2022</td>
      <td>79</td>
      <td>Miami Grand Prix</td>
      <td>2022-05-08</td>
      <td>Miami International Autodrome</td>
      <td>Miami</td>
      <td>USA</td>
      <td>25.9581</td>
      <td>-80.2389</td>
      <td>POINT (-80.2389 25.9581)</td>
    </tr>
    <tr>
      <th>1099</th>
      <td>1102</td>
      <td>2023</td>
      <td>79</td>
      <td>Miami Grand Prix</td>
      <td>2023-05-07</td>
      <td>Miami International Autodrome</td>
      <td>Miami</td>
      <td>USA</td>
      <td>25.9581</td>
      <td>-80.2389</td>
      <td>POINT (-80.2389 25.9581)</td>
    </tr>
    <tr>
      <th>1100</th>
      <td>1119</td>
      <td>2023</td>
      <td>80</td>
      <td>Las Vegas Grand Prix</td>
      <td>2023-11-19</td>
      <td>Las Vegas Strip Street Circuit</td>
      <td>Las Vegas</td>
      <td>United States</td>
      <td>36.1147</td>
      <td>-115.1730</td>
      <td>POINT (-115.173 36.1147)</td>
    </tr>
  </tbody>
</table>
<p>1101 rows × 11 columns</p>
</div>




```python
# tidy up col names
races_circuits.rename(columns={"name_x": "race_name", "name_y": "circuit_name", "date": "race_date"},inplace=True)
races_circuits.head()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>raceId</th>
      <th>year</th>
      <th>circuitId</th>
      <th>race_name</th>
      <th>race_date</th>
      <th>circuit_name</th>
      <th>location</th>
      <th>country</th>
      <th>lat</th>
      <th>lng</th>
      <th>geometry</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>2009</td>
      <td>1</td>
      <td>Australian Grand Prix</td>
      <td>2009-03-29</td>
      <td>Albert Park Grand Prix Circuit</td>
      <td>Melbourne</td>
      <td>Australia</td>
      <td>-37.8497</td>
      <td>144.968</td>
      <td>POINT (144.968 -37.8497)</td>
    </tr>
    <tr>
      <th>1</th>
      <td>18</td>
      <td>2008</td>
      <td>1</td>
      <td>Australian Grand Prix</td>
      <td>2008-03-16</td>
      <td>Albert Park Grand Prix Circuit</td>
      <td>Melbourne</td>
      <td>Australia</td>
      <td>-37.8497</td>
      <td>144.968</td>
      <td>POINT (144.968 -37.8497)</td>
    </tr>
    <tr>
      <th>2</th>
      <td>36</td>
      <td>2007</td>
      <td>1</td>
      <td>Australian Grand Prix</td>
      <td>2007-03-18</td>
      <td>Albert Park Grand Prix Circuit</td>
      <td>Melbourne</td>
      <td>Australia</td>
      <td>-37.8497</td>
      <td>144.968</td>
      <td>POINT (144.968 -37.8497)</td>
    </tr>
    <tr>
      <th>3</th>
      <td>55</td>
      <td>2006</td>
      <td>1</td>
      <td>Australian Grand Prix</td>
      <td>2006-04-02</td>
      <td>Albert Park Grand Prix Circuit</td>
      <td>Melbourne</td>
      <td>Australia</td>
      <td>-37.8497</td>
      <td>144.968</td>
      <td>POINT (144.968 -37.8497)</td>
    </tr>
    <tr>
      <th>4</th>
      <td>71</td>
      <td>2005</td>
      <td>1</td>
      <td>Australian Grand Prix</td>
      <td>2005-03-06</td>
      <td>Albert Park Grand Prix Circuit</td>
      <td>Melbourne</td>
      <td>Australia</td>
      <td>-37.8497</td>
      <td>144.968</td>
      <td>POINT (144.968 -37.8497)</td>
    </tr>
  </tbody>
</table>
</div>



### Join to results, drivers, constructors and status


```python
f1_summary = results.merge(status, on='statusId').merge(races_circuits,on='raceId').merge(drivers,on='driverId').merge(constructors,on='constructorId')
f1_summary.head()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>resultId</th>
      <th>raceId</th>
      <th>driverId</th>
      <th>constructorId</th>
      <th>number</th>
      <th>grid</th>
      <th>position</th>
      <th>positionText</th>
      <th>positionOrder</th>
      <th>points</th>
      <th>...</th>
      <th>location</th>
      <th>country</th>
      <th>lat</th>
      <th>lng</th>
      <th>geometry</th>
      <th>dob</th>
      <th>nationality_x</th>
      <th>name_x</th>
      <th>name_y</th>
      <th>nationality_y</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>18</td>
      <td>1</td>
      <td>1</td>
      <td>22</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>10.0</td>
      <td>...</td>
      <td>Melbourne</td>
      <td>Australia</td>
      <td>-37.84970</td>
      <td>144.96800</td>
      <td>POINT (144.968 -37.8497)</td>
      <td>1985-01-07</td>
      <td>British</td>
      <td>Lewis Hamilton</td>
      <td>McLaren</td>
      <td>British</td>
    </tr>
    <tr>
      <th>1</th>
      <td>27</td>
      <td>19</td>
      <td>1</td>
      <td>1</td>
      <td>22</td>
      <td>9</td>
      <td>5</td>
      <td>5</td>
      <td>5</td>
      <td>4.0</td>
      <td>...</td>
      <td>Kuala Lumpur</td>
      <td>Malaysia</td>
      <td>2.76083</td>
      <td>101.73800</td>
      <td>POINT (101.738 2.76083)</td>
      <td>1985-01-07</td>
      <td>British</td>
      <td>Lewis Hamilton</td>
      <td>McLaren</td>
      <td>British</td>
    </tr>
    <tr>
      <th>2</th>
      <td>57</td>
      <td>20</td>
      <td>1</td>
      <td>1</td>
      <td>22</td>
      <td>3</td>
      <td>13</td>
      <td>13</td>
      <td>13</td>
      <td>0.0</td>
      <td>...</td>
      <td>Sakhir</td>
      <td>Bahrain</td>
      <td>26.03250</td>
      <td>50.51060</td>
      <td>POINT (50.5106 26.0325)</td>
      <td>1985-01-07</td>
      <td>British</td>
      <td>Lewis Hamilton</td>
      <td>McLaren</td>
      <td>British</td>
    </tr>
    <tr>
      <th>3</th>
      <td>69</td>
      <td>21</td>
      <td>1</td>
      <td>1</td>
      <td>22</td>
      <td>5</td>
      <td>3</td>
      <td>3</td>
      <td>3</td>
      <td>6.0</td>
      <td>...</td>
      <td>Montmeló</td>
      <td>Spain</td>
      <td>41.57000</td>
      <td>2.26111</td>
      <td>POINT (2.26111 41.57)</td>
      <td>1985-01-07</td>
      <td>British</td>
      <td>Lewis Hamilton</td>
      <td>McLaren</td>
      <td>British</td>
    </tr>
    <tr>
      <th>4</th>
      <td>90</td>
      <td>22</td>
      <td>1</td>
      <td>1</td>
      <td>22</td>
      <td>3</td>
      <td>2</td>
      <td>2</td>
      <td>2</td>
      <td>8.0</td>
      <td>...</td>
      <td>Istanbul</td>
      <td>Turkey</td>
      <td>40.95170</td>
      <td>29.40500</td>
      <td>POINT (29.405 40.9517)</td>
      <td>1985-01-07</td>
      <td>British</td>
      <td>Lewis Hamilton</td>
      <td>McLaren</td>
      <td>British</td>
    </tr>
  </tbody>
</table>
<p>5 rows × 35 columns</p>
</div>




```python
f1_summary.columns
```




    Index(['resultId', 'raceId', 'driverId', 'constructorId', 'number', 'grid',
           'position', 'positionText', 'positionOrder', 'points', 'laps', 'time',
           'milliseconds', 'fastestLap', 'rank', 'fastestLapTime',
           'fastestLapSpeed', 'statusId', 'positionDiff', 'status', 'year',
           'circuitId', 'race_name', 'race_date', 'circuit_name', 'location',
           'country', 'lat', 'lng', 'geometry', 'dob', 'nationality_x', 'name_x',
           'name_y', 'nationality_y'],
          dtype='object')




```python
# tidy up column names
f1_summary.rename(columns={"name_x": "driver_name", "name_y": "constr_name", "nationality_x": "driver_nat", "nationality_y": "constr_nat"},inplace=True)
```


```python
f1_summary.columns
```




    Index(['resultId', 'raceId', 'driverId', 'constructorId', 'number', 'grid',
           'position', 'positionText', 'positionOrder', 'points', 'laps', 'time',
           'milliseconds', 'fastestLap', 'rank', 'fastestLapTime',
           'fastestLapSpeed', 'statusId', 'positionDiff', 'status', 'year',
           'circuitId', 'race_name', 'race_date', 'circuit_name', 'location',
           'country', 'lat', 'lng', 'geometry', 'dob', 'driver_nat', 'driver_name',
           'constr_name', 'constr_nat'],
          dtype='object')




```python
f1_summary
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>resultId</th>
      <th>raceId</th>
      <th>driverId</th>
      <th>constructorId</th>
      <th>number</th>
      <th>grid</th>
      <th>position</th>
      <th>positionText</th>
      <th>positionOrder</th>
      <th>points</th>
      <th>...</th>
      <th>location</th>
      <th>country</th>
      <th>lat</th>
      <th>lng</th>
      <th>geometry</th>
      <th>dob</th>
      <th>driver_nat</th>
      <th>driver_name</th>
      <th>constr_name</th>
      <th>constr_nat</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>18</td>
      <td>1</td>
      <td>1</td>
      <td>22</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>10.0</td>
      <td>...</td>
      <td>Melbourne</td>
      <td>Australia</td>
      <td>-37.84970</td>
      <td>144.96800</td>
      <td>POINT (144.968 -37.8497)</td>
      <td>1985-01-07</td>
      <td>British</td>
      <td>Lewis Hamilton</td>
      <td>McLaren</td>
      <td>British</td>
    </tr>
    <tr>
      <th>1</th>
      <td>27</td>
      <td>19</td>
      <td>1</td>
      <td>1</td>
      <td>22</td>
      <td>9</td>
      <td>5</td>
      <td>5</td>
      <td>5</td>
      <td>4.0</td>
      <td>...</td>
      <td>Kuala Lumpur</td>
      <td>Malaysia</td>
      <td>2.76083</td>
      <td>101.73800</td>
      <td>POINT (101.738 2.76083)</td>
      <td>1985-01-07</td>
      <td>British</td>
      <td>Lewis Hamilton</td>
      <td>McLaren</td>
      <td>British</td>
    </tr>
    <tr>
      <th>2</th>
      <td>57</td>
      <td>20</td>
      <td>1</td>
      <td>1</td>
      <td>22</td>
      <td>3</td>
      <td>13</td>
      <td>13</td>
      <td>13</td>
      <td>0.0</td>
      <td>...</td>
      <td>Sakhir</td>
      <td>Bahrain</td>
      <td>26.03250</td>
      <td>50.51060</td>
      <td>POINT (50.5106 26.0325)</td>
      <td>1985-01-07</td>
      <td>British</td>
      <td>Lewis Hamilton</td>
      <td>McLaren</td>
      <td>British</td>
    </tr>
    <tr>
      <th>3</th>
      <td>69</td>
      <td>21</td>
      <td>1</td>
      <td>1</td>
      <td>22</td>
      <td>5</td>
      <td>3</td>
      <td>3</td>
      <td>3</td>
      <td>6.0</td>
      <td>...</td>
      <td>Montmeló</td>
      <td>Spain</td>
      <td>41.57000</td>
      <td>2.26111</td>
      <td>POINT (2.26111 41.57)</td>
      <td>1985-01-07</td>
      <td>British</td>
      <td>Lewis Hamilton</td>
      <td>McLaren</td>
      <td>British</td>
    </tr>
    <tr>
      <th>4</th>
      <td>90</td>
      <td>22</td>
      <td>1</td>
      <td>1</td>
      <td>22</td>
      <td>3</td>
      <td>2</td>
      <td>2</td>
      <td>2</td>
      <td>8.0</td>
      <td>...</td>
      <td>Istanbul</td>
      <td>Turkey</td>
      <td>40.95170</td>
      <td>29.40500</td>
      <td>POINT (29.405 40.9517)</td>
      <td>1985-01-07</td>
      <td>British</td>
      <td>Lewis Hamilton</td>
      <td>McLaren</td>
      <td>British</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>26075</th>
      <td>23289</td>
      <td>964</td>
      <td>839</td>
      <td>209</td>
      <td>31</td>
      <td>20</td>
      <td>21</td>
      <td>21</td>
      <td>21</td>
      <td>0.0</td>
      <td>...</td>
      <td>Suzuka</td>
      <td>Japan</td>
      <td>34.84310</td>
      <td>136.54100</td>
      <td>POINT (136.541 34.8431)</td>
      <td>1996-09-17</td>
      <td>French</td>
      <td>Esteban Ocon</td>
      <td>Manor Marussia</td>
      <td>British</td>
    </tr>
    <tr>
      <th>26076</th>
      <td>23308</td>
      <td>965</td>
      <td>839</td>
      <td>209</td>
      <td>31</td>
      <td>22</td>
      <td>18</td>
      <td>18</td>
      <td>18</td>
      <td>0.0</td>
      <td>...</td>
      <td>Austin</td>
      <td>USA</td>
      <td>30.13280</td>
      <td>-97.64110</td>
      <td>POINT (-97.6411 30.1328)</td>
      <td>1996-09-17</td>
      <td>French</td>
      <td>Esteban Ocon</td>
      <td>Manor Marussia</td>
      <td>British</td>
    </tr>
    <tr>
      <th>26077</th>
      <td>23333</td>
      <td>966</td>
      <td>839</td>
      <td>209</td>
      <td>31</td>
      <td>20</td>
      <td>21</td>
      <td>21</td>
      <td>21</td>
      <td>0.0</td>
      <td>...</td>
      <td>Mexico City</td>
      <td>Mexico</td>
      <td>19.40420</td>
      <td>-99.09070</td>
      <td>POINT (-99.0907 19.4042)</td>
      <td>1996-09-17</td>
      <td>French</td>
      <td>Esteban Ocon</td>
      <td>Manor Marussia</td>
      <td>British</td>
    </tr>
    <tr>
      <th>26078</th>
      <td>23346</td>
      <td>967</td>
      <td>839</td>
      <td>209</td>
      <td>31</td>
      <td>22</td>
      <td>12</td>
      <td>12</td>
      <td>12</td>
      <td>0.0</td>
      <td>...</td>
      <td>São Paulo</td>
      <td>Brazil</td>
      <td>-23.70360</td>
      <td>-46.69970</td>
      <td>POINT (-46.6997 -23.7036)</td>
      <td>1996-09-17</td>
      <td>French</td>
      <td>Esteban Ocon</td>
      <td>Manor Marussia</td>
      <td>British</td>
    </tr>
    <tr>
      <th>26079</th>
      <td>23369</td>
      <td>968</td>
      <td>839</td>
      <td>209</td>
      <td>31</td>
      <td>20</td>
      <td>13</td>
      <td>13</td>
      <td>13</td>
      <td>0.0</td>
      <td>...</td>
      <td>Abu Dhabi</td>
      <td>UAE</td>
      <td>24.46720</td>
      <td>54.60310</td>
      <td>POINT (54.6031 24.4672)</td>
      <td>1996-09-17</td>
      <td>French</td>
      <td>Esteban Ocon</td>
      <td>Manor Marussia</td>
      <td>British</td>
    </tr>
  </tbody>
</table>
<p>26080 rows × 35 columns</p>
</div>



### Save our merged dataset to csv


```python
f1_summary.to_csv('f1_summary.csv', index=False, encoding='utf-8')
```

### Unveiling insights through visualization

The final step of a data project, the visualization, is often regarded as the fun part; the icing on the cake. This is true to an extent, but it is important to have a clear idea of what story you want to tell, and who your audience is. This will help you decide which metrics and types of visualization are appropriate.

My ultimate goal is to deploy a Streamlit app for F1 enthusiasts like my son (and I have to say more recently myself) and so when I had the idea for the project I was already visualizing how the app should look like. So, the whole process has basically been reverse engineering. 


```python
f1_stats = pd.read_csv('f1_summary.csv')
```


```python
# user selection to be changed
circuit = 'Albert Park Grand Prix Circuit'
```


```python
circuit_df = f1_stats[f1_stats['circuit_name'] == circuit]
circuit_df
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>resultId</th>
      <th>raceId</th>
      <th>driverId</th>
      <th>constructorId</th>
      <th>number</th>
      <th>grid</th>
      <th>position</th>
      <th>positionText</th>
      <th>positionOrder</th>
      <th>points</th>
      <th>...</th>
      <th>location</th>
      <th>country</th>
      <th>lat</th>
      <th>lng</th>
      <th>geometry</th>
      <th>dob</th>
      <th>driver_nat</th>
      <th>driver_name</th>
      <th>constr_name</th>
      <th>constr_nat</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>18</td>
      <td>1</td>
      <td>1</td>
      <td>22</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>10.0</td>
      <td>...</td>
      <td>Melbourne</td>
      <td>Australia</td>
      <td>-37.8497</td>
      <td>144.968</td>
      <td>POINT (144.968 -37.8497)</td>
      <td>1985-01-07</td>
      <td>British</td>
      <td>Lewis Hamilton</td>
      <td>McLaren</td>
      <td>British</td>
    </tr>
    <tr>
      <th>18</th>
      <td>371</td>
      <td>36</td>
      <td>1</td>
      <td>1</td>
      <td>2</td>
      <td>4</td>
      <td>3</td>
      <td>3</td>
      <td>3</td>
      <td>6.0</td>
      <td>...</td>
      <td>Melbourne</td>
      <td>Australia</td>
      <td>-37.8497</td>
      <td>144.968</td>
      <td>POINT (144.968 -37.8497)</td>
      <td>1985-01-07</td>
      <td>British</td>
      <td>Lewis Hamilton</td>
      <td>McLaren</td>
      <td>British</td>
    </tr>
    <tr>
      <th>35</th>
      <td>7573</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>18</td>
      <td>\N</td>
      <td>D</td>
      <td>20</td>
      <td>0.0</td>
      <td>...</td>
      <td>Melbourne</td>
      <td>Australia</td>
      <td>-37.8497</td>
      <td>144.968</td>
      <td>POINT (144.968 -37.8497)</td>
      <td>1985-01-07</td>
      <td>British</td>
      <td>Lewis Hamilton</td>
      <td>McLaren</td>
      <td>British</td>
    </tr>
    <tr>
      <th>53</th>
      <td>20352</td>
      <td>338</td>
      <td>1</td>
      <td>1</td>
      <td>2</td>
      <td>11</td>
      <td>6</td>
      <td>6</td>
      <td>6</td>
      <td>8.0</td>
      <td>...</td>
      <td>Melbourne</td>
      <td>Australia</td>
      <td>-37.8497</td>
      <td>144.968</td>
      <td>POINT (144.968 -37.8497)</td>
      <td>1985-01-07</td>
      <td>British</td>
      <td>Lewis Hamilton</td>
      <td>McLaren</td>
      <td>British</td>
    </tr>
    <tr>
      <th>71</th>
      <td>20780</td>
      <td>841</td>
      <td>1</td>
      <td>1</td>
      <td>3</td>
      <td>2</td>
      <td>2</td>
      <td>2</td>
      <td>2</td>
      <td>18.0</td>
      <td>...</td>
      <td>Melbourne</td>
      <td>Australia</td>
      <td>-37.8497</td>
      <td>144.968</td>
      <td>POINT (144.968 -37.8497)</td>
      <td>1985-01-07</td>
      <td>British</td>
      <td>Lewis Hamilton</td>
      <td>McLaren</td>
      <td>British</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>25960</th>
      <td>25460</td>
      <td>1076</td>
      <td>852</td>
      <td>213</td>
      <td>22</td>
      <td>13</td>
      <td>15</td>
      <td>15</td>
      <td>15</td>
      <td>0.0</td>
      <td>...</td>
      <td>Melbourne</td>
      <td>Australia</td>
      <td>-37.8497</td>
      <td>144.968</td>
      <td>POINT (144.968 -37.8497)</td>
      <td>2000-05-11</td>
      <td>Japanese</td>
      <td>Yuki Tsunoda</td>
      <td>AlphaTauri</td>
      <td>Italian</td>
    </tr>
    <tr>
      <th>25982</th>
      <td>25895</td>
      <td>1100</td>
      <td>852</td>
      <td>213</td>
      <td>22</td>
      <td>12</td>
      <td>10</td>
      <td>10</td>
      <td>10</td>
      <td>1.0</td>
      <td>...</td>
      <td>Melbourne</td>
      <td>Australia</td>
      <td>-37.8497</td>
      <td>144.968</td>
      <td>POINT (144.968 -37.8497)</td>
      <td>2000-05-11</td>
      <td>Japanese</td>
      <td>Yuki Tsunoda</td>
      <td>AlphaTauri</td>
      <td>Italian</td>
    </tr>
    <tr>
      <th>25994</th>
      <td>25900</td>
      <td>1100</td>
      <td>856</td>
      <td>213</td>
      <td>21</td>
      <td>15</td>
      <td>15</td>
      <td>15</td>
      <td>15</td>
      <td>0.0</td>
      <td>...</td>
      <td>Melbourne</td>
      <td>Australia</td>
      <td>-37.8497</td>
      <td>144.968</td>
      <td>POINT (144.968 -37.8497)</td>
      <td>1995-02-06</td>
      <td>Dutch</td>
      <td>Nyck de Vries</td>
      <td>AlphaTauri</td>
      <td>Italian</td>
    </tr>
    <tr>
      <th>26038</th>
      <td>22932</td>
      <td>948</td>
      <td>836</td>
      <td>209</td>
      <td>94</td>
      <td>21</td>
      <td>16</td>
      <td>16</td>
      <td>16</td>
      <td>0.0</td>
      <td>...</td>
      <td>Melbourne</td>
      <td>Australia</td>
      <td>-37.8497</td>
      <td>144.968</td>
      <td>POINT (144.968 -37.8497)</td>
      <td>1994-10-18</td>
      <td>German</td>
      <td>Pascal Wehrlein</td>
      <td>Manor Marussia</td>
      <td>British</td>
    </tr>
    <tr>
      <th>26059</th>
      <td>22935</td>
      <td>948</td>
      <td>837</td>
      <td>209</td>
      <td>88</td>
      <td>22</td>
      <td>\N</td>
      <td>R</td>
      <td>19</td>
      <td>0.0</td>
      <td>...</td>
      <td>Melbourne</td>
      <td>Australia</td>
      <td>-37.8497</td>
      <td>144.968</td>
      <td>POINT (144.968 -37.8497)</td>
      <td>1993-01-22</td>
      <td>Indonesian</td>
      <td>Rio Haryanto</td>
      <td>Manor Marussia</td>
      <td>British</td>
    </tr>
  </tbody>
</table>
<p>558 rows × 35 columns</p>
</div>



### Filter DataFrame for podium finishes


```python
circuit_df.columns
```




    Index(['resultId', 'raceId', 'driverId', 'constructorId', 'number', 'grid',
           'position', 'positionText', 'positionOrder', 'points', 'laps', 'time',
           'milliseconds', 'fastestLap', 'rank', 'fastestLapTime',
           'fastestLapSpeed', 'statusId', 'positionDiff', 'status', 'year',
           'circuitId', 'race_name', 'race_date', 'circuit_name', 'location',
           'country', 'lat', 'lng', 'geometry', 'dob', 'driver_nat', 'driver_name',
           'constr_name', 'constr_nat'],
          dtype='object')




```python
position = circuit_df[["driver_name", "positionOrder"]]
position
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>driver_name</th>
      <th>positionOrder</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Lewis Hamilton</td>
      <td>1</td>
    </tr>
    <tr>
      <th>18</th>
      <td>Lewis Hamilton</td>
      <td>3</td>
    </tr>
    <tr>
      <th>35</th>
      <td>Lewis Hamilton</td>
      <td>20</td>
    </tr>
    <tr>
      <th>53</th>
      <td>Lewis Hamilton</td>
      <td>6</td>
    </tr>
    <tr>
      <th>71</th>
      <td>Lewis Hamilton</td>
      <td>2</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>25960</th>
      <td>Yuki Tsunoda</td>
      <td>15</td>
    </tr>
    <tr>
      <th>25982</th>
      <td>Yuki Tsunoda</td>
      <td>10</td>
    </tr>
    <tr>
      <th>25994</th>
      <td>Nyck de Vries</td>
      <td>15</td>
    </tr>
    <tr>
      <th>26038</th>
      <td>Pascal Wehrlein</td>
      <td>16</td>
    </tr>
    <tr>
      <th>26059</th>
      <td>Rio Haryanto</td>
      <td>19</td>
    </tr>
  </tbody>
</table>
<p>558 rows × 2 columns</p>
</div>




```python
podium = position.query('positionOrder in [1,2,3]')     
podium
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>driver_name</th>
      <th>positionOrder</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Lewis Hamilton</td>
      <td>1</td>
    </tr>
    <tr>
      <th>18</th>
      <td>Lewis Hamilton</td>
      <td>3</td>
    </tr>
    <tr>
      <th>71</th>
      <td>Lewis Hamilton</td>
      <td>2</td>
    </tr>
    <tr>
      <th>90</th>
      <td>Lewis Hamilton</td>
      <td>3</td>
    </tr>
    <tr>
      <th>110</th>
      <td>Fernando Alonso</td>
      <td>2</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>11688</th>
      <td>Max Verstappen</td>
      <td>1</td>
    </tr>
    <tr>
      <th>12814</th>
      <td>Jenson Button</td>
      <td>1</td>
    </tr>
    <tr>
      <th>12831</th>
      <td>Rubens Barrichello</td>
      <td>2</td>
    </tr>
    <tr>
      <th>13457</th>
      <td>Jarno Trulli</td>
      <td>3</td>
    </tr>
    <tr>
      <th>13493</th>
      <td>Ralf Schumacher</td>
      <td>3</td>
    </tr>
  </tbody>
</table>
<p>78 rows × 2 columns</p>
</div>



### Create a pivot table for podium finishes


```python
podium_pivot = podium.pivot_table(index="driver_name", columns="positionOrder", aggfunc="size", fill_value=0)
podium_pivot
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>positionOrder</th>
      <th>1</th>
      <th>2</th>
      <th>3</th>
    </tr>
    <tr>
      <th>driver_name</th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>Charles Leclerc</th>
      <td>1</td>
      <td>0</td>
      <td>0</td>
    </tr>
    <tr>
      <th>Damon Hill</th>
      <td>1</td>
      <td>0</td>
      <td>0</td>
    </tr>
    <tr>
      <th>David Coulthard</th>
      <td>2</td>
      <td>2</td>
      <td>0</td>
    </tr>
    <tr>
      <th>Eddie Irvine</th>
      <td>1</td>
      <td>0</td>
      <td>1</td>
    </tr>
    <tr>
      <th>Felipe Massa</th>
      <td>0</td>
      <td>0</td>
      <td>1</td>
    </tr>
    <tr>
      <th>Fernando Alonso</th>
      <td>1</td>
      <td>2</td>
      <td>3</td>
    </tr>
    <tr>
      <th>George Russell</th>
      <td>0</td>
      <td>0</td>
      <td>1</td>
    </tr>
    <tr>
      <th>Giancarlo Fisichella</th>
      <td>1</td>
      <td>0</td>
      <td>0</td>
    </tr>
    <tr>
      <th>Heinz-Harald Frentzen</th>
      <td>0</td>
      <td>1</td>
      <td>1</td>
    </tr>
    <tr>
      <th>Jacques Villeneuve</th>
      <td>0</td>
      <td>1</td>
      <td>0</td>
    </tr>
    <tr>
      <th>Jarno Trulli</th>
      <td>0</td>
      <td>0</td>
      <td>1</td>
    </tr>
    <tr>
      <th>Jenson Button</th>
      <td>3</td>
      <td>0</td>
      <td>1</td>
    </tr>
    <tr>
      <th>Juan Pablo Montoya</th>
      <td>0</td>
      <td>2</td>
      <td>0</td>
    </tr>
    <tr>
      <th>Kevin Magnussen</th>
      <td>0</td>
      <td>1</td>
      <td>0</td>
    </tr>
    <tr>
      <th>Kimi Räikkönen</th>
      <td>2</td>
      <td>1</td>
      <td>3</td>
    </tr>
    <tr>
      <th>Lewis Hamilton</th>
      <td>2</td>
      <td>6</td>
      <td>2</td>
    </tr>
    <tr>
      <th>Max Verstappen</th>
      <td>1</td>
      <td>0</td>
      <td>1</td>
    </tr>
    <tr>
      <th>Michael Schumacher</th>
      <td>4</td>
      <td>1</td>
      <td>0</td>
    </tr>
    <tr>
      <th>Mika Häkkinen</th>
      <td>1</td>
      <td>0</td>
      <td>1</td>
    </tr>
    <tr>
      <th>Nick Heidfeld</th>
      <td>0</td>
      <td>1</td>
      <td>0</td>
    </tr>
    <tr>
      <th>Nico Rosberg</th>
      <td>2</td>
      <td>1</td>
      <td>1</td>
    </tr>
    <tr>
      <th>Ralf Schumacher</th>
      <td>0</td>
      <td>0</td>
      <td>3</td>
    </tr>
    <tr>
      <th>Robert Kubica</th>
      <td>0</td>
      <td>1</td>
      <td>0</td>
    </tr>
    <tr>
      <th>Rubens Barrichello</th>
      <td>0</td>
      <td>4</td>
      <td>1</td>
    </tr>
    <tr>
      <th>Sebastian Vettel</th>
      <td>3</td>
      <td>1</td>
      <td>3</td>
    </tr>
    <tr>
      <th>Sergio Pérez</th>
      <td>0</td>
      <td>1</td>
      <td>0</td>
    </tr>
    <tr>
      <th>Valtteri Bottas</th>
      <td>1</td>
      <td>0</td>
      <td>1</td>
    </tr>
    <tr>
      <th>Vitaly Petrov</th>
      <td>0</td>
      <td>0</td>
      <td>1</td>
    </tr>
  </tbody>
</table>
</div>



### Plotting a horizontal stacked bar chart of podium finishes


```python
# Import pandas and matplotlib
import pandas as pd
import matplotlib.pyplot as plt

# Define a list of colors for each positionOrder
colors = ["gold", "silver", "orange"]

# Plot the pivot table as a horizontal stacked barchart
podium_pivot.plot(kind="barh", stacked=True, color=colors)

# Set the title and axis labels
plt.title("Podium finishes by driver")
plt.xlabel("Finishes")
plt.ylabel("Driver name")

# Get the legend object and change its title
legend = plt.legend()
legend.set_title("Podium place")

# Show the plot
plt.show()
```


    
![png](f1_files/f1_93_0.png)
    



```python

```

### Filter DataFrame for safety incidents


```python
status = circuit_df[["driver_name", "year", "status"]]
status
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>driver_name</th>
      <th>year</th>
      <th>status</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Lewis Hamilton</td>
      <td>2008</td>
      <td>Finished</td>
    </tr>
    <tr>
      <th>18</th>
      <td>Lewis Hamilton</td>
      <td>2007</td>
      <td>Finished</td>
    </tr>
    <tr>
      <th>35</th>
      <td>Lewis Hamilton</td>
      <td>2009</td>
      <td>Disqualified</td>
    </tr>
    <tr>
      <th>53</th>
      <td>Lewis Hamilton</td>
      <td>2010</td>
      <td>Finished</td>
    </tr>
    <tr>
      <th>71</th>
      <td>Lewis Hamilton</td>
      <td>2011</td>
      <td>Finished</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>25960</th>
      <td>Yuki Tsunoda</td>
      <td>2022</td>
      <td>+1 Lap</td>
    </tr>
    <tr>
      <th>25982</th>
      <td>Yuki Tsunoda</td>
      <td>2023</td>
      <td>Finished</td>
    </tr>
    <tr>
      <th>25994</th>
      <td>Nyck de Vries</td>
      <td>2023</td>
      <td>Collision</td>
    </tr>
    <tr>
      <th>26038</th>
      <td>Pascal Wehrlein</td>
      <td>2016</td>
      <td>+1 Lap</td>
    </tr>
    <tr>
      <th>26059</th>
      <td>Rio Haryanto</td>
      <td>2016</td>
      <td>Mechanical</td>
    </tr>
  </tbody>
</table>
<p>558 rows × 3 columns</p>
</div>




```python
accident = status.query('status in ["Accident","Collision", "Spun off", "Fatal accident","Collision damage","Damage"]')
accident
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>driver_name</th>
      <th>year</th>
      <th>status</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>145</th>
      <td>Fernando Alonso</td>
      <td>2016</td>
      <td>Collision</td>
    </tr>
    <tr>
      <th>223</th>
      <td>Heikki Kovalainen</td>
      <td>2009</td>
      <td>Collision</td>
    </tr>
    <tr>
      <th>2086</th>
      <td>Nico Rosberg</td>
      <td>2011</td>
      <td>Collision</td>
    </tr>
    <tr>
      <th>2222</th>
      <td>Michael Schumacher</td>
      <td>2011</td>
      <td>Collision</td>
    </tr>
    <tr>
      <th>2509</th>
      <td>Robert Kubica</td>
      <td>2008</td>
      <td>Collision</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>15300</th>
      <td>Jos Verstappen</td>
      <td>1997</td>
      <td>Spun off</td>
    </tr>
    <tr>
      <th>15393</th>
      <td>Toranosuke Takagi</td>
      <td>1998</td>
      <td>Spun off</td>
    </tr>
    <tr>
      <th>21094</th>
      <td>Esteban Gutiérrez</td>
      <td>2016</td>
      <td>Collision</td>
    </tr>
    <tr>
      <th>21218</th>
      <td>Kevin Magnussen</td>
      <td>2023</td>
      <td>Accident</td>
    </tr>
    <tr>
      <th>25994</th>
      <td>Nyck de Vries</td>
      <td>2023</td>
      <td>Collision</td>
    </tr>
  </tbody>
</table>
<p>82 rows × 3 columns</p>
</div>



### Create a pivot table for safety incidents


```python
accident_pivot = accident.pivot_table(index="year", columns=["status"], aggfunc="size", fill_value=0)
accident_pivot
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>status</th>
      <th>Accident</th>
      <th>Collision</th>
      <th>Damage</th>
      <th>Spun off</th>
    </tr>
    <tr>
      <th>year</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>1996</th>
      <td>0</td>
      <td>3</td>
      <td>0</td>
      <td>0</td>
    </tr>
    <tr>
      <th>1997</th>
      <td>0</td>
      <td>3</td>
      <td>0</td>
      <td>2</td>
    </tr>
    <tr>
      <th>1998</th>
      <td>0</td>
      <td>2</td>
      <td>0</td>
      <td>1</td>
    </tr>
    <tr>
      <th>1999</th>
      <td>0</td>
      <td>3</td>
      <td>0</td>
      <td>1</td>
    </tr>
    <tr>
      <th>2000</th>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>1</td>
    </tr>
    <tr>
      <th>2001</th>
      <td>0</td>
      <td>2</td>
      <td>0</td>
      <td>1</td>
    </tr>
    <tr>
      <th>2002</th>
      <td>0</td>
      <td>8</td>
      <td>0</td>
      <td>1</td>
    </tr>
    <tr>
      <th>2003</th>
      <td>2</td>
      <td>0</td>
      <td>0</td>
      <td>1</td>
    </tr>
    <tr>
      <th>2005</th>
      <td>2</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
    </tr>
    <tr>
      <th>2006</th>
      <td>6</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
    </tr>
    <tr>
      <th>2007</th>
      <td>1</td>
      <td>2</td>
      <td>0</td>
      <td>0</td>
    </tr>
    <tr>
      <th>2008</th>
      <td>1</td>
      <td>7</td>
      <td>0</td>
      <td>0</td>
    </tr>
    <tr>
      <th>2009</th>
      <td>1</td>
      <td>3</td>
      <td>0</td>
      <td>1</td>
    </tr>
    <tr>
      <th>2010</th>
      <td>0</td>
      <td>3</td>
      <td>0</td>
      <td>1</td>
    </tr>
    <tr>
      <th>2011</th>
      <td>0</td>
      <td>2</td>
      <td>0</td>
      <td>0</td>
    </tr>
    <tr>
      <th>2012</th>
      <td>1</td>
      <td>4</td>
      <td>0</td>
      <td>0</td>
    </tr>
    <tr>
      <th>2013</th>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>1</td>
    </tr>
    <tr>
      <th>2014</th>
      <td>0</td>
      <td>2</td>
      <td>0</td>
      <td>0</td>
    </tr>
    <tr>
      <th>2015</th>
      <td>1</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
    </tr>
    <tr>
      <th>2016</th>
      <td>0</td>
      <td>2</td>
      <td>0</td>
      <td>0</td>
    </tr>
    <tr>
      <th>2019</th>
      <td>0</td>
      <td>0</td>
      <td>1</td>
      <td>0</td>
    </tr>
    <tr>
      <th>2022</th>
      <td>1</td>
      <td>0</td>
      <td>0</td>
      <td>1</td>
    </tr>
    <tr>
      <th>2023</th>
      <td>2</td>
      <td>5</td>
      <td>0</td>
      <td>0</td>
    </tr>
  </tbody>
</table>
</div>



### Plotting a horizontal stacked bar chart of safety incidents


```python
# Import pandas and matplotlib
import pandas as pd
import matplotlib.pyplot as plt

# Plot the pivot table as a horizontal stacked barchart
accident_pivot.plot(kind="barh", stacked=True)

# Set the title and axis labels
plt.title("Incidents by type")
plt.xlabel("Number of incidents")
plt.ylabel("Year")

# Get the legend object and change its title
legend = plt.legend()
legend.set_title("Incident")

# Show the plot
plt.show()
```


    
![png](f1_files/f1_101_0.png)
    


### Further safety metric - % of drivers finishing the race


```python
finishers = len(circuit_df[circuit_df['statusId'] == 1])
finishers
```




    215




```python
starters = len(circuit_df.grid)
starters
```




    558




```python
finish_per_cent = round(finishers / starters * 100,2)
finish_per_cent
```




    38.53




```python
circuit_df.columns
```




    Index(['resultId', 'raceId', 'driverId', 'constructorId', 'number', 'grid',
           'position', 'positionText', 'positionOrder', 'points', 'laps', 'time',
           'milliseconds', 'fastestLap', 'rank', 'fastestLapTime',
           'fastestLapSpeed', 'statusId', 'positionDiff', 'status', 'year',
           'circuitId', 'race_name', 'race_date', 'circuit_name', 'location',
           'country', 'lat', 'lng', 'geometry', 'dob', 'driver_nat', 'driver_name',
           'constr_name', 'constr_nat'],
          dtype='object')



### Fastest Lap

We do not have legitimate fastest lap times for all drivers. Sometimes NAN values are used - in this case `\N` has been used. 


```python
# Drop the missing values
circuit_df = circuit_df[circuit_df['fastestLapTime'] != '\\N']
```


```python
circuit_df
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>resultId</th>
      <th>raceId</th>
      <th>driverId</th>
      <th>constructorId</th>
      <th>number</th>
      <th>grid</th>
      <th>position</th>
      <th>positionText</th>
      <th>positionOrder</th>
      <th>points</th>
      <th>...</th>
      <th>location</th>
      <th>country</th>
      <th>lat</th>
      <th>lng</th>
      <th>geometry</th>
      <th>dob</th>
      <th>driver_nat</th>
      <th>driver_name</th>
      <th>constr_name</th>
      <th>constr_nat</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>18</td>
      <td>1</td>
      <td>1</td>
      <td>22</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>10.0</td>
      <td>...</td>
      <td>Melbourne</td>
      <td>Australia</td>
      <td>-37.8497</td>
      <td>144.968</td>
      <td>POINT (144.968 -37.8497)</td>
      <td>1985-01-07</td>
      <td>British</td>
      <td>Lewis Hamilton</td>
      <td>McLaren</td>
      <td>British</td>
    </tr>
    <tr>
      <th>18</th>
      <td>371</td>
      <td>36</td>
      <td>1</td>
      <td>1</td>
      <td>2</td>
      <td>4</td>
      <td>3</td>
      <td>3</td>
      <td>3</td>
      <td>6.0</td>
      <td>...</td>
      <td>Melbourne</td>
      <td>Australia</td>
      <td>-37.8497</td>
      <td>144.968</td>
      <td>POINT (144.968 -37.8497)</td>
      <td>1985-01-07</td>
      <td>British</td>
      <td>Lewis Hamilton</td>
      <td>McLaren</td>
      <td>British</td>
    </tr>
    <tr>
      <th>35</th>
      <td>7573</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>18</td>
      <td>\N</td>
      <td>D</td>
      <td>20</td>
      <td>0.0</td>
      <td>...</td>
      <td>Melbourne</td>
      <td>Australia</td>
      <td>-37.8497</td>
      <td>144.968</td>
      <td>POINT (144.968 -37.8497)</td>
      <td>1985-01-07</td>
      <td>British</td>
      <td>Lewis Hamilton</td>
      <td>McLaren</td>
      <td>British</td>
    </tr>
    <tr>
      <th>53</th>
      <td>20352</td>
      <td>338</td>
      <td>1</td>
      <td>1</td>
      <td>2</td>
      <td>11</td>
      <td>6</td>
      <td>6</td>
      <td>6</td>
      <td>8.0</td>
      <td>...</td>
      <td>Melbourne</td>
      <td>Australia</td>
      <td>-37.8497</td>
      <td>144.968</td>
      <td>POINT (144.968 -37.8497)</td>
      <td>1985-01-07</td>
      <td>British</td>
      <td>Lewis Hamilton</td>
      <td>McLaren</td>
      <td>British</td>
    </tr>
    <tr>
      <th>71</th>
      <td>20780</td>
      <td>841</td>
      <td>1</td>
      <td>1</td>
      <td>3</td>
      <td>2</td>
      <td>2</td>
      <td>2</td>
      <td>2</td>
      <td>18.0</td>
      <td>...</td>
      <td>Melbourne</td>
      <td>Australia</td>
      <td>-37.8497</td>
      <td>144.968</td>
      <td>POINT (144.968 -37.8497)</td>
      <td>1985-01-07</td>
      <td>British</td>
      <td>Lewis Hamilton</td>
      <td>McLaren</td>
      <td>British</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>25960</th>
      <td>25460</td>
      <td>1076</td>
      <td>852</td>
      <td>213</td>
      <td>22</td>
      <td>13</td>
      <td>15</td>
      <td>15</td>
      <td>15</td>
      <td>0.0</td>
      <td>...</td>
      <td>Melbourne</td>
      <td>Australia</td>
      <td>-37.8497</td>
      <td>144.968</td>
      <td>POINT (144.968 -37.8497)</td>
      <td>2000-05-11</td>
      <td>Japanese</td>
      <td>Yuki Tsunoda</td>
      <td>AlphaTauri</td>
      <td>Italian</td>
    </tr>
    <tr>
      <th>25982</th>
      <td>25895</td>
      <td>1100</td>
      <td>852</td>
      <td>213</td>
      <td>22</td>
      <td>12</td>
      <td>10</td>
      <td>10</td>
      <td>10</td>
      <td>1.0</td>
      <td>...</td>
      <td>Melbourne</td>
      <td>Australia</td>
      <td>-37.8497</td>
      <td>144.968</td>
      <td>POINT (144.968 -37.8497)</td>
      <td>2000-05-11</td>
      <td>Japanese</td>
      <td>Yuki Tsunoda</td>
      <td>AlphaTauri</td>
      <td>Italian</td>
    </tr>
    <tr>
      <th>25994</th>
      <td>25900</td>
      <td>1100</td>
      <td>856</td>
      <td>213</td>
      <td>21</td>
      <td>15</td>
      <td>15</td>
      <td>15</td>
      <td>15</td>
      <td>0.0</td>
      <td>...</td>
      <td>Melbourne</td>
      <td>Australia</td>
      <td>-37.8497</td>
      <td>144.968</td>
      <td>POINT (144.968 -37.8497)</td>
      <td>1995-02-06</td>
      <td>Dutch</td>
      <td>Nyck de Vries</td>
      <td>AlphaTauri</td>
      <td>Italian</td>
    </tr>
    <tr>
      <th>26038</th>
      <td>22932</td>
      <td>948</td>
      <td>836</td>
      <td>209</td>
      <td>94</td>
      <td>21</td>
      <td>16</td>
      <td>16</td>
      <td>16</td>
      <td>0.0</td>
      <td>...</td>
      <td>Melbourne</td>
      <td>Australia</td>
      <td>-37.8497</td>
      <td>144.968</td>
      <td>POINT (144.968 -37.8497)</td>
      <td>1994-10-18</td>
      <td>German</td>
      <td>Pascal Wehrlein</td>
      <td>Manor Marussia</td>
      <td>British</td>
    </tr>
    <tr>
      <th>26059</th>
      <td>22935</td>
      <td>948</td>
      <td>837</td>
      <td>209</td>
      <td>88</td>
      <td>22</td>
      <td>\N</td>
      <td>R</td>
      <td>19</td>
      <td>0.0</td>
      <td>...</td>
      <td>Melbourne</td>
      <td>Australia</td>
      <td>-37.8497</td>
      <td>144.968</td>
      <td>POINT (144.968 -37.8497)</td>
      <td>1993-01-22</td>
      <td>Indonesian</td>
      <td>Rio Haryanto</td>
      <td>Manor Marussia</td>
      <td>British</td>
    </tr>
  </tbody>
</table>
<p>352 rows × 35 columns</p>
</div>




```python
fastest_lap = circuit_df[["driver_name", "fastestLapTime", "race_date"]]
```


```python
# Group by fastestLapTime
fastest_lap = fastest_lap.groupby(by=["fastestLapTime"]).min()
fastest_lap
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>driver_name</th>
      <th>race_date</th>
    </tr>
    <tr>
      <th>fastestLapTime</th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>1:20.235</th>
      <td>Sergio Pérez</td>
      <td>2023-04-02</td>
    </tr>
    <tr>
      <th>1:20.260</th>
      <td>Charles Leclerc</td>
      <td>2022-04-10</td>
    </tr>
    <tr>
      <th>1:20.342</th>
      <td>Max Verstappen</td>
      <td>2023-04-02</td>
    </tr>
    <tr>
      <th>1:20.467</th>
      <td>Carlos Sainz</td>
      <td>2023-04-02</td>
    </tr>
    <tr>
      <th>1:20.476</th>
      <td>Fernando Alonso</td>
      <td>2023-04-02</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>1:41.351</th>
      <td>Christian Klien</td>
      <td>2006-04-02</td>
    </tr>
    <tr>
      <th>1:43.132</th>
      <td>Vitaly Petrov</td>
      <td>2010-03-28</td>
    </tr>
    <tr>
      <th>1:43.223</th>
      <td>Adrian Sutil</td>
      <td>2010-03-28</td>
    </tr>
    <tr>
      <th>1:49.947</th>
      <td>Lewis Hamilton</td>
      <td>2014-03-16</td>
    </tr>
    <tr>
      <th>2:27.276</th>
      <td>Bruno Senna</td>
      <td>2010-03-28</td>
    </tr>
  </tbody>
</table>
<p>345 rows × 2 columns</p>
</div>




```python
# get fastest lap time from the first value [0] of the index [fastestLapTime]
fastest_lap_time = fastest_lap.index[0]
fastest_lap_time
```




    '1:20.235'




```python
# get fastest driver from the first value [0] of driver_name
fastest_lap_driver = fastest_lap.driver_name[0]
fastest_lap_driver
```




    'Sergio Pérez'




```python
# get date of fastest lap from the first value [0] of race_date
fastest_lap_date = fastest_lap.race_date[0]
fastest_lap_date
```




    '2023-04-02'



### Streamlit

Now that we have decided on the features of interest and how we would like to present them it's time to pull everything together and create a working app that users can interact with.

Streamlit is a Python library that allows you to create web-apps and dashboard by just writing Python code. It provides you with a wide range of UI widgets and layouts that can be used to build user- interfaces. Your streamlit app is just a regular Python file with a `.py` extension.

Streamlit is fantastic because it allows you to preview your app in the browser, as you code it. Any changes you make are immediately appplied to the app in real time, which is invaluable for debugging. You can slowy build, test, debug, build test ensuring there are no unexpected glitches on final deployment. 

### Installation and Setting up the Environment

You need to install the streamlit package to create the app. We will be using Anaconda to install streamlit and related packages on your machine. Please review the [Anaconda Installation Guide]((https://courses.spatialthoughts.com/python-foundation.html#installation-and-setting-up-the-environment)) for step-by-step instructions.

1. Once you have installed Anaconda, open Anaconda Prompt or a Terminal and run the following commands :


```python
conda update --all
conda create --name streamlit -y
conda activate streamlit
```

2. Now your environment is ready. We will install the required packages. First install geopandas :


```python
conda install -c conda-forge geopandas  -y
```

3. Next we will install streamlit and leafmap.


```python
pip install streamlit streamlit-folium leafmap
```

4. After the installation is done, run the following command :


```python
streamlit hello
```

A new browser tab will open and display the streamlit Hello app.

Your installation is now complete. You can close the terminal window to stop the streamlit server.

### Creating our Streamlit app

All the hard work has been done, it's the last lap and the chequered flag is in sight! 

To view a working prototype locally in our browser, simply navigate to the directory where the `app.py` file is and run the following from the command line :


```python
streamlit run app.py
```

`app.py`


```python
import streamlit as st
import geopandas as gpd
from geojson import Feature, Point, FeatureCollection
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
import leafmap.foliumap as leafmap
import altair as alt

# cosmetic config
st.set_page_config(page_title='Dashboard', layout='wide')

st.title('Formula One - Data Pitstop - 1950 to 2023')

st.sidebar.title('About')
st.sidebar.info('F1 stats and maps for 35 race circuits')

# Add a dropdown to enable user to choose type of basemap  
base_map = st.selectbox('Select a basemap', ['OpenStreetMap', 'Stamen Terrain', 'Stamen Toner'])

# specify file path and filenames
data_url = 'https://raw.githubusercontent.com/Stephen137/formula_one/main/data/'
geojson_file = 'f1-circuits.geojson'
csv_file = 'f1_summary.csv'

@st.cache_data
# custom function to load in our spatial data
def read_gdf(url):
    gdf = gpd.read_file(url)
    return gdf

@st.cache_data
# custom function to load circuit statistics
def read_csv(url):
    df = pd.read_csv(url)
    return df

# Process start
data_load_state = st.text('Engines revving...')  

# Concatenate file names
geojson_url = data_url + geojson_file
f1_summary_url = data_url + csv_file

# create circuits GeoDataFrame
circuits_gdf = read_gdf(geojson_url)

# create non spatial F1 stats DataFrame
f1_stats_df = read_csv(f1_summary_url)

# Process complete
data_load_state.text('Lights out and away we go ... !')

# add a dropdown for circuit selection and filter dataset based on user choice
circuits = circuits_gdf.sort_values(by="Name").Name.unique()
# circuits = f1_stats_df.sort_values(by="circuit_name").circuit_name.unique()
circuit = st.sidebar.selectbox('Select a Circuit', circuits)

circuit_df = f1_stats_df[f1_stats_df['circuit_name'] == circuit]

# create a map
m = leafmap.Map(
    layers_control=True,
    draw_control=False,
    measure_control=False,
    fullscreen_control=False,
    tiles=base_map,
    hover_style={"fillOpacity": 0.7},
)

# add circuits layer
m.add_gdf(
    gdf=circuits_gdf,
    zoom_to_layer=False,
    layer_name='circuits',
    info_mode='on_hover',
    style={'color': '#7fcdbb', 'fillOpacity': 0.3, 'weight': 0.5},
    hover_style={"fillOpacity": 0.7},
    )

# filter for user circuit selection
selected_gdf = circuits_gdf[circuits_gdf['Name'] == circuit]

# add the user selected circuits layer
m.add_gdf(
    gdf=selected_gdf,
    layer_name='selected',
    zoom_to_layer=True,
    info_mode='on_hover',
    style={'color': 'red', 'fill': None, 'weight': 2},
    hover_style={"fillOpacity": 0.7},
 )

m_streamlit = m.to_streamlit(600, 600)

# Drop invalid values 
circuit_df = circuit_df[circuit_df['fastestLapTime'] != '\\N']

# filter for fastest lap
fastest_lap = circuit_df[["driver_name", "fastestLapTime", "race_date"]]
fastest_lap = fastest_lap.groupby(by=["fastestLapTime"]).min()

# fastest lap details based on user circuit selection
# deal with potential errors by allowing our code to continue to be executed
try:
    fastest_lap_time = fastest_lap.index[0]
except IndexError:
    pass
try:
    fastest_lap_driver = fastest_lap.driver_name[0]
except IndexError:
    pass
try:
    fastest_lap_date = fastest_lap.race_date[0]
except:
    pass

try: 
    st.text(f'The fastest lap time recorded at {circuit} is {fastest_lap_time}, clocked by {fastest_lap_driver} on {fastest_lap_date}.')
except NameError:
    pass
st.text(f'The bar chart below provides a breakdown of the champagne soaked podium finishers : ')

# add a stacked horizontal bar chart to show podium finishes for selected circuit
position = circuit_df[["driver_name", "positionOrder"]]
podium = position.query('positionOrder in [1,2,3]') 

podium_pivot = podium.pivot_table(index="driver_name", columns="positionOrder", aggfunc="size", fill_value=0)

st.bar_chart(podium_pivot)


st.text(f'The bar chart below shows the number of major incidents by year : ')

# add a stacked horizontal bar chart to show serious accidents for selected circuit
status = circuit_df[["driver_name", "year", "status"]]
accident = status.query('status in ["Accident","Collision", "Spun off", "Fatal accident","Collision damage","Damage"]')

accident_pivot = accident.pivot_table(index="year", columns="status", aggfunc="size", fill_value=0)

st.bar_chart(accident_pivot)

# Percentage of drivers who finish a race for chosen circuit
starters = len(circuit_df.grid)
finishers = len(circuit_df[circuit_df['statusId'] == 1])

# deal with potential errors by allowing our code to continue to be executed
try:
    finish_per_cent = round(finishers / starters * 100,2)
except ZeroDivisionError:
    pass
try:
    st.text(f'From a total of {starters} drivers who have started a race at {circuit}, {finish_per_cent} % completed the race.')
except ZeroDivisionError:
    pass
except NameError:
    pass
```

### Publishing our app with Streamlit Cloud

Streamlit provides free hosting for your streamlit apps. In this section, we will now learn how to deploy an app to Streamlit cloud and configure it correctly.

### Upload the app to GitHub

To run your app on Streamlit Cloud, you need to upload your app to GitHub. Streamlit supports both private and public repositories. 

### Add App dependencies

If your app needs a third-party Python package, you need to add it in a separate file called `requirements.txt`. The packages listed in the file will be installed on Streamlit Cloud before running the app.

For our app, we have created the `requirements.txt` file with the following content and uploaded it to GitHub in the same directory as the `app.py`.

`requirements.txt`


```python
streamlit
folium
streamlit-folium
```

You may also specify other dependencies for your app. Learn more at [App dependencies](https://docs.streamlit.io/streamlit-cloud/get-started/deploy-an-app/app-dependencies) documentation.

### Replace Sensitive Data with Secrets

It is not a good practice to store API keys or passwords in the code as it can be seen by others and can be misused. Streamlit provides an easy way for [Secrets Management](https://docs.streamlit.io/streamlit-cloud/get-started/deploy-an-app/connect-to-data-sources/secrets-management). You can store any `key=value` pairs in a separate location and access it in the app using `st.secrets`.

While doing local development, you create a folder named `.streamlit` in the app directory and store any `key=value` pairs in a file named `secrets.toml`. For example, if you want to store the ORS API Key, you can create a new file `secrets.toml` in the `.streamlit directory` with the following content. (Replace <your api key> with the actual key).


```python
'ORS_API_KEY' = '<your api key>'
```

### Deploy your App

Now you are ready to deploy your app to Streamlit Cloud.

1. Visit [Streamlit Cloud](https://streamlit.io/cloud) and sign-in. If you do not have an account, you can click *Sign-up* and create a new account. Once logged-in, click the *New app* button.

2. Click Paste GitHub URL and paste the URL to your streamlit app.py file. For my example, this is `f1_app.py` but you should select you own.  Next, click *Advanced settings* :

3. This dialog allows you to store your private information required by your apps, such as API keys, username/password for your database, etc. For my example I don't require to enter anything, however if your app does require an API key, then you need to enter the API Key in the following format and replace with your actual API key. Click Save.


```python
'ORS_API_KEY' = '<your key>'
```

4. You are now ready to deploy the app. Click *Deploy!* 

5. Your app will now be deployed and will be accessible via the provided URL. You can visit your Dashboard to manage the app once it is deployed.

The app is now live! Visit the [F1 app](https://f1apppy-6oapycqh3zokdnwcvxjbqi.streamlit.app/) to see it in action!

### Improvements

The app is very basic and only reflects static data at the moment (up to and including the Belgian Grand Prix held on 31 July 2023) The visualizations within the map are the default `st.bar_chart` and colours etc are not customized. A checklist of improvements are included below:

- keep the app up to date by using a workflow orchestration tool such as [Prefect](https://www.prefect.io/) to schedule runs (say every two weeks) using a cron scheduler

- increase the number of circuit maps

- customize the visualizations within the app to look more like the ones produced in this Jupyter NoteBook using matplotlib
