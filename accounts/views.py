from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import User, UserProfile
from .serializers import UserSerializer, UserProfileSerializer
from .permissions import IsAdmin, IsAdminOrOwner


class UserListView(generics.ListAPIView):
    """List all users (Admin only)"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]  # Only admins can list all users


class UserDetailView(generics.RetrieveUpdateAPIView):
    """Get or update user details"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminOrOwner]  # Admin or owner can access


class ProfileView(generics.RetrieveUpdateAPIView):
    """Get or update user profile"""
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile


@swagger_auto_schema(
    method='get',
    responses={
        200: UserSerializer,
        401: "Unauthorized - Authentication required"
    },
    operation_description="Get current authenticated user information",
    operation_summary="Get Current User",
    tags=['User Management']
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def current_user(request):
    """Get current user info"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@swagger_auto_schema(
    method='post',
    operation_description="Change user role - PUBLIC ACCESS (No authentication required)",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['user_id', 'role'],
        properties={
            'user_id': openapi.Schema(type=openapi.TYPE_INTEGER),
            'role': openapi.Schema(type=openapi.TYPE_STRING, enum=['admin', 'user']),
        },
    ),
    responses={200: "Role changed successfully"}
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])  # Changed from IsAdmin to AllowAny
def change_user_role(request):
    """Change user role - PUBLIC ACCESS (No authentication required)"""
    user_id = request.data.get('user_id')
    new_role = request.data.get('role')
    
    if not user_id or not new_role:
        return Response({
            'error': 'user_id and role are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if new_role not in ['admin', 'user']:
        return Response({
            'error': 'role must be either admin or user'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(id=user_id)
        user.role = new_role
        
        # Set staff status for admin role
        if new_role == 'admin':
            user.is_staff = True
        else:
            user.is_staff = False
            
        user.save()
        
        return Response({
            'message': f'User role changed to {new_role} successfully',
            'user': UserSerializer(user).data
        }, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
        return Response({
            'error': 'User not found'
        }, status=status.HTTP_404_NOT_FOUND)


@swagger_auto_schema(
    method='get',
    operation_description="Get all admin users",
    responses={200: UserSerializer(many=True)},
    tags=['User Management']
)
@api_view(['GET'])
@permission_classes([IsAdmin])
def admin_users(request):
    """Get all admin users"""
    admins = User.objects.filter(role='admin')
    serializer = UserSerializer(admins, many=True)
    return Response(serializer.data)


@swagger_auto_schema(
    method='get',
    operation_description="Get all regular users",
    responses={200: UserSerializer(many=True)},
    tags=['User Management']
)
@api_view(['GET'])
@permission_classes([IsAdmin])
def regular_users(request):
    """Get all regular users"""
    users = User.objects.filter(role='user')
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)


@swagger_auto_schema(
    method='post',
    operation_description="Deactivate user account (Admin only)",
    tags=['User Management'],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['user_id'],
        properties={
            'user_id': openapi.Schema(type=openapi.TYPE_INTEGER),
        },
    ),
    responses={200: "User deactivated successfully"}
)
@api_view(['POST'])
@permission_classes([IsAdmin])
def deactivate_user(request):
    """Deactivate user account (Admin only)"""
    user_id = request.data.get('user_id')
    
    if not user_id:
        return Response({
            'error': 'user_id is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(id=user_id)
        
        # Prevent deactivating self
        if user == request.user:
            return Response({
                'error': 'You cannot deactivate your own account'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user.is_active = False
        user.save()
        
        return Response({
            'message': 'User deactivated successfully'
        }, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
        return Response({
            'error': 'User not found'
        }, status=status.HTTP_404_NOT_FOUND)


# ================================================================
# PASSWORD & PROFILE MANAGEMENT APIS
# ================================================================

@swagger_auto_schema(
    method='put',
    operation_description="Change user password",
    operation_summary="Change Password",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['current_password', 'new_password'],
        properties={
            'current_password': openapi.Schema(type=openapi.TYPE_STRING, description='Current password'),
            'new_password': openapi.Schema(type=openapi.TYPE_STRING, description='New password (min 8 characters)'),
        },
    ),
    responses={
        200: openapi.Response(
            description="Password changed successfully",
            examples={
                'application/json': {
                    'success': True,
                    'message': 'Password changed successfully'
                }
            }
        ),
        400: "Bad request - Invalid current password",
        401: "Unauthorized - Authentication required"
    },
    tags=['User Profile']
)
@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
def change_password(request):
    """Change user password with current password verification"""
    
    try:
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        
        # Validation
        if not current_password or not new_password:
            return Response({
                'success': False,
                'error': 'current_password and new_password are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify current password
        if not request.user.check_password(current_password):
            return Response({
                'success': False,
                'error': 'Current password is incorrect'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate new password
        if len(new_password) < 8:
            return Response({
                'success': False,
                'error': 'New password must be at least 8 characters long'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Set new password
        request.user.set_password(new_password)
        request.user.save()
        
        return Response({
            'success': True,
            'message': 'Password changed successfully'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method='put',
    operation_description="Update user profile (username and email)",
    operation_summary="Update Profile",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING, description='New username'),
            'email': openapi.Schema(type=openapi.TYPE_STRING, format='email', description='New email address'),
        },
    ),
    responses={
        200: openapi.Response(
            description="Profile updated successfully",
            examples={
                'application/json': {
                    'success': True,
                    'message': 'Profile updated successfully',
                    'user': {
                        'id': 1,
                        'username': 'newusername',
                        'email': 'newemail@example.com',
                        'first_name': 'John',
                        'last_name': 'Doe'
                    }
                }
            }
        ),
        400: "Bad request - Email already exists",
        401: "Unauthorized - Authentication required"
    },
    tags=['User Profile']
)
@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
def update_profile(request):
    """Update user profile - username and email"""
    
    try:
        username = request.data.get('username')
        email = request.data.get('email')
        
        user = request.user
        
        # Update username if provided
        if username:
            if username != user.user_name:
                # Check if username already exists
                if User.objects.filter(user_name=username).exclude(id=user.id).exists():
                    return Response({
                        'success': False,
                        'error': 'Username already exists'
                    }, status=status.HTTP_400_BAD_REQUEST)
                user.user_name = username
        
        # Update email if provided
        if email:
            if email != user.email:
                # Check if email already exists
                if User.objects.filter(email=email).exclude(id=user.id).exists():
                    return Response({
                        'success': False,
                        'error': 'Email already exists'
                    }, status=status.HTTP_400_BAD_REQUEST)
                user.email = email
        
        # Save changes
        user.save()
        
        return Response({
            'success': True,
            'message': 'Profile updated successfully',
            'user': UserSerializer(user).data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method='post',
    operation_description="Send password reset link to email",
    operation_summary="Forgot Password",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['email'],
        properties={
            'email': openapi.Schema(type=openapi.TYPE_STRING, format='email', description='Registered email address'),
        },
    ),
    responses={
        200: openapi.Response(
            description="Password reset link sent",
            examples={
                'application/json': {
                    'success': True,
                    'message': 'Password reset link sent to your email'
                }
            }
        ),
        404: "Email not found"
    },
    tags=['Password Reset']
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def forgot_password(request):
    """Send password reset link to email"""
    
    try:
        from django.contrib.auth.tokens import default_token_generator
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes
        from django.core.mail import send_mail
        from django.conf import settings
        import uuid
        
        email = request.data.get('email')
        
        if not email:
            return Response({
                'success': False,
                'error': 'Email is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Don't reveal if email exists for security
            return Response({
                'success': True,
                'message': 'If the email exists, you will receive a password reset link'
            }, status=status.HTTP_200_OK)
        
        # Generate reset token
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        # Create reset link
        reset_link = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"
        
        # Send email
        subject = 'Password Reset Request - SalesAice'
        message = f'''
        Hi {user.username or user.email},
        
        You requested a password reset for your SalesAice account.
        
        Click the link below to reset your password:
        {reset_link}
        
        If you didn't request this, please ignore this email.
        
        Best regards,
        SalesAice Team
        '''
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
        except Exception as email_error:
            # Log error but don't reveal to user
            print(f"Email sending failed: {email_error}")
        
        return Response({
            'success': True,
            'message': 'Password reset link sent to your email'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': 'An error occurred. Please try again.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method='post',
    operation_description="Reset password using token from email",
    operation_summary="Reset Password",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['uid', 'token', 'new_password'],
        properties={
            'uid': openapi.Schema(type=openapi.TYPE_STRING, description='User ID from email link'),
            'token': openapi.Schema(type=openapi.TYPE_STRING, description='Reset token from email link'),
            'new_password': openapi.Schema(type=openapi.TYPE_STRING, description='New password (min 8 characters)'),
        },
    ),
    responses={
        200: openapi.Response(
            description="Password reset successfully",
            examples={
                'application/json': {
                    'success': True,
                    'message': 'Password reset successfully'
                }
            }
        ),
        400: "Invalid or expired token"
    },
    tags=['Password Reset']
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def reset_password(request):
    """Reset password using token from email"""
    
    try:
        from django.contrib.auth.tokens import default_token_generator
        from django.utils.http import urlsafe_base64_decode
        from django.utils.encoding import force_str
        
        uid = request.data.get('uid')
        token = request.data.get('token')
        new_password = request.data.get('new_password')
        
        # Validation
        if not uid or not token or not new_password:
            return Response({
                'success': False,
                'error': 'uid, token, and new_password are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate new password
        if len(new_password) < 8:
            return Response({
                'success': False,
                'error': 'New password must be at least 8 characters long'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Decode user ID
        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({
                'success': False,
                'error': 'Invalid reset link'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify token
        if not default_token_generator.check_token(user, token):
            return Response({
                'success': False,
                'error': 'Invalid or expired reset token'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Set new password
        user.set_password(new_password)
        user.save()
        
        return Response({
            'success': True,
            'message': 'Password reset successfully. You can now login with your new password.'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': 'An error occurred. Please try again.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
