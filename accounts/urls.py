from django.urls import path
from . import views
from dashboard.admin_dashboard_api import AdminDashboardAPIView
from .user_management_api import UserManagementAPIView
from .user_type_api import UserTypeAPIView
from .admin_views import UserDetailAPIView, AdminUserAPIView, AdminUserStatusAPIView

urlpatterns = [
    # Admin dashboard endpoint  
    path('admin/dashboard/', AdminDashboardAPIView.as_view(), name='admin-dashboard'),
    
    # 👥 USER MANAGEMENT API - Complete user data with statistics
    path('admin/users/', UserManagementAPIView.as_view(), name='admin-user-management'),
    
    # 👤 USER TYPE API - Simple UserType format
    path('users/data/', UserTypeAPIView.as_view(), name='user-type-api'),
    
    # 📊 USER DETAILS API - Comprehensive user details for admin
    path('admin/users/<str:userId>/details/', UserDetailAPIView.as_view(), name='admin-user-details'),
    
    #  ADMIN USER STATUS API - Update user status
    path('admin/users/<str:userId>/status/', AdminUserStatusAPIView.as_view(), name='admin-user-status'),
    
    # � ADMIN USER API - Get, Update and Delete user 
    path('admin/users/<str:userId>/', AdminUserAPIView.as_view(), name='admin-user-get-update-delete'),
    
    path('users/', views.UserListView.as_view(), name='user-list'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user-detail'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('me/', views.current_user, name='current-user'),
    
    # Admin role management
    path('change-role/', views.change_user_role, name='change-user-role'),
    path('admins/', views.admin_users, name='admin-users'),
    path('regular-users/', views.regular_users, name='regular-users'),
    path('deactivate-user/', views.deactivate_user, name='deactivate-user'),
    
    # Password & Profile Management APIs
    path('user/change-password/', views.change_password, name='change-password'),
    path('user/profile/', views.update_profile, name='update-profile'),
    path('user/forgot-password/', views.forgot_password, name='forgot-password'),
    path('user/reset-password/', views.reset_password, name='reset-password'),
]
