import json
import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from recipes.models import Recipe, Ingredient, RecipeIngredient
from users.models import Follow
from django.core.files import File
from django.conf import settings


User = get_user_model()

class Command(BaseCommand):
    help = 'Загружает тестовые данные из JSON файла'

    def handle(self, *args, **options):
        data_dir = os.path.join(settings.BASE_DIR.parent, 'data')
        json_file = os.path.join(data_dir, 'test_data.json')
        images_dir = os.path.join(data_dir, 'images')

        if not os.path.exists(json_file):
            self.stdout.write(self.style.ERROR(f'Файл {json_file} не найден'))
            return

        try:
            with open(json_file, encoding='utf-8') as f:
                data = json.load(f)

            for user_data in data.get('users', []):
                user, created = User.objects.get_or_create(
                    email=user_data['email'],
                    defaults={
                        'username': user_data['username'],
                        'first_name': user_data['first_name'],
                        'last_name': user_data['last_name'],
                    }
                )
                if created:
                    user.set_password(user_data['password'])
                    user.save()
                    self.stdout.write(self.style.SUCCESS(f'Создан пользователь {user.username}'))

            for subscription in data.get('subscriptions', []):
                follower = User.objects.get(email=subscription['follower'])
                following = User.objects.get(email=subscription['following'])
                
                if not Follow.objects.filter(follower=follower, following=following).exists():
                    Follow.objects.create(follower=follower, following=following)
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Создана подписка: {follower.username} -> {following.username}'
                        )
                    )

            for recipe_data in data.get('recipes', []):
                author = User.objects.get(email=recipe_data['author_email'])
                
                if Recipe.objects.filter(name=recipe_data['name'], author=author).exists():
                    continue

                recipe = Recipe(
                    author=author,
                    name=recipe_data['name'],
                    text=recipe_data['text'],
                    cooking_time=recipe_data['cooking_time']
                )

                image_name = recipe_data['image']
                image_path = os.path.join(images_dir, image_name)
                if os.path.exists(image_path):
                    with open(image_path, 'rb') as img_file:
                        recipe.image.save(
                            image_name,
                            File(img_file),
                            save=False
                        )

                recipe.save()

                for ingredient_data in recipe_data['ingredients']:
                    ingredient = Ingredient.objects.get(name=ingredient_data['name'])
                    RecipeIngredient.objects.create(
                        recipe=recipe,
                        ingredient=ingredient,
                        amount=ingredient_data['amount']
                    )

                self.stdout.write(self.style.SUCCESS(f'Создан рецепт {recipe.name}'))

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Произошла ошибка при загрузке данных: {str(e)}')
            ) 