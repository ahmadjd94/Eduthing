from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.status import HTTP_404_NOT_FOUND, HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.generics import get_object_or_404

from django.db.utils import IntegrityError

from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from .models import Member, Booklet, Appointment, Order

from .serializers import (
    UserSerializer, BookletSerializer, AppointmentCreationSerializer, AppointmentApprovalSerializer,
    OrderSerializer
)

from .query import BookletQuerySerializer, TeahcerQuerySerializer


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


class LoginView(APIView):
    permission_classes = (AllowAny,)
    def post(self, request, format=None):
        data = request.data

        username = data.get('username', None)
        password = data.get('password', None)

        user = authenticate(username=username, password=password)
        if not user:
            return Response({'error': 'Invalid Credentials'},
                            status=HTTP_404_NOT_FOUND)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key},
                        status=HTTP_200_OK)


class TeacherLoginView(APIView):
    def post(self, request, format=None):
        data = request.data

        username = data.get('username', None)
        password = data.get('password', None)
        print(username, password)
        user = authenticate(username=username, password=password)
        if not user:
            return Response({'error': 'Invalid Credentials'},
                            status=HTTP_404_NOT_FOUND)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key},
                        status=HTTP_200_OK)


class TeacherListView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, format=None):
        query = TeahcerQuerySerializer(data=request.query_params)

        if query.is_valid():
            query = Member.objects.filter(type="TEACHER",**query.data)
            serializer = UserSerializer(query, many=True)

            return Response(serializer.data, status=HTTP_200_OK)

        return Response(query.errors, status=HTTP_400_BAD_REQUEST)


class BookletAPI(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (AllowAny,)

    def post(self, request, format=None):
        request_data = request.data
        request_data.update({
            "tutor": request.user.id
        })
        serializer = BookletSerializer(data=request_data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=HTTP_200_OK)

        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

    def get(self, request, format=None):

        query_serializer = BookletQuerySerializer(data=request.query_params)
        print(request.query_params)
        if query_serializer.is_valid():
            print(query_serializer.data)
            query = Booklet.objects.filter(**query_serializer.data)
            serializer = BookletSerializer(query, many=True)

            return Response(serializer.data, status=HTTP_200_OK)

        return Response(query_serializer.errors, status=HTTP_400_BAD_REQUEST)


class AppointmentAPI(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (AllowAny,)

    def post(self, request, format=None):
        request_data = request.data
        request_data.update({
            "student": request.user
        })
        if request.user.member.type == "STUDENT":
            serializer = AppointmentCreationSerializer(data=request_data)

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
    permission_classes = (AllowAny,)

    def get(self, request, pk: int, format=None):

        query = get_object_or_404(Appointment, pk)
        serializer = BookletSerializer(query, many=True)

        return Response(serializer.data, status=HTTP_200_OK)

    def patch(self, request, pk: int, format=None):

        query = Booklet.objects.get_object_or_404(pk)
        serializer = BookletSerializer(query, many=True)

        return Response(serializer.data, status=HTTP_200_OK)


class OrderAPI(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (AllowAny,)

    def post(self, request, format=None):
        request_data = request.data
        request_data.update({
            "student": request.user
        })
        if request.user.member.type == "STUDENT":
            serializer = OrderSerializer(data=request_data)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=HTTP_200_OK)

            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

        return Response(data={"error": "must be a student to create an order"}, status=HTTP_401_UNAUTHORIZED)

    def get(self, request, format=None):

        queryset = Order.object.all()
        serializer = BookletSerializer(queryset, many=True)

        return Response(serializer.data, status=HTTP_200_OK)

class OrderDetailAPI(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (AllowAny,)

    def get(self, request, pk: int, format=None):

        query = get_object_or_404(Order, pk)
        serializer = OrderSerializer(query, many=True)

        return Response(serializer.data, status=HTTP_200_OK)

    def patch(self, request, pk: int, format=None):

        query = get_object_or_404(Order, pk)
        serializer = OrderSerializer(query, many=True)

        return Response(serializer.data, status=HTTP_200_OK)

