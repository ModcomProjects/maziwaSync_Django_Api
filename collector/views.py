from core.serializers import MilkCollectionSerializer, NoticeSerializer, RecentCollectionSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status,generics
from rest_framework.views import APIView


from django.utils import timezone
from django.db.models import Sum

from core.models import FarmerProfile, Notice, PorterProfile, MilkCollection


from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from core.models import MilkCollection

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def PorterDashboardView(request):
    try:
        porter = request.user.porter_profile
    except PorterProfile.DoesNotExist:
        return Response({"error": "Only porters can access this dashboard."}, status=403)

    today = timezone.now().date()
    week_start = today - timedelta(days=7)
    month_start = today.replace(day=1)

    # Today collections
    today_collections = MilkCollection.objects.filter(porter=porter, collection_date=today)
    total_collections_today = today_collections.count()
    total_liters_today = today_collections.aggregate(total=Sum("liters"))["total"] or 0
    total_amount_today = today_collections.aggregate(total=Sum("total_amount"))["total"] or 0

    # Weekly and monthly totals
    weekly_collections = MilkCollection.objects.filter(porter=porter, collection_date__gte=week_start)
    monthly_collections = MilkCollection.objects.filter(porter=porter, collection_date__gte=month_start)
    total_liters_week = weekly_collections.aggregate(total=Sum("liters"))["total"] or 0
    total_liters_month = monthly_collections.aggregate(total=Sum("liters"))["total"] or 0

    # Last 5 collections
    last_collections = MilkCollection.objects.filter(porter=porter).order_by("-created_at")[:5]

    # Serialize multiple MilkCollection records.
    # Since last_collections is a QuerySet (multiple objects),
    # we must set many=True so DRF serializes each collection individually.
    # Without many=True, DRF treats the QuerySet as a single object and
    # raises errors when trying to access fields like farmer, liters, etc.
    last_collections_list = RecentCollectionSerializer(
        last_collections,
        many=True
    ).data  # .data returns the serialized JSON-ready representation of the QuerySet

    response_data = {
        "date": today,
        "assigned_farmers": porter.assigned_farmers.count(),
        "total_collections_today": total_collections_today,
        "total_liters_today": total_liters_today,
        "total_amount_today": total_amount_today,
        "total_liters_week": total_liters_week,
        "total_liters_month": total_liters_month,
        "last_collections": last_collections_list,
        "porter_name": f"{porter.first_name} {porter.last_name}",
        "employee_id": porter.employee_id,
        "route_name": porter.route_name,
    }

    return Response(response_data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def AddMilkCollection(request):

    # Get logged-in porter
    try:
        porter = request.user.porter_profile
    except PorterProfile.DoesNotExist:
        return Response(
            {"error": "Only porters can add milk collections."},
            status=status.HTTP_403_FORBIDDEN
        )

    farmer_code = request.data.get('farmer_code')

    try:
        farmer = FarmerProfile.objects.get(
            membership_number=farmer_code
        )
    except FarmerProfile.DoesNotExist:
        return Response(
            {"error": "Farmer not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    collection = MilkCollection.objects.create(
        farmer=farmer,
        porter=porter,
        liters=request.data.get('liters'),
        session=request.data.get('session')
    )

    return Response({
        "message": "Milk collection recorded successfully.",
        "collection_id": collection.id,
        "farmer": f"{farmer.first_name} {farmer.last_name}",
        "porter": f"{porter.first_name} {porter.last_name}",
        "liters": collection.liters
    }, status=status.HTTP_201_CREATED)




class MyCollectionsView(generics.ListAPIView):
    serializer_class = MilkCollectionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        porter = self.request.user.porter_profile

        collections = (
            MilkCollection.objects
            .filter(porter=porter)
            .select_related('farmer')
            .order_by('-created_at')
        )

        return collections
    

class PorterNoticeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        notices = Notice.objects.filter(
            target__in=['ALL', 'PORTERS']
        ).order_by('-created_at')

        serializer = NoticeSerializer(notices, many=True)

        return Response(serializer.data)