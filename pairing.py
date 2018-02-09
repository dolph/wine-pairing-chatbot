# This Python file uses the following encoding: utf-8
from __future__ import unicode_literals

import copy
import itertools
import json
import random


# This is the data for the wine pairing combinatorics that we're going to
# pre-compute as dialog nodes.
d = None
with open('winefolly.json', 'r') as f:
    d = json.loads(f.read())

# This is the basis for the conversation that we're going to generate.
workspace = None
with open('workspace.json', 'r') as f:
    workspace = json.loads(f.read())


foods = list(d.keys())
categories = list(d[foods[0]].keys())

# The keys are how we track wines programmatically, and the values are how we
# refer to those wines colloquially.
CATEGORY_COLLOQUIAL = {
    'bold-red': 'bold red wine',
    'medium-red': 'medium red wine',
    'light-red': 'light red wine',
    'rose': 'rose',
    'rich-white': 'rich white wine',
    'light-white': 'light white wine',
    'sparkling': 'sparkling wine',
    'sweet-white': 'sweet white wine',
    'dessert': 'dessert wine'
}

# These are like-sets of wine that we can use to produce more natural dialog.
REDS = set([
    'light red wine',
    'medium red wine',
    'bold red wine'])
WHITES = set([
    'rich white wine',
    'light white wine',
    'sweet white wine'])

# These are specific varietals of the broader categories that we're using.
VARIETALS = {
    'bold-red': [
        'Malbec',
        'Cabernet Sauvignon'],
    'medium-red': [
        'Merlot',
        'Zinfandel'],
    'light-red': [
        'Pinot Noir',
        'Grenache'],
    'rose': [
        'Provencal Rose',
        'White Zinfandel'],
    'rich-white': [
        'Chardonnay'],
    'light-white': [
        'Sauvignon blanc',
        'Pinot Grigio'],
    'sparkling': [
        'Champagne',
        'Prosecco'],
    'sweet-white': [
        'Moscato',
        'Riesling'],
    'dessert': [
        'Port',
        'Sherry'],
}


# This is the basis for the Watson conversation dialog nodes that we'll be
# producing. There are additional keys that we'll populate for individual node
# instances, but we'll always start with a copy of this template.
DIALOG_NODE_TEMPLATE = {
    "output": {
        "text": {
            "selection_policy": "sequential",
            "values": []
        }
    },
    "next_step": {
        "behavior": "jump_to",
        "dialog_node": "node_3_1515535851961",
        "selector": "body"
    }
}

# The initial value here is based on the established conversation dialog tree,
# and we build from there, changing this value as we create new nodes.
PREVIOUS_NODE_ID = "Welcome"


def build_node(entities, text):
    global PREVIOUS_NODE_ID

    # Start with a copy of our template.
    node = copy.deepcopy(DIALOG_NODE_TEMPLATE)

    # Populate the values that make this dialog node unique.
    node['dialog_node'] = 'node_2_%d' % (
        random.randrange(1111111111111, 9999999999999))
    node['conditions'] = ' && '.join(entities)
    node['output']['text']['values'].append(text)

    # Set the previous sibling to the last node ID we created.
    node['previous_sibling'] = PREVIOUS_NODE_ID

    # Remember the current node ID for later use.
    PREVIOUS_NODE_ID = node['dialog_node']

    return node


def _oxford(s, conjunction):
    """Join list into a Oxford-comma separated string with a conjunction."""
    l = list(s)

    if len(l) == 0:
        raise Exception('List is empty! Unable to build comma-separated list.')
    elif len(l) == 1:
        # Return the one element by itself.
        return l[0]
    elif len(l) == 2:
        # Return both elements, joined with the conjunction.
        return (' %s ' % conjunction).join(l)
    if len(l) >= 3:
        # Return all elements, first joined with commas, with the last element
        # joined with a comma and conjunction.
        return '%s, %s %s' % (
            ', '.join(l[:-1]),
            conjunction,
            l[-1])


def oxford_or(s):
    """Join set into a Oxford-comma separated string with an OR."""
    return _oxford(s, 'or')


def oxford_and(s):
    """Join set into a Oxford-comma separated string with an AND."""
    return _oxford(s, 'and')


def summarize_wine_categories(s):
    """List wines as you would colloquially."""
    if s.issuperset(REDS):
        s = s.difference(REDS)
        s.add('any red wine')
    if s.issuperset(WHITES):
        s = s.difference(WHITES)
        s.add('any white wine')
    return s


NODES = []

# We're going to pre-compute results for a certain number of ingredients.
for number_of_foods in range(4, 0, -1):

    # Track the number of iterations so that we can fine tune the size of the
    # output.
    iteration = 0

    # selected_foods will be the foods that we're making a pairing against.
    for selected_foods in itertools.combinations(foods, number_of_foods):
        iteration += 1
        if number_of_foods == 4 and iteration >= 13383:
            break
        # For each selected food, we're going to start by collecting the
        # pairing recommendations, and adding them to the ratings.
        ratings = []
        for food in selected_foods:
            for category in categories:
                ratings.append((category, d[food][category]))
        ratings = sorted(ratings, key=lambda rating: -1 * rating[1])

        primary = [
            rating[0] for rating in ratings if rating[1] == ratings[0][1]]

        primary_colloquials = set()
        primary_variatals = set()
        for x in primary:
            primary_colloquials.add(CATEGORY_COLLOQUIAL[x])
            for variatal in VARIETALS[x]:
                primary_variatals.add(variatal)

        if len(primary_colloquials) == len(CATEGORY_COLLOQUIAL):
            response = (
                'I would recommend any wine for that. You literally can\'t go '
                'wrong.')
        else:
            response = 'I would recommend a {0}, such as {1}.'.format(
                oxford_or(summarize_wine_categories(primary_colloquials)),
                oxford_or(primary_variatals))

        node = build_node(selected_foods, response)
        workspace['dialog_nodes'].append(node)


# 1 is a magic value here, based on the established conversation dialog tree
# that we have appended to, which corresponds to the "cheers!" node. We set the
# previous sibling to be the last dialog node that we created.
workspace['dialog_nodes'][1]['previous_sibling'] = PREVIOUS_NODE_ID

# Output compressed JSON to stdout. This can be redirected to a JSON file.
print(json.dumps(workspace, indent=None, separators=(',', ':')))
