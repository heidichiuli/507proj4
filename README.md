# 507proj4

This project extracts Billboard Top100 Artists from the Billboard website, extracts artist name from the list to use to search for concert information on the Ticketmaster website through Ticketmaster Discovery API.  The code is compatible with Python 3.

INSTALL / IMPORT

packages are listed in requirements.txt


DATA SOURCES

1. Billboard website url: https://www.billboard.com/charts/artist-100
2. Ticketmaster Discovery API documentation: https://developer.ticketmaster.com/products-and-docs/apis/discovery-api/v2/


TICKETMASTER API KEYS

1. Register for an API on https://developer-acct.ticketmaster.com/user/register
2. Save CONSUMER_KEY and CONSUMER_SECRET in a separate file in your working directory (containing proj4.py) as secrets.py


PLOTLY INSTALLATION

1. To install Plotly's python package, use the package manager pip inside your terminal:

$ pip3 install plotly
OR
$pip install plotly

2. Set your credentials in the terminal by replacing username and api-key to your own:

$ python3
$>>>import plotly $>>>plotly.tools.set_credentials_file(username='DemoAccount', api_key='lr1c37zw81')


CODE STRUCTURE:

1. Create Database 'proj4.sqlite'
2. Scrape current Billboard Top100 Artist Website, create CSV file and insert into Artists Table
3. Using Artist name from CSV, lookup_events() function uses artist name as keyword search term on Ticketmaster Discovery API (** artists who do not have concerts in 2018 or do not match exactly to keywords are omitted**)
4. Event information from Ticketmaster is used to create Events Table in the database

COMMAND OPTIONS:

You will be prompted to enter in commands on the command line in your terminal.  4 options are available, type help for the list of options:

1. artists
  creates bar graph, visualizes Billboard 100 Artists and their respective number of events in 2018
2. venues state=  
  creates bar graph, visualizes number of events per venue per state (use state abbreviation)
3. events rank=
  creates map, visualizes event locations held by artist specified by their Billboard rank
4. genre country=
  creates pie chart, visualizes genre distribution specified by country (use country abbreviation)
