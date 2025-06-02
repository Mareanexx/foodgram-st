from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from .constants import (
    MAX_LENGTH_RECIPE_NAME,
    MIN_VALUE_COOKING_TIME,
    MAX_VALUE_COOKING_TIME,
    MIN_VALUE_INGREDIENT_AMOUNT,
    MAX_VALUE_INGREDIENT_AMOUNT,
    MAX_LENGTH_INGREDIENT_NAME,
    MAX_LENGTH_MEASUREMENT_UNIT,
    RECIPE_IMAGES_PATH
)

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(
        max_length=MAX_LENGTH_INGREDIENT_NAME,
        verbose_name="Название",
        help_text="Название"
    )
    measurement_unit = models.CharField(
        max_length=MAX_LENGTH_MEASUREMENT_UNIT,
        verbose_name="Единица измерения",
        help_text="Единица измерения (гр/мл)"
    )

    class Meta:
        ordering = ('name',)
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_ingredient_measurement_unit'
            ),
        )

    def __str__(self):
        return f"{self.name} ({self.measurement_unit})"


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name="Автор (пользователь)"
    )
    name = models.CharField(
        max_length=MAX_LENGTH_RECIPE_NAME,
        verbose_name="Название"
    )
    image = models.ImageField(
        upload_to=RECIPE_IMAGES_PATH,
        verbose_name="Фото"
    )
    text = models.TextField(
        verbose_name="Описание"
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name="Ингредиенты"
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=(
            MinValueValidator(MIN_VALUE_COOKING_TIME),
            MaxValueValidator(MAX_VALUE_COOKING_TIME)
        ),
        verbose_name="Время приготовления (мин)"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )

    class Meta:
        ordering = ('-created_at',)
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        default_related_name = 'recipes'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name="Рецепт"
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_in_recipes',
        verbose_name="Ингредиент"
    )
    amount = models.PositiveSmallIntegerField(
        validators=(
            MinValueValidator(MIN_VALUE_INGREDIENT_AMOUNT),
            MaxValueValidator(MAX_VALUE_INGREDIENT_AMOUNT)
        ),
        verbose_name="Количество"
    )

    class Meta:
        ordering = ('recipe', 'ingredient__name',)
        verbose_name = "Ингредиент в рецепте"
        verbose_name_plural = "Ингредиенты в рецептах"
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_recipe_ingredient'
            ),
        )

    def __str__(self):
        return f"{self.ingredient.name} — {self.amount} {self.ingredient.measurement_unit}"


class UserRecipeRelation(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="%(class)ss",
        verbose_name="Пользователь"
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="%(class)ss",
        verbose_name="Рецепт"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )

    class Meta:
        abstract = True
        ordering = ('-created_at',)
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_%(class)s_user_recipe'
            ),
        )

    def __str__(self):
        return f"{self.user} → {self.recipe}"


class Favourite(UserRecipeRelation):
    class Meta(UserRecipeRelation.Meta):
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"
        default_related_name = 'favourites'


class ShoppingCart(UserRecipeRelation):
    class Meta(UserRecipeRelation.Meta):
        verbose_name = "Список покупок"
        verbose_name_plural = "Список покупок"
        default_related_name = 'shoppingcarts'
