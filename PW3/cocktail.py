import xml.etree.ElementTree as ET
import sys
import copy


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
        ingredient_set = self.get_ingredient_set()
        return sum([1 if x in ingredient_set else 0 for x in desired_ingredients] +
                    [-1 if x in ingredient_set else 0 for x in undesired_ingredients])

    def replace_ingredient(self, old, new):
        for i, ingredient in enumerate(self.ingredients):
            if ingredient[0] == old:
                break
        self.ingredients[i] = (new, self.ingredients[i][1], self.ingredients[i][2])
        self.title += ' with ' + new + ' instead of ' + old

    def get_ingredient_set(self):
        return set([x[0] for x in self.ingredients])

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


def adapt_solution(cocktail, desired_ingredients, undesired_ingredients, ingredient_categories):
    ingredient_set = cocktail.get_ingredient_set()
    missing_desired_ingredients = set(desired_ingredients) - (ingredient_set & set(desired_ingredients))
    contained_undesired_ingredients = ingredient_set & set(undesired_ingredients)

    if missing_desired_ingredients:
        print('These desired ingredients are missing: ' + str(missing_desired_ingredients))

    if contained_undesired_ingredients:
        print('These undesired ingredients are contained: ' + str(contained_undesired_ingredients))

    if missing_desired_ingredients or contained_undesired_ingredients:
        print('Adapting cocktail so that it contains all desired ingredients and no undesired ones.')

        adapted_cocktail = copy.deepcopy(cocktail)

        # Our general strategy is to replace an ingredient in the original recipe only with an ingredient of the
        # same category. Therefore we extracted the categories of ingredients.

        while missing_desired_ingredients or contained_undesired_ingredients:
            # Check if an undesired ingredient can be replaced by a desired one
            # This is the most favorable case, so try this first
            hit = False
            if missing_desired_ingredients and contained_undesired_ingredients:
                for missing_desired_ingredient in  missing_desired_ingredients:
                    for contained_undesired_ingredient in contained_undesired_ingredients:
                        if ingredient_categories[missing_desired_ingredient] ==\
                                ingredient_categories[contained_undesired_ingredient]:
                            print('Since the missing desired ingredient ' + str(missing_desired_ingredient) +
                                  ' and the contained undesired ingredient ' + str(contained_undesired_ingredient)
                                  + ' are of the same category ' + str(ingredient_categories[missing_desired_ingredient]) +
                                  ' we can replace ' + str(contained_undesired_ingredient) + ' by '
                                  + str(missing_desired_ingredient))
                            hit = True
                            break
                    if hit:
                        break
                if hit:
                    cocktail.replace_ingredient(contained_undesired_ingredient, missing_desired_ingredient)
                    missing_desired_ingredients.remove(missing_desired_ingredient)
                    contained_undesired_ingredients.remove(contained_undesired_ingredient)

            print(cocktail)
            print(adapted_cocktail)




    print(missing_desired_ingredients, contained_undesired_ingredients)


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
    ingredient_categories = load_ingredient_categories()

    cocktails = build_case_base(root)

    desired_ingredients = ['gin', 'orange juice', 'cointreau', 'raspberry']
    undesired_ingredients = ['cognac']
    print('Searching for a cocktail with constraints')
    print("\tdesired ingredients: " + str(desired_ingredients))
    print("\tundesired ingredients: " + str(undesired_ingredients))
    cocktail = find_most_similar(cocktails, desired_ingredients, undesired_ingredients)[1]
    print()
    print("Most similar cocktail found:")
    print(cocktail)
    print()
    adapt_solution(cocktail, desired_ingredients, undesired_ingredients, ingredient_categories)

if __name__ == '__main__':
    main()
