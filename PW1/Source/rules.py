import numpy as np
import pandas as pd
import itertools

# COMMAND LINE ARGUMENTS #
#file_name, class_index = '../Data/contact-lenses.csv', 4
#file_name, class_index = '../Data/balance-scale.data', 0
file_name, class_index = '../Data/car.data', 6
#file_name, class_index = '../Data/nursery.data', 8
#file_name, class_index = '../Data/agaricus-lepiota.data', 0

# index of the column that contains the class label
test_percentage = 0.1 # percentage of the dataset that will be used for testing
seed = 42 # in order to be able to reproduce my results
print_coverage = True

dataset = pd.read_csv(file_name, sep=',', header=None).values
num_rows, num_cols = np.shape(dataset)
num_test_rows = int(round(test_percentage * num_rows))
num_training_rows = num_rows - num_test_rows
feature_indices = list(range(class_index)) + list(range(class_index + 1, num_cols))
np.random.seed(seed)
np.random.shuffle(dataset)
training = dataset[num_test_rows:]
test = dataset[:num_test_rows]

print('Number of training instances: ' + str(num_training_rows))
print('Number of test instances: ' + str(num_test_rows))

def print_rule(feature_combination, attribute_values, assigned_class):
    out = ''
    for feature_index, attribute_value in zip(feature_combination, attribute_values):
        out += '#' + str(feature_index) + ' = ' + str(attribute_value) + ' ∧ '
    print(out[:-2] + '⇒ ' + str(assigned_class))

# Data structure for a rule. Tuple (features, values, class)
# where features: list of indices of the involved features
# values = values of these features
# class = class that is assigned to instance if it satisfies the condition
rules = []
unclassified = training # in the beginning the whole training set is unclassified

while unclassified.shape[0]:
    for num_combinations in range(1, num_cols):
        all_in_same_class = None # just declare it outside the below loop so we can propagate the break
        for feature_combination in itertools.combinations(feature_indices, num_combinations):
            satisfy_indices = [0]
            all_in_same_class = True
            for index in range(1, unclassified.shape[0]):
                conditions_satisfied = True
                for feature_index in feature_combination:
                    if unclassified[0][feature_index] != unclassified[index][feature_index]:
                        conditions_satisfied = False
                        break
                if conditions_satisfied:
                    if unclassified[0][class_index] != unclassified[index][class_index]:
                        all_in_same_class = False
                        break
                    satisfy_indices.append(index)

            # Create a new rule when all instances that satisfy the condition
            # are in the same class
            if all_in_same_class:
                new_rule = (feature_combination,
                            [unclassified[0][feature_index] for feature_index in feature_combination],
                            unclassified[0][class_index])
                print_rule(*new_rule)
                if print_coverage:
                    print('Coverage: {} instances {:.2f}% of all instances'.
                          format(len(satisfy_indices), 100 * len(satisfy_indices) / num_training_rows))
                rules.append(new_rule)
                unclassified = np.delete(unclassified, satisfy_indices, 0)
                break
        if all_in_same_class:
            break

print('Number of derived rules: ' + str(len(rules)))

# Finally use our rules to predict class labels on the test dataset
num_classified_correctly = 0
for instance in test:
    for rule in rules:
        condition_satisfied = True
        for (x, y) in zip(rule[0], range(len(rule[0]))):
            if instance[x] != rule[1][y]:
                condition_satisfied = False
                break
        if condition_satisfied:
            if instance[class_index] == rule[2]:
                num_classified_correctly += 1
            break
print('Accuracy on test dataset: {:.2f}%'.format(100 * num_classified_correctly / num_test_rows))

#numpy.savetxt('rules.txt', )



