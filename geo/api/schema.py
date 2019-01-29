import json

import graphene

from geo.models.place import Place as PlaceModel
from graphene.types.generic import GenericScalar


class GeoJSON(GenericScalar):
    """
    This class is mostly for documentation purposes - there's no GeoJSON validation
    and we don't allow querying against the GeoJSON fields.
    """

    pass


class Place(graphene.ObjectType):
    """
    The API representation of a "Place"
    """

    id = graphene.Int(description="the place ID in the geo backend")
    name = graphene.String(description="human-readable place name")
    center = GeoJSON(description="center of this place in geojson format")
    polygon = GeoJSON(description="polygon representing this place in geojson format")
    popularity = graphene.Int(description="integer denoting a the place's popularity")
    distance = graphene.Float(
        description="the distance in meters from the place (for queries where a lat/long is provided)"
    )

    def resolve_polygon(self, info):
        return json.loads(self.polygon)

    def resolve_center(self, info):
        return json.loads(self.center)


class Query(graphene.ObjectType):
    """
    The root query object
    """

    nearby = graphene.List(
        Place,
        lat=graphene.Float(
            description="latitude to be used for the query", required=True
        ),
        lon=graphene.Float(
            description="longitude to be used for the query", required=True
        ),
        radius=graphene.Float(
            description="radius in meters by which to limit search results",
            default_value=500,
        ),
    )
    reverse_geolocate = graphene.List(
        Place,
        lat=graphene.Float(
            description="latitude to be used for the query", required=True
        ),
        lon=graphene.Float(
            description="longitude to be used for the query", required=True
        ),
        weighted=graphene.Boolean(
            description="denotes whether the query should weight the results via their popularity while reverse-geolocating",
            default_value=False,
        ),
    )

    def resolve_nearby(self, info, **kwargs):
        query = PlaceModel.nearby(**kwargs)
        return query

    def resolve_reverse_geolocate(self, info, **kwargs):
        query = PlaceModel.reverse_geolocate(**kwargs)
        return query


schema = graphene.Schema(query=Query)
