"""
Parses content from CSV files
"""
import csv

def get_rows_as_list(filename):
    """Returns a list of rows (represented as a list)"""
    with open(filename, newline='') as csvfile:
        csvreader = csv.reader(csvfile)
        return list(csvreader)

def get_rows_as_dict(filename):
    '''Returns as a dictionary of rows'''
    with open(filename, newline='') as csvfile:
        csvreader = csv.reader(csvfile)
        return {row[0]: row[1:] for row in csvreader}