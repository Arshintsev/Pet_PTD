from django.contrib import admin

from .models import Question, Topic


class ShortDescriptionMixin:
    short_description_length = 25
    short_description_field = 'description'

    @admin.display(description='Описание')
    def short_description_col(self, obj):
        value = getattr(obj, self.short_description_field, '')
        return (value[:self.short_description_length] +
                ('...' if len(value) > self.short_description_length else ''))


@admin.register(Question)
class AdminQuestion(admin.ModelAdmin, ShortDescriptionMixin):
    list_display = ('id', 'title', 'topic', 'short_description_col')
    search_fields = ('title', 'description')
    list_display_links =('id', 'title', 'topic')
    list_filter = ('topic',)
    autocomplete_fields = ('topic',)



@admin.register(Topic)
class AdminTopic(admin.ModelAdmin, ShortDescriptionMixin):
    list_display = ('id', 'title', 'short_description_col')
    search_fields = ('title', 'description')
    list_display_links = ('id', 'title')


