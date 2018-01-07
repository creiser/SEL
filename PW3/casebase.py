import xml.etree.ElementTree as ET
from cocktail import Cocktail

root = None


def parse_official_case_base():
    global root
    if not root:
        root = ET.parse('ccc_cocktails.xml').getroot()


def extract_ingredients():
    parse_official_case_base()
    ingredients = set()
    for recipe in root:
        for ingredient in recipe.find('ingredients'):
            ingredients.add(ingredient.attrib['food'].lower())

    top_level_element = ET.Element('ingredients')
    for ingredient in ingredients:
        inner_element = ET.SubElement(top_level_element, 'ingredient')
        inner_element.attrib['food'] = ingredient
        inner_element.attrib['category'] = '' # category will be assigned in the file
    ET.ElementTree(top_level_element).write("categories_raw.xml")


def load_ingredient_categories():
    ingredient_categories = {}
    for ingredient in ET.parse('categories.xml').getroot():
        ingredient_categories[ingredient.attrib['food']] = ingredient.attrib['category']
    return ingredient_categories


def load_official_case_base():
    parse_official_case_base()
    # Extract all cocktails
    cocktails = []
    for recipe in root:
        ingredients = []
        for ingredient in recipe.find('ingredients'):
            ingredients.append((ingredient.attrib['food'].lower(),
                                ingredient.attrib['quantity'],
                                ingredient.attrib['unit']))
        cocktails.append(Cocktail(recipe.find('title').text, ingredients, True))
    return cocktails


def save_case_base(cocktails):
    root = ET.Element('cocktails')
    for cocktail in cocktails:
        cocktail_element = ET.SubElement(root, 'cocktail')
        cocktail_element.attrib['title'] = cocktail.title
        for ingredient in cocktail.ingredients:
            ingredient_element = ET.SubElement(cocktail_element, 'ingredient')
            ingredient_element.attrib['food'], ingredient_element.attrib['quantity'],\
            ingredient_element.attrib['unit'] = ingredient
    ET.ElementTree(root).write('case_base.xml')


def load_case_base():
    cocktails = []
    root = ET.parse('case_base.xml').getroot()
    for cocktail_element in root:
        ingredients = []
        for ingredient_element in cocktail_element:
            ingredients.append((ingredient_element.attrib['food'], ingredient_element.attrib['quantity'],
                                ingredient_element.attrib['unit']))
        cocktails.append(Cocktail(cocktail_element.attrib['title'], ingredients, True))
    return cocktails