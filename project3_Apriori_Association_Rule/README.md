Columbia University
COMS E6111  Advanced Database Systems
Project 3  Association Rule


a) Your name and your partner's name and Columbia UNI

Su Shen (ss4716)
Sihan Wang (sw2921)


b) A list of all the files that you are submitting

association_rule.py                 // The python file to execute the program.
README.md                           // README
output.txt                          // The output file showing the sample output under 
filter.py                           // The python file filtering on occurence of complaint type column


c)  A detailed description explaining: 
    (a) which NYC Open Data data set(s) you used to generate the INTEGRATED-DATASET file?
        311 Service Requests from 2010 to Present

    (b) what (high-level) procedure you used to map the original NYC Open Data data set(s) into your INTEGRATED-DATASET file?
        The procedures can be segmented into following 3 steps:

        1. Due to the large amount of the original data, we filter the original data and pick only the data between "01/01/2015 12:00:00 AM" and "01/01/2015 11:59:59 PM" on the column "Created Date".
        
        2. We removed some columns manually in advance are: Created Date, Closed Date, Address Type, Status, Due Date, Resolution Action Updated Date, Park Facility Name, School Name, School Number, School Region, School Code, School Phone Number, School Address, School City, School State, School Zip, School Not Found, School or Citywid Complaint, Vechile Type, Taxi Company Borough, Taxi Pick Up Location, Bridge Highway Name, Bridge Highway Direction, Road Ramp, Bridge Highway Segment, Garage Lot Name, Ferry Direction, Ferry Terminal Name. Those columns are either almost empty or dominant by only one type. For example in the "Address Type" column, "Address" takes up 99% of the all rows. 

        3. Because the support value of column "complaint type" is very low, we removed some rows first. If the occurences of a specific "complaint type" is less than 30, we delete the whole row. We use the "filter.py" to execute this step. This step removes approximately 450/3100 rows.

    (c) what makes your choice of INTEGRATED-DATASET file interesting
        First there are a lot of columns in each row, which means there will be vairous items in each transaction. This will be more appropriate for the implementation of a-priori algorithm and generating association rules.

        Second, running a-priori algorithm on this dataset will give us some insight on which complaint type is more prevalent in different seasons. For example, since we only focus on the date in winter, the most dominant complaint type is Heating problem, which is quite intuitive.

(d) Clear description of how to run your program (note that your project must compile/run under Linux in your CS account)

    $ python association_rule.py <input_data> <min_sup> <min_conf>

    Example:
    $ python association_rule.py ModifiedData.csv 0.15 0.7

e) A clear description of the internal design of your project
    We follow strictly the implementation of original a-priori algorithm described in the "Section 2.1 of the Agrawal and Srikant paper in VLDB 1994". We describe the steps here again:

    1. compute the large 1-itemsets.
    2. we iteratively find the large (k)-itemsets(denote as l_k) until l_k-1 becomes empty
    We continously find the candidates k-itemsets(denote as c_k) from l_k-1 through the join and prune step described in the paper. Then we loop through all the transactions in the database,
    get the itemsets both in c_k and a specific transaction. After then we leave only the itemsets exceeding the minimun support.

    After generating the frequent itemsets, we generate the associate rules from only the itemsets in frequent itemsets. For each itemset, we calculate all the possible rules can be derived.


f) The command line specification of an interesting sample run (i.e., a min_sup, min_conf combination that produces interesting results). Briefly explain why the results are interesting.
    
    set min_sup = 0.15 min_conf = 0.7, and we could see the result on the output.txt.
    
    And we choose the January result, the weather is very cold. So the complaint about the heat water takes up the most of complaints in our dataset. The support value reaches 43.0% and according to the association rules of hot water, we could know that head hot water problem always happen on the residential buildings, because the complaints are from ordinary people, and complaints are all about the residential buildings. And acoording to [HPD] ==> [RESIDENTIAL BUILDING] (Conf: 100.0%, Supp: 57.7%), we could know that the HPD(NYC Housing Preservation and Development) are responsible for the resident hot water. And [ENTIRE BUILDING,HEAT/HOT WATER] ==> [Department of Housing Preservation and Development] (Conf: 99.6%, Supp: 28.5%) means that the complaints about the heat water are always in the entire building not just a one resident problem.
    And [BRONX,RESIDENTIAL BUILDING] ==> [HEAT/HOT WATER] (Conf: 72.2%, Supp: 19.3%), in New York city, the Bronx problem are most severe comparing other districts.
    not Only Brnox, there is same complaint in Brooklyn [BROOKLYN,Department of Housing Preservation and Development] ==> [HEAT/HOT WATER] (Conf: 76.2%, Supp: 18.2%), but we can see that the support value is very low. In this associating rule, we could know that Brooklyn don't have too much prolem in complaints, and maybe the residential buildings are better
    than the Bronx. But the confidence is high, because it is winter, and the hot water problem take most of complaints