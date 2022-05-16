from rest_framework import serializers


class ProductSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=250)
    slug = serializers.SlugField(max_length=250)
    description = serializers.CharField()
    price = serializers.IntegerField()
    stock = serializers.IntegerField()
    available = serializers.BooleanField(default=True)
    created = serializers.DateTimeField()
    updated = serializers.DateTimeField()
