# This Python file uses the following encoding: utf-8
from __future__ import unicode_literals

import copy
import uuid
import itertools
import json
import random


d = None
with open('winefolly.json', 'r') as f:
    d = json.loads(f.read())

workspace = None
with open('workspace.json', 'r') as f:
    workspace = json.loads(f.read())


foods = list(d.keys())
categories = list(d[foods[0]].keys())

CATEGORY_COLLOQUIAL = {
    'bold-red': 'bold red wine',
    'medium-red': 'medium red wine',
    'light-red': 'light red wine',
    # 'rose': 'rosé',
    'rose': 'rose',
    'rich-white': 'rich white wine',
    'light-white': 'light white wine',
    'sparkling': 'sparkling wine',
    'sweet-white': 'sweet white wine',
    'dessert': 'dessert wine'
}
REDS = set([
    'light red wine',
    'medium red wine',
    'bold red wine'])
WHITES = set([
    'rich white wine',
    'light white wine',
    'sweet white wine'])

VARIETALS = {
    'bold-red': [
        'Malbec',
        # 'Shiraz',
        'Cabernet Sauvignon'],
        # 'Mourvèdre',
        # 'Bordeaux blend'],
        # 'Meritage',
        # 'Pinotage'],
    'medium-red': [
        'Merlot',
        # 'Sangiovese',
        'Zinfandel'],
        # 'Cabernet Franc',
        # 'Tempranillo'],
        # 'Nebbiolo',
        # 'Barbera'],
        # 'Côtes du Rhône blend'],
    'light-red': [
        'Pinot Noir',
        'Grenache'],
        # 'Gamay',
        # 'St. Laurent',
        # 'Carignan',
        # 'Counoise'],
    'rose': [
        'Provencal Rose',
        'White Zinfandel'],
        # 'Rosé de Loire',
        # 'Pinot Noir Rosé',
        # 'Syrah Rosé',
        # 'Garnacha Rosado'],
        # 'Bandol Rosé',
        # 'Tempranillo Rosé',
        # 'Saignée method Rosé'],
    'rich-white': [
        'Chardonnay'],
        # 'Sémillon',
        # 'Viognier',
        # 'Marsanne',
        # 'Roussanne'],
    'light-white': [
        'Sauvignon blanc',
        # 'Albarino',
        # 'Pinot Blanc',
        # 'Vermentino',
        # 'Melon de Bourgogne',
        # 'Garganega',
        # 'Trebbiano',
        'Pinot Grigio'],
    'sparkling': [
        'Champagne',
        'Prosecco'],
        # 'Cremant',
        # 'Cava'],
        # 'Metodo classico'],
    'sweet-white': [
        'Moscato',
        'Riesling'],
        # 'Chenin Blanc',
        # 'Gewurztraminer',
        # 'a late-harvest white'],
        # 'Alsatian Pinot Gris'],
    'dessert': [
        'Port',
        'Sherry'],
        # 'Madeira'],
        # 'Vin Santo',
        # 'Pedro Ximénez']
}


DIALOG_NODE_TEMPLATE = {
    # Normally, milliseconds since UNIX epoch, e.g. : "node_2_1515535851961"
    # "dialog_node": None,
    # "title": None,
    # "conditions": None,
    # "context": None,
    # "description": None,
    "output": {
        "text": {
            "selection_policy": "sequential",
            "values": []
        }
    },
    # "previous_sibling": None,
    "next_step": {
        "behavior": "jump_to",
        "dialog_node": "node_3_1515535851961",
        "selector": "body"
    },
    # "parent": None,
    # "type": "standard",
    # "metadata": {},
    # "created": "2018-01-01T00:00:00.000Z",
    # "updated": "2018-01-01T00:00:00.000Z"
}

PREVIOUS_NODE_ID = "Welcome"


def new_node_id():
    # return 'node_2_%s' % uuid.uuid4().hex[:6]
    return 'node_2_%d' % random.randrange(1111111111111, 9999999999999)

def build_node(entities, text):
    global PREVIOUS_NODE_ID

    node = copy.deepcopy(DIALOG_NODE_TEMPLATE)
    node['dialog_node'] = new_node_id()
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
        alternatives = [
            rating[0] for rating in ratings if rating[1] == ratings[0][1] - 1]

        primary_colloquials = set()
        primary_variatals = set()
        for x in primary:
            primary_colloquials.add(CATEGORY_COLLOQUIAL[x])
            for variatal in VARIETALS[x]:
                primary_variatals.add(variatal)

        alternative_colloquials = set()
        for x in alternatives:
            alternative_colloquials.add(CATEGORY_COLLOQUIAL[x])

        response = ''
        """
        if len(primary_colloquials) == len(CATEGORY_COLLOQUIAL):
            response += (
                'I would recommend any wine for that. You literally can\'t go '
                'wrong.')
        else:
        """
        response += 'I would recommend a {0}, such as {1}.'.format(
            oxford_or(summarize_wine_categories(primary_colloquials)),
            oxford_or(primary_variatals))

        if False and alternative_colloquials:
            response += (
                ' You could alternatively go for a {0}.'.format(
                    oxford_or(summarize_wine_categories(alternative_colloquials))))

        node = build_node(selected_foods, response)
        workspace['dialog_nodes'].append(node)

        # print(response)
    # print(number_of_foods)

workspace['dialog_nodes'][1]['previous_sibling'] = PREVIOUS_NODE_ID
print(json.dumps(workspace, indent=None, separators=(',', ':')))
