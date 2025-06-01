from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name="Название",
        help_text="Название"
    )
    measurement_unit = models.CharField(
        max_length=64,
        verbose_name="Единица измерения",
        help_text="Единица измерения (гр/мл)"
    )

    class Meta:
        ordering = ['name']
        unique_together = ('name', 'measurement_unit')
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

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
        max_length=256,
        verbose_name="Название"
    )
    image = models.ImageField(
        upload_to='recipes/images/',
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
    cooking_time = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Время приготовления (мин)"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

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
    amount = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Количество"
    )

    class Meta:
        unique_together = ('recipe', 'ingredient')
        verbose_name = "Ингредиент в рецепте"
        verbose_name_plural = "Ингредиенты в рецептах"

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
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="unique_%(class)s_user_recipe"
            )
        ]

    def __str__(self):
        return f"{self.user} → {self.recipe}"


class Favourite(UserRecipeRelation):
    class Meta:
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"


class ShoppingCart(UserRecipeRelation):
    class Meta:
        verbose_name = "Список покупок"
        verbose_name_plural = "Список покупок"
