from rest_framework.views import APIView
from rest_framework.response import Response

from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.generics import get_object_or_404

from django.db.utils import IntegrityError

from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from rest_framework_jwt.views import ObtainJSONWebToken


from rest_framework import status
from datetime import datetime

from rest_framework_jwt.settings import api_settings

from .models import Member, Booklet, Appointment, Order, APPROVED, TEACHER, STUDENT

from .serializers import (
    UserSerializer, BookletSerializer, AppointmentSerializer,
    OrderSerializer,
)

from .query import BookletQuerySerializer, TeahcerQuerySerializer

jwt_response_payload_handler = api_settings.JWT_RESPONSE_PAYLOAD_HANDLER


class SignupView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            try:
                target_user = Member.objects.create_user(**request.data)
                target_user.save()
            except IntegrityError:
                return Response({"error":"Username already exist"}, status=HTTP_400_BAD_REQUEST)

            return Response(serializer.data)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class TeacherListView(APIView): #end point tested
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        query = TeahcerQuerySerializer(data=request.query_params)

        if query.is_valid():
            query = Member.objects.filter(type="TEACHER",**query.data)
            serializer = UserSerializer(query, many=True)

            return Response(serializer.data, status=HTTP_200_OK)

        return Response(query.errors, status=HTTP_400_BAD_REQUEST)


class BookletAPI(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        request_data = request.data
        if request.user.member.type == TEACHER:

            request_data.update({
                "tutor": request.user.id
            })
            serializer = BookletSerializer(data=request_data)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=HTTP_200_OK)

            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

        return Response({"error": "user must be a teacher"}, status=HTTP_401_UNAUTHORIZED)

    def get(self, request, format=None):
        query_serializer = BookletQuerySerializer(data=request.query_params)

        if query_serializer.is_valid():
            query = Booklet.objects.filter(**query_serializer.data)
            serializer = BookletSerializer(query, many=True)

            return Response(serializer.data, status=HTTP_200_OK)

        return Response(query_serializer.errors, status=HTTP_400_BAD_REQUEST)


class AppointmentAPI(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def post(self, request,):
        request_data = request.data
        request_data.update({
            "student": request.user
        })
        if request.user.member.type == STUDENT:
            serializer = AppointmentSerializer(data=request_data)

            if serializer.is_valid():
                serializer.save()

                return Response(serializer.data, status=HTTP_200_OK)

            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

        return Response(data={"error": "must be a student to create an appointment"}, status=HTTP_401_UNAUTHORIZED)

    def get(self, request, format=None):
        query_serializer = BookletQuerySerializer(data=request.query_params)

        if query_serializer.is_valid():
            query = Booklet.objects.filter(**query_serializer.data)
            serializer = BookletSerializer(query, many=True)

            return Response(serializer.data, status=HTTP_200_OK)

        return Response(query_serializer.errors, status=HTTP_400_BAD_REQUEST)


class AppointmentDetailAPI(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk: int, format=None):

        query = get_object_or_404(Appointment, pk)
        serializer = BookletSerializer(query, many=True)

        return Response(serializer.data, status=HTTP_200_OK)

    def patch(self, request, pk: int, format=None):

        query = Appointment.objects.get_object_or_404(pk)
        query.status = APPROVED
        query.save()
        serializer = AppointmentSerializer(query, many=True)

        return Response(serializer.data, status=HTTP_200_OK)


class OrderAPI(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        request_data = request.data
        request_data.update({
            "student": request.user
        })
        if request.user.member.type == STUDENT:
            serializer = OrderSerializer(data=request_data)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=HTTP_200_OK)

            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

        return Response(data={"error": "must be a student to create an order"}, status=HTTP_401_UNAUTHORIZED)

    def get(self):

        queryset = Order.objects.all()
        serializer = OrderSerializer(queryset, many=True)

        return Response(serializer.data, status=HTTP_200_OK)


class OrderDetailAPI(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def get(self, pk: int):

        query = get_object_or_404(Order, pk)
        serializer = OrderSerializer(query, many=True)

        return Response(serializer.data, status=HTTP_200_OK)

    def patch(self,  pk: int):

        query = get_object_or_404(Order, pk)
        serializer = OrderSerializer(query, many=True)

        return Response(serializer.data, status=HTTP_200_OK)


class JSONWebToken(ObtainJSONWebToken):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user = serializer.object.get('user') or request.user
            user_data = UserSerializer(user.member)
            print(user_data.data)
            token = serializer.object.get('token')
            response_data = {**jwt_response_payload_handler(token, user, request), **user_data.data}
            response = Response(response_data)
            if api_settings.JWT_AUTH_COOKIE:
                expiration = (datetime.utcnow() +
                              api_settings.JWT_EXPIRATION_DELTA)
                response.set_cookie(api_settings.JWT_AUTH_COOKIE,
                                    token,
                                    expires=expiration,
                                    httponly=True)
            return response

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoggedInUserView(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def get(self, request):

        serializer = UserSerializer(request.user.member)

        return Response(serializer.data, status=HTTP_200_OK)

    def patch(self, request, format=None):
        member = request.user.member

        serializer = UserSerializer(instance=member, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=HTTP_200_OK)

        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
