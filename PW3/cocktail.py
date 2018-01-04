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

def main():
    # Load case base
    tree = ET.parse('ccc_cocktails.xml')
    root = tree.getroot()

    for recipe in root:
        for ingredient in recipe.find('ingredients'):

    # Build dict with all ingredients and assign them a unique ID
    # for easier handling
    #ingredient_id = 0
    #ingredient_dict = {}
    #for recipe in root:
    #    for ingredient in recipe.find('ingredients'):
    #        food = ingredient.attrib['food'].lower()
    #        if food not in ingredient_dict:
    #            ingredient_dict[food] = ingredient_id
    #            ingredient_id += 1

    # Extract all cocktails
    cocktails = []
    for recipe in root:
        ingredients = []
        for ingredient in recipe.find('ingredients'):
            food = ingredient.attrib['food'].lower()
            ingredients.append((ingredient.attrib['food'].lower(),
                            ingredient.attrib['quantity'],
                            ingredient.attrib['unit'], True))
        cocktails.append(Cocktail(recipe.find('title').text, ingredients))

    for cocktail in cocktails:
        print(cocktail)

    print('most similar')
    print(find_most_similar(cocktails, ['orange juice', 'gin'], ['cointreau'])[1])

if __name__ == '__main__':
    main()
