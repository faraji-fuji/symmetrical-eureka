from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from core.models import Building, Floor, Office, MyUser
from core.serializers import RegisterMyUserSerializer, GetMyUserSerializer
from core.serializers import LoginSerializer, BuildingSerializer, VerifyOtpSerializer
from core.serializers import FloorSerializer, OfficeSerializer, ResendOtpSerializer
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
import logging
import random
import datetime
from django.utils import timezone
import core.utils.helpers as h



logger = logging.getLogger(__name__)

# @api_view(['POST'])
# def login_user(request):
#     if request.method == "POST":
#         serializer = LoginSerializer(data=request.data)
        
#         if serializer.is_valid():
#             username = serializer.validated_data.get("username")
#             password = serializer.validated_data.get("password")

#             user = authenticate(username=username, password=password)
            
#             if user is not None:
#                 login(request, user)

#                 logger.info(f"User '{username}' logged in.")
#                 return Response({"detail":"log in successful"}, 
#                                 status=status.HTTP_200_OK)
            
#             logger.warning(f"Failed login attempt for user '{username}'.")
#             return Response({"detail":"incorrect username or password"},
#                             status=status.HTTP_401_UNAUTHORIZED)
        
#         logger.error(f"Login validation failed: '{serializer.errors}'.")
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

#     logger.error("Invalid request method for login.")
#     return Response({"detail":"invalid request method"},
#                     status=status.HTTP_405_METHOD_NOT_ALLOWED)

# @api_view(['POST'])
# def logout_user(request):
#     if request.method == "POST":
#         logout(request)
#         return Response({"detail":"log out successful"}, 
#                                 status=status.HTTP_200_OK)
    
#     return Response({"detail":"invalid request method"},
#                     status=status.HTTP_405_METHOD_NOT_ALLOWED)

def handle_send_sms_message_result(result):
    is_rejected = result.get('is_rejected')
    if is_rejected:
        error = result.get('error')
        return Response({"detail":error}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    is_resolved = result.get('is_resolved')
    if is_resolved:
        response = result.get('response')
        return Response(response.json(), response.status_code)
    
    is_successful = result.get('is_successful')
    if is_successful:
        return Response({"detail":"OTP sent successfuly"}, status=status.HTTP_200_OK)


@api_view(['POST'])
def verify_otp(request):
    if request.method == 'POST':
        serializer = VerifyOtpSerializer(data=request.data)

        if serializer.is_valid():
            request_otp = serializer.validated_data.get('otp')
            email = serializer.validated_data.get('email')
         
            user = MyUser.objects.get(email=email)

        
            if user.otp == request_otp and not user.has_otp_expired():
                user.mark_phone_as_verified()
                return Response({'detail': 'OTP verified and phone number marked as verified.'}, status=status.HTTP_200_OK)
            else:
                return Response({'detail': 'Invalid OTP or expired OTP.'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response({"detail":"invalid request methos"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['POST'])
def resend_otp(request):
    if request.method == 'POST':

        serializer = ResendOtpSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data.get('email')

            user = MyUser.objects.get(email=email)
            message = f"{user.otp} is your code. Please do not share it with anyone."
            h.send_sms_message(
                phone_number=user.phone_number, 
                message=message)

            return Response({"detail":"OTP regenerated successfully."})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response({"detail":"invalid request method"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['POST'])
def generate_otp(request):
    if request.method == 'POST':

        serializer = ResendOtpSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data.get('email')

            user = MyUser.objects.get(email=email)
            user.otp = str(random.randint(100000, 999999))
            user.otp_expiry = timezone.now() + datetime.timedelta(minutes=3)
            user.save()

            # send otp
            message = f"{user.otp} is your code. Please do not share it with anyone."
            result = h.send_sms_message(
                phone_number=user.phone_number, 
                message=message)
            
            return handle_send_sms_message_result(result)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response({"detail":"invalid request method"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)



@api_view(['GET', 'POST'])
def user_list(request):
    """
    List all users, or create a new user.
    """
    if request.method == 'GET':
        users = MyUser.objects.all()
        serializer = GetMyUserSerializer(users, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = RegisterMyUserSerializer(data=request.data)
        if serializer.is_valid():

            user = MyUser.objects.create_user(
                serializer.validated_data.get('username'),
                serializer.validated_data.get('email'),
                serializer.validated_data.get('password'))
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def user_detail(request, pk):
    """
    Retrieve, update or delete a user.
    """
    try:
        user = MyUser.objects.get(pk=pk)
    except MyUser.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = GetMyUserSerializer(user)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = GetMyUserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

@api_view(['GET', 'POST'])
def building_list(request):
    """
    List all buildings, or create a new building.
    """
    if request.method == 'GET':
        buildings = Building.objects.all()
        serializer = BuildingSerializer(buildings, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = BuildingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def building_detail(request, pk):
    """
    Retrieve, update or delete a building.
    """
    try:
        building = Building.objects.get(pk=pk)
    except Building.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = BuildingSerializer(building)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = BuildingSerializer(building, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        building.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
def floor_list(request):
    """
    List all floors, or create a new floor.
    """
    if request.method == 'GET':
        floors = Floor.objects.all()
        serializer = FloorSerializer(floors, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = FloorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def floor_detail(request, pk):
    """
    Retrieve, update or delete a floor.
    """
    try:
        floor = Floor.objects.get(pk=pk)
    except Floor.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = FloorSerializer(floor)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = FloorSerializer(floor, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        floor.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

@api_view(['GET', 'POST'])
def office_list(request):
    """
    List all offices, or create a new office.
    """
    if request.method == 'GET':
        office = Office.objects.all()
        serializer = OfficeSerializer(office, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = OfficeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def office_detail(request, pk):
    """
    Retrieve, update or delete an office.
    """
    try:
        office = Office.objects.get(pk=pk)
    except Office.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = OfficeSerializer(office)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = OfficeSerializer(office, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        office.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    