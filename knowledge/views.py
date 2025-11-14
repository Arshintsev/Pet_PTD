import random

from django.db.models import BooleanField, Exists, OuterRef, Q, Value
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Question, Topic, UserQuestionProgress
from .serializers import QuestionSerializer, TopicSerializer


class QuestionPagination(PageNumberPagination):
    """Пагинация для вопросов."""
    page_size = 9
    page_size_query_param = 'page_size'
    max_page_size = 50


class QuestionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet для модели Question.
    Поддерживает фильтрацию по теме, сложности, поиску и статусу изученности.
    """
    queryset = Question.objects.filter(is_active=True).select_related('topic')
    serializer_class = QuestionSerializer
    permission_classes = [AllowAny]
    pagination_class = QuestionPagination

    def get_queryset(self):
        """Возвращает queryset с аннотацией user_learned и применяет фильтры из query_params."""
        user = self.request.user if self.request.user.is_authenticated else None
        qs = super().get_queryset()

        # Аннотация — изучен ли
        if user:
            learned_subquery = UserQuestionProgress.objects.filter(
                user=user,
                question=OuterRef('pk'),
                is_learned=True
            )
            qs = qs.annotate(user_learned=Exists(learned_subquery))
        else:
            qs = qs.annotate(user_learned=Value(False, output_field=BooleanField()))

        params = self.request.query_params
        topic = params.get('topic')
        difficulty = params.get('difficulty')
        search = params.get('search')
        only_new = self._parse_bool(params.get('only_new'))
        is_learned = self._parse_bool(params.get('is_learned'))

        # Фильтрации
        if topic not in (None, '', 'any', 'all'):
            qs = qs.filter(topic_id=topic)

        if difficulty not in (None, '', 'any', 'all'):
            qs = qs.filter(difficulty=difficulty)

        if search:
            s = search.strip().lower()
            qs = qs.filter(
                Q(title__icontains=s)
                | Q(description__icontains=s)
                | Q(topic__title__icontains=s)
            )

        # Фильтрация по изученности
        if user:
            if only_new is True:
                qs = qs.filter(user_learned=False)
            elif is_learned is not None:
                qs = qs.filter(user_learned=is_learned)

        return qs

    @staticmethod
    def _parse_bool(value):
        """
        Преобразует строку в булево значение.
        Возвращает True/False или None при невозможности преобразования.
        """
        if value is None:
            return None

        v = str(value).strip().lower()
        if v in {'true', '1', 'yes', 'y', 'on'}:
            return True
        if v in {'false', '0', 'no', 'n', 'off'}:
            return False
        return None

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def mark_learned(self, request, pk=None):
        """
        Помечает вопрос как изученный/не изученный для текущего пользователя.
        Ожидает параметр is_learned в POST-запросе.
        """
        question = self.get_object()
        is_learned_value = self._parse_bool(request.data.get('is_learned'))

        if is_learned_value is None:
            return Response(
                {'detail': 'Параметр is_learned должен быть булевым значением.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        progress, _ = UserQuestionProgress.objects.get_or_create(
            user=request.user,
            question=question,
        )
        progress.is_learned = is_learned_value
        progress.save(update_fields=['is_learned', 'updated_at'])

        question.user_learned = progress.is_learned
        serializer = self.get_serializer(question)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def random(self, request):
        """Возвращает случайный невыученный вопрос для текущего пользователя."""
        learned_qs = self.get_queryset().filter(user_learned=False)
        count = learned_qs.count()
        if count == 0:
            return Response({'detail': 'Нет невыученных вопросов'}, status=404)

        random_index = random.randint(0, count - 1)
        question = learned_qs[random_index]
        serializer = self.get_serializer(question)
        return Response(serializer.data)


class TopicViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для модели Topic."""
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    permission_classes = [AllowAny]
