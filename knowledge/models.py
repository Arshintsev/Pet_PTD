from django.db import models
from django.db.models import PROTECT
from users.models import User


class Question(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Легкий'),
        ('medium', 'Средний'),
        ('hard', 'Сложный'),
    ]
    title = models.CharField(
        max_length=255,
        unique=True,
        verbose_name= "Вопрос"
    )
    description = models.TextField(blank=True, verbose_name="Описание")
    is_active = models.BooleanField(default=True, verbose_name="Активный")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата изменения")
    topic = models.ForeignKey(
        'Topic',
        on_delete=PROTECT,
        related_name='questions',
        verbose_name = "Тема")
    difficulty = models.CharField(
        max_length=10,
        choices=DIFFICULTY_CHOICES,
        default='medium',
        verbose_name="Сложность"
    )

    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"

    def __str__(self):
        return self.title

    def soft_delete(self):
        if self.is_active:
            self.is_active = False
            self.save(update_fields=['is_active', 'updated_at'])

class Topic(models.Model):
    title = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="Тема"
    )
    description = models.TextField(blank=True, verbose_name="Описание")

    class Meta:
        verbose_name = "Тема"
        verbose_name_plural = "Темы"

    def __str__(self):
        return self.title


class UserQuestionProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    is_learned = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'question')

    def __str__(self):
        return (f"{self.user.email} - {self.question.id} "
                f"({'изучен' if self.is_learned else 'новый'})")
