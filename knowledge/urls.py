from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import QuestionViewSet, TopicViewSet

router = DefaultRouter()
router.register(r'questions', QuestionViewSet, basename='question')
router.register(r'topics', TopicViewSet, basename='topic')

urlpatterns = [
    path('', include(router.urls)),
]
