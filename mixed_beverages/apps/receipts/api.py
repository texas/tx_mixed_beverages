from rest_framework import routers, serializers, viewsets

from . import models


class ReceiptSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Receipt


class ReceiptViewSet(viewsets.ModelViewSet):
    queryset = models.Receipt.objects.all()
    serializer_class = ReceiptSerializer


class BusinessSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Business


class BusinessViewSet(viewsets.ModelViewSet):
    queryset = models.Business.objects.all()
    serializer_class = BusinessSerializer


class ReceiptInlineSerializer(serializers.ModelSerializer):
    """
    Just get the data neccessary for charting tax over time.

    Include TABC permit # in case the location has changed.
    """

    class Meta:
        model = models.Receipt
        fields = ("total", "date", "tabc_permit")
        ordering = ("date",)


class LatestReceiptSerializer(serializers.ModelSerializer):
    """
    Just get the latest receipt so we know the name of this `Location`.
    """

    class Meta:
        model = models.Receipt
        exclude = ("location",)


class LocationSerializer(serializers.ModelSerializer):
    receipts = ReceiptInlineSerializer(many=True, read_only=True)

    class Meta:
        model = models.Location
        fields = ("id", "receipts", "data")


class LocationViewSet(viewsets.ModelViewSet):
    queryset = models.Location.objects.all().prefetch_related("receipts")
    serializer_class = LocationSerializer


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r"receipts", ReceiptViewSet)
router.register(r"business", BusinessViewSet)
router.register(r"location", LocationViewSet)
