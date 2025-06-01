from django.contrib import admin
from .models import User, Follow
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User
    list_display = (
        'id',
        'email',
        'username',
        'first_name',
        'last_name',
        'avatar',
        'is_staff'
    )
    list_filter = (
        'email',
        'username',
        'is_staff',
        'is_active'
    )
    search_fields = (
        'email',
        'username'
    )


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('follower', 'following')
    list_filter = ('follower', 'following')
    search_fields = (
        'follower__username',
        'follower__email',
        'following__username',
        'following__email'
    )
