from collections import defaultdict
from collections import OrderedDict
import csv

dicts = defaultdict(int)

with open('MyData.csv','rU') as dataFile:
		reader = csv.reader(dataFile)
		database = list(reader)

		for row in database:
			dicts[row[3]] += 1


with open('ModifiedData.csv', 'wb') as csvfile:
	spamwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
	for row in database:
		if dicts[row[3]] > 30:
			spamwriter.writerow(row)

counter = 0
ordered_dict = OrderedDict(sorted(dicts.items(), key=lambda (k, v) : v, reverse=True))
for key in ordered_dict:
	print key, ordered_dict[key]
	counter += ordered_dict[key]

print counter