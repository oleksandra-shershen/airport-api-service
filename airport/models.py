import os
import uuid

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.template.defaultfilters import slugify


class Airport(models.Model):
    name = models.CharField(max_length=255)
    closest_big_city = models.CharField(max_length=255)

    def __str__(self) -> str:
        return f"{self.name} ({self.closest_big_city})"


class Route(models.Model):
    source = models.ForeignKey(
        Airport, on_delete=models.CASCADE, related_name="source_routes"
    )
    destination = models.ForeignKey(
        Airport, on_delete=models.CASCADE, related_name="destination_routes"
    )
    distance = models.IntegerField()

    def __str__(self) -> str:
        return f"{self.source} to {self.destination} ({self.distance} km)"


class AirplaneType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.name


def airplane_image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.name)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads/airplanes/", filename)


class Airplane(models.Model):
    name = models.CharField(max_length=255)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()
    airplane_type = models.ForeignKey(
        AirplaneType, on_delete=models.CASCADE, related_name="airplanes"
    )
    image = models.ImageField(null=True, upload_to=airplane_image_file_path)

    @property
    def capacity(self) -> int:
        return self.rows * self.seats_in_row

    def __str__(self) -> str:
        return self.name


class Crew(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self) -> str:
        return self.first_name + " " + self.last_name


class Flight(models.Model):
    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        related_name="flights"
    )
    airplane = models.ForeignKey(
        Airplane, on_delete=models.CASCADE, related_name="flights"
    )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    crews = models.ManyToManyField(Crew, blank=True, related_name="flights")

    def __str__(self) -> str:
        return (
            f"Flight {self.id} from {self.route.source} "
            f"to {self.route.destination} "
            f"on {self.departure_time.strftime('%Y-%m-%d %H:%M')}"
        )


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders"
    )

    def __str__(self):
        return str(self.created_at)

    class Meta:
        ordering = ["-created_at"]


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    flight = models.ForeignKey(
        Flight,
        on_delete=models.CASCADE,
        related_name="tickets"
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="tickets"
    )

    @staticmethod
    def validate_ticket(row, seat, airplane, error_to_raise):
        for ticket_attr_value, ticket_attr_name, airplane_attr_name in [
            (row, "row", "rows"),
            (seat, "seat", "seats_in_row"),
        ]:
            count_attrs = getattr(airplane, airplane_attr_name)
            if not (1 <= ticket_attr_value <= count_attrs):
                raise error_to_raise(
                    {
                        ticket_attr_name: f"{ticket_attr_name} number "
                                          f"must be in available range: "
                                          f"(1, {count_attrs})"
                    }
                )

    def clean(self):
        self.validate_ticket(
            self.row,
            self.seat,
            self.flight.airplane,
            ValidationError
        )

    def save(
            self,
            force_insert=False,
            force_update=False,
            using=None,
            update_fields=None
    ):
        self.full_clean()
        return super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return f"{str(self.flight)} (Row: {self.row}, Seat: {self.seat})"

    class Meta:
        unique_together = ("flight", "row", "seat")
        ordering = ["row", "seat"]
