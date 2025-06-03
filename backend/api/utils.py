import string
from django.db.models import Sum, F
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO
from datetime import datetime
from django.shortcuts import redirect, get_object_or_404
from django.http import Http404, HttpResponseRedirect
from recipes.models import Recipe


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
    try:
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        try:
            pdfmetrics.registerFont(TTFont('CustomFont', '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'))
            pdfmetrics.registerFont(TTFont('CustomFont-Bold', '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf'))
            font_name = 'CustomFont'
            font_name_bold = 'CustomFont-Bold'
        except:
            font_name = 'Helvetica'
            font_name_bold = 'Helvetica-Bold'
        
        pdf.setFont(font_name_bold, 24)
        pdf.drawString(50, height - 70, 'Список покупок')
        
        y = height - 120
        pdf.setFont(font_name, 14)
        
        for i, item in enumerate(ingredients, 1):
            ingredient_name = item['ingredient__name']
            amount = item['total_amount']
            measurement_unit = item['ingredient__measurement_unit']
            
            line = f'{i}. {ingredient_name} — {amount} {measurement_unit}'
            pdf.drawString(50, y, line)
            y -= 30
            
            if y < 50:
                pdf.showPage()
                pdf.setFont(font_name, 14)
                y = height - 50
        
        pdf.setFont(font_name_bold, 12)
        current_date = datetime.now().strftime("%d.%m.%Y %H:%M")
        pdf.drawString(50, 30, f'Foodgram | Сформировано: {current_date}')
        
        pdf.showPage()
        pdf.save()
        
        buffer.seek(0)
        return buffer
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")
        raise


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


def short_link_redirect(request, short_id):
    def base62_decode(s):
        base = len(BASE62)
        num = 0
        for char in s:
            num = num * base + BASE62.index(char)
        return num

    try:
        recipe_id = base62_decode(short_id)
    except Exception:
        return HttpResponseRedirect('/recipes')

    recipe = get_object_or_404(Recipe, id=recipe_id)
    return HttpResponseRedirect(f'/recipes/{recipe.id}')
