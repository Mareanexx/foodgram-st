import string
from django.db.models import Sum, F
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO
from datetime import datetime
from django.conf import settings
import os


BASE62 = string.digits + string.ascii_letters


def base62_encode(num):
    if num == 0:
        return BASE62[0]
    arr = []
    base = len(BASE62)
    while num:
        num, rem = divmod(num, base)
        arr.append(BASE62[rem])
    arr.reverse()
    return ''.join(arr)


def generate_shopping_list_pdf(user, ingredients):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    fonts_dir = os.path.join(settings.BASE_DIR, 'static', 'fonts')
    pdfmetrics.registerFont(TTFont('Roboto-Regular', os.path.join(fonts_dir, 'roboto_regular.ttf')))
    pdfmetrics.registerFont(TTFont('Roboto-Bold', os.path.join(fonts_dir, 'roboto_bold.ttf')))
    
    pdf.setFont('Roboto-Bold', 24)
    pdf.drawString(50, height - 70, 'Список покупок')
    
    y = height - 120
    pdf.setFont('Roboto-Regular', 14)
    
    for i, item in enumerate(ingredients, 1):
        ingredient_name = item['ingredient__name']
        amount = item['total_amount']
        measurement_unit = item['ingredient__measurement_unit']
        
        line = f'{i}. {ingredient_name} — {amount} {measurement_unit}'
        pdf.drawString(50, y, line)
        y -= 30
        
        if y < 50:
            pdf.showPage()
            pdf.setFont('Roboto-Regular', 14)
            y = height - 50
    
    pdf.setFont('Roboto-Bold', 12)
    current_date = datetime.now().strftime("%d.%m.%Y %H:%M")
    pdf.drawString(50, 30, f'Foodgram | Сформировано: {current_date}')
    
    pdf.showPage()
    pdf.save()
    
    buffer.seek(0)
    return buffer


def get_shopping_list_ingredients(user):
    return (
        user.shoppingcarts.values(
            'recipe__recipe_ingredients__ingredient__name',
            'recipe__recipe_ingredients__ingredient__measurement_unit'
        )
        .annotate(
            total_amount=Sum('recipe__recipe_ingredients__amount'),
            ingredient__name=F('recipe__recipe_ingredients__ingredient__name'),
            ingredient__measurement_unit=F(
                'recipe__recipe_ingredients__ingredient__measurement_unit'
            )
        )
        .order_by('ingredient__name')
    ) 