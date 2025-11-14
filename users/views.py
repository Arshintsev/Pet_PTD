from knowledge.models import Question, Topic, UserQuestionProgress
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from users.serializers import ProfileStatsSerializer


class ProfileViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def stats(self, request):
        user = request.user

        # Сколько вопросов изучено
        questions_learned = UserQuestionProgress.objects.filter(user=user,
                                                                is_learned=True).count()

        # Сколько тем полностью изучено
        topics_learned = 0
        for topic in Topic.objects.all():
            total_questions = Question.objects.filter(topic=topic,
                                                      is_active=True).count()
            learned_questions = UserQuestionProgress.objects.filter(
                user=user,
                question__topic=topic,
                is_learned=True
            ).count()
            if total_questions > 0 and learned_questions == total_questions:
                topics_learned += 1

        # уровень прогресса
        total_questions_all = Question.objects.filter(is_active=True).count()
        progress = f"{int((questions_learned / total_questions_all * 100)
                          if total_questions_all else 0)}%"

        serializer = ProfileStatsSerializer({
            "questions_learned": questions_learned,
            "topics_learned": topics_learned,
            "progress": progress
        })
        return Response(serializer.data)
