
class Cocktail:
    def __init__(self, title, ingredients, success):
        self.title = title

        # List of tuples: (food, quantity, unit)
        self.ingredients = ingredients
        self.success = success  # currently unused, but could be useful for "Learning from failure"

    def replace_ingredient(self, old, new, use_old_quantities=True):
        for i, ingredient in enumerate(self.ingredients):
            if ingredient[0] == old:
                break
        if use_old_quantities:
            self.ingredients[i] = (new, self.ingredients[i][1], self.ingredients[i][2])
        else:
            self.ingredients[i] = new
        self.title += ' with ' + self.ingredients[i][0] + ' instead of ' + old

    def add_ingredient(self, new):
        self.ingredients.append(new)
        self.title += ' and a bit of ' + new[0]

    def remove_ingredient(self, ingredient):
        self.ingredients = [x for x in self.ingredients if x[0] != ingredient]
        self.title += ' without ' + ingredient

    def get_ingredient_set(self):
        return set([x[0] for x in self.ingredients])

    def __str__(self):
        out = self.title + '\n'
        for ingredient in self.ingredients:
            out += ingredient[1] + ingredient[2] + ' ' + ingredient[0] + '\n'
        return out
