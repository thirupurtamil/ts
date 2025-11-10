from rest_framework import serializers
from .models import NiftyExpiry, NiftyOptionSnapshot

class NiftyOptionSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = NiftyOptionSnapshot
        fields = '__all__'


class NiftyExpirySerializer(serializers.ModelSerializer):
    snapshots = NiftyOptionSnapshotSerializer(many=True, read_only=True)

    class Meta:
        model = NiftyExpiry
        fields = ['id', 'expiry_date', 'created_at', 'snapshots']