import os
import unittest
import urllib

import geo.app as geo_app
from geo.models.place import Place
from geo.models.base import Session


class GraphQLTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        geo_app.app.testing = True
        cls.app = geo_app.app.test_client()

        with geo_app.app.app_context():
            geo_app.init_db(os.getenv("POSTGRES_URL"))

        Place.query.delete()

        session = Session()
        session.add(
            Place(
                id=1,
                name="Upper West Side",
                latitude=40.787751,
                longitude=-73.975883,
                center_raw="POINT(-73.975883 40.787751)",
                polygon_raw="POLYGON((-73.996142 40.769848,-73.996142 40.805802,-73.958354 40.805802,-73.958354 40.769848,-73.996142 40.769848))",
                popularity=1000,
            )
        )
        session.add(
            Place(
                id=2,
                name="Central Park",
                latitude=40.764356,
                longitude=-73.973057,
                center_raw="POINT(-73.973057 40.764356)",
                polygon_raw="POLYGON((-73.973057 40.764356, -73.981898 40.768094, -73.958209 40.800621, -73.949282 40.796853, -73.973057 40.764356))",
                popularity=10000,
            )
        )
        session.commit()

    @classmethod
    def tearDownClass(cls):
        Place.query.delete()

    def test_border_query(self):
        query = """
        {
            reverseGeolocate(lat: 40.778513, lon: -73.974493){
                id
                name
                popularity
                distance
            }
        }
        """
        query_string = urllib.parse.urlencode({"query": query})

        response = self.app.get("/graphql", query_string=query_string)
        results = response.json.get("data", {}).get("reverseGeolocate")

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].get("id"), 1)
        self.assertEqual(results[1].get("id"), 2)
        self.assertEqual(len(results[1]), 4)

    def test_border_query_weighted(self):
        query = """
        {
            reverseGeolocate(lat: 40.778513, lon: -73.974493, weighted: true){
                id
                name
                popularity
                distance
            }
        }
        """
        query_string = urllib.parse.urlencode({"query": query})

        response = self.app.get("/graphql", query_string=query_string)
        results = response.json.get("data", {}).get("reverseGeolocate")

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].get("id"), 2)
        self.assertEqual(results[1].get("id"), 1)

    def test_border_query_nearby_no_radius(self):
        query = """
        {
            nearby(lat: 40.778513, lon: -73.974493, radius: 0){
                id
                name
                popularity
                distance
            }
        }
        """
        query_string = urllib.parse.urlencode({"query": query})

        response = self.app.get("/graphql", query_string=query_string)
        results = response.json.get("data", {}).get("nearby")

        self.assertEqual(len(results), 0)

    def test_border_query_nearby_one_match(self):
        query = """
        {
            nearby(lat: 40.778513, lon: -73.974493, radius: 1500){
                id
                name
                popularity
                distance
            }
        }
        """
        query_string = urllib.parse.urlencode({"query": query})

        response = self.app.get("/graphql", query_string=query_string)
        results = response.json.get("data", {}).get("nearby")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].get("id"), 1)

    def test_border_query_nearby_both_match(self):
        query = """
        {
            nearby(lat: 40.778513, lon: -73.974493, radius: 2500){
                id
                name
                popularity
                distance
            }
        }
        """
        query_string = urllib.parse.urlencode({"query": query})

        response = self.app.get("/graphql", query_string=query_string)
        results = response.json.get("data", {}).get("nearby")

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].get("id"), 1)


if __name__ == "__main__":
    unittest.main()
