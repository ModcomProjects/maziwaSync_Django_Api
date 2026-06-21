from django.contrib import admin
from .models import User, FarmerProfile, PorterProfile, MilkCollection, Feedback, Notice, Payment

# Register Custom User
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'phone_number', 'is_staff')
    list_filter = ('role', 'is_staff')

# Register FarmerProfile
@admin.register(FarmerProfile)
class FarmerProfileAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'phone_number', 'farm_name', 'total_milk_delivered')
    search_fields = ('first_name', 'last_name', 'phone_number', 'national_id')

# Register PorterProfile
@admin.register(PorterProfile)
class PorterProfileAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'employee_id', 'route_name', 'total_collections')
    search_fields = ('first_name', 'last_name', 'employee_id')

# Register MilkCollection
@admin.register(MilkCollection)
class MilkCollectionAdmin(admin.ModelAdmin):
    list_display = ('farmer', 'liters', 'session', 'collection_date', 'total_amount')
    list_filter = ('session', 'collection_date')

# Register Feedback
@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('title', 'farmer', 'status', 'created_at')
    list_filter = ('status',)

# Register Notice
@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ('title', 'target', 'is_important', 'created_at')
    list_filter = ('target', 'is_important')

# Register Payment
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('farmer', 'amount', 'payment_method', 'status', 'payment_date')
    list_filter = ('status', 'payment_method')