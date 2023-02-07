from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializer import PetSerializer
from groups.models import Group
from traits.models import Trait
from django.forms.models import model_to_dict
from pets.models import Pet
from traits.serializer import TraitSerializer
from rest_framework.pagination import PageNumberPagination


class PetView(APIView, PageNumberPagination):
    def post(self, request):

        pet_data = PetSerializer(data=request.data)
        pet_data.is_valid()
        if pet_data.is_valid() is False:
            return Response(pet_data.errors, 400)
        group = pet_data.validated_data["group"]
        traits = pet_data.validated_data["traits"]
        trait_list = []
        pet_group = ""
        for trait in traits:
            try:
                found_trait = Trait.objects.get(name__contains=trait["name"])
                trait_list.append(model_to_dict(found_trait))
            except Trait.DoesNotExist:
                new_trait = Trait.objects.create(**trait)
                trait_list.append(model_to_dict(new_trait))

        try:
            pet_group = Group.objects.get(
                scientific_name__exact=group["scientific_name"]
            )
            pet_data.validated_data["group"] = model_to_dict(pet_group)
        except Group.DoesNotExist:
            pet_group = Group.objects.create(**group)
            pet_data.validated_data["group"] = model_to_dict(pet_group)

        try:
            Pet.objects.get(name__contains=pet_data.validated_data["name"])
            return Response("Pet Already Exists", 400)

        except Pet.DoesNotExist:
            pet = Pet.objects.create(
                name=pet_data.validated_data["name"],
                group=pet_group,
                weight=pet_data.validated_data["weight"],
                age=pet_data.validated_data["age"],
                sex=pet_data.validated_data["sex"],
            )
            for trait in trait_list:
                found_trait = Trait.objects.get(id=trait["id"])
                pet.traits.add(found_trait)
            pet.save()

            pet_data.validated_data["traits"] = trait_list
            pet_id = model_to_dict(pet)
            teste = Pet.objects.get(id=pet_id["id"])
            serializer = PetSerializer(teste)
        return Response(serializer.data, 201)

    def get(self, request):
        pets = Pet.objects.all()
        result_page = self.paginate_queryset(pets, request, view=self)
        serializer = PetSerializer(result_page, many=True)
        return self.get_paginated_response(serializer.data)
