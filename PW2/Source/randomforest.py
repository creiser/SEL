# Example usage:
# python ./randomforest.py ../Data/house-votes-84.data -t 0.9 -c first -pm
# python ./randomforest.py ../Data/agaricus-lepiota.data -t 0.9 -c first -pm
# python ./randomforest.py ../Data/car.data -t 0.9 -c last -pm

import numpy as np
import pandas as pd
import itertools
import argparse
import math
import random

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
parser.add_argument('-nt', '--num_trees',
                    help='Number of decision trees built. Default: 100',
                    type=int, default=100)
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

asubtree = {}
atree = {'attribute_index' : 0, 'leaves' : {'blue' : '+', 'red' : asubtree}}

# TODO: Make sure that everything is a str.


def create_attribute_subsets(subset, attribute_index):
    attribute_subsets = {}
    for sample in subset:
        if sample[attribute_index] in attribute_subsets:
            attribute_subsets[sample[attribute_index]].append(sample)
        else:
            attribute_subsets[sample[attribute_index]] = [sample]
    return attribute_subsets


def create_class_counts(subset):
    class_counts = {}
    for sample in subset:
        if sample[class_index] in class_counts:
            class_counts[sample[class_index]] += 1
        else:
            class_counts[sample[class_index]] = 1
    return class_counts


def get_most_common_class(subset):
    max_class_count, most_common_class = -1, ''
    class_counts = create_class_counts(subset)
    for the_class, class_count in class_counts.items():
        if class_count > max_class_count:
            max_class_count, most_common_class = class_count, the_class
    return most_common_class


# Aggregate all the attribute values
attribute_values = [None] * num_cols
for attribute_index in feature_indices:
    attribute_values[attribute_index] = list(set([x[attribute_index] for x in dataset]))

def build_tree(subset, unused_attributes):
    # If all elements of subset are in the same class
    if len(set([x[class_index] for x in subset])) == 1:
        return subset[0][class_index]

    if len(unused_attributes) == 0:
        # Get most common class
        return get_most_common_class(subset)

    min_index, min_entropy = 0, 100000000
    for attribute_index in unused_attributes:
        # Create subsets for that given attribute
        attribute_subsets = create_attribute_subsets(subset, attribute_index)

        # Calculate entropy of the generated subsets
        entropy = 0
        for attribute_subset in attribute_subsets.values():
            class_counts = create_class_counts(attribute_subset)

            attribute_subset_entropy = 0
            for class_count in class_counts.values():
                p_x = class_count / len(attribute_subset)
                attribute_subset_entropy -= p_x * math.log(p_x)

            entropy += (len(attribute_subset) / len(subset)) * attribute_subset_entropy

        # Minimum
        if entropy < min_entropy:
            min_index, min_entropy = attribute_index, entropy

    # Copy list otherwise our passed feature_indices array will be modified.
    unused_attributes = list(unused_attributes)
    unused_attributes.remove(min_index)

    # Reconstruct subsets of best attribute and use them to build subtrees recursively
    attribute_subsets = create_attribute_subsets(subset, min_index)
    tree = {'attribute_index': min_index, 'subtrees': {}}

    # Make sure to add for all values that exist in the training dataset labels
    most_common_class = None
    for attribute_value in attribute_values[min_index]:
        if attribute_value in attribute_subsets and len(attribute_subsets[attribute_value]):
            tree['subtrees'][attribute_value] = build_tree(attribute_subsets[attribute_value], unused_attributes)
        else:
            if not most_common_class:
                most_common_class = get_most_common_class(subset)
            tree['subtrees'][attribute_value] = most_common_class

    return tree


def classify(example, tree):
    if isinstance(tree, str):
        return tree
    else:
        return classify(example, tree['subtrees'][example[tree['attribute_index']]])

def majority_vote(example, trees):
    votes = {}
    for tree in trees:
        prediction = classify(example, tree)
        #print(prediction)
        if prediction in votes:
            votes[prediction] += 1
        else:
            votes[prediction] = 1
    majority_prediction, max_vote = None, 0
    for prediction, num_votes in votes.items():
        if num_votes > max_vote:
            majority_prediction, max_vote = prediction, num_votes
    return majority_prediction


def pretty_tree(tree):
    if isinstance(tree, str):
        return tree
    else:
        pretty_subtrees = {}
        for attribute_value, subtree in tree['subtrees'].items():
            pretty_subtrees[attribute_value] = pretty_tree(subtree)
        return { 'attribute_index' : header[tree['attribute_index']], 'subtrees' : pretty_subtrees}

the_tree = build_tree(training, feature_indices)
#print(pretty_tree(the_tree))

num_classified_correctly = sum([classify(example, the_tree) ==
                                example[class_index] for example in test])
print('Single tree: Accuracy on test dataset: {:.2f}%'.format(100 * num_classified_correctly / num_test_rows))

# Perform bootstrap aggregating: Build trees from multiple sample sets
trees = []
for i in range(args.num_trees):
    bootstrap_sample_set = [random.choice(training) for j in range(len(training))]
    trees.append(build_tree(bootstrap_sample_set, feature_indices))
    #print(pretty_tree(trees[-1]))

num_classified_correctly = sum([majority_vote(example, trees) ==
                                example[class_index] for example in test])
print('Bagging: Accuracy on test dataset: {:.2f}%'.format(100 * num_classified_correctly / num_test_rows))

