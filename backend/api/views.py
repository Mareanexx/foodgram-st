from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from users.models import User, Follow
from users.serializers import (
    UserSerializer,
    UserCreateSerializer,
    AvatarSerializer
)
from djoser.views import UserViewSet as DjoserUserViewSet
from .pagination import CustomPagination
from recipes.models import Recipe, Favourite, ShoppingCart, Ingredient
from recipes.serializers import (
    RecipeSerializer,
    RecipeCreateSerializer,
    RecipeMinifiedSerializer,
    IngredientSerializer
)   
from recipes.filters import RecipeFilter, IngredientFilter
from .utils import base62_encode
from api.permissions import OwnerOrReadOnly
from rest_framework import filters as drf_filters


class UserViewSet(DjoserUserViewSet):
    queryset = User.objects.all()
    pagination_class = CustomPagination
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ['create', 'list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['post'],
        permission_classes=[IsAuthenticated]
    )
    def set_password(self, request):
        user = request.user
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')

        if not user.check_password(current_password):
            return Response(
                {'current_password': ['Неверный пароль']},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(new_password)
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['put', 'delete'],
        permission_classes=[IsAuthenticated],
        url_path='me/avatar'
    )
    def avatar(self, request):
        user = request.user

        if request.method == 'PUT':
            if not request.data:
                return Response(
                    {'avatar': ['Это поле обязательно.']},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = AvatarSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'DELETE':
            if user.avatar:
                user.avatar.delete()
                user.avatar = None
                user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), OwnerOrReadOnly()]
        return [AllowAny()]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return RecipeCreateSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.select_related(
            'author'
        ).prefetch_related(
            'recipe_ingredients',
            'recipe_ingredients__ingredient'
        )

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_link(self, request, pk=None):
        recipe = self.get_object()
        short = base62_encode(recipe.id)
        short_url = request.build_absolute_uri(f'/s/{short}')
        return Response({'short-link': short_url})

    def _handle_relation(self, request, recipe, model, error_exists, error_not_exists):
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Учетные данные не были предоставлены."},
                status=status.HTTP_401_UNAUTHORIZED
            )
            
        user = request.user
        obj = model.objects.filter(user=user, recipe=recipe)
        
        if request.method == 'POST':
            if obj.exists():
                return Response({'errors': error_exists}, status=400)
            model.objects.create(user=user, recipe=recipe)
            data = RecipeMinifiedSerializer(recipe, context={'request': request}).data
            return Response(data, status=201)
        if request.method == 'DELETE':
            if not obj.exists():
                return Response({'errors': error_not_exists}, status=400)
            obj.delete()
            return Response(status=204)

    @action(detail=True, methods=['post', 'delete'], url_path='favorite')
    def favorite(self, request, pk=None):
        recipe = self.get_object()
        return self._handle_relation(
            request, recipe, Favourite,
            'Рецепт уже в избранном.', 'Рецепта не было в избранном.'
        )

    @action(detail=True, methods=['post', 'delete'], url_path='shopping_cart')
    def shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        return self._handle_relation(
            request, recipe, ShoppingCart,
            'Рецепт уже в списке покупок.', 'Рецепта не было в списке покупок.'
        )


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter
