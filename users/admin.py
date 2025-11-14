from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Profile, User


# Inline для профиля — будет отображаться прямо на странице пользователя
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Профиль'
    fk_name = 'user'


# Админка для пользователя
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User
    inlines = [ProfileInline]  # подключаем профиль
    list_display = ('id', 'email', 'username',
                    'is_active', 'is_staff', 'is_superuser')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('email', 'username')
    ordering = ('id',)

    # Какие поля показывать на странице редактирования
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser',
                                    'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    # Какие поля показывать при создании нового пользователя
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2',
                       'is_active', 'is_staff', 'is_superuser')}
         ),
    )

    # Используем fk_name для корректной связи с inline
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        return super().get_inline_instances(request, obj)


# Опционально — отдельная админка для профиля, если нужен быстрый доступ
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'bio', 'avatar')
    search_fields = ('user__email', 'user__username', 'bio')
