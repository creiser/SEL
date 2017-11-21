# Example usage:
# python ./randomforest.py ../Data/house-votes-84.data -t 0.9 -c first -pm
# python ./randomforest.py ../Data/agaricus-lepiota.data -t 0.9 -c first -pm
# python ./randomforest.py ../Data/car.data -t 0.9 -c last -pm

import numpy as np
import pandas as pd
import itertools
import argparse

def percentage_type(x):
    x = float(x)
    if not 0.0 <= x <= 1.0:
        raise argparse.ArgumentTypeError("Value must be between 0.0 and 1.0")
    return x

parser = argparse.ArgumentParser('randomforest')
parser.add_argument('file_name',
                    help='.csv file that both contain training and test data.', type=str)
parser.add_argument('-c', '--class_index',
                    help='Index of the column that contains the class label. Use "first" respective "last" to specify'
                         ' the class label is in the first respective the last column. Default: "last"',
                    type=str, default='last')
parser.add_argument('-t', '--test_percentage',
                    help='Percentage from 0.0 to 1.0 of the dataset that will be used for testing. Default: 0.1',
                    type=percentage_type, default=0.1)
parser.add_argument('-s', '--seed',
                    help='Seed with which the random number generator is initialized. Default: 42',
                    type=int, default=42)
parser.add_argument('-pm', '--print_metrics',
                    help='If set detailed metrics (precision, coverage) of each generated rule is printed.',
                    action='store_true')
args = parser.parse_args()

dataset = pd.read_csv(args.file_name, sep=',')
header = list(dataset)
dataset = dataset.values
num_rows, num_cols = np.shape(dataset)
num_test_rows = int(round(args.test_percentage * num_rows))
num_training_rows = num_rows - num_test_rows
if args.class_index == 'first':
    args.class_index = 0
elif args.class_index == 'last':
    args.class_index = num_cols - 1
elif args.class_index.is_digit() and not 0 <= int(args.class_index) < num_cols:
    parser.print_usage()
    exit('randomforest: error: argument -c/--class_index: Class index is out of bounds.')
class_index = args.class_index
feature_indices = list(range(class_index)) + list(range(class_index + 1, num_cols))
np.random.seed(args.seed)
np.random.shuffle(dataset)
training = dataset[num_test_rows:]
test = dataset[:num_test_rows]
print('Number of training instances: ' + str(num_training_rows))
print('Number of test instances: ' + str(num_test_rows))









































if False:
    def print_rule(feature_combination, attribute_values, assigned_class):
        out = 'IF '
        for feature_index, attribute_value in zip(feature_combination, attribute_values):
            out += header[feature_index] + ' = ' + str(attribute_value) + ' AND '
        print(out[:-4] + 'THEN ' + str(assigned_class))

    # Data structure for a rule. Tuple (feature_combination, attribute_values, assigned_class)
    # where feature_combination: list of indices of the involved features
    # attribute_values = values of these features
    # assigned_class = class that is assigned to instance if it satisfies the condition
    rules = []
    unclassified = training # in the beginning the whole training set is unclassified

    # Continue as long as there are unclassified examples.
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

                # Create a new rule only if all instances that satisfy the condition
                # are in the same class
                if all_in_same_class:
                    new_rule = (feature_combination,
                                [unclassified[0][feature_index] for feature_index in feature_combination],
                                unclassified[0][class_index])
                    print_rule(*new_rule)
                    if args.print_metrics:
                        # Printing the precision during training makes no sense since with this algorithm the precision
                        # of each rule is 1.0
                        print('Coverage: {} instances {:.2f}% of all instances'.
                              format(len(satisfy_indices), 100 * len(satisfy_indices) / num_training_rows))
                    rules.append(new_rule)
                    # Delete all the examples that are covered by the new rule
                    unclassified = np.delete(unclassified, satisfy_indices, 0)
                    break
            if all_in_same_class:
                break

    print('Number of derived rules: ' + str(len(rules)))


    # Finally use our rules to predict class labels on the test dataset
    num_classified_correctly = 0
    rule_classified_correctly_arr = [0] * len(rules)
    rule_used_arr = [0] * len(rules)
    for instance in test:
        for rule_index, rule in enumerate(rules):
            condition_satisfied = True
            for (x, y) in zip(rule[0], range(len(rule[0]))):
                if instance[x] != rule[1][y]:
                    condition_satisfied = False
                    break
            if condition_satisfied:
                rule_used_arr[rule_index] += 1
                # Compare the predicted label to the actual label
                if instance[class_index] == rule[2]:
                    num_classified_correctly += 1
                    rule_classified_correctly_arr[rule_index] += 1
                break

    if args.print_metrics:
        print('-' * 80 + '\n\nDetailed metrics for using the rules on the test dataset:')
        for rule, rule_used, rule_classified_correctly in zip(rules, rule_used_arr, rule_classified_correctly_arr):
            print_rule(*rule)
            print('Coverage: {} instances {:.2f}% of all instances'.
                  format(rule_used, 100 * rule_used / num_test_rows))
            print('Precision: {:.2f}%'.format(100 * rule_classified_correctly / rule_used))

    print('Accuracy on test dataset: {:.2f}%'.format(100 * num_classified_correctly / num_test_rows))
