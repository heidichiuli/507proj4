import sqlite3
import requests
import csv
import json
from bs4 import BeautifulSoup
import plotly.plotly as py
import plotly.graph_objs as go
from plotly.graph_objs import *
import secrets

#---------SECRETS FILE
API_KEY = secrets.CONSUMER_KEY

#----------HELP TEXT
def load_help_text():
    with open('help.txt') as f:
        return f.read()

#----------CACHE FILES
CACHE_FNAME = 'proj4_cache.json'
try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    CACHE_DICTION = json.loads(cache_contents)
    cache_file.close()
except:
    CACHE_DICTION = {}

def get_unique_key(url):
    return url

def discovery_params_unique_combo(baseurl, params):
    alphabetized_keys = sorted(params.keys())
    res = []
    for k in alphabetized_keys:
        res.append("{}={}".format(k, params[k]))
    #print(baseurl + '&'.join(res))
    return baseurl + '&'.join(res)

def make_request_using_cache(url):
    unique_ident = get_unique_key(url)

    if unique_ident in CACHE_DICTION:
        print("Getting cached data...")
        return CACHE_DICTION[unique_ident]

    else:
        print("Making a request for new data...")
        resp = requests.get(url)
        CACHE_DICTION[unique_ident] = resp.text
        dumped_json_cache = json.dumps(CACHE_DICTION)
        fw = open(CACHE_FNAME, 'w')
        fw.write(dumped_json_cache)
        fw.close()
        return CACHE_DICTION[unique_ident]

#----------CLASS
class TopArtists:
    def __init__(self, artist_name, current_week, last_week, peak_ranking, weeks_on_chart):
        self.artist = artist_name
        self.current = current_week
        self.last = last_week
        self.peak = peak_ranking
        self.weeks = weeks_on_chart

    def __str__(self):
        return '{}, {}, {}, {}, {}'.format(self.artist, self.current, self.last, self.peak, self.weeks)

#-----------REQUEST DATA, RETURN BILLBOARD ARTIST CLASS STR.
def get_billboard_data():
    billboard_list = []
    baseurl = 'https://www.billboard.com/charts/artist-100'
    page_text = make_request_using_cache(baseurl)
    page_soup = BeautifulSoup(page_text, 'html.parser')

    chart_data = page_soup.find(class_ = 'chart-data js-chart-data')
    chart_item = chart_data.find_all(class_ = 'chart-row')

    for item in chart_item:
        main_info = item.find(class_ = 'chart-row__main-display')
        current_week = main_info.find(class_ = 'chart-row__current-week').string
        artist_name = main_info.find(class_ = 'chart-row__artist').string.strip()
        artist_name = artist_name.replace(',', '')

        secondary_info = item.find(class_ = 'chart-row__secondary')
        last_week_info = secondary_info.find(class_ = 'chart-row__last-week')
        last_week = last_week_info.find(class_ = 'chart-row__value').string
        peak_info = secondary_info.find(class_ = 'chart-row__top-spot')
        peak_ranking = peak_info.find(class_ = 'chart-row__value').string

        weeks_info = secondary_info.find(class_ = 'chart-row__weeks-on-chart')
        weeks_on_chart = weeks_info.find(class_ = 'chart-row__value').string

        billboard_instance = TopArtists(artist_name, current_week, last_week, peak_ranking, weeks_on_chart)
        billboard_list.append(billboard_instance.__str__())

    return billboard_list

#-----------REQUEST DATA, RETURN TICKETMASTER JSON TEXT
def get_events_data(artist_name):
    events_list = []
    baseurl = 'https://app.ticketmaster.com/discovery/v2/events.json?'
    parameters = {}
    parameters['keyword'] = artist_name.replace(' ', '')
    parameters['classificationName'] = 'music'
    parameters['size'] = 50 #default is 20 events
    parameters['apikey'] = API_KEY
    unique_url = discovery_params_unique_combo(baseurl, parameters)
    event_request = make_request_using_cache(unique_url)
    json_text = json.loads(event_request)
    return json_text


