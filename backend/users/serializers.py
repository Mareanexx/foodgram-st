from rest_framework import serializers
from .models import User, Follow
from recipes.models import Recipe


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    avatar = serializers.ImageField(allow_null=True, required=False)

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar'
        )
        read_only_fields = ('id', 'is_subscribed')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user.follows.filter(author=obj).exists()
        return False


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password'
        )

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ('user', 'author')
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'author'),
                message='Вы уже подписаны на этого автора'
            )
        ]

    def validate(self, data):
        if data['user'] == data['author']:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя'
            )
        return data
