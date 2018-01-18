
class Cocktail:
    def __init__(self, title, ingredients, success):
        self.title = title

        # List of tuples: (food, quantity, unit)
        self.ingredients = ingredients
        self.success = success  # currently unused, but could be useful for "Learning from failure"

    def replace_ingredient(self, old, new):
        for i, ingredient in enumerate(self.ingredients):
            if ingredient[0] == old:
                break
        rest = self.ingredients[i][len(new):]
        self.ingredients[i] = new + rest if type(rest) is tuple else (rest, )
        self.title += ' with ' + self.ingredients[i][0] + ' instead of ' + old

    def add_ingredient(self, new):
        self.ingredients.append(new)
        self.title += ' and a bit of ' + new[0]

    def remove_ingredient(self, ingredient):
        self.ingredients = [x for x in self.ingredients if x[0] != ingredient]
        self.title += ' without ' + ingredient

    def get_ingredient_set(self):
        return set([x[0] for x in self.ingredients])

    def get_ingredient_quantity(self, ingredient):
        return [x[1] for x in self.ingredients if x[0] == ingredient][0]

    def __str__(self):
        out = self.title + '\n'
        for ingredient in self.ingredients:
            out += ingredient[1] + ingredient[2] + ' ' + ingredient[0] + '\n'
        return out
