import csv
import collections

'''
Script is used to check for duplicates in companylist_full.csv
'''

with open ('companylist_full.csv', newline='') as csvfile:
	symbol_list = []
	spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
	for row in spamreader:
		symbol = row[0]
		symbol_list.append(symbol)
	print ([item for item, count in collections.Counter(symbol_list).items() if count > 1])