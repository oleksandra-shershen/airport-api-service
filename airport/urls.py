from django.urls import path, include
from rest_framework import routers

from airport.views import AirportViewSet, AirplaneViewSet

router = routers.DefaultRouter()
router.register("airports", AirportViewSet)
router.register("airplanes", AirplaneViewSet)

urlpatterns = [path("", include(router.urls))]

app_name = "airport"
