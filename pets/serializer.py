from rest_framework import serializers
from groups.serializer import GroupSerializer
from traits.serializer import TraitSerializer
from pets.models import Sex


class PetSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=50)
    age = serializers.IntegerField()
    weight = serializers.FloatField()
    sex = serializers.CharField(default=Sex.DEFAULT)
    group = GroupSerializer()
    traits = TraitSerializer(many=True)


class UpdatePetSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=50, required=False)
    age = serializers.IntegerField(required=False)
    weight = serializers.FloatField(required=False)
    sex = serializers.CharField(default=Sex.DEFAULT, required=False)
    group = GroupSerializer(required=False)
    traits = TraitSerializer(many=True, required=False)
