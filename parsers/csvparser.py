"""
Parses content from CSV files
"""
import csv

def get_rows_as_list(filename):
    """Returns a list of rows (represented as a list)"""
    with open(filename, newline='') as csvfile:
        csvreader = csv.reader(csvfile)
        return list(csvreader)
