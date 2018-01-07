import copy
import random
import os.path
import sys
import casebase


def get_similarity_to_query(cocktail, desired_ingredients, undesired_ingredients, ingredient_categories):
    if not cocktail.success:
        return -sys.maxsize - 1
    # We use dry runs of the adapt_solution method to calculate an edit distance.
    return -adapt_solution(cocktail, desired_ingredients, undesired_ingredients, ingredient_categories, True)[1]


def find_most_similar(cocktails, desired_ingredients, undesired_ingredients, ingredient_categories):
    max_sim, most_similar = -sys.maxsize - 1, None
    for cocktail in cocktails:
        sim = get_similarity_to_query(cocktail, desired_ingredients, undesired_ingredients, ingredient_categories)
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


def get_random_ingredient_of_same_category(ingredient, ingredient_categories):
    ingredients_of_same_category = [x[0] for x in list(ingredient_categories.items())
                                    if x[1] == ingredient_categories[ingredient]]
    return random.choice(ingredients_of_same_category)


def get_missing_desired_ingredients_and_contained_undesired_ingredients(cocktail, desired_ingredients,
                                                                        undesired_ingredients):
    ingredient_set = cocktail.get_ingredient_set()
    return desired_ingredients - (ingredient_set & desired_ingredients), ingredient_set & undesired_ingredients


def adapt_solution(cocktail, desired_ingredients, undesired_ingredients, ingredient_categories, dry_run=False):
    edit_distance = 0
    missing_desired_ingredients, contained_undesired_ingredients = \
        get_missing_desired_ingredients_and_contained_undesired_ingredients(cocktail, desired_ingredients,
                                                                            undesired_ingredients)
    if not dry_run:
        print_solution_status(None, missing_desired_ingredients, contained_undesired_ingredients)

    if missing_desired_ingredients or contained_undesired_ingredients:
        if not dry_run:
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
                        if not dry_run:
                            print('Since the missing desired ingredient ' + str(missing_desired_ingredient) +
                                  ' and the contained undesired ingredient ' + str(contained_undesired_ingredient)
                                  + ' are of the same category ' +
                                  str(ingredient_categories[missing_desired_ingredient]) + ' we can replace ' +
                                  str(contained_undesired_ingredient) + ' by ' + str(missing_desired_ingredient))
                        hit = True
                        break
                if hit:
                    break
            if hit:
                adapted_cocktail.replace_ingredient(contained_undesired_ingredient, missing_desired_ingredient)
                missing_desired_ingredients.remove(missing_desired_ingredient)
                contained_undesired_ingredients.remove(contained_undesired_ingredient)
                if not dry_run:
                    print_solution_status(adapted_cocktail, missing_desired_ingredients,
                                          contained_undesired_ingredients)
                edit_distance += 1
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
                        if not dry_run:
                            print('Since the missing desired ingredient ' + str(missing_desired_ingredient) +
                                  ' and the optional ingredient ' + str(optional_ingredient)
                                  + ' are of the same category ' + ' we can replace ' + str(optional_ingredient) +
                                  ' by ' + str(missing_desired_ingredient))
                        hit = True
                        break
                if hit:
                    break
            if hit:
                adapted_cocktail.replace_ingredient(optional_ingredient, missing_desired_ingredient)
                missing_desired_ingredients.remove(missing_desired_ingredient)
                if not dry_run:
                    print_solution_status(adapted_cocktail, missing_desired_ingredients,
                                          contained_undesired_ingredients)
                edit_distance += 1
            else:
                break  # need to use another rule

        # We can replace a contained undesired ingredient by a random ingredient of the same category. At least
        # the category is preserved but there is some risk due to the random choice.
        while contained_undesired_ingredients:
            contained_undesired_ingredient = contained_undesired_ingredients.pop()
            random_ingredient = contained_undesired_ingredient
            while random_ingredient in undesired_ingredients:
                random_ingredient = get_random_ingredient_of_same_category(contained_undesired_ingredient,
                                                                           ingredient_categories)
            if not dry_run:
                print('We replace the contained undesired ingredient ' + str(contained_undesired_ingredient) +
                      ' by the random ingredient ' + str(random_ingredient) + ' of the same category ' +
                      str(ingredient_categories[random_ingredient]))
            adapted_cocktail.replace_ingredient(contained_undesired_ingredient, random_ingredient)
            if not dry_run:
                print_solution_status(adapted_cocktail, missing_desired_ingredients, contained_undesired_ingredients)
            edit_distance += 1

        # Now comes the most unfavorable strategy: we just add a little bit of the remaining missing desired ingredients
        # to the cocktail. This is the only operation that changes the number of ingredients and does not respect
        # the category of an ingredient.
        while missing_desired_ingredients:
            missing_desired_ingredient = missing_desired_ingredients.pop()
            if not dry_run:
                print('We add a little bit of the missing desired ingredient ' + str(missing_desired_ingredient))
            unit = 'cl' if ingredient_categories[missing_desired_ingredient] in ['alcoholic', 'nonalcoholic'] else ''
            adapted_cocktail.add_ingredient((missing_desired_ingredient, '1', unit))
            if not dry_run:
                print_solution_status(adapted_cocktail, missing_desired_ingredients, contained_undesired_ingredients)
            edit_distance += 2 # give this more weight because of its very heuristic nature
        return adapted_cocktail, edit_distance
    else:
        if not dry_run:
            print('Found cocktail already contains all desired ingredients and no undesired ones, so it can be '
                  'directly used.')
        return None, 0