#----------INITIALIZE DATABASE
def init_db(db_name):
    try:
        conn = sqlite3.connect(db_name)
        cur = conn.cursor()
    except Exception as e:
        print(e)

    try:
        simple_check = 'SELECT * FROM "Artists"'
        cur.execute(simple_check)

        user_input = input('Table exists.  Delete? yes/no: ')
        if user_input == 'yes':
            statement = 'DROP TABLE IF EXISTS "Artists";'
            statement2 = 'DROP TABLE IF EXISTS "Events";'
            cur.execute(statement)
            cur.execute(statement2)
            conn.commit()

            my_dict = {}

            statement = '''
                CREATE TABLE 'Artists' (
                    'Artist' TEXT PRIMARY KEY,
                    'CurrentRank' INTEGER NOT NULL,
                    'LastWeek' INTEGER,
                    'PeakRanking' INTEGER NOT NULL,
                    'WeeksOnChart' INTEGER
                );
            '''

            statement2 = '''
                CREATE TABLE 'Events' (
                'EventId' INTEGER PRIMARY KEY AUTOINCREMENT,
                'EventName' TEXT NOT NULL,
                'Artist' TEXT NOT NULL,
                'OtherArtist' TEXT,
                'Genre' TEXT,
                'Date' TEXT,
                'Venue' TEXT,
                'City' TEXT,
                'State' TEXT,
                'Country' TEXT,
                'Longitude' NUMBER,
                'Latitude' NUMBER,
                FOREIGN KEY('Artist') REFERENCES 'Artists'('Artist')
                );
            '''

            cur.execute(statement)
            cur.execute(statement2)
            conn.commit()
            conn.close()
        else:
            pass
    except:
        statement = '''
            CREATE TABLE 'Artists' (
                'Artist' TEXT PRIMARY KEY,
                'CurrentRank' INTEGER NOT NULL,
                'LastWeek' INTEGER,
                'PeakRanking' INTEGER NOT NULL,
                'WeeksOnChart' INTEGER
            );
        '''
        statement2 = '''
            CREATE TABLE 'Events' (
            'EventId' INTEGER PRIMARY KEY AUTOINCREMENT,
            'EventName' TEXT NOT NULL,
            'Artist' TEXT NOT NULL,
            'OtherArtist' TEXT,
            'Genre' TEXT,
            'Date' TEXT,
            'Venue' TEXT,
            'City' TEXT,
            'State' TEXT,
            'Country' TEXT,
            'Longitude' NUMBER,
            'Latitude' NUMBER,
            FOREIGN KEY('Artist') REFERENCES 'Artists'('Artist')
            );
        '''
        cur.execute(statement)
        cur.execute(statement2)
        conn.commit()
        conn.close()

#----------MAKE ARTIST TABLE
def insert_artist(csv_file): #artists table
    conn = sqlite3.connect('proj4.sqlite')
    cur = conn.cursor()

    for row in csv_file:
        insertion = (row[0], row[1], row[2], row[3], row[4])
        statement = '''
            INSERT INTO 'Artists'
            VALUES (?, ?, ?, ?, ?)
        '''
        cur.execute(statement, insertion)
    conn.commit()
    conn.close()

