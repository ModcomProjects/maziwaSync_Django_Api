from rest_framework import serializers
from core.models import MilkCollection, Feedback,FarmerProfile, Notice, PorterProfile

# potters serializer for milk collection

class MilkCollectionSerializer(serializers.ModelSerializer):
    farmer_name = serializers.SerializerMethodField()
    farmer_code = serializers.CharField(
        source='farmer.membership_number',
        read_only=True
    )

    class Meta:
        model = MilkCollection
        fields = [
            'id',
            'farmer_code',
            'farmer_name',
            'liters',
            'session',
            'total_amount',
            'collection_date',
        ]

    def get_farmer_name(self, obj):
        return f"{obj.farmer.first_name} {obj.farmer.last_name}"
    



# Farmers Serializer 

# ============================================================
# FARMER COLLECTIONS
# ============================================================

class MilkCollectionSerializer(serializers.ModelSerializer):
    porter_name = serializers.SerializerMethodField()

    class Meta:
        model = MilkCollection
        fields = [
            'id',
            'liters',
            'session',
            'price_per_liter',
            'total_amount',
            'collection_date',
            'porter_name',
        ]

    def get_porter_name(self, obj):
        return f"{obj.porter.first_name} {obj.porter.last_name}"


# ============================================================
# FEEDBACK
# ============================================================

class FeedbackSerializer(serializers.ModelSerializer):

    class Meta:
        model = Feedback

        fields = [
            'id',
            'title',
            'description',  # change to 'message' if you renamed it
            'status',
            'created_at',
            'updated_at',
        ]

        read_only_fields = [
            'status',
            'created_at',
            'updated_at',
        ]



class FarmerSerializer(serializers.ModelSerializer):

    class Meta:
        model = FarmerProfile
        fields = '__all__'


class PorterSerializer(serializers.ModelSerializer):

    class Meta:
        model = PorterProfile
        fields = '__all__'



class NoticeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notice
        fields = '__all__'
        read_only_fields = ['created_by']


# serializer for porters dashboard
class RecentCollectionSerializer(serializers.ModelSerializer):
    farmer_name = serializers.SerializerMethodField()

    class Meta:
        model = MilkCollection
        fields = [
            "id",
            "farmer_name",
            "liters",
            "session",
            "collection_date",
            "total_amount",
        ]

    def get_farmer_name(self, obj):
        return f"{obj.farmer.first_name} {obj.farmer.last_name}"