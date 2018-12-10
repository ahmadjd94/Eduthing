from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Appointment, Booklet, Order, SYSTEMS, PAYMENT_METHODS, GroupAppointment, Upload, Member, APPOINTMENT_STATUSES


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ('username', 'email')


class BookletSerializer(serializers.ModelSerializer):
    tutor = serializers.PrimaryKeyRelatedField(queryset=Member.objects.all())
    type = serializers.CharField(required=True)
    subject = serializers.CharField(max_length=32, required=True)
    price = serializers.FloatField(required=True)
    year_published = serializers.DateField(required=True)
    education_system = serializers.ChoiceField(choices=SYSTEMS)
    stock = serializers.IntegerField(required=True)

    class Meta:
        model = Booklet
        fields = ('tutor', 'type', 'subject', 'price', 'year_published', 'education_system', 'stock')


class OrderSerializer (serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    address = serializers.CharField(max_length=32)
    payment_method = serializers.ChoiceField(choices=PAYMENT_METHODS)

    class Meta:
        model = Order


class AppointmentCreationSerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(queryset=Member.objects.filter(type="STUDENT"))
    tutor = serializers.PrimaryKeyRelatedField(queryset=Member.objects.filter(type="TEACHER"))
    subject = serializers.CharField(max_length=32)
    time = serializers.DateTimeField()
    address = serializers.CharField(max_length=32)
    duration = serializers.TimeField()
    price = serializers.FloatField()

    class Meta:
        model = Appointment
        fields = ('subject', 'time', 'address', 'price', 'tutor', 'duration', 'student')


class AppointmentApprovalSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(choices=APPOINTMENT_STATUSES, required=True)

    class Meta:
        model = Appointment


class GroupAppointmentSerializer(serializers.ModelSerializer):
    subject = serializers.CharField(max_length=32)
    time = serializers.DateTimeField()
    address = serializers.CharField(max_length=32)
    duration = serializers.TimeField()
    price_per_student = serializers.FloatField()
    teacher_rating = serializers.IntegerField()

    class Meta:
        model = GroupAppointment


class UploadSerializer(serializers.ModelSerializer):
    version = serializers.IntegerField()

    class Meta:
        model = Upload
