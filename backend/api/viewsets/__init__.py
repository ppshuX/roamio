"""
Viewsets 包
将大型 viewsets.py 拆分为多个模块
"""
from .auth_viewset import AuthViewSet
from .user_viewset import UserViewSet
from .comment_viewset import CommentViewSet, CommentFilter
from .trip_viewset import TripViewSet
from .trip_plan_viewset import TripPlanViewSet
from .event_viewset import TripEventViewSet

__all__ = [
    'AuthViewSet',
    'UserViewSet',
    'CommentViewSet',
    'CommentFilter',
    'TripViewSet',
    'TripPlanViewSet',
    'TripEventViewSet',
]
