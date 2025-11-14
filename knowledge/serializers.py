from rest_framework import serializers
from .models import Question, Topic, UserQuestionProgress


class TopicSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Topic."""

    class Meta:
        model = Topic
        fields = ('id', 'title', 'description')


class QuestionSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Question с информацией о прогрессе пользователя."""

    topic = TopicSerializer(read_only=True)
    is_learned = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ('id', 'title', 'description', 'difficulty', 'topic', 'is_learned')

    def get_is_learned(self, obj: Question) -> bool:
        """
        Возвращает True, если пользователь выучил вопрос, иначе False.
        Проверка через атрибут obj.user_learned или модель UserQuestionProgress.
        """
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False

        if hasattr(obj, 'user_learned'):
            return bool(obj.user_learned)

        return UserQuestionProgress.objects.filter(
            user=request.user,
            question=obj,
            is_learned=True
        ).exists()
