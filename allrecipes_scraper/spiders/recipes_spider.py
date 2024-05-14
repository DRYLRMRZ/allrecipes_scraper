import scrapy
import re
from fractions import Fraction


def convert_ingredient(ingredient):
    unit_mapping = {
        "tablespoons": "tbsp",
        "tablespoon": "tbsp",
        "teaspoons": "tsp",
        "teaspoon": "tsp",
        "cups": "cups",
        "cup": "cups",
        "pounds": "lbs",
        "pound": "lb",
        "ounces": "oz",
        "ounce": "oz",
        "grams": "g",
        "gram": "g",
        "kilograms": "kg",
        "kilogram": "kg"
    }
    fractions_mapping = {
        "¼": 0.25,
        "½": 0.5,
        "¾": 0.75,
        "⅓": 0.33,
        "⅔": 0.67,
        "⅕": 0.20,
        "⅖": 0.40,
        "⅗": 0.60,
        "⅘": 0.80,
        "⅙": 0.17,
        "⅚": 0.83,
        "⅛": 0.13,
        "⅜": 0.38,
        "⅝": 0.63,
        "⅞": 0.88
    }

    parts = ingredient.split()

    for index, part in enumerate(parts):
        if part in fractions_mapping:
            parts[index] = str(fractions_mapping[part])
        if part in unit_mapping:
            parts[index] = unit_mapping[part]
    if str(parts[1]).replace('.', '').isdigit():
        combined_number = float(parts[0]) + float(parts[1])
        new_parts_list = [str(combined_number), *parts[2:]]
    else:
        new_parts_list = parts
    converted_ingredient = ' '.join(new_parts_list)

    return converted_ingredient


class RecipesSpider(scrapy.Spider):
    name = 'recipes'

    def __init__(self, url=None, *args, **kwargs):
        super(RecipesSpider, self).__init__(*args, **kwargs)
        self.start_urls = [url] if url else []

    def parse(self, response):
        title = response.xpath('//meta[@itemprop="name"]/@content').get()
        description = response.xpath('//meta[@name="description"]/@content').get()
        portions_element = response.xpath('//div[@class="mntl-recipe-details__label" and text()="Servings:"]//following-sibling::div')
        portions_text = portions_element.xpath('string()').get().strip()
        ingredients_elements = response.xpath('//ul[@class="mntl-structured-ingredients__list"]//li')
        ingredients_list = []
        for element in ingredients_elements:
            line_string = element.xpath('string()').get().strip()
            ingredients_list.append(line_string)
        converted_ingredients = [convert_ingredient(ingredient) for ingredient in ingredients_list]
        ingredients = '\n\n'.join(converted_ingredients)
        methods_elements = response.xpath('//ol[@id="mntl-sc-block_1-0"]//p')
        methods_list = []
        for index, element in enumerate(methods_elements):
            line_string = element.xpath('string()').get().strip()
            methods_list.append(f'{index+1}. {line_string}')
        methods = '\n\n'.join(methods_list)

        yield {
            'title': title,
            'description': description,
            'portions': int(portions_text),
            'ingredients': ingredients,
            'methods': methods
        }

