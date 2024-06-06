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


class AirplaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = ("id", "name")