def print_commands():
    print('Commands:')
    print('\tadd ingredient quantity unit: Adds an ingredient to the cocktail.')
    print('\treplace ingredient new-ingredient quantity unit: Replaces an ingredient in the cocktail.')
    print('\tremove ingredient: Removes an ingredient from the cocktail.')
    print('\tsave Saves the edited cocktail to the case base')


def evaluate_solution(adapted_cocktail, desired_ingredients, undesired_ingredients, ingredient_categories, cocktails):
    answer = ''
    while answer != 'y' and answer != 'n':
        print('Is this a good cocktail? (y/n)')
        answer = input()
    if answer == 'n':
        print('Manual improvement of the cocktail by an expert.')
        print('You can edit the cocktail with the following commands, but make sure that it satisfies the constraints')
        print("\tdesired ingredients: " + str(desired_ingredients))
        print("\tundesired ingredients: " + str(undesired_ingredients))
        print_commands()
        missing_desired_ingredients = contained_undesired_ingredients = set([0])
        while missing_desired_ingredients or contained_undesired_ingredients:
            command = ['']
            while command[0] != 'save':
                command = input().split()
                if not command:
                    command = ['']
                    continue
                if command[0] == 'add':
                    ingredient, quantity, unit = command[1:]
                    ingredient = ingredient.replace('-', ' ')
                    unit = unit.replace('none', '')
                    if ingredient not in ingredient_categories:
                        print('The ingredient ' + str(ingredient) + ' does not exist.')
                    else:
                        adapted_cocktail.add_ingredient((ingredient, quantity, unit))
                elif command[0] == 'replace':
                    ingredient, new_ingredient, quantity, unit = command[1:]
                    ingredient = ingredient.replace('-', ' ')
                    new_ingredient = new_ingredient.replace('-', ' ')
                    unit = unit.replace('none', '')
                    if ingredient not in adapted_cocktail.get_ingredient_set():
                        print('The cocktail does not contain the ingredient ' + str(ingredient))
                    else:
                        if new_ingredient not in ingredient_categories:
                            print('The ingredient ' + str(new_ingredient) + ' does not exist.')
                        else:
                            print('replacing ingredient..')
                            adapted_cocktail.replace_ingredient(ingredient, (new_ingredient, quantity, unit), False)
                elif command[0] == 'remove':
                    ingredient = command[1]
                    ingredient = ingredient.replace('-', ' ')
                    if ingredient not in adapted_cocktail.get_ingredient_set():
                        print('The cocktail does not contain the ingredient ' + str(ingredient))
                    else:
                        adapted_cocktail.remove_ingredient(ingredient)

            missing_desired_ingredients, contained_undesired_ingredients = \
                get_missing_desired_ingredients_and_contained_undesired_ingredients(adapted_cocktail,
                                                                                    desired_ingredients,
                                                                                    undesired_ingredients)
            print_solution_status(adapted_cocktail, missing_desired_ingredients, contained_undesired_ingredients)
            if missing_desired_ingredients or contained_undesired_ingredients:
                print('Please adapt the cocktail so it contains all desired ingredients and no undesired ones.')
                print_commands()

    answer = ''
    while answer != 'y' and answer != 'n':
        print('Would you like to rename the cocktail? (y/n)')
        answer = input()
    if answer == 'y':
        adapted_cocktail.title = input('Please enter the new title of the cocktail\n')

    print('Saving new cocktail to case base.')
    cocktails.append(adapted_cocktail)


