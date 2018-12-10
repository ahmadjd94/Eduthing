from django.contrib.auth.models import User
from django.db import models


SYSTEMS = (
    ("IGCSE", "IGCSE"),
    ("SAT", "SAT"),
    ("TAWJIHI", "TAWJIHI"),
)
PAYMENT_METHODS = (
    ("VISA", "VISA"),
    ("CASH_ON_DELIVERY", "CASH_ON_DELIVERY"),
    ("E-FAWATERKOM", "E-FAWATERKOM"),
)


MEMBER_TYPES = (
    ("STUDENT", "STUDENT"),
    ("TEACHER", "TEACHER")
)

BOOKLET_TYPES = (
    ("BOOKLET", "BOOKLET"),
    ("PAST_PAPER", "PAST_PAPER")
)

APPOINTMENT_STATUSES = (
    ("APPROVED", "APPROVED"),
    ("WAITING", "WAITING"),
    ("CANCELED", "CANCELED"),
)


class Member (User):
    type = models.CharField(max_length=32, choices=MEMBER_TYPES)
    phone = models.CharField(max_length=32)
    gender = models.CharField(max_length=32)
    education = models.CharField(choices=SYSTEMS, max_length=32)
    date_of_birth = models.DateField()
    address = models.CharField(max_length=32)
    card_number = models.CharField(max_length=16)
    card_expire_date = models.DateField()
    group_lectures = models.BooleanField()
    max_number_per_group = models.IntegerField()
    price_per_hour = models.FloatField()


class Booklet(models.Model):
    type = models.CharField(choices=BOOKLET_TYPES, max_length=32)
    tutor = models.ForeignKey("member", on_delete=models.CASCADE, related_name="booklets")
    subject = models.CharField(max_length=32)
    price = models.FloatField()
    year_published = models.DateField()
    education_system = models.CharField(choices=SYSTEMS, max_length=32)
    stock = models.IntegerField()

    objects = models.manager


class Chat(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=32)
    admin = models.ForeignKey("member", on_delete=models.CASCADE)


class ChatMember(models.Model):
    chat = models.ForeignKey("chat", on_delete=models.CASCADE)
    member = models.ForeignKey("member", on_delete=models.DO_NOTHING, related_name="chats")

    class Meta:
        unique_together = ("chat", "member")


class Messages(models.Model):
    id = models.IntegerField(primary_key=True)
    sender = models.ForeignKey("member", on_delete=models.CASCADE, related_name="messages")
    chat = models.ForeignKey("chat", on_delete=models.CASCADE)


class Order (models.Model):
    id = models.IntegerField(primary_key=True)
    booklet = models.ForeignKey("booklet", on_delete=models.CASCADE)
    student = models.ForeignKey("member", on_delete=models.CASCADE)
    address = models.CharField(max_length=32)
    payment_method = models.CharField(choices=PAYMENT_METHODS, max_length=32)


class Appointment(models.Model):
    student = models.ForeignKey("member", on_delete=models.CASCADE, related_name="student_appointments")
    tutor = models.ForeignKey("member", on_delete=models.CASCADE, related_name="teacher_appointments")
    subject = models.CharField(max_length=32)
    time = models.DateTimeField()
    address = models.CharField(max_length=32)
    duration = models.TimeField()
    price = models.FloatField()
    student_rating = models.IntegerField(default=0)
    teacher_rating = models.IntegerField(default=0)
    status = models.CharField(choices=APPOINTMENT_STATUSES, max_length=32, default="WAITING")

    class Meta:
        db_table = "appointment"


class GroupAppointment(models.Model):
    id = models.IntegerField(primary_key=True)
    tutor = models.ForeignKey("member", on_delete=models.CASCADE, related_name="tutor_group_appointments")
    subject = models.CharField(max_length=32)
    time = models.DateTimeField()
    address = models.CharField(max_length=32)
    duration = models.TimeField()
    price_per_student = models.FloatField()
    teacher_rating = models.IntegerField()

    class Meta:
        db_table = "group_appointment"


class GroupAppointmentStudents(models.Model):
    appointment = models.ForeignKey("GroupAppointment", on_delete=models.CASCADE)
    student = models.ForeignKey("member", on_delete=models.CASCADE, related_name="student_group_appointments")


class Upload(models.Model):
    tutor = models.ForeignKey("member", on_delete=models.CASCADE)
    booklet = models.ForeignKey("booklet", on_delete=models.CASCADE)
    version = models.IntegerField()
