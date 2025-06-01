import csv
import os
from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Загружает ингредиенты из CSV файла в базу данных'

    def handle(self, *args, **options):
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))), 'data')
        csv_file = os.path.join(data_dir, 'ingredients.csv')

        if not os.path.exists(csv_file):
            self.stdout.write(self.style.ERROR(f'Файл {csv_file} не найден'))
            return

        try:
            with open(csv_file, encoding='utf-8') as file:
                reader = csv.reader(file)
                ingredients_to_create = []
                
                for row in reader:
                    if len(row) != 2:
                        continue
                    
                    name, measurement_unit = row
                    
                    if not Ingredient.objects.filter(
                        name=name,
                        measurement_unit=measurement_unit
                    ).exists():
                        ingredients_to_create.append(
                            Ingredient(
                                name=name,
                                measurement_unit=measurement_unit
                            )
                        )

                if ingredients_to_create:
                    Ingredient.objects.bulk_create(ingredients_to_create)
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Успешно загружено {len(ingredients_to_create)} ингредиентов'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.SUCCESS('Все ингредиенты уже существуют в базе данных')
                    )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Произошла ошибка при загрузке ингредиентов: {str(e)}')
            )
