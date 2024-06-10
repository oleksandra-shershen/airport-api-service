from django.db import transaction
from rest_framework import serializers

from airport.models import (
    Airport,
    Airplane,
    AirplaneType,
    Route,
    Ticket,
    Order,
    Flight,
    Crew,
)


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ("id", "name", "closest_big_city")


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = ("id", "name")


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name", "full_name")


class AirplaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = ("id", "name", "rows", "seats_in_row", "airplane_type", "capacity", "image")


class AirplaneImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = ("id", "image")


class AirplaneListSerializer(serializers.ModelSerializer):
    airplane_type = serializers.CharField(source="airplane_type.name")

    class Meta:
        model = Airplane
        fields = ("id", "name", "airplane_type", "capacity")


class AirplaneDetailSerializer(serializers.ModelSerializer):
    airplane_type = AirplaneTypeSerializer()

    class Meta:
        model = Airplane
        fields = ("id", "name", "rows", "seats_in_row", "capacity", "airplane_type", "image")


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = (
            "id",
            "source",
            "destination",
            "distance"
        )


class RouteListSerializer(RouteSerializer):
    source = serializers.StringRelatedField()
    destination = serializers.StringRelatedField()


class RouteDetailSerializer(RouteSerializer):
    destination = AirportSerializer()
    source = AirportSerializer()


class FlightSerializer(serializers.ModelSerializer):
    departure_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M")
    arrival_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M")

    class Meta:
        model = Flight
        fields = ("id", "route", "airplane", "departure_time", "arrival_time", "crews")


class FlightListSerializer(FlightSerializer):
    route = serializers.StringRelatedField()
    airplane = serializers.StringRelatedField()
    departure_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M")
    arrival_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M")

    class Meta:
        model = Flight
        fields = ("id", "route", "airplane", "departure_time", "arrival_time")


class FlightDetailSerializer(serializers.ModelSerializer):
    route = RouteDetailSerializer()
    airplane = AirplaneDetailSerializer()
    crews = CrewSerializer(many=True)
    departure_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M")
    arrival_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M")

    class Meta:
        model = Flight
        fields = ("id", "route", "airplane", "departure_time", "arrival_time", "crews")
