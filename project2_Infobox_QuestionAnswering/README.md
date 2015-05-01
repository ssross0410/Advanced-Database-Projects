Columbia University
COMS E6111  Advanced Database Systems
Project 2


a) Your name and your partner's name and Columbia UNI

Su Shen (ss4716)
Sihan Wang (sw2921)


b) A list of all the files that you are submitting

pa2.py                      // The python file to execute the query expansion.
README.md                   // README
transcript              // The transcript of running required test cases


c)  A clear description of how to run your program (note that your project must compile/run under Linux in your CS account)

Enter into the directory where the pa2.py file is located. 
Run:

1. python pa2.py -key <freebase API key> -q <query> -t <infobox|question>

2. python pa2.py -key <freebase API key> -f <file of queries> -t <infobox|question>

3. python pa2.py -key <freebase API key> (NOT REQUIRED)


d) A clear description of the internal design of your project

1. INFOBOX:
The program will make query request from Freebase API, and then it will iterate the result and find a valid one to make the infobox. In infobox, the program will using Freebase Types that has been set up at first getting useful information. There are "compound" object, when meeting this object, the program will go into further step to get usefulmation. After that, the program will print the information following the teacher's one.

2. QUESTION:
The program will first check if the query is in a correct format, i.e., "who created <X>?"(question mark is a must here!). Then through the Freebase MQL Read API, it will generate two seperate queries and find the names of the authors and the names of the businessperson who created <X>. After sorting the answer by name, it will extract the needed information from the "answer" dictionary obtained from the freebase MQL API, and output them line by line. Each line will be in the form "<Name> (as <Answer Type>) created <X1> [, <X2>, .... , and <Xn>]."


e) Your Freebase API Key (so we can test your project) as well as the requests per second per user that you have set when you configured your Google project (see Freebase Basics section)

key: AIzaSyDRXrrGJAJDCZr0i3xak_y0oMsOztLmqL4

