from rest_framework import serializers
from recipes.models import Recipe, Ingredient, RecipeIngredient, Favourite, ShoppingCart
from foodgram_backend.fields import CustomBase64ImageField


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)
        read_only_fields = fields


class FavouriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favourite
        fields = ('user', 'recipe',)
        extra_kwargs = {
            'user': {'write_only': True},
            'recipe': {'write_only': True},
        }

    def validate(self, data):
        user = data['user']
        recipe = data['recipe']
        if Favourite.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError("Рецепт уже в избранном.")
        return data

    def to_representation(self, instance):
        return RecipeMinifiedSerializer(instance.recipe, context=self.context).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe',)
        extra_kwargs = {
            'user': {'write_only': True},
            'recipe': {'write_only': True},
        }

    def validate(self, data):
        user = data['user']
        recipe = data['recipe']
        if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError("Рецепт уже в корзине покупок.")
        return data

    def to_representation(self, instance):
        return RecipeMinifiedSerializer(instance.recipe, context=self.context).data


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class RecipeSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    ingredients = IngredientInRecipeSerializer(
        source='recipe_ingredients',
        many=True,
        read_only=True,
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = CustomBase64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_author(self, obj):
        from users.serializers import UserSerializer
        return UserSerializer(obj.author, context=self.context).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Favourite.objects.filter(
                user=request.user,
                recipe=obj,
            ).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return ShoppingCart.objects.filter(
                user=request.user,
                recipe=obj,
            ).exists()
        return False


class RecipeCreateSerializer(RecipeSerializer):
    ingredients = serializers.ListField(
        child=serializers.DictField(
            child=serializers.IntegerField(),
        ),
        write_only=True,
    )

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError("Нужен хотя бы один ингредиент")
        
        ingredient_ids = [item.get('id') for item in value]
        if not all(isinstance(id_, int) for id_ in ingredient_ids):
            raise serializers.ValidationError("ID ингредиента должен быть числом")
            
        if not all(item.get('amount', 0) > 0 for item in value):
            raise serializers.ValidationError(
                "Количество ингредиента должно быть положительным числом"
            )
            
        if len(set(ingredient_ids)) != len(ingredient_ids):
            raise serializers.ValidationError("Ингредиенты не должны повторяться")
            
        if not Ingredient.objects.filter(id__in=ingredient_ids).count() == len(ingredient_ids):
            raise serializers.ValidationError("Указан несуществующий ингредиент")
            
        return value

    def validate_cooking_time(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Время приготовления должно быть положительным числом"
            )
        return value

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        
        recipe_ingredients = []
        for ingredient_data in ingredients_data:
            ingredient = Ingredient.objects.get(id=ingredient_data['id'])
            recipe_ingredients.append(
                RecipeIngredient(
                    recipe=recipe,
                    ingredient=ingredient,
                    amount=ingredient_data['amount'],
                ),
            )
        RecipeIngredient.objects.bulk_create(recipe_ingredients)
        
        return recipe

    def update(self, instance, validated_data):
        if 'ingredients' not in validated_data:
            raise serializers.ValidationError({
                "ingredients": ["Обязательное поле."],
            })
            
        ingredients_data = validated_data.pop('ingredients')
        instance.recipe_ingredients.all().delete()
        recipe_ingredients = []
        for ingredient_data in ingredients_data:
            ingredient = Ingredient.objects.get(id=ingredient_data['id'])
            recipe_ingredients.append(
                RecipeIngredient(
                    recipe=instance,
                    ingredient=ingredient,
                    amount=ingredient_data['amount'],
                ),
            )
        RecipeIngredient.objects.bulk_create(recipe_ingredients)
        
        return super().update(instance, validated_data)
    
    def to_representation(self, instance):
        return RecipeSerializer(instance, context=self.context).data


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)
        read_only_fields = fields
