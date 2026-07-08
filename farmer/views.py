from datetime import date
from django.utils import timezone
from django.db.models import Sum
from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet

from rest_framework.exceptions import PermissionDenied


from core.models import (MilkCollection,Feedback, Notice)

from core.serializers import (MilkCollectionSerializer,FeedbackSerializer, NoticeSerializer)
from farmer.services import CattleAIService


# ============================================================
# FARMER DASHBOARD
# ============================================================

class FarmerDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        farmer = request.user.farmer_profile

        collections = MilkCollection.objects.filter(
            farmer=farmer
        )

        total_collections = collections.count()

        total_liters = collections.aggregate(
            total=Sum('liters')
        )['total'] or 0

        total_amount = collections.aggregate(
            total=Sum('total_amount')
        )['total'] or 0

        today_collection = collections.filter(
            collection_date=date.today()
        ).aggregate(
            total=Sum('liters')
        )['total'] or 0

        current_month = timezone.now().month

        monthly_liters = collections.filter(
            collection_date__month=current_month
        ).aggregate(
            total=Sum('liters')
        )['total'] or 0

        monthly_earnings = collections.filter(
            collection_date__month=current_month
        ).aggregate(
            total=Sum('total_amount')
        )['total'] or 0

        return Response({
            "total_collections": total_collections,
            "total_liters": total_liters,
            "total_amount": total_amount,
            "today_collection":today_collection,
            "monthly_earnings":monthly_earnings,
            "monthly_liters":monthly_liters
        })


# ============================================================
# FARMER COLLECTIONS
# ============================================================

class FarmerCollectionsView(ListAPIView):
    serializer_class = MilkCollectionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        farmer = self.request.user.farmer_profile

        collections = (
            MilkCollection.objects
            .filter(farmer=farmer)
            .select_related('porter')
            .order_by('-created_at')
        )

        return collections


# ============================================================
# FEEDBACK CRUD
# ============================================================

class FeedbackViewSet(ModelViewSet):
    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        try:
            farmer = self.request.user.farmer_profile
        except:
            raise PermissionDenied(
                "Only farmers can access this endpoint."
            )

        feedbacks = Feedback.objects.filter(
            farmer=farmer
        ).order_by('-created_at')

        return feedbacks

    def perform_create(self, serializer):
        farmer = self.request.user.farmer_profile
        serializer.save(farmer=farmer)


    
class FarmerNoticeView(generics.ListAPIView):
    serializer_class = NoticeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        notices=( 
            Notice.objects
            .filter(target__in=['ALL', 'FARMERS'])
            .order_by('-created_at')
        )
        return notices
    


# Instantiate the object once globally when the server boots up

@api_view(['POST'])
@permission_classes([AllowAny])
def predict_disease_view(request):
    print("========== AI PREDICT HIT ==========")
    data = request.data
    print(data)
    
    # Extract matching payload keys
    animal = data.get('Animal', 'cow')
    age = data.get('Age', 0)
    temp = data.get('Temperature', 101.5)
    description = data.get('Description', '')

    ai_service = CattleAIService()
    
    # Process straight through your precise object instance method
    result = ai_service.predict(animal,age,temp,description)
    
    return Response(result)