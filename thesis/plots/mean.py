import statistics

file = open('data', 'r')
values = []
for line in file:
    value = float(line[line.index(',') + 1 : -2])
    #print(value)
    values.append(value)
print(statistics.mean(values))
