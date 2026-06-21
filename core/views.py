from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated,IsAdminUser
from rest_framework.response import Response
from django.db import IntegrityError, transaction
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status

from .models import User, FarmerProfile, PorterProfile


# ============================================================
# REGISTER
# ============================================================
@api_view(['POST'])
@permission_classes([IsAdminUser])
@transaction.atomic
def RegisterView(request):
    data = request.data

    # Extract User model variables
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role')
    phone_number = data.get('phone_number')

    # Validate required fields
    if not username or not email or not password:
        return Response({"error": "Username, email, and password are required."}, status=400)

    # Check duplicates
    if User.objects.filter(username=username).exists():
        return Response({"error": "Username already exists."}, status=400)
    if User.objects.filter(email=email).exists():
        return Response({"error": "Email already exists."}, status=400)

    try:
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role=role,
            phone_number=phone_number
        )

        # Role-specific profile
        if role == 'farmer':
            FarmerProfile.objects.create(
                user=user,
                first_name=data['first_name'],
                last_name=data['last_name'],
                national_id=data['national_id'],
                phone_number=phone_number,
                farm_name=data.get('farm_name', '')
            )
        elif role == 'porter':
            PorterProfile.objects.create(
                user=user,
                first_name=data['first_name'],
                last_name=data['last_name'],
                employee_id=data['employee_id'],
                phone_number=phone_number,
                national_id=data['national_id'],
                route_name=data.get('route_name', '')
            )

        return Response({
            "user_id": user.id,
            "username": user.username,
            "role": user.role,
            "message": f"{role.capitalize()} registered successfully."
        }, status=201)

    except IntegrityError as e:
        return Response({"error": "Integrity error: " + str(e)}, status=400)
    except Exception as e:
        return Response({"error": str(e)}, status=400)



# ============================================================
# LOGIN
# ============================================================

@api_view(['POST'])
@permission_classes([AllowAny])
def LoginView(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(username=username, password=password)
    
    if not user:
        return Response({'error': 'Invalid credentials'}, status=401)
    
    refresh = RefreshToken.for_user(user)
    
    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user_id': user.id,
        'username': user.username,
        'role': user.role
    })


# ============================================================
# LOGOUT
# ============================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def LogoutView(request):
    try:
        refresh_token = request.data.get("refresh")
        token = RefreshToken(refresh_token)
        token.blacklist()   # requires SIMPLE_JWT['BLACKLIST_AFTER_ROTATION'] = True
        return Response({"message": "Logout successful."}, status=status.HTTP_205_RESET_CONTENT)
    except TokenError:
        return Response({"error": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e: 
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    
# ============================================================
# GET CURRENT USER
# ============================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def MeView(request):
    user = request.user
    
    profile_data = {}
    
    if user.role == 'farmer' and hasattr(user, 'farmer_profile'):
        p = user.farmer_profile
        profile_data = {
            'first_name': p.first_name,
            'last_name': p.last_name,
            'phone_number': p.phone_number,
            'farm_name': p.farm_name
        }
    elif user.role == 'porter' and hasattr(user, 'porter_profile'):
        p = user.porter_profile
        profile_data = {
            'first_name': p.first_name,
            'last_name': p.last_name,
            'employee_id': p.employee_id,
            'route_name': p.route_name
        }
    
    return Response({
        'id': user.id,
        'username': user.username,
        'role': user.role,
        'profile': profile_data
    })