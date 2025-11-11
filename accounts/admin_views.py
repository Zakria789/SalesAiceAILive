from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.contrib.auth import get_user_model
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import datetime, timedelta
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.shortcuts import get_object_or_404

from accounts.models import User
from accounts.permissions import IsAdmin
from subscriptions.models import Subscription, BillingHistory
from HumeAiTwilio.models import TwilioCall, ConversationLog

User = get_user_model()


class UserDetailAPIView(APIView):
    """
    Admin API to get comprehensive user details including call history, billing, and analytics
    ADMIN ACCESS ONLY - Returns detailed user information for admin dashboard
    """
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    
    @swagger_auto_schema(
        tags=['Admin'],
        operation_summary="Get User Details",
        operation_description="Get comprehensive user details including call history, billing history, activity logs, and analytics",
        manual_parameters=[
            openapi.Parameter('userId', openapi.IN_PATH, description="User ID", type=openapi.TYPE_STRING)
        ],
        responses={
            200: openapi.Response(
                description="User details",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'user': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'id': openapi.Schema(type=openapi.TYPE_STRING),
                                'name': openapi.Schema(type=openapi.TYPE_STRING),
                                'email': openapi.Schema(type=openapi.TYPE_STRING),
                                'role': openapi.Schema(type=openapi.TYPE_STRING, enum=['admin', 'user']),
                                'status': openapi.Schema(type=openapi.TYPE_STRING, enum=['active', 'inactive', 'banned', 'pending']),
                                'phone': openapi.Schema(type=openapi.TYPE_STRING),
                                'company': openapi.Schema(type=openapi.TYPE_STRING),
                                'joinedAt': openapi.Schema(type=openapi.TYPE_STRING),
                                'lastLoginAt': openapi.Schema(type=openapi.TYPE_STRING),
                                'totalCalls': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'minutesUsed': openapi.Schema(type=openapi.TYPE_NUMBER),
                                'currentPlan': openapi.Schema(type=openapi.TYPE_STRING),
                                'billingStatus': openapi.Schema(type=openapi.TYPE_STRING, enum=['active', 'overdue', 'cancelled']),
                                'avatar': openapi.Schema(type=openapi.TYPE_STRING),
                                'profile': openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        'bio': openapi.Schema(type=openapi.TYPE_STRING),
                                        'timezone': openapi.Schema(type=openapi.TYPE_STRING),
                                        'language': openapi.Schema(type=openapi.TYPE_STRING),
                                        'notifications': openapi.Schema(
                                            type=openapi.TYPE_OBJECT,
                                            properties={
                                                'email': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                                'sms': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                                'push': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                            }
                                        )
                                    }
                                )
                            }
                        ),
                        'callHistory': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'id': openapi.Schema(type=openapi.TYPE_STRING),
                                    'date': openapi.Schema(type=openapi.TYPE_STRING),
                                    'duration': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'type': openapi.Schema(type=openapi.TYPE_STRING, enum=['inbound', 'outbound']),
                                    'status': openapi.Schema(type=openapi.TYPE_STRING, enum=['completed', 'missed', 'failed']),
                                    'phoneNumber': openapi.Schema(type=openapi.TYPE_STRING),
                                    'cost': openapi.Schema(type=openapi.TYPE_NUMBER),
                                    'transcript': openapi.Schema(type=openapi.TYPE_STRING),
                                }
                            )
                        ),
                        'billingHistory': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'id': openapi.Schema(type=openapi.TYPE_STRING),
                                    'date': openapi.Schema(type=openapi.TYPE_STRING),
                                    'amount': openapi.Schema(type=openapi.TYPE_NUMBER),
                                    'type': openapi.Schema(type=openapi.TYPE_STRING, enum=['charge', 'refund', 'credit']),
                                    'status': openapi.Schema(type=openapi.TYPE_STRING, enum=['paid', 'pending', 'failed']),
                                    'description': openapi.Schema(type=openapi.TYPE_STRING),
                                    'invoice': openapi.Schema(type=openapi.TYPE_STRING),
                                }
                            )
                        ),
                        'activityLogs': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'id': openapi.Schema(type=openapi.TYPE_STRING),
                                    'timestamp': openapi.Schema(type=openapi.TYPE_STRING),
                                    'action': openapi.Schema(type=openapi.TYPE_STRING),
                                    'details': openapi.Schema(type=openapi.TYPE_STRING),
                                    'ipAddress': openapi.Schema(type=openapi.TYPE_STRING),
                                    'userAgent': openapi.Schema(type=openapi.TYPE_STRING),
                                    'status': openapi.Schema(type=openapi.TYPE_STRING, enum=['success', 'warning', 'error']),
                                }
                            )
                        ),
                        'analytics': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'totalSpent': openapi.Schema(type=openapi.TYPE_NUMBER),
                                'avgCallDuration': openapi.Schema(type=openapi.TYPE_NUMBER),
                                'successRate': openapi.Schema(type=openapi.TYPE_NUMBER),
                                'mostActiveDay': openapi.Schema(type=openapi.TYPE_STRING),
                                'callsByMonth': openapi.Schema(
                                    type=openapi.TYPE_ARRAY,
                                    items=openapi.Schema(
                                        type=openapi.TYPE_OBJECT,
                                        properties={
                                            'month': openapi.Schema(type=openapi.TYPE_STRING),
                                            'calls': openapi.Schema(type=openapi.TYPE_INTEGER),
                                        }
                                    )
                                ),
                            }
                        ),
                    }
                )
            ),
            401: "Unauthorized - Authentication required",
            403: "Forbidden - Admin access required",
            404: "User not found"
        }
    )
    def get(self, request, userId):
        """Get comprehensive user details for admin dashboard"""
        try:
            # Get the user
            user = get_object_or_404(User, id=userId)
            
            # Get user's subscription
            user_subscription = Subscription.objects.filter(user=user, status='active').first()
            
            # Get user's calls
            user_calls = TwilioCall.objects.filter(user=user).order_by('-started_at')
            
            # Calculate total minutes used
            total_duration_seconds = user_calls.aggregate(total=Sum('duration'))['total'] or 0
            total_minutes_used = round(total_duration_seconds / 60, 2)
            
            # Determine user role
            user_role = 'admin' if user.is_staff or user.is_superuser else 'user'
            
            # Determine user status
            if not user.is_active:
                user_status = 'inactive'
            elif hasattr(user, 'is_verified') and not user.is_verified:
                user_status = 'pending'
            else:
                user_status = 'active'
            
            # Build user object
            user_data = {
                'id': str(user.id),
                'name': user.get_full_name() or user.user_name,
                'email': user.email,
                'role': user_role,
                'status': user_status,
                'phone': getattr(user, 'phone', None),
                'company': None,  # Add company field to User model if needed
                'joinedAt': user.date_joined.isoformat(),
                'lastLoginAt': user.last_login.isoformat() if user.last_login else None,
                'totalCalls': user_calls.count(),
                'minutesUsed': total_minutes_used,
                'currentPlan': user_subscription.plan.name if user_subscription else "No Plan",
                'billingStatus': self._get_billing_status(user_subscription),
                'avatar': self._get_avatar_url(user),
                'profile': self._get_user_profile(user)
            }
            
            # Get call history (last 100 calls)
            call_history = self._get_call_history(user_calls[:100])
            
            # Get billing history
            billing_history = self._get_billing_history(user)
            
            # Get activity logs (mock for now - implement based on your logging system)
            activity_logs = self._get_activity_logs(user)
            
            # Calculate analytics
            analytics = self._calculate_analytics(user, user_calls)
            
            response_data = {
                'user': user_data,
                'callHistory': call_history,
                'billingHistory': billing_history,
                'activityLogs': activity_logs,
                'analytics': analytics
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': f'Error fetching user details: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _get_avatar_url(self, user):
        """Safely get user avatar URL"""
        try:
            # First check if the user has an avatar field
            if not hasattr(user, 'avatar'):
                return None
            
            # Check the value from the database directly without triggering file access
            avatar_field = user._meta.get_field('avatar')
            avatar_value = getattr(user, avatar_field.attname, None)  # Get the raw field value
            
            # If there's no file name stored, return None
            if not avatar_value:
                return None
            
            # Now safely try to get the URL
            return user.avatar.url
        except (ValueError, AttributeError, OSError):
            return None
    
    def _get_billing_status(self, subscription):
        """Determine billing status from subscription"""
        if not subscription:
            return 'cancelled'
        
        if subscription.status == 'active':
            # Check if payment is overdue (you might need to implement this logic)
            return 'active'
        elif subscription.status == 'past_due':
            return 'overdue'
        else:
            return 'cancelled'
    
    def _get_user_profile(self, user):
        """Get user profile information"""
        # If you have a separate Profile model, get it here
        # For now, return default values
        return {
            'bio': getattr(user, 'bio', None),
            'timezone': getattr(user, 'timezone', 'UTC'),
            'language': getattr(user, 'language', 'en'),
            'notifications': {
                'email': True,  # Default values - implement based on your preferences system
                'sms': False,
                'push': True,
            }
        }
    
    def _get_call_history(self, calls):
        """Convert TwilioCall objects to CallRecord format"""
        call_records = []
        
        for call in calls:
            # Map call status
            if call.status == 'completed':
                mapped_status = 'completed'
            elif call.status in ['no_answer', 'busy']:
                mapped_status = 'missed'
            else:
                mapped_status = 'failed'
            
            # Map call direction
            call_type = 'inbound' if call.direction == 'inbound' else 'outbound'
            
            # Calculate cost (implement your pricing logic)
            cost = self._calculate_call_cost(call)
            
            # Get transcript if available
            transcript = None
            conversation = ConversationLog.objects.filter(call=call).first()
            if conversation:
                transcript = conversation.message[:500] + "..." if len(conversation.message) > 500 else conversation.message
            
            call_record = {
                'id': str(call.id),
                'date': call.started_at.isoformat() if call.started_at else call.created_at.isoformat(),
                'duration': call.duration,
                'type': call_type,
                'status': mapped_status,
                'phoneNumber': call.to_number if call_type == 'outbound' else call.from_number,
                'cost': cost,
                'transcript': transcript
            }
            
            call_records.append(call_record)
        
        return call_records
    
    def _calculate_call_cost(self, call):
        """Calculate cost for a call based on duration and rates"""
        # Implement your pricing logic here
        # Example: $0.02 per minute
        minutes = call.duration / 60 if call.duration else 0
        cost_per_minute = 0.02
        return round(minutes * cost_per_minute, 2)
    
    def _get_billing_history(self, user):
        """Get user's billing history from local DB and Stripe if needed"""
        billing_records = []
        
        # First, get from local BillingHistory model (through subscription)
        billing_history = BillingHistory.objects.filter(subscription__user=user).order_by('-created_at')[:50]
        
        for record in billing_history:
            billing_record = {
                'id': str(record.id),
                'date': record.created_at.isoformat(),
                'amount': float(record.amount),
                'type': record.transaction_type or 'charge',
                'status': record.status or 'paid',
                'description': record.description or f"Billing for {record.billing_period}",
                'invoice': getattr(record, 'invoice_url', None)
            }
            billing_records.append(billing_record)
        
        # If no local billing history, fetch from Stripe
        if not billing_records and hasattr(user, 'stripe_customer_id') and user.stripe_customer_id:
            stripe_billing = self._get_stripe_billing_history(user)
            billing_records.extend(stripe_billing)
        
        return billing_records
    
    def _get_stripe_billing_history(self, user):
        """Fetch billing history from Stripe API"""
        stripe_records = []
        
        try:
            import stripe
            from django.conf import settings
            
            # Set Stripe API key
            stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', None)
            
            if not stripe.api_key:
                print("Warning: STRIPE_SECRET_KEY not configured")
                return []
            
            # Get charges for this customer
            charges = stripe.Charge.list(
                customer=user.stripe_customer_id,
                limit=50
            )
            
            for charge in charges.data:
                # Map Stripe charge status to our status
                if charge.status == 'succeeded':
                    status = 'paid'
                elif charge.status == 'pending':
                    status = 'pending'
                else:
                    status = 'failed'
                
                # Determine transaction type
                transaction_type = 'refund' if charge.refunded else 'charge'
                
                stripe_record = {
                    'id': f"stripe_{charge.id}",
                    'date': timezone.datetime.fromtimestamp(charge.created).isoformat(),
                    'amount': charge.amount / 100,  # Convert from cents to dollars
                    'type': transaction_type,
                    'status': status,
                    'description': charge.description or f"Stripe charge {charge.id[:8]}",
                    'invoice': charge.receipt_url
                }
                stripe_records.append(stripe_record)
            
            # Get invoices for this customer
            invoices = stripe.Invoice.list(
                customer=user.stripe_customer_id,
                limit=25
            )
            
            for invoice in invoices.data:
                # Map invoice status
                if invoice.status == 'paid':
                    status = 'paid'
                elif invoice.status == 'open':
                    status = 'pending'
                else:
                    status = 'failed'
                
                invoice_record = {
                    'id': f"stripe_inv_{invoice.id}",
                    'date': timezone.datetime.fromtimestamp(invoice.created).isoformat(),
                    'amount': invoice.amount_paid / 100,
                    'type': 'charge',
                    'status': status,
                    'description': f"Invoice {invoice.number or invoice.id[:8]} - {invoice.description or 'Subscription'}",
                    'invoice': invoice.invoice_pdf
                }
                stripe_records.append(invoice_record)
            
            # Sort by date (newest first)
            stripe_records.sort(key=lambda x: x['date'], reverse=True)
            
            print(f"✅ Retrieved {len(stripe_records)} billing records from Stripe for user {user.email}")
            
        except ImportError:
            print("Warning: stripe library not installed. Run: pip install stripe")
        except Exception as e:
            print(f"Error fetching Stripe billing history: {str(e)}")
        
        return stripe_records[:30]  # Return max 30 records
    
    def _get_activity_logs(self, user):
        """Get user activity logs"""
        # This is a mock implementation
        # You should implement based on your actual logging system
        activity_logs = []
        
        # Example activity logs based on user's recent actions
        recent_calls = TwilioCall.objects.filter(user=user).order_by('-created_at')[:10]
        
        for call in recent_calls:
            activity = {
                'id': f"call_{call.id}",
                'timestamp': call.created_at.isoformat(),
                'action': f"Made {call.direction} call",
                'details': f"Call to {call.to_number if call.direction == 'outbound' else call.from_number}",
                'ipAddress': None,  # Would need to be stored during call creation
                'userAgent': None,  # Would need to be stored during call creation
                'status': 'success' if call.status == 'completed' else ('warning' if call.status in ['no_answer', 'busy'] else 'error')
            }
            activity_logs.append(activity)
        
        return activity_logs[:20]  # Return last 20 activities
    
    def _calculate_analytics(self, user, user_calls):
        """Calculate user analytics"""
        # Total spent (from billing history)
        billing_history = BillingHistory.objects.filter(subscription__user=user)
        total_spent = billing_history.aggregate(total=Sum('amount'))['total'] or 0
        
        # Average call duration
        completed_calls = user_calls.filter(status='completed')
        avg_duration = completed_calls.aggregate(avg=Avg('duration'))['avg'] or 0
        avg_duration_minutes = round(avg_duration / 60, 2) if avg_duration else 0
        
        # Success rate
        total_calls = user_calls.count()
        successful_calls = completed_calls.count()
        success_rate = (successful_calls / total_calls * 100) if total_calls > 0 else 0
        
        # Most active day
        most_active_day = self._get_most_active_day(user_calls)
        
        # Calls by month (last 12 months)
        calls_by_month = self._get_calls_by_month(user_calls)
        
        return {
            'totalSpent': float(total_spent),
            'avgCallDuration': avg_duration_minutes,
            'successRate': round(success_rate, 2),
            'mostActiveDay': most_active_day,
            'callsByMonth': calls_by_month
        }
    
    def _get_most_active_day(self, user_calls):
        """Find the day of week with most calls"""
        from django.db.models import Case, When, IntegerField
        
        # Annotate calls with day of week
        calls_by_weekday = user_calls.extra(
            select={'weekday': "strftime('%%w', started_at)"}
        ).values('weekday').annotate(
            count=Count('id')
        ).order_by('-count')
        
        if calls_by_weekday:
            weekday_num = calls_by_weekday[0]['weekday']
            weekdays = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
            return weekdays[int(weekday_num)]
        
        return 'No data'
    
    def _get_calls_by_month(self, user_calls):
        """Get calls grouped by month for last 12 months"""
        calls_by_month = []
        current_date = timezone.now().date()
        
        for i in range(12):
            # Calculate month
            if i == 0:
                month_start = current_date.replace(day=1)
                month_end = current_date
            else:
                month_date = current_date.replace(day=1) - timedelta(days=i*30)
                month_start = month_date.replace(day=1)
                # Get last day of month
                if month_start.month == 12:
                    month_end = month_start.replace(year=month_start.year+1, month=1, day=1) - timedelta(days=1)
                else:
                    month_end = month_start.replace(month=month_start.month+1, day=1) - timedelta(days=1)
            
            # Count calls for this month
            month_calls = user_calls.filter(
                started_at__date__gte=month_start,
                started_at__date__lte=month_end
            ).count()
            
            calls_by_month.append({
                'month': month_start.strftime('%b %Y'),
                'calls': month_calls
            })
        
        return list(reversed(calls_by_month))  # Oldest first
    
    def _get_stripe_billing_history(self, user):
        """Get billing history from Stripe if available"""
        try:
            import stripe
            from django.conf import settings
            
            stripe.api_key = settings.STRIPE_SECRET_KEY
            
            # Get customer from Stripe
            if hasattr(user, 'stripe_customer_id') and user.stripe_customer_id:
                charges = stripe.Charge.list(customer=user.stripe_customer_id, limit=20)
                
                stripe_records = []
                for charge in charges.data:
                    record = {
                        'id': f"stripe_{charge.id}",
                        'date': datetime.fromtimestamp(charge.created).isoformat(),
                        'amount': charge.amount / 100,  # Convert from cents
                        'type': 'refund' if charge.refunded else 'charge',
                        'status': 'paid' if charge.paid else 'failed',
                        'description': charge.description or f"Charge for {charge.amount / 100}",
                        'invoice': getattr(charge, 'invoice', None)
                    }
                    stripe_records.append(record)
                
                return stripe_records
                
        except Exception as e:
            # If Stripe fails, return empty list
            print(f"Stripe billing history error: {e}")
            
        return []


class AdminUserStatusAPIView(APIView):
    """
    Admin API to update user status
    PATCH: Updates user status (active/inactive/banned/pending)
    """
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    
    @swagger_auto_schema(
        tags=['Admin'],
        operation_summary="Update User Status",
        operation_description="Update user status (active/inactive/banned/pending)",
        manual_parameters=[
            openapi.Parameter('userId', openapi.IN_PATH, description="User ID", type=openapi.TYPE_STRING)
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'status': openapi.Schema(
                    type=openapi.TYPE_STRING, 
                    enum=['active', 'inactive', 'banned', 'pending'],
                    description="New user status"
                )
            },
            required=['status']
        ),
        responses={
            200: openapi.Response(
                description="Status updated successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'user': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'id': openapi.Schema(type=openapi.TYPE_STRING),
                                'name': openapi.Schema(type=openapi.TYPE_STRING),
                                'email': openapi.Schema(type=openapi.TYPE_STRING),
                                'status': openapi.Schema(type=openapi.TYPE_STRING)
                            }
                        )
                    }
                )
            ),
            400: "Bad request - Invalid status",
            401: "Unauthorized - Authentication required",
            403: "Forbidden - Admin access required",
            404: "User not found"
        }
    )
    def patch(self, request, userId):
        """Update user status"""
        try:
            user = get_object_or_404(User, id=userId)
            data = request.data
            
            if 'status' not in data:
                return Response(
                    {'error': 'Status field is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            new_status = data['status']
            valid_statuses = ['active', 'inactive', 'banned', 'pending']
            
            if new_status not in valid_statuses:
                return Response(
                    {'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Update user status based on the value
            if new_status == 'active':
                user.is_active = True
            elif new_status in ['inactive', 'banned', 'pending']:
                user.is_active = False
            
            # Store the specific status (you might want to add a status field to your User model)
            # For now, we'll use is_active and you can extend this with a custom status field
            user.save()
            
            return Response({
                'message': f'User status updated to {new_status}',
                'user': {
                    'id': str(user.id),
                    'name': user.get_full_name() or user.user_name,
                    'email': user.email,
                    'status': new_status
                }
            })
            
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Status update failed: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )



class AdminUserAPIView(APIView):
    """
    Admin API to get and update user details
    GET: Returns user details in simplified format
    PATCH: Updates user details
    """
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    
    @swagger_auto_schema(
        tags=['Admin'],
        operation_summary="Get User",
        operation_description="Get user details in simplified format for admin dashboard",
        manual_parameters=[
            openapi.Parameter('userId', openapi.IN_PATH, description="User ID", type=openapi.TYPE_STRING)
        ],
        responses={
            200: openapi.Response(
                description="User details",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_STRING),
                        'name': openapi.Schema(type=openapi.TYPE_STRING),
                        'email': openapi.Schema(type=openapi.TYPE_STRING),
                        'role': openapi.Schema(type=openapi.TYPE_STRING, enum=['admin', 'user']),
                        'status': openapi.Schema(type=openapi.TYPE_STRING, enum=['active', 'inactive', 'banned', 'pending']),
                        'phone': openapi.Schema(type=openapi.TYPE_STRING),
                        'company': openapi.Schema(type=openapi.TYPE_STRING),
                        'joinedAt': openapi.Schema(type=openapi.TYPE_STRING),
                        'lastLoginAt': openapi.Schema(type=openapi.TYPE_STRING),
                        'totalCalls': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'minutesUsed': openapi.Schema(type=openapi.TYPE_NUMBER),
                        'currentPlan': openapi.Schema(type=openapi.TYPE_STRING),
                        'billingStatus': openapi.Schema(type=openapi.TYPE_STRING, enum=['active', 'overdue', 'cancelled']),
                        'avatar': openapi.Schema(type=openapi.TYPE_STRING),
                        'profile': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'bio': openapi.Schema(type=openapi.TYPE_STRING),
                                'timezone': openapi.Schema(type=openapi.TYPE_STRING),
                                'language': openapi.Schema(type=openapi.TYPE_STRING),
                                'notifications': openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        'email': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                        'sms': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                        'push': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                    }
                                )
                            }
                        )
                    }
                )
            ),
            401: "Unauthorized - Authentication required",
            403: "Forbidden - Admin access required", 
            404: "User not found"
        }
    )
    def get(self, request, userId):
        """Get user details for admin dashboard"""
        try:
            user = get_object_or_404(User, id=userId)
            
            # Get user's subscription
            subscription = Subscription.objects.filter(user=user).first()
            
            # Get call statistics
            calls = TwilioCall.objects.filter(user=user)
            total_calls = calls.count()
            total_duration = calls.aggregate(Sum('duration'))['duration__sum'] or 0
            minutes_used = total_duration / 60
            
            # Get billing status
            billing_status = self._get_billing_status(subscription)
            
            # Get current plan (convert to string)
            current_plan = subscription.plan.name if subscription and subscription.plan else "Free"
            
            response_data = {
            'id': str(user.id),
            'name': user.get_full_name() or user.user_name,
            'email': user.email,
            'role': 'admin' if user.is_staff else 'user',
            'status': 'active' if user.is_active else 'inactive',
            'phone': getattr(user, 'phone_number', None),
            'company': getattr(user, 'company', None),
            'joinedAt': user.date_joined.isoformat(),
            'lastLoginAt': user.last_login.isoformat() if user.last_login else None,
            'totalCalls': total_calls,
            'minutesUsed': round(minutes_used, 2),
            'currentPlan': current_plan,
            'billingStatus': billing_status,
            'avatar': self._get_avatar_url(user),
            'profile': self._get_user_profile(user)
        }
        
            return Response(response_data)
            
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Internal server error: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @swagger_auto_schema(
        tags=['Admin'],
        operation_summary="Update User",
        operation_description="Update user details",
        manual_parameters=[
            openapi.Parameter('userId', openapi.IN_PATH, description="User ID", type=openapi.TYPE_STRING)
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING),
                'email': openapi.Schema(type=openapi.TYPE_STRING),
                'phone': openapi.Schema(type=openapi.TYPE_STRING),
                'company': openapi.Schema(type=openapi.TYPE_STRING),
                'role': openapi.Schema(type=openapi.TYPE_STRING, enum=['admin', 'user']),
                'status': openapi.Schema(type=openapi.TYPE_STRING, enum=['active', 'inactive', 'banned', 'pending']),
                'currentPlan': openapi.Schema(type=openapi.TYPE_STRING),
                'billingStatus': openapi.Schema(type=openapi.TYPE_STRING),
                'bio': openapi.Schema(type=openapi.TYPE_STRING),
                'timezone': openapi.Schema(type=openapi.TYPE_STRING),
                'language': openapi.Schema(type=openapi.TYPE_STRING),
                'notifications': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'email': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'sms': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'push': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    }
                )
            }
        ),
        responses={
            200: "User updated successfully",
            400: "Bad request - Validation error",
            401: "Unauthorized - Authentication required",
            403: "Forbidden - Admin access required",
            404: "User not found"
        }
    )
    def patch(self, request, userId):
        """Update user details"""
        try:
            user = get_object_or_404(User, id=userId)
            data = request.data
            
            # Update basic user fields
            if 'name' in data:
                # Split name into first_name and last_name if possible
                name_parts = data['name'].strip().split(' ', 1)
                user.first_name = name_parts[0]
                user.last_name = name_parts[1] if len(name_parts) > 1 else ''
                user.user_name = data['name']
            
            if 'email' in data:
                user.email = data['email']
            
            if 'phone' in data:
                user.phone_number = data['phone']
            
            if 'company' in data:
                user.company = data['company']
            
            if 'role' in data:
                user.is_staff = data['role'] == 'admin'
                user.is_superuser = data['role'] == 'admin'
            
            if 'status' in data:
                user.is_active = data['status'] == 'active'
            
            # Update profile fields
            if 'bio' in data:
                user.bio = data['bio']
            
            if 'timezone' in data:
                user.timezone = data['timezone']
            
            if 'language' in data:
                user.language = data['language']
            
            # Handle subscription/plan updates
            if 'currentPlan' in data:
                subscription = Subscription.objects.filter(user=user).first()
                if subscription:
                    from subscriptions.models import SubscriptionPlan
                    try:
                        plan = SubscriptionPlan.objects.get(name=data['currentPlan'])
                        subscription.plan = plan
                        subscription.save()
                    except SubscriptionPlan.DoesNotExist:
                        pass
            
            user.save()
            
            return Response({
                'message': 'User updated successfully',
                'user': {
                    'id': str(user.id),
                    'name': user.get_full_name() or user.user_name,
                    'email': user.email,
                    'company': getattr(user, 'company', None)
                }
            })
            
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Update failed: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @swagger_auto_schema(
        tags=['Admin'],
        operation_summary="Delete User",
        operation_description="Permanently delete a user and all associated data",
        manual_parameters=[
            openapi.Parameter('userId', openapi.IN_PATH, description="User ID", type=openapi.TYPE_STRING)
        ],
        responses={
            200: openapi.Response(
                description="User deleted successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'deleted_user': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'id': openapi.Schema(type=openapi.TYPE_STRING),
                                'name': openapi.Schema(type=openapi.TYPE_STRING),
                                'email': openapi.Schema(type=openapi.TYPE_STRING)
                            }
                        )
                    }
                )
            ),
            401: "Unauthorized - Authentication required",
            403: "Forbidden - Admin access required", 
            404: "User not found",
            400: "Cannot delete admin user"
        }
    )
    def delete(self, request, userId):
        """Delete user"""
        try:
            user = get_object_or_404(User, id=userId)
            
            # Prevent deletion of admin users (safety measure)
            if user.is_staff or user.is_superuser:
                return Response(
                    {'error': 'Cannot delete admin users'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Store user info before deletion
            deleted_user_info = {
                'id': str(user.id),
                'name': user.get_full_name() or user.user_name,
                'email': user.email
            }
            
            # Delete the user (this will cascade delete related objects)
            user.delete()
            
            return Response({
                'message': 'User deleted successfully',
                'deleted_user': deleted_user_info
            })
            
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Delete failed: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def _get_billing_status(self, subscription):
        """Determine billing status from subscription"""
        if not subscription:
            return 'cancelled'
        
        if subscription.status == 'active':
            return 'active'
        elif subscription.status == 'past_due':
            return 'overdue'
        else:
            return 'cancelled'
    
    def _get_user_profile(self, user):
        """Get user profile information"""
        return {
            'bio': getattr(user, 'bio', None),
            'timezone': getattr(user, 'timezone', 'UTC'),
            'language': getattr(user, 'language', 'en'),
            'notifications': {
                'email': True,
                'sms': False,
                'push': True,
            }
        }
    
    def _get_avatar_url(self, user):
        """Safely get user avatar URL"""
        try:
            if hasattr(user, 'avatar') and user.avatar:
                if hasattr(user.avatar, 'url'):
                    return user.avatar.url
            return None
        except (ValueError, AttributeError):
            return None