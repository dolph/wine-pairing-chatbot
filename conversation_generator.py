# This Python file uses the following encoding: utf-8
from __future__ import unicode_literals

import copy
import json
import random


# This is the basis for the conversation that we're going to generate.
workspace = None
with open('workspace.json', 'r') as f:
    workspace = json.loads(f.read())


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
        # Hardcoded value based on the established conversation dialog tree:
        "dialog_node": "node_3_1515535851961",
        "selector": "body"
    }
}

# The initial value here is based on the established conversation dialog tree,
# and we build from there, changing this value as we create new nodes.
PREVIOUS_NODE_ID = "Welcome"


def build_node(entities, text):
    """Build a conversation node.

    `entities` is the list of conversation entities that will trigger this
    dialog node. The more entities that are specified, the more specific the
    match becomes.

    `text` is the value of Watson's conversational response.

    """
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


NODES = []

# We're going to pre-compute results for a certain number of ingredients.
for i in range(1000):
    entities = []
    response = 'Hello, %d' % i
    node = build_node(entities, response)
    workspace['dialog_nodes'].append(node)


# 1 is a magic value here, based on the established conversation dialog tree
# that we have appended to, which corresponds to the "cheers!" node. We set the
# previous sibling to be the last dialog node that we created.
workspace['dialog_nodes'][1]['previous_sibling'] = PREVIOUS_NODE_ID

# Output compressed JSON to stdout. This can be redirected to a JSON file.
print(json.dumps(workspace, indent=None, separators=(',', ':')))
