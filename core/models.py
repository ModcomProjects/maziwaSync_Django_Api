from django.db import models
from django.contrib.auth.models import AbstractUser

# ============================================================
# CUSTOM USER MODEL (First - before any profile uses it)
# ============================================================

class User(AbstractUser):
    """Custom User model with role-based access"""
    ROLE_CHOICES = (
        ('farmer', 'Farmer'),
        ('porter', 'Porter'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='farmer')
    phone_number = models.CharField(max_length=15, unique=True)
    
    def __str__(self):
        return f"{self.username} ({self.role})"


# ============================================================
# BASE ABSTRACT MODEL
# ============================================================

class BaseModel(models.Model):
    """Abstract base model with common timestamp fields"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True


# ============================================================
# FARMER PROFILE
# ============================================================

class FarmerProfile(BaseModel):
    """Complete farmer profile - all information a cooperative needs"""
    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='farmer_profile'
    )
    
    # Personal Information
    profile_image = models.ImageField(
        upload_to='farmers/profiles/', 
        null=True, 
        blank=True
    )
    national_id = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=10, 
        choices=[('MALE', 'Male'), ('FEMALE', 'Female')], 
        null=True, 
        blank=True
    )
    
    # Contact Information
    phone_number = models.CharField(max_length=15, unique=True)
    alternate_phone = models.CharField(max_length=15, blank=True, null=True)
    email_address = models.EmailField(blank=True, null=True)
    
    # Farm Information
    farm_name = models.CharField(max_length=200, blank=True, null=True)
    farm_size_acres = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    number_of_cows = models.IntegerField(default=0)
    membership_number = models.CharField(max_length=50, unique=True, blank=True, null=True)
    join_date = models.DateField(auto_now_add=True)
    
    # Banking Information
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    bank_branch = models.CharField(max_length=100, blank=True, null=True)
    account_number = models.CharField(max_length=50, blank=True, null=True)
    mpesa_number = models.CharField(max_length=15, blank=True, null=True)
    
    # Statistics (auto-updated by system)
    total_milk_delivered = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_earnings = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"


# ============================================================
# PORTER PROFILE
# ============================================================

class PorterProfile(BaseModel):
    """Porter/Collector profile"""
    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='porter_profile'
    )
    profile_image = models.ImageField(
        upload_to='porters/profiles/', 
        null=True, 
        blank=True
    )
    employee_id = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, unique=True)
    national_id = models.CharField(max_length=20, unique=True)
    route_name = models.CharField(max_length=200)
    assigned_farmers = models.ManyToManyField(
        FarmerProfile, 
        related_name='assigned_porters', 
        blank=True
    )
    hire_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    total_collections = models.IntegerField(default=0)
    total_liters_collected = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.employee_id}"


# ============================================================
# MILK COLLECTION
# ============================================================

class MilkCollection(BaseModel):
    """Daily milk collection record"""
    
    SESSION_CHOICES = [
        ('MORNING', 'Morning'),
        ('EVENING', 'Evening'),
    ]
    
    farmer = models.ForeignKey(FarmerProfile, on_delete=models.CASCADE, related_name='collections')
    porter = models.ForeignKey(PorterProfile,on_delete=models.CASCADE,related_name='collections')
    liters = models.DecimalField(max_digits=10, decimal_places=2)
    session = models.CharField(max_length=10, choices=SESSION_CHOICES)
    collection_date = models.DateField(auto_now_add=True)
    price_per_liter = models.DecimalField(max_digits=8, decimal_places=2, default=50.00)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    
    def __str__(self):
        return f"{self.collection_date}: {self.farmer.first_name} - {self.liters}L"
    
    def save(self, *args, **kwargs):
        self.total_amount = self.liters * self.price_per_liter
        super().save(*args, **kwargs)


# ============================================================
# FEEDBACK
# ============================================================

class Feedback(BaseModel):
    """Farmer complaints tracking"""
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('RESOLVED', 'Resolved'),
        ('REJECTED', 'Rejected'),
    ]
    
    farmer = models.ForeignKey(
        FarmerProfile, 
        on_delete=models.CASCADE, 
        related_name='feedbacks'
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    resolved_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    
    def __str__(self):
        return self.title


# ============================================================
# NOTICE / ANNOUNCEMENT
# ============================================================

class Notice(BaseModel):
    """System announcements for different user groups"""
    
    TARGET_CHOICES = [
        ('ALL', 'All Users'),
        ('FARMERS', 'Farmers Only'),
        ('PORTERS', 'Porters Only'),
    ]
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    target = models.CharField(max_length=10, choices=TARGET_CHOICES, default='ALL')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    is_important = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title


# ============================================================
# PAYMENT
# ============================================================

class Payment(BaseModel):
    """Payment records for milk deliveries"""
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]
    
    METHOD_CHOICES = [
        ('MPESA', 'M-Pesa'),
        ('CASH', 'Cash'),
    ]
    
    farmer = models.ForeignKey(
        FarmerProfile, 
        on_delete=models.CASCADE, 
        related_name='payments'
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=10, choices=METHOD_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    originator_conversation_id = models.CharField(max_length=100, unique=True, blank=True, null=True)
    transaction_ref = models.CharField(max_length=100, unique=True)
    payment_date = models.DateTimeField()
    
    def __str__(self):
        return f"{self.transaction_ref} - KES {self.amount}"