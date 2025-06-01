from rest_framework import serializers
from .models import User, Follow    
from foodgram_backend.fields import CustomBase64ImageField

class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    avatar = CustomBase64ImageField(allow_null=True, required=False)

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
            return request.user.follower.filter(following=obj).exists()
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


class AvatarSerializer(serializers.ModelSerializer):
    avatar = CustomBase64ImageField(required=True, allow_null=False)

    class Meta:
        model = User
        fields = ('avatar',)

    def validate(self, attrs):
        if not attrs.get('avatar'):
            raise serializers.ValidationError(
                {'avatar': 'Это поле обязательно.'}
            )
        return attrs
