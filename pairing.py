import json


d = None
with open('winefolly.json', 'r') as f:
    d = json.loads(f.read())


foods = list(d.keys())
categories = list(d[foods[0]].keys())

for i1 in range(0, len(foods)):
    for i2 in range(i1 + 1, len(foods)):
        for i3 in range(i2 + 1, len(foods)):
            for i4 in range(i3 + 1, len(foods)):
                for i5 in range(i4 + 1, len(foods)):
                    for i6 in range(i5 + 1, len(foods)):
                        food1 = foods[i1]
                        food2 = foods[i2]
                        food3 = foods[i3]
                        food4 = foods[i4]
                        food5 = foods[i5]
                        food6 = foods[i6]

                        for category in categories:
                            rating = d[food1][category] + d[food2][category] + d[food3][category] + d[food4][category] + d[food5][category] + d[food6][category]
                            if rating >= 3:
                                print(food1, food2, food3, food4, food5, food6, category, rating)
