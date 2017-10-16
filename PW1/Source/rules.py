import numpy as np
import pandas as pd
import itertools

# COMMAND LINE ARGUMENTS #
file_name = '../Data/contact-lenses.csv'
class_index = 4 # index of the column that contains the class label
test_percentage = 0.1 # percentage of the dataset that will be used for testing
seed = 42 # in order to be able to reproduce my results

dataset = pd.read_csv(file_name, sep=',', header=None).values
num_rows, num_cols = np.shape(dataset)
num_test_rows = int(round(test_percentage * num_rows))
feature_indices = list(range(class_index)) + list(range(class_index + 1, num_cols))
np.random.seed(seed)
np.random.shuffle(dataset)
training = dataset[num_test_rows:]
test = dataset[:num_test_rows]


# First we determine which values a certain feature can take.
feature_values = dict()
for i in feature_indices:
    # i-th column's values will be extracted
    feature_values[i] = list(set(training[:, i]))
    #print(feature_values[i])

# Data structure for a rule. Tuple (features, values, class)
# where features: list of indices of the involved features
# values = values of these features
# class = class that is assigned to instance if it satisfies the condition
rules = []
feature_combinations = feature_indices
unclassified = training
for num_combinations in range(1, num_cols):
    # If there are no unclassified instances we can stop
    if not unclassified.size:
        break
    feature_combinations = list(itertools.combinations(feature_indices, num_combinations))

    for feature_combination in feature_combinations:
        possible_rules = list(itertools.product(*[feature_values[i] for i in feature_combination]))

        for possible_rule in possible_rules:
            first_class = None
            satisfy_indices = []
            all_in_same_class = True
            for index, instance in enumerate(unclassified):
                condition_satisfied = True
                for (x, y) in zip(feature_combination, range(num_combinations)):
                    if instance[x] != possible_rule[y]:
                        condition_satisfied = False
                        break
                if condition_satisfied:
                    #print('c: ' + str(possible_rule) + ' i: ' + str(instance))
                    if first_class == None:
                        first_class = instance[class_index]
                    elif first_class != instance[class_index]:
                        all_in_same_class = False
                        break
                    satisfy_indices.append(index)

            # Create a new rule when all instances that satisfy the condition
            # are in the same class and also check that at least one instance
            # satisfies the rule
            if all_in_same_class and satisfy_indices != []:
                new_rule = (feature_combination, possible_rule, first_class)
                print(new_rule)
                print(satisfy_indices)
                rules.append(new_rule)
                unclassified = np.delete(unclassified, satisfy_indices, 0)
            #print(np.shape(unclassified))

    #print(list(feature_combinations))

#features = df.values[:,[1,2,3,4]]
#print(features)
#labels = df.values[:,0]
#print(labels)






