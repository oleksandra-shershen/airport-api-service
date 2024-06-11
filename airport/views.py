from datetime import datetime

from django.db.models import F, Count
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from airport.models import Airport, AirplaneType, Airplane, Crew, Route, Flight, Order
from airport.permissions import IsAdminOrIfAuthenticatedReadOnly
from airport.serializers import (
    AirportSerializer,
    AirplaneSerializer,
    AirplaneTypeSerializer,
    CrewSerializer,
    AirplaneListSerializer,
    AirplaneDetailSerializer,
    RouteListSerializer,
    RouteDetailSerializer,
    RouteSerializer,
    FlightListSerializer,
    FlightDetailSerializer,
    FlightSerializer,
    OrderSerializer,
    OrderListSerializer,
    AirplaneImageSerializer,
)

class AirportViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    @extend_schema(
        summary="Retrieve a list of airports",
        responses={
            200: OpenApiResponse(response=AirportSerializer, description="Successful response with a list of airports"),
            400: OpenApiResponse(description="Bad Request - Invalid query parameters"),
            401: OpenApiResponse(description="Unauthorized - Authentication credentials were not provided or are invalid"),
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class AirplaneTypeViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    @extend_schema(
        summary="Retrieve a list of airplane types",
        responses={
            200: OpenApiResponse(response=AirplaneTypeSerializer, description="Successful response with a list of airplane types"),
            400: OpenApiResponse(description="Bad Request - Invalid query parameters"),
            401: OpenApiResponse(description="Unauthorized - Authentication credentials were not provided or are invalid"),
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class CrewViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    @extend_schema(
        summary="Retrieve a list of crew members",
        responses={
            200: OpenApiResponse(response=CrewSerializer, description="Successful response with a list of crew members"),
            400: OpenApiResponse(description="Bad Request - Invalid query parameters"),
            401: OpenApiResponse(description="Unauthorized - Authentication credentials were not provided or are invalid"),
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all().select_related("airplane_type")
    serializer_class = AirplaneSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return AirplaneListSerializer
        elif self.action == "retrieve":
            return AirplaneDetailSerializer
        elif self.action == "upload-image":
            return AirplaneImageSerializer
        return AirplaneSerializer

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
        permission_classes=[IsAdminUser],
    )
    @extend_schema(
        summary="Upload an image for a specific airplane",
        responses={
            200: OpenApiResponse(response=AirplaneImageSerializer, description="Image uploaded successfully"),
            400: OpenApiResponse(description="Bad Request - Invalid image data"),
            401: OpenApiResponse(description="Unauthorized - Authentication credentials were not provided or are invalid"),
            403: OpenApiResponse(description="Forbidden - You do not have permission to perform this action"),
        }
    )
    def upload_image(self, request, pk=None):
        """Endpoint for uploading image to specific airplane"""
        airplane = self.get_object()
        serializer = self.get_serializer(airplane, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Retrieve a list of airplanes",
        responses={
            200: OpenApiResponse(response=AirplaneListSerializer, description="Successful response with a list of airplanes"),
            400: OpenApiResponse(description="Bad Request - Invalid query parameters"),
            401: OpenApiResponse(description="Unauthorized - Authentication credentials were not provided or are invalid"),
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all().select_related("source", "destination")
    serializer_class = RouteSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer
        elif self.action == "retrieve":
            return RouteDetailSerializer
        return RouteSerializer

    @extend_schema(
        summary="Retrieve a list of routes",
        responses={
            200: OpenApiResponse(response=RouteListSerializer, description="Successful response with a list of routes"),
            400: OpenApiResponse(description="Bad Request - Invalid query parameters"),
            401: OpenApiResponse(description="Unauthorized - Authentication credentials were not provided or are invalid"),
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class FlightViewSet(viewsets.ModelViewSet):
    queryset = (
        Flight.objects.all()
        .select_related("route", "airplane")
        .prefetch_related("crews")
        .annotate(
            tickets_available=(
                F("airplane__rows") * F("airplane__seats_in_row")
                - Count("tickets")
            )
        )
    )
    serializer_class = FlightSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer
        elif self.action == "retrieve":
            return FlightDetailSerializer
        return FlightSerializer

    @extend_schema(
        summary="Retrieve a list of flights",
        responses={
            200: OpenApiResponse(response=FlightListSerializer, description="Successful response with a list of flights"),
            400: OpenApiResponse(description="Bad Request - Invalid query parameters"),
            401: OpenApiResponse(description="Unauthorized - Authentication credentials were not provided or are invalid"),
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class OrderPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 100


class OrderViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Order.objects.prefetch_related(
        "tickets__flight__route", "tickets__flight__airplane"
    )
    serializer_class = OrderSerializer
    pagination_class = OrderPagination
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer

        return OrderSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @extend_schema(
        summary="Retrieve a list of orders",
        responses={
            200: OpenApiResponse(response=OrderListSerializer, description="Successful response with a list of orders"),
            400: OpenApiResponse(description="Bad Request - Invalid query parameters"),
            401: OpenApiResponse(description="Unauthorized - Authentication credentials were not provided or are invalid"),
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
