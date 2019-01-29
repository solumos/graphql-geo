from __future__ import annotations
from typing import List

import sqlalchemy as sa
import geoalchemy2 as ga

from geo.models.base import Base


DEFAULT_LIMIT = 10
DEFAULT_INTERSECT_BUFFER = 100

# type definitions for annotations
Point = sa.sql.expression.Cast
STDistance = ga.functions.ST_Distance
STIntersects = ga.functions.ST_Intersects


class Place(Base):
    """
    A simple model denoting a "place", which could be any geographical entity
    with a name, coordinates, and a polygon.
    """

    __tablename__ = "place"

    id = sa.Column(sa.BigInteger, primary_key=True)
    name = sa.Column(sa.String, nullable=False)
    latitude = sa.Column(sa.Float, nullable=False)
    longitude = sa.Column(sa.Float, nullable=False)
    center_raw = sa.Column("center", ga.Geography("POINT"), nullable=False)
    center = sa.orm.column_property(ga.functions.ST_AsGeoJSON(center_raw))
    polygon_raw = sa.Column("polygon", ga.Geography("POLYGON"))
    polygon = sa.orm.column_property(ga.functions.ST_AsGeoJSON(polygon_raw))
    popularity = sa.Column(sa.BigInteger, nullable=False, default=0)

    def __init__(self, *args, **kwargs) -> None:
        super(Place, self).__init__(*args, **kwargs)
        self.__distance = None

    @property
    def distance(self) -> float:
        return self.__distance

    @distance.setter
    def distance(self, value: float) -> None:
        self.__distance = value

    @staticmethod
    def _format_point_postgis(lat: float, lon: float) -> Point:
        """
        Format the lat/lon as a PostGIS Point Geography, to be used in
        SQLAlchemy queries.

        :param lat: latitude value
        :param lon: longitude value

        :return: the lat/lon pair in SQL representation, a PostGIS POINT cast
            to a PostGIS Geography type
        """
        return sa.cast("POINT({} {})".format(lon, lat), ga.types.Geography)

    @staticmethod
    def _set_distances(results: List[(Place, float)]) -> List[Place]:
        """
        For a list of tuples containing Place + distance, set each provided
        distance value onthe distance property of the corresponding Place.

        :param results: Place + distance pairs from our queries
        :return: Places, with the `distance` property set
        """
        all_entities = []

        for entity, distance in results:
            entity.distance = distance
            all_entities.append(entity)

        return all_entities

    @classmethod
    def _postgis_distance(cls, point: Point) -> STDistance:
        """
        For a given Point, return the geoalchemy ST_Distance instance
        denoting the distance that a point resides from a Place's center.
        Compiling the ST_Intersects function to raw SQL is handled by SQLAlchemy.

        :param point:
        :return: the resulting geoalchemy STDistance class instance
        """
        return ga.functions.ST_Distance(cls.center_raw, point)

    @classmethod
    def _postgis_buffered_intersect(
        cls, point: Point, buffer: int = DEFAULT_INTERSECT_BUFFER
    ) -> STIntersects:
        """
        For a given Point, return the geoalchemy ST_Intersects instance
        denoting the filter for checking whether a buffered point intersects
        a Place's polygon. Compiling the ST_Intersects function to raw SQL
        is handled by SQLAlchemy.
    
        :param point: a PostGIS-formatted point
        :param buffer: the buffer around the point
        :return: the resulting geoalchemy STIntersects class instance
        """
        return ga.functions.ST_Intersects(
            Place.polygon_raw, ga.functions.ST_Buffer(point, DEFAULT_INTERSECT_BUFFER)
        )

    @classmethod
    def nearby(cls, lat: float, lon: float, radius: float) -> List[Place]:
        """
        Find places nearest to the given lat/lon, limited to the provided
        radius in meters.

        :param lat: latitude
        :param lon: longitude
        :param radius:
        :return:
        """
        formatted_point = cls._format_point_postgis(lat, lon)
        distance = cls._postgis_distance(formatted_point)
        query = (
            cls.query.with_entities(cls, distance)
            .filter(distance < radius)
            .order_by(distance)
            .limit(DEFAULT_LIMIT)
            .all()
        )
        return cls._set_distances(query)

    @classmethod
    def reverse_geolocate(
        cls, lat: float, lon: float, weighted: bool = False
    ) -> List[Place]:
        """
        Given the provided latitude and longitude, find a set of candidate
        places that the lat/lon may be associated with.

        :param lat: latitude
        :param lon: longitude
        :param weighted: denotes whether the query should be weighted by popularity
        :return: candidate Places
        """
        formatted_point = cls._format_point_postgis(lat, lon)
        distance = cls._postgis_distance(formatted_point)

        ordering = (distance + 1) / (Place.popularity + 1) if weighted else distance

        query = (
            cls.query.with_entities(cls, distance)
            .filter(cls._postgis_buffered_intersect(formatted_point))
            .order_by(ordering)
            .limit(DEFAULT_LIMIT)
            .all()
        )
        return cls._set_distances(query)
