from django.urls import path, include
from rest_framework import routers

from airport.views import AirportViewSet, AirplaneViewSet, AirplaneTypeViewSet, CrewViewSet

router = routers.DefaultRouter()
router.register("airports", AirportViewSet)
router.register("airplanes", AirplaneViewSet)
router.register("airplane_types", AirplaneTypeViewSet)
router.register("crews", CrewViewSet)

urlpatterns = [path("", include(router.urls))]

app_name = "airport"
