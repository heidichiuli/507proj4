import unittest
from proj4 import *


class TestDataAccess(unittest.TestCase):

    def test_Billboard_webscrape(self):
        #1. test Billboard webscrape
        scrape_inst = get_billboard_data()
        self.assertEqual(len(scrape_inst), 100)

    def test_Ticketmaster_Json(self):
        #2. test Json data retrieval
        api_inst = get_events_data('Ed Sheeran')
        self.assertEqual(len(api_inst['_embedded']['events']), 10)


class TestClass(unittest.TestCase):

    def testConstructor(self):
        #3. test class constructor
        a = TopArtists('Cardi B', 1, 6, 1, 39)
        self.assertEqual(a.artist, 'Cardi B')
        #4. test class constructor
        self.assertEqual(a.current, 1)


    def testString(self):
        #5. test class string
        a = TopArtists('Cardi B', 1, 6, 1, 39)
        self.assertEqual(a.__str__(), 'Cardi B, 1, 6, 1, 39')


class TestDatabase(unittest.TestCase):

    def test_artist_table(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql = 'SELECT Artist FROM Artists'
        results = cur.execute(sql)
        result_list = results.fetchall()
        artist_list=[]
        for tuple in result_list:
            artist_list.append(tuple[0])

        #6. test length of Artist Database
        self.assertEqual(len(result_list), 100)
        #7. test artist in Database
        self.assertIn('The Weeknd', artist_list)

    def test_events_table(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql = 'SELECT EventId FROM Events'
        results = cur.execute(sql)
        results_list = results.fetchall()

        #8. test length of Events Database
        self.assertEqual(len(results_list), 720)

        sql = '''
            SELECT Events.Artist, COUNT(Events.EventId)
            FROM Events
            WHERE Events.Artist = 'The Weeknd'
        '''
        results = cur.execute(sql)
        results_list = results.fetchall()

        #9. test event sql count in Database
        self.assertEqual(len(results_list), 1)

        sql = 'SELECT Artist FROM Events'
        results = cur.execute(sql)
        results_list = results.fetchall()
        artist_list = []
        for tuple in results_list:
            artist_list.append(tuple[0])

        #10. test lookup_events - filter out 2 artists with no concert/no referential integrity
        self.assertNotIn('Cardi B', artist_list)

class TestDataProcessing(unittest.TestCase):

    def test_commands(self):
        results = process_command('artists')
        #11 test process_command('artists') - bar chart
        self.assertEqual(results[0], '21 Savage')

    def test_bar(self):
        #12 test bar graph
        try:
            bar_venue('CA')
        except:
            self.fail()

    def test_map(self):
        #13 test map
        try:
            map_concerts(3)
        except:
            self.fail()

        #14 test map command, artist with no events
        self.assertEqual(map_concerts(1), 0)

    def test_pie(self):
        #15 test pie chart
        try:
            pie_genre('US')
        except:
            self.fail()





unittest.main()
