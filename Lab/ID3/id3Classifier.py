import math
import json

def classify(tree, attribute_type, instance):
    if 'result' in tree:
        return tree['result']
    attribute = tree['attribute']
    if attribute_type[attribute] == 'D':
        return classify(tree['children'][instance[attribute]], attribute_type, instance)
    return classify(tree['children']['lt' if float(instance[attribute]) < tree['middle_value'] else 'gt'], attribute_type, instance)

def print_tree(tree, attribute_type, tabs=0):
    if 'result' in tree:
        print(' ' * 2 * tabs + 'result:', tree['result'])
        return
    print(' ' * 2 * tabs + 'attribute:', tree['attribute'])
    if attribute_type[tree['attribute']] == 'D':
        for value, subtree in tree['children'].items():
            print(' ' * 2 * tabs + f'= {value}:')
            print_tree(subtree, attribute_type, tabs + 1)
    else:
        print(' ' * 2 * tabs + f"< {tree['middle_value']}:")
        print_tree(tree['children']['lt'], attribute_type, tabs + 1)
        print(' ' * 2 * tabs + f"> {tree['middle_value']}:")
        print_tree(tree['children']['gt'], attribute_type, tabs + 1)

def JsonTree(tree, attribute_type):
    if 'result' in tree:
        return {'result': tree['result']}
    tree_json = {'attribute': tree['attribute']}
    if attribute_type[tree['attribute']] == 'D':
        tree_json['children'] = {value: JsonTree(subtree, attribute_type) 
                                 for value, subtree in tree['children'].items()}
    else:
        tree_json['middle_value'] = tree['middle_value']
        tree_json['children'] = {'lt': JsonTree(tree['children']['lt'], attribute_type),
                                 'gt': JsonTree(tree['children']['gt'], attribute_type)}
    return tree_json

def entropy(elements):
    total = sum(elements)
    return -sum(value / total * math.log(value / total, 2) if value != 0 else 0 for value in elements)

def computeID3(instances, attributeType, attributeVector = None):
    if attributeVector is None:
        attributeVector = set(range(len(instances[0])-1))
    if len({element[-1] for element in instances}) == 1:
        return {'result' : instances[0][-1]}
    if len(attributeVector) == 0:
        count = {}
        for element in instances:
            count[element[-1]] = count.get(element[-1],0) + 1
        return {'result' : max((count,value) for (value, count) in count.items())[1]}
    best_attribute = (math.inf,-1)
    for attribute in attributeVector:
        if attributeType[attribute] == 'D':
            attribute_entropy = 0
            for attribute_value in {element[attribute] for element in instances}:
                count = {}
                for element in instances:
                    if element[attribute] == attribute_value:
                        count[element[-1]] = count.get(element[-1],0) + 1
                attribute_entropy += sum(count.values()) / len(instances) * entropy(list(count.values()))
                best_attribute = min(best_attribute, (attribute_entropy, attribute))
        else:
            attributeElVector = sorted(list({float(element[attribute]) for element in instances}))
            for (index, value) in enumerate(attributeElVector[1:], 1):
                middlePoint = (attributeElVector[index - 1] + value) / 2
                count_lt = {}
                count_gt = {}
                for element in instances:
                    if float(element[attribute]) < middlePoint:
                        count_lt[element[-1]] = count_lt.get(element[-1], 0) + 1
                    else:
                        count_gt[element[-1]] = count_gt.get(element[-1], 0) + 1
                    attribute_entropy = sum(count_lt.values()) / len(instances) * entropy(list(count_lt.values()))            
                    attribute_entropy += sum(count_gt.values()) / len(instances) * entropy(list(count_gt.values()))
                    best_attribute = min(best_attribute, (attribute_entropy, attribute, middlePoint))

    bestAttribute = best_attribute[1]
    partitions = {}
    for instance in instances:
        if attributeType[bestAttribute] == 'D':
            partitions.setdefault(instance[bestAttribute], []).append(instance)
        else:
            partitions.setdefault('lt' if float(instance[bestAttribute]) < best_attribute[2] else 'gt', []).append(instance)

    tree = {'attribute': bestAttribute, 'children': {}}
    for (value, instances) in partitions.items():
        remove_best_attribute = True
        if attributeType[bestAttribute] == 'C':
            remove_best_attribute = len({instance[bestAttribute] for instance in instances}) == 1
            tree['middle_value'] = best_attribute[2]
        tree['children'][value] = computeID3(
            instances,
            attributeType,
            attributeVector - ({bestAttribute} if remove_best_attribute else set())
        )
    return tree

with open('data.csv') as file:
    lines = file.read().split('\n')
attribute_type = lines[0].split(',')
instances = [tuple(val for val in line.split(',')) for line in lines[1:] if line]


tree = computeID3(instances, attribute_type)
print_tree(tree, attribute_type)
print('\nclassification results:')
for instance in instances:
    print(classify(tree, attribute_type, instance), end=' ')
print('\n')

tree_json = JsonTree(tree, attribute_type)
with open('result.json', 'w') as file:
    json.dump(tree_json, file, indent=2)
