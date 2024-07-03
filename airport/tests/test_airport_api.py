from datetime import datetime
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from airport.models import Airport, Route, AirplaneType, Airplane, Flight
from airport.serializers import AirplaneListSerializer, FlightListSerializer

AIRPLANE_URL = reverse("airport:airplane-list")
FLIGHT_URL = reverse("airport:flight-list")


def sample_airplane_type(**params):
    defaults = {
        "name": "Boeing"
    }
    defaults.update(params)
    return AirplaneType.objects.create(**defaults)


def sample_airplane(**params):
    airplane_type = sample_airplane_type()
    defaults = {
        "name": "Boeing 747",
        "rows": 30,
        "seats_in_row": 6,
        "airplane_type": airplane_type
    }
    defaults.update(params)
    return Airplane.objects.create(**defaults)


def sample_airport(**params):
    defaults = {
        "name": "Test Airport",
        "closest_big_city": "Test City"
    }
    defaults.update(params)
    return Airport.objects.create(**defaults)


def sample_route(**params):
    airport = sample_airport()
    defaults = {
        "source": airport,
        "destination": airport,
        "distance": 1000
    }
    defaults.update(params)
    return Route.objects.create(**defaults)


def sample_flight(**params):
    route = sample_route()
    airplane = sample_airplane()
    defaults = {
        "route": route,
        "airplane": airplane,
        "departure_time": datetime(2024, 6, 11, 10, 0),
        "arrival_time": datetime(2024, 6, 11, 14, 0)
    }
    defaults.update(params)
    return Flight.objects.create(**defaults)


class UnauthenticatedAirplaneApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(AIRPLANE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedAirplaneApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass"
        )
        self.client.force_authenticate(self.user)

    def test_list_airplanes(self):
        sample_airplane()
        sample_airplane()

        res = self.client.get(AIRPLANE_URL)

        airplanes = Airplane.objects.order_by("id")
        serializer = AirplaneListSerializer(airplanes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_filter_airplanes_by_type(self):
        airplane_type = sample_airplane_type(name="Airbus")
        airplane1 = sample_airplane()
        airplane2 = sample_airplane(name="Airbus A320", airplane_type=airplane_type)

        res = self.client.get(AIRPLANE_URL, {"airplane_type": airplane_type.id})

        serializer1 = AirplaneListSerializer(airplane1)
        serializer2 = AirplaneListSerializer(airplane2)

        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer1.data, res.data)

    def test_filter_airplanes_by_name(self):
        airplane1 = sample_airplane(name="Boeing 747")
        airplane2 = sample_airplane(name="Airbus A320")

        res = self.client.get(AIRPLANE_URL, {"name": "Boeing"})

        serializer1 = AirplaneListSerializer(airplane1)
        serializer2 = AirplaneListSerializer(airplane2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)


class AuthenticatedFlightApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass"
        )
        self.client.force_authenticate(self.user)

    def test_list_flights(self):
        flight1 = sample_flight()
        flight2 = sample_flight()

        res = self.client.get(FLIGHT_URL)

        flights = Flight.objects.order_by("id")
        serializer = FlightListSerializer(flights, many=True)

        expected_data = serializer.data
        for flight in expected_data:
            flight['tickets_available'] = 180  # 30 rows * 6 seats_in_row = 180

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, expected_data)

    def test_filter_flights_by_route(self):
        route1 = sample_route()
        route2 = sample_route()
        flight1 = sample_flight(route=route1)
        flight2 = sample_flight(route=route2)

        res = self.client.get(FLIGHT_URL, {"route": route1.id})

        serializer1 = FlightListSerializer(flight1)
        serializer1_data = serializer1.data
        serializer1_data['tickets_available'] = 180

        self.assertIn(serializer1_data, res.data)

    def test_filter_flights_by_airplane(self):
        airplane1 = sample_airplane()
        airplane2 = sample_airplane()
        flight1 = sample_flight(airplane=airplane1)
        flight2 = sample_flight(airplane=airplane2)

        res = self.client.get(FLIGHT_URL, {"airplane": airplane1.id})

        serializer1 = FlightListSerializer(flight1)
        serializer1_data = serializer1.data
        serializer1_data['tickets_available'] = 180

        self.assertIn(serializer1_data, res.data)

    def test_filter_flights_by_departure_time(self):
        flight1 = sample_flight(departure_time=datetime(2024, 6, 11, 10, 0))
        flight2 = sample_flight(departure_time=datetime(2024, 6, 12, 10, 0))

        res = self.client.get(FLIGHT_URL, {"departure_time": "2024-06-11"})

        serializer1 = FlightListSerializer(flight1)
        serializer1_data = serializer1.data
        serializer1_data['tickets_available'] = 180

        self.assertIn(serializer1_data, res.data)