def main():
    # Check if we have already established our own case base (with our own cocktails)
    if os.path.isfile('case_base.xml'):
        print('Load our case base.')
        cocktails = casebase.load_case_base()
    else:
        # Load official case base: the case base that is provided by the challenge
        print('Load official case base.')
        cocktails = casebase.load_official_case_base()
        # Extract all ingredients from the official case base
        casebase.extract_ingredients()

    ingredient_categories = casebase.load_ingredient_categories()

    while True:
        print('Please enter all desired ingredients as a space separated list. Substitute spaces in the ingredient\'s '
              'name by dashes. Enter "exit" to terminate the application.')
        desired_ingredients_with_not_existing = set([x.replace('-', ' ') for x in input().split()])
        desired_ingredients = copy.copy(desired_ingredients_with_not_existing)
        for desired_ingredient in desired_ingredients_with_not_existing:
            if desired_ingredient not in ingredient_categories and desired_ingredient != 'exit':
                print('Warning: The ingredient ' + str(desired_ingredient) + ' does not exist and will be ignored.')
                desired_ingredients.remove(desired_ingredient)

        if 'exit' in desired_ingredients:
            break

        print('Please enter all undesired ingredients as a space separated list.')
        undesired_ingredients_with_not_existing = set([x.replace('-', ' ') for x in input().split()])
        undesired_ingredients = copy.copy(undesired_ingredients_with_not_existing)
        for undesired_ingredient in undesired_ingredients_with_not_existing:
            if undesired_ingredient not in ingredient_categories:
                print('Warning: The ingredient ' + str(undesired_ingredient) + ' does not exist and will be ignored.')
                undesired_ingredients.remove(undesired_ingredient)


        #desired_ingredients = set(['gin', 'sparkling water', 'anise basil', 'brown sugar',
        #                           'ice cube', 'lemongrass', 'champagne'])
        #undesired_ingredients = set(['white rum', 'lime'])
        #desired_ingredients = set(['orange juice', 'gin', 'cognac'])
        #undesired_ingredients = set(['apple liqueur'])
        print('Searching for a cocktail with constraints')
        print("\tdesired ingredients: " + str(desired_ingredients))
        print("\tundesired ingredients: " + str(undesired_ingredients))
        cocktail = find_most_similar(cocktails, desired_ingredients, undesired_ingredients, ingredient_categories)[1]
        print()
        print("Most similar cocktail found:")
        print(cocktail)
        print()
        adapted_cocktail = adapt_solution(cocktail, desired_ingredients, undesired_ingredients, ingredient_categories)[0]
        if adapted_cocktail:
            evaluate_solution(adapted_cocktail, desired_ingredients, undesired_ingredients, ingredient_categories,
                              cocktails)
        casebase.save_case_base(cocktails)


if __name__ == '__main__':
    main()