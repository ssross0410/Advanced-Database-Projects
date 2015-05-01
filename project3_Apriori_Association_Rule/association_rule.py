import sys
import csv
import collections
import itertools
from operator import itemgetter
from collections import OrderedDict

# dict of all the large itemsets
item_sets = {}

# dict of frequent itemsets, support value greater than the min support 
freq_items = {}

# the association rule dict
associate_rule = {}

# the main function
def main():
    if len(sys.argv) == 4:
        fileName = sys.argv[1]
        minSup = sys.argv[2]
        minConf = sys.argv[3]
    else:
        error()
    try:
        with open(fileName,'rU') as dataFile:
            reader = csv.reader(dataFile)
            database = list(reader)
            transaction_num = len(database)
            apriori(database, minSup)
            get_association(database, minConf)
            
            printing = [(y, freq_items[x][y]) for x in freq_items.keys()
                for y in freq_items[x].keys()]
            printing = sorted(printing, key=itemgetter(1), reverse=True)

            ordered_asso = OrderedDict(sorted(associate_rule.items(), key=lambda (k, (v1, v2)):
                [float(v1)/float(v2), v2], reverse=True))

            write_output(printing, ordered_asso, minSup, minConf, transaction_num)
    except:
        error()

# The main functino to execute apriori algorithm
def apriori(database, minSup):
    freq_itemsets1(database, minSup)
    prev_lk = []
    for key in freq_items[1]:
        prev_lk.append(key)

    k = 2
    while prev_lk:  
        cur_ck = get_candidate_itemsets(prev_lk)
        k_item_sets = {}
        for transaction in database:
            transaction = set(transaction)
            Ct = get_Ct_candidate(transaction, cur_ck)
            for Ct_candidate in Ct:
                get_support(transaction, Ct_candidate, k_item_sets)

        item_sets[k] = k_item_sets
        k_freq_itemsets = {}
        cur_lk = []
        for item, support in k_item_sets.iteritems():
            if int(support) >= int(float(minSup) * len(database)):
                k_freq_itemsets[item] = support
                cur_lk.append(item)
        freq_items[k] = k_freq_itemsets
        prev_lk = cur_lk
        k += 1

def freq_itemsets1(database, minSup):
    rowNum = 0
    itemsets_1 = {}
    for row in database:
        row = set(row)
        rowNum += 1
        for item in row:
            if item != 'NA' and item != 'N/A':
                items = [item]
                if item and rowNum != 1:
                    tup = tuple(items)
                    if tup in itemsets_1:
                        itemsets_1[tup] += 1
                    else:
                        itemsets_1[tup] = 1

    item_sets[1] = itemsets_1
    freq_itemsets_1 = {}
    for key, value in itemsets_1.iteritems():
        if int(value) >= int(float(minSup) * rowNum):
            freq_itemsets_1[key] = value
    freq_items[1] = freq_itemsets_1

def get_candidate_itemsets(prev_lk):
    cur_ck = [] 
    length = 0

    # the join step
    for set1, set2 in itertools.combinations(prev_lk, 2):
        length = len(set1)
        if set1[:-1] == set2[:-1]:
            addedItems = [set1[-1], set2[-1]]
            newSet = set1[:-1] + tuple(addedItems)
            cur_ck.append(newSet)
    
    # the prune step
    for itemset in cur_ck:
        for subset in itertools.combinations(itemset, length):
            if not subset in prev_lk:
                cur_ck.remove(itemset)
                break

    return cur_ck

def get_Ct_candidate(transaction, cur_ck):
    Ct = list(cur_ck)
    for itemset in Ct:
        for item in itemset:
            if not item in transaction:
                Ct.remove(itemset)
                break
    return Ct

def get_support(transaction, Ct_candidate, k_item_sets):
    if all(item in transaction for item in Ct_candidate):
        if Ct_candidate in k_item_sets:
            k_item_sets[Ct_candidate] += 1
        else:
            k_item_sets[Ct_candidate] = 1

def get_association(database, minConf):
    for rhs in freq_items[1].keys():
        length = 0
        for value in freq_items.values():
            for lhs, lhs_support in value.iteritems():
                length = len(lhs)
                if all(i not in lhs for i in rhs):
                    for transaction in database:
                        if all(left_item in transaction for left_item in lhs) and \
                                all(rgt_item in transaction for rgt_item in rhs):
                            rule = '['
                            for left_item in lhs:
                                rule += left_item + ','
                            rule = rule[:-1] + ']'
                            for rgt_item in rhs:
                                rule += ' ==> [' + rgt_item + ']'
                            if rule in associate_rule:
                                associate_rule[rule][0] += 1
                            else:
                                l1 = []
                                l1.append(1)
                                l1.append(lhs_support)
                                associate_rule[rule] = l1

def write_output(printing, ordered_asso, minSup, minConf, transaction_num):
    with open('output.txt', 'wt') as output:
            message = "High-frequency itemsets (min_sup={0}%)\n".format(float(minSup)*100)
            output.write(message + '\n')
            for tup in printing:
                message =  "[{0}], {1:.1f}%".format(",".join(list(tup[0])), 
                    float(tup[1])/float(transaction_num) * 100)
                output.write(message + '\n')
            output.write("\n\n")
            message = "High-confidence associate rules (min_conf={0}%)\n".format(
                float(minConf)*100)
            output.write(message)
            for tup in ordered_asso:
                conf = float(ordered_asso[tup][0])/float(ordered_asso[tup][1])
                if conf >= float(minConf):
                    message = "{0} (Conf: {1:.1f}%, Supp: {2:.1f}%)".format(tup ,conf*100, 
                        float(ordered_asso[tup][1])/float(transaction_num)*100)
                    output.write(message + '\n')        

def error():
    print 'Usage:' + "\n" + 'python association_rule.py <input_data> <min_sup> <min_conf>'

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print "\n"
        exit()