from rest_framework import serializers

from .models import BOOKLET_TYPES, SYSTEMS


class BookletQuerySerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=BOOKLET_TYPES, required=False)
    subject = serializers.CharField(max_length=32, required=False)
    year = serializers.IntegerField(required=False)
    education_system = serializers.ChoiceField(choices=SYSTEMS, required=False)

    def to_representation(self, instance):
        query = {}
        print(instance)
        type_query = instance.get("type")
        subject_query = instance.get("subject")
        year_query = instance.get("year")

        if type_query:
            query.update({
                "type__icontains": type_query
            })

        if subject_query:
            query.update({
                "subject__icontains": subject_query
            })

        if year_query:
            query.update({
                "year_published__year": year_query
            })

        return query


class TeahcerQuerySerializer(serializers.Serializer):
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    education = serializers.ChoiceField(choices=SYSTEMS, required=False)

    def to_representation(self, instance):
        query = {}

        first_name_query = instance.get("first_name")
        last_name_query = instance.get("last_name")
        education_query = instance.get("education")

        if first_name_query:
            query.update({
                "first_name__icontains": first_name_query
            })

        if last_name_query:
            query.update({
                "last_name__icontains": last_name_query
            })

        if education_query:
            query.update({
                "education__icontains": education_query
            })

        return query
