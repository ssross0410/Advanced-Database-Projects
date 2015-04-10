Columbia University
COMS E6111 	Advanced Database Systems
Project 1 	Information retrieval system based on user-provided relevance feedback


a)
	Su Shen (ss4716)
	Sihan Wang (sw2921)


b)
	queryExpansion.py        	// The python file to execute the query expansion.
	README.md      				// README
	transcript					// The transcript of running three queries: musk, gates, columbia


c)
	Enter into the directory where the queryExpansion.py file is located. 
	Run:
	python queryExpansion.py <bing account key> <desired precision> <query>

	e.g.,
	python queryExpansion.py dxDIzFPjU6qIN0CCfZ46isw7N117bXj4YrQrZP5DOSY 0.9 jaguar


d) A clear description of the internal design of your project

	The program will first receive input (a user query which is typically a word being relevant to target
	) and a expected precision that is out of all documents returned by Bing. At first, we need to set account 
	key which is provided by Bing API, and then set the format that we want to receive(In this project, we 
	choose to use Json format instead of XML).Then after the search through Bing API, exactly top 10 of the 
	search results will be displayed to the user one by one, and user will choose whether each document 
	is relevant or not by typing 'Y' and 'N'.Based on the user feedback, the program will utilize 
	Rocchio's algorithm by analyzing 'Title' and 'Summary' to obtain the top two words related. The detailed 
	implementation of Rocchio's algorithm is introduced in the e) part. After that the query will expanded by 
	these top two words and run the Bing search again. The program will continuously run in this manner until 
	the desired precision@10 is achieved.

	And also, there could be possible condition that results from bing does not have any relevant 
	docment according to user decision, in this case, we will stop the program immediately

e) description of query-modification method 

	1) Clear content
		the program will firstly delete all the puctuations and delete all stop words such as
		"a", "the" etc. In this homework, we assume that these stopwords would not be in the target 
		words.

	2) Set weight for every words using tf-idf
		At the every iteration, we will count terms appearance whatever they are in 
		relevant docment or irrelevant document. And we also need to record the number of 
		times occured in all documents, if one word appears many times in one docment, we 
		still record 1. In this way, we could avoid some common words that are irrelevant 
		with the topic but with high weight. And at last, we use tf-idf equation to indicate 
		the weight for every term: w = tf*log(N/# of times appear in different documents)

	3) Run Rocchio algorithm (after large number words testing, we set alpha = 1, beta = 0.5, gamma
	   = 0.5)
		The equation is q = alpha*q0 + beta/|Dr|*Sum(vector dj) - gamma/|Dnr|*Sum(vector dj)
		So q0 is our old vector space, which consists of old words by '1' or '0', and mutiply
		the weight of term that we get from the 1). And in this case, we could get the new query
		vector. And it consists of all the words excluding stopwords

		The value of parameters are achieved by large number of words testing 

	4) 
		After run Rocchio algorithm, we choose two 2 words which has highest socre in the new query 
		vector that is provided in 3) (choose except words that have been in the query)

	5) 
		Create the new query with two new words, and the order of the two words are decided by the score of 
		these two words

f) Account key: MzbAA3AoGQiKgyVaXPccIVlaex1pMadm+Rr4kxe0TPo

