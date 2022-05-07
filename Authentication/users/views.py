from email.policy import HTTP
from tokenize import Token
from rest_framework.views import APIView
from rest_framework.response import Response 
from users.permissions import IsOwnerOrReadOnly
from .models import Register
from .serializers import UserSerializers,RegisterSerializers,RegisterUpdateSerializer,LoginSerializer,LogoutSerializer
from rest_framework import serializers, status
from rest_framework import generics
from rest_framework import permissions 
from django.core import serializers
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
# permission class is set to authinticate or read only
# persmiss
class UserView(APIView): 
    def get(self,request,format=None):
        users=Register.objects.get(email__iexact="keder@gmail.com")
        # tok = users.tokens()
        return Response(UserSerializers(users,many=True).data) 
        # return Response(tok) 


class RegisterView(APIView):
    # permission_classes = [IsAuthenticated]
    def post(self,request,format=None):
        if Register.objects.filter(email__iexact=request.data["email"]).exists():
            serialized=RegisterSerializers(data=request.data)
            if serialized.is_valid():
                serialized.save()
                return Response("User successfully created",status.HTTP_200_OK)
            else:
                return Response(serialized.errors,status.HTTP_400_BAD_REQUEST)
        else :
            return Response("User Already exists",status.HTTP_400_BAD_REQUEST)

    # permission_classes=[IsOwnerOrReadOnly]
    def put(self,request,format=None):
        if Register.objects.filter(email__iexact=request.data['email']).exists():
            reg_user=Register.objects.get(email=request.data['email'])
            serialized_data=RegisterSerializers(instance=reg_user,data=request.data)
            if serialized_data.is_valid():
                serialized_data.save()
                return Response("User successfully updated",status.HTTP_200_OK)
            else:
                return Response(serialized_data.errors,status.HTTP_200_OK)
        else: 
            return Response("User does not exist",status.HTTP_400_BAD_REQUEST)


class LogInView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    def post(self,request):
        serializers_data = self.serializer_class(data=request.data)
        serializers_data.is_valid(raise_exception=True)

        email = serializers_data.data.get("email")
        log_in_obj = Register.objects.filter(email__iexact=email)
        log_in_obj_json = serializers.serialize("json", log_in_obj)
        # print(log_in_obj_json[0])

        # serialized_user_data = UserSerializers(data = log_in_obj)
        # serialized_user_data.is_valid(raise_exception=True)
        return Response(serializers_data.data,status=status.HTTP_200_OK)




class LogOutView(APIView):
    serializer_class = LogoutSerializer
    def post(self,request,format=None):
        serializers_data = self.serializer_class(data=request.data)
        serializers_data.is_valid(raise_exception=True)
        try : 
            token = RefreshToken(serializers_data.data)
            token.blacklist()
        except TokenError:
            msg = 'Successfully logged out'
        return Response(msg,status=status.HTTP_200_OK)




# whenever send a request from frontend to backend use ACCESS TOKEN , refresh can't be verified in backend
# when a user data is required in front end then use REFRESH TOKEN


# login - api/token/(return 401 or wrong creds)
# logout - 
    # - add user refresh token to the blacklist api -(http://127.0.0.1:8000/api/token/blacklist/).
    # - now after logging out if a user has the previous refresh token , he cant be able to hit any API cause it require a access token.
    # - If an access token is being expier we have to generate the access token with the refresh toke.But the refresh token is blacklisted.
    # - Any API can be accessed further untill user again logged in.
# reset_password - password_reset/
# update_user - register/(put)
# activate_user - 