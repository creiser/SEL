import xml.etree.ElementTree as ET
import sys


class Cocktail:
    def __init__(self, title, ingredients, success):
        self.title = title

        # List of tuples: (food, quantity, unit)
        self.ingredients = ingredients
        self.success = success

    # Count number of matching ingredients with query
    def similarity(self, desired_ingredients, undesired_ingredients):
        if not self.success:
            return -sys.maxsize - 1

        ingredient_set = set([x[0] for x in self.ingredients])
        return sum([1 if x in ingredient_set else 0 for x in desired_ingredients] +
                    [-1 if x in ingredient_set else 0 for x in undesired_ingredients])

    def __str__(self):
        out = self.title + '\n'
        for ingredient in self.ingredients:
            out += ingredient[1] + ingredient[2] + ' ' + ingredient[0] + '\n'
        return out


def find_most_similar(cocktails, desired_ingredients, undesired_ingredients):
    max_sim, most_similar = -sys.maxsize - 1, None
    for cocktail in cocktails:
        sim = cocktail.similarity(desired_ingredients, undesired_ingredients)
        if sim > max_sim:
            max_sim, most_similar = sim, cocktail
    return max_sim, most_similar


def extract_ingredients(root):
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


def build_case_base(root):
    # Extract all cocktails
    cocktails = []
    for recipe in root:
        ingredients = []
        for ingredient in recipe.find('ingredients'):
            food = ingredient.attrib['food'].lower()
            ingredients.append((ingredient.attrib['food'].lower(),
                                ingredient.attrib['quantity'],
                                ingredient.attrib['unit'], True))
        cocktails.append(Cocktail(recipe.find('title').text, ingredients, True))
    return cocktails


def main():
    # Load case base
    tree = ET.parse('ccc_cocktails.xml')
    root = tree.getroot()

    extract_ingredients(root)
    print(load_ingredient_categories())

    cocktails = build_case_base(root)

    #for cocktail in cocktails:
    #    print(cocktail)

    #print('most similar')
    #print(find_most_similar(cocktails, ['orange juice', 'gin'], ['cointreau'])[1])

if __name__ == '__main__':
    main()
