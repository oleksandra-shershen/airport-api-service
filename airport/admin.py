from django.contrib import admin

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

admin.site.register(Airport)
admin.site.register(AirplaneType)
admin.site.register(Route)
admin.site.register(Order)
admin.site.register(Ticket)
admin.site.register(Flight)
admin.site.register(Crew)
admin.site.register(Airplane)