#----------MAKE EVENTS TABLE
def insert_events(item): #events table
    conn = sqlite3.connect('proj4.sqlite')
    cur = conn.cursor()

    event_name = item['name']
    try:
        artist = item['_embedded']['attractions'][0]['name']
    except:
        artist = 'N/A'
    try:
        artist2 = item['_embedded']['attractions'][1]['name']
    except:
        artist2 = 'N/A'
    try:
        genre = item['classifications'][0]['genre']['name']
    except:
        genre = 'N/A'
    try:
        date = item['dates']['start']['localDate']
    except:
        date = 'N/A'
    try:
        venue = item['_embedded']['venues'][0]['name']
    except:
        venue = 'N/A'
    try:
        city = item['_embedded']['venues'][0]['city']['name']
    except:
        city = 'N/A'
    try:
        state = item['_embedded']['venues'][0]['state']['stateCode']
    except:
        state = 'N/A'
    try:
        country = item['_embedded']['venues'][0]['country']['countryCode']
    except:
        country = 'N/A'
    try:
        longitude = item['_embedded']['venues'][0]['location']['longitude']
    except:
        longitude = 'N/A'
    try:
        latitude = item['_embedded']['venues'][0]['location']['latitude']
    except:
        latitude = 'N/A'

    insertion = (event_name, artist, artist2, genre, date, venue, city, state, country, longitude, latitude)
    statement = '''
        INSERT INTO 'Events'
        VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
    cur.execute(statement, insertion)
    conn.commit()
    conn.close()

#------ USING BILLBOARD -> LOOK UP TICKETMASTER DATA
def lookup_events(number):
    for artist in artist_list[:number]: #selects number of Billboard artists
        print(artist[0]) #billboard artist name
        t_search = get_events_data(artist[0]) #find Ticketmaster events for each artist
        if t_search['page']['totalElements'] == 0:
            print('no results for this artist')
        else:
            for item in t_search['_embedded']['events']: #parse through each event
                try:
                    t_artist = item['_embedded']['attractions'][0]['name']
                    if  t_artist == artist[0]: #check for referential integrity (billboard primary = ticketmaster foreign)
                        insert_events(item)
                except:
                    continue


#----- COMMAND: MAKE BAR GRAPH1 - Artist and # Events
def bar_artists(): # artist and event count
    conn = sqlite3.connect('proj4.sqlite')
    cur = conn.cursor()

    statement = '''
        SELECT Events.Artist, COUNT(Events.EventId)
        FROM Events
        GROUP BY Events.Artist
        '''
    result = cur.execute(statement).fetchall()

    artist_list = []
    events_list = []
    for tuple in result:
        artist_list.append(tuple[0])
        events_list.append(tuple[1])

    data = [go.Bar(
            x = artist_list,
            y = events_list
    )]

    layout = go.Layout(
        title = 'Billboard Top100 Artists and 2018 Concerts'
    )

    fig = go.Figure(data=data, layout=layout)
    py.plot(fig, file_name = 'artist_event_count')
    conn.commit()
    conn.close()
    return artist_list


#----- COMMAND: MAKE BAR GRAPH2 - Popular Venue in a State
def bar_venue(state_abbr):
    state_abbr = state_abbr.upper()

    conn=sqlite3.connect('proj4.sqlite')
    cur = conn.cursor()

    statement = '''
        SELECT Venue, State, COUNT(EventId)
        FROM Events
        '''
    statement += 'WHERE Events.State="' + state_abbr + '" GROUP BY Events.Venue'
    result = cur.execute(statement).fetchall()

    venue_list = []
    states_list = []
    events_list = []
    for tuple in result:
        venue_list.append(tuple[0])
        states_list.append(tuple[1])
        events_list.append(tuple[2])

    if state_abbr in states_list:
        data = [go.Bar(
                x = venue_list,
                y = events_list
        )]

        layout = go.Layout(
            title = 'Concert Venues in ' + state_abbr
        )

        fig = go.Figure(data=data, layout=layout)
        py.plot(fig, filename='venue_event_count')
        conn.commit()
        conn.close()
        return venue_list
    else:
        return print('Sorry, state not found, try again!')


#-------COMMAND: PLOT MAP OF EVENTS
def map_concerts(artist_rank):
    conn = sqlite3.connect('proj4.sqlite')
    cur = conn.cursor()

    statement = 'SELECT Artists.CurrentRank, Events.Artist, Events.Longitude, Events.Latitude '
    statement += 'FROM Events LEFT JOIN Artists ON Events.Artist=Artists.Artist '
    statement +='WHERE Artists.CurrentRank=' + str(artist_rank)
    result = cur.execute(statement).fetchall()

    if len(result) == 0:
        print('Sorry, no events available.')
        return len(result)
    else:
        lon_vals = []
        lat_vals = []
        artist_vals = []
        counter = 0
        for tuple in result:
            if tuple[2] != 0 and tuple[3] != 0:
                lon_vals.append(tuple[2])
                lat_vals.append(tuple[3])
                artist_vals.append(tuple[1])
            else:
                counter+=1
                continue
        print('....plotting concerts')
        print(str(counter) + ' events had invalid long/lat information')

        data = [ dict(
            type = 'scattergeo',
            lon = lon_vals,
            lat = lat_vals,
            text = artist_vals,
            mode = 'markers',
            marker = dict(
                size = 8,
                symbol = 'star',
                color = 'red'
            ))]

        layout = dict(
            title = artist_vals[0] + ' Concerts <br>(Hover for artist)',
            geo = dict(
            scope = 'world',
            projection = dict(type = 'equirectangular'),
            showland = True,
            landcolor = "rgb(250, 250, 250)",
            subunitcolor = "rgb(100, 217, 217)",
            countrycolor = "rgb(217, 100, 217)",
            counterywidth = 3,
            subunitwidth = 3
            ),
        )

        fig = dict(data=data, layout=layout)
        py.plot(fig, validate=False, filename = 'artist events')


#-------COMMAND: PIE CHART OF GENRE - genre distribution in a country
def pie_genre(country_code):
    country_code = country_code.upper()

    conn = sqlite3.connect('proj4.sqlite')
    cur = conn.cursor()

    statement = 'SELECT Country, Genre, COUNT(Genre) FROM Events '
    statement += 'WHERE Country="' + country_code + '" '
    statement += 'GROUP BY Country, Genre'
    result = cur.execute(statement).fetchall()

    country_list = []
    genre_list = []
    count_list = []
    for tuple in result:
        country_list.append(tuple[0])
        genre_list.append(tuple[1])
        count_list.append(tuple[2])

    labels = genre_list
    values = count_list

    if country_code in country_list:
        fig = {
            'data':[{'values': values, 'labels': labels, 'type': 'pie'}],
            'layout':{'title': 'Music Genre Distribtion in ' + country_code}
        }
        py.plot(fig, filename='pie_genre')
        # trace = go.Pie(labels=labels, values=values)
        # py.plot([trace], filename='genre_pie_chart')
    else:
        return print('Sorry, country not found, try again!')


def process_command(response):

    response_split = response.split(' ')
    first_word = response_split[0]

    if len(response_split) == 1:
        #----------INVOKE BAR_ARTISTS - artists event count
        if first_word == 'artists':
            return bar_artists()
        else:
            print('Command not recognized: ' + response)
    elif len(response_split) == 2:
        second_word = response_split[1]
        #----------INVOKE MAP_CONCERTS - map events for artist by billboard rank
        if first_word == 'events':
            if '=' in second_word:
                param = second_word.split('=')
                if param[0] == 'rank':
                    if int(param[1]) in range(1,101):
                        map_concerts(param[1])
                    else:
                        print('Command not recognized: ' + response)
                else:
                    print('Command not recognized: ' + response)
            else:
                print('Command not recognized: ' + response)
        #----------INVOKE BAR_VENUE - venues in state
        elif first_word == 'venues':
            if '=' in second_word:
                param = second_word.split('=')
                if param[0] == 'state':
                    bar_venue(param[1])
                else:
                    print('Command not recognized: ' + response)
            else:
                print('Command not recognized: ' + response)
        #----------INVOKE PIE_GENRE - distribution of genre per country
        elif first_word == 'genre':
            if '=' in second_word:
                param = second_word.split('=')
                if param[0] == 'country':
                    pie_genre(param[1])
                else:
                    print('Command not recognized: ' + response)
            else:
                print('Command not recognized: ' + response)
        else:
            print('Command not recognized: ' + response)
    else:
        print('Command not recognized: ' + response)


#----------INTERACTIVE
def interactive_prompt():
    help_text = load_help_text()
    response = ''
    while response != 'exit':
        response = input('\nEnter a command: ')
        if response == 'help':
            print(help_text)
        elif response == 'exit':
            print('bye!')
        else:
            process_command(response)


########################### INVOKE FUNCTIONS #####################

#------ CREATE BILLBOARD CSV FILE USING CLASS
csv_file = open('billboard.csv', 'w')
fieldnames = 'Artist, CurrentRanking, LastWeek, PeakRanking, WeeksOnChart\n'
csv_file.write(fieldnames)
for item in get_billboard_data():
    csv_file.write(item + '\n')
csv_file.close()
#
# #------- CREATE DATABASE
DBNAME = 'proj4.sqlite'
init_db(DBNAME)
# #_______ CREATE ARTIST TABLE
f = open('billboard.csv')
artist_data = csv.reader(f)
artist_list = list(artist_data)
del(artist_list[0])
insert_artist(artist_list)
#----------CREATE TICKETMASTER TABLE
lookup_events(100)



if __name__=="__main__":
    interactive_prompt()
