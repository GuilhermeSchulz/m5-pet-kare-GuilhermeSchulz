from django.shortcuts import render
from rest_framework.views import APIView, status
from rest_framework.response import Response
from .serializer import PetSerializer, UpdatePetSerializer
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
            return Response("Pet Already Exists", status.HTTP_400_BAD_REQUEST)

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
        return Response(serializer.data, status.HTTP_201_CREATED)

    def get(self, request):
        pet_trait = request.query_params.get("trait", None)
        if pet_trait is not None:
            pets_traits = Pet.objects.filter(traits__name__icontains=pet_trait)
            result_page = self.paginate_queryset(pets_traits, request, view=self)
            serializer = PetSerializer(result_page, many=True)
            return self.get_paginated_response(serializer.data)
        pets = Pet.objects.all()
        result_page = self.paginate_queryset(pets, request, view=self)
        serializer = PetSerializer(result_page, many=True)
        return self.get_paginated_response(serializer.data)


class PetSpecificView(APIView):
    def get(self, request, pet_id):
        try:
            pet = Pet.objects.get(pk=pet_id)
        except Pet.DoesNotExist:
            return Response({"detail": "Not found."}, status.HTTP_404_NOT_FOUND)
        pet_return = PetSerializer(pet)
        return Response(pet_return.data, status.HTTP_200_OK)

    def patch(self, request, pet_id):
        try:
            pet = Pet.objects.get(pk=pet_id)
        except Pet.DoesNotExist:
            return Response({"detail": "Not found."}, status.HTTP_404_NOT_FOUND)

        sex_pet = request.data.get("sex", None)
        if sex_pet and sex_pet not in [
            "Male",
            "Female",
            "Not Informed",
        ]:
            return Response(
                {"sex": [f'"{request.data["sex"]}" is not a valid choice.']},
                status.HTTP_400_BAD_REQUEST,
            )

        group_pet = request.data.get("group", None)
        if group_pet is not None:
            try:
                group = Group.objects.get(
                    scientific_name__contains=group_pet["scientific_name"]
                )
            except Group.DoesNotExist:
                group = Group.objects.create(**group_pet)

            pet.group = group

        traits_pet = request.data.get("traits", None)
        if traits_pet is not None:
            traits = []
            for trait in traits_pet:
                try:
                    t = Trait.objects.get(name__icontains=trait["trait_name"])
                except Trait.DoesNotExist:
                    validate_t = TraitSerializer(data=trait)
                    validate_t.is_valid()
                    t = Trait.objects.create(**validate_t.validated_data)
                traits.append(t)
            pet.traits.set(traits)

        Pet.objects.filter(pk=pet_id).update(
            name=request.data.get("name", pet.name),
            age=request.data.get("age", pet.age),
            weight=request.data.get("weight", pet.weight),
            sex=request.data.get("sex", pet.sex),
        )
        pet.name = request.data.get("name", pet.name)
        pet.age = request.data.get("age", pet.age)
        pet.weight = request.data.get("weight", pet.weight)
        pet.sex = request.data.get("sex", pet.sex)
        pet.save()

        teste = Pet.objects.get(pk=pet_id)
        teste_serializer = PetSerializer(teste)

        print(teste_serializer.data)
        pet_return = PetSerializer(pet)
        pet_return.data
        return Response(pet_return.data, status.HTTP_200_OK)

    def delete(self, request, pet_id):
        try:
            pet = Pet.objects.get(pk=pet_id).delete()
        except Pet.DoesNotExist:
            return Response({"detail": "Not found."}, status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_204_NO_CONTENT)
