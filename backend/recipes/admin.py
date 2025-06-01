from django.contrib import admin
from .models import Recipe, Ingredient, Favourite, ShoppingCart, RecipeIngredient


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'measurement_unit',
    )
    search_fields = ('name',)
    list_filter = ('measurement_unit',)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'author',
        'favorites_count',
    )
    search_fields = (
        'name',
        'author__username',
        'author__email',
        'recipe__name',
    )
    list_filter = (
        'author',
        'name',
    )
    inlines = [RecipeIngredientInline]

    def favorites_count(self, obj):
        return Favourite.objects.filter(recipe=obj).count()
    favorites_count.short_description = 'В избранном'


@admin.register(Favourite)
class FavouriteAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe',
    )
    search_fields = (
        'user__username',
        'user__email',
        'recipe__name',
    )


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe',)
    search_fields = (
        'user__username',
        'user__email',
        'recipe__name',
    )
    list_filter = ('user', 'recipe',)


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'recipe',
        'ingredient',
        'amount',
    )
    search_fields = (
        'recipe__name',
        'ingredient__name',
    )
    list_filter = ('recipe', 'ingredient',)
