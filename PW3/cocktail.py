import xml.etree.ElementTree as ET
import sys
import copy
import random


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

    def add_ingredient(self, new):
        self.ingredients.append(new)
        self.title += ' and a bit of ' + new[0]

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


def print_solution_status(adapted_cocktail, missing_desired_ingredients, contained_undesired_ingredients):
    if adapted_cocktail:
        print('Current cocktail:')
        print(adapted_cocktail)
    if missing_desired_ingredients:
        print('These desired ingredients are missing: ' + str(missing_desired_ingredients))
    if contained_undesired_ingredients:
        print('These undesired ingredients are contained: ' + str(contained_undesired_ingredients))
    print()


def get_random_ingredient_of_same_catgegory(ingredient, ingredient_categories):
    ingredients_of_same_category = [x[0] for x in list(ingredient_categories.items())
                                    if x[1] == ingredient_categories[ingredient]]
    return random.choice(ingredients_of_same_category)

def adapt_solution(cocktail, desired_ingredients, undesired_ingredients, ingredient_categories):
    ingredient_set = cocktail.get_ingredient_set()
    desired_ingredients = set(desired_ingredients)
    undesired_ingredients = set(undesired_ingredients)
    missing_desired_ingredients = desired_ingredients - (ingredient_set & desired_ingredients)
    contained_undesired_ingredients = ingredient_set & undesired_ingredients

    print_solution_status(None, missing_desired_ingredients, contained_undesired_ingredients)

    if missing_desired_ingredients or contained_undesired_ingredients:
        print('Adapting cocktail so that it contains all desired ingredients and no undesired ones.')

        adapted_cocktail = copy.deepcopy(cocktail)

        # Our general strategy is to replace an ingredient in the original recipe only with an ingredient of the
        # same category. Therefore we extracted the categories of ingredients.

        # Check if an undesired ingredient can be replaced by a desired one
        # This is the most favorable case, since we kill two birds with one stone. So try this first.
        while missing_desired_ingredients and contained_undesired_ingredients:
            hit = False
            for missing_desired_ingredient in missing_desired_ingredients:
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
                adapted_cocktail.replace_ingredient(contained_undesired_ingredient, missing_desired_ingredient)
                missing_desired_ingredients.remove(missing_desired_ingredient)
                contained_undesired_ingredients.remove(contained_undesired_ingredient)
                print_solution_status(adapted_cocktail, missing_desired_ingredients, contained_undesired_ingredients)
            else:
                break  # need to use another rule

        # After that we check if a missing desired ingredient can be added by replacement of an existing
        # ingredient of the same category. The replaced ingredient is not an undesired one.
        # But we also have to check to not accidentally replace another desired ingredient.
        # We call this third category of ingredients optional: All contained ingredients that are not
        # desired or undesired are optional.
        while missing_desired_ingredients:
            hit = False
            for missing_desired_ingredient in missing_desired_ingredients:
                # Make sure to work on the ingredient set of the updated cocktail.
                for optional_ingredient in adapted_cocktail.get_ingredient_set():
                    # The second condition determines if optional_ingredient is actually optional.
                    if ingredient_categories[missing_desired_ingredient] == ingredient_categories[optional_ingredient]\
                            and optional_ingredient not in desired_ingredients:
                        print('Since the missing desired ingredient ' + str(missing_desired_ingredient) +
                              ' and the optional ingredient ' + str(optional_ingredient)
                              + ' are of the same category ' + str(ingredient_categories[missing_desired_ingredient]) +
                              ' we can replace ' + str(optional_ingredient) + ' by '
                              + str(missing_desired_ingredient))
                        hit = True
                        break
                if hit:
                    break
            if hit:
                adapted_cocktail.replace_ingredient(optional_ingredient, missing_desired_ingredient)
                missing_desired_ingredients.remove(missing_desired_ingredient)
                print_solution_status(adapted_cocktail, missing_desired_ingredients, contained_undesired_ingredients)
            else:
                break  # need to use another rule

        # We can replace a contained undesired ingredient by a random ingredient of the same category. At least
        # the category is preserved but there is some risk due to the random choice.
        while contained_undesired_ingredients:
            contained_undesired_ingredient = contained_undesired_ingredients.pop()
            random_ingredient = get_random_ingredient_of_same_catgegory(contained_undesired_ingredient,
                                                                        ingredient_categories)
            print('We replace the contained undesired ingredient ' + str(contained_undesired_ingredient) +
                  ' by the random ingredient ' + str(random_ingredient) + ' of the same category ' +
                  str(ingredient_categories[random_ingredient]))
            adapted_cocktail.replace_ingredient(contained_undesired_ingredient, random_ingredient)
            print_solution_status(adapted_cocktail, missing_desired_ingredients, contained_undesired_ingredients)

        # Now comes the most unfavorable strategy: we just add a little bit of the remaining missing desired ingredients
        # to the cocktail. This is the only operation that changes the number of ingredients and does not respect
        # the category of an ingredient.
        while missing_desired_ingredients:
            missing_desired_ingredient = missing_desired_ingredients.pop()
            print('We add a little bit of the missing desired ingredient ' + str(missing_desired_ingredient))
            unit = 'cl' if ingredient_categories[missing_desired_ingredient] in ['alcoholic', 'nonalcoholic'] else ''
            adapted_cocktail.add_ingredient((missing_desired_ingredient, '1', unit))
            print_solution_status(adapted_cocktail, missing_desired_ingredients, contained_undesired_ingredients)

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

    desired_ingredients = ['gin', 'sparkling water', 'anise basil', 'brown sugar', 'ice cube', 'lemongrass', 'champagne']
    undesired_ingredients = ['white rum', 'lime']
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
