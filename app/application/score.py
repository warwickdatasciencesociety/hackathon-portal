import random
import math
import os
def evaluate_score(filename, ml_filename):
    import csv
    truth = {}
    user = {}
    try:
        print(os.listdir('.'))
        with open(ml_filename) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    line_count += 1
                    continue
                else:
                    truth[row[0]] = row[3]
                    
        with open(filename) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    line_count += 1
                    continue
                else:
                    if row[0] in truth.keys():
                        user[row[0]] = row[3]
        

        rmse = 0
        for i in truth.keys():
            rmse += (float(truth[i]) - float(user[i])) ** 2 
        rmse = rmse / len(truth)
        rmse = rmse ** .5
        return rmse
    except:
        return 2147483647
