from sets import Set
import urllib, urllib2, json
import base64
import sys
import math
import collections
import re


#Provide your account key here
accountKey = ''

stopWords = [	r"\ba\b",	r"\bable\b",    	r"\babout\b",	    r"\bacross\b",	r"\bafter\b",	     r"\ball\b",	r"\balmost\b",
		r"\balso\b",	r"\bam\b",	  	r"\bamong\b", 	    r"\ban\b",		r"\band\b",	     r'\bany\b',	r'\bare\b',
		r'\bas\b',	r'\bat\b',		r'\bbe\b',	    r'\bbecause\b',	r'\bbeen\b',	     r'\bbut\b',	r'\bby\b',
		r'\bcan\b',	r'\bcannot\b',		r'\bcould\b',	    r'\bdear\b',	r'\bdid\b',	     r'\bdo\b',		r'\bdoes\b',
		r'\beither\b',	r'\belse\b',		r'\bever\b',	    r'\bevery\b',	r'\bfor\b',	     r'\bfrom\b',	r'\bget\b',
		r'\bgot\b',	r'\bhad\b',		r'\bhas\b', 	    r'\bhave\b',	r'\bhe\b',	     r'\bher\b',	r'\bhers\b',
		r'\bhim\b',	r'\bhis\b',		r'\bhow\b',	    r'\bhowever\b',	r'\bi\b',  	     r'\bif\b',		r'\bin\b',
		r'\binto\b',	r'\bis\b',		r'\bit\b',	    r'\bits\b',		r'\bjust\b',	     r'\bleast\b',	r'\blet\b',
		r'\blike\b',	r'\blikely\b',		r'\bmay\b',	    r'\bme\b',		r'\bmight\b',	     r'\bmost\b',	r'\bmust\b',
		r'\bmy\b',	r'\bneither\b',		r'\bno\b',	    r'\bnor\b',		r'\bnot\b',	     r'\bof\b',		r'\boff\b',
		r'\boften\b',	r'\bon\b',		r'\bonly\b',	    r'\bor\b',		r'\bother\b',	     r'\bour\b',	r'\bown\b',
		r'\brather\b',	r'\bsaid\b',		r'\bsay\b',	    r'\bsays\b',	r'\bshe\b',	     r'\bshould\b',	r'\bsince\b',
		r'\bso\b',	r'\bsome\b',		r'\bthan\b',	    r'\bthat\b',	r'\bthe\b',	     r'\btheir\b',	r'\bthem\b',
		r'\bthen\b',	r'\bthere\b',		r'\bthese\b',       r'\bthey\b',	r'\bthis\b',	     r'\btis\b',	r'\bto\b',
		r'\btoo\b',	r'\btwas\b',		r'\bus\b',	    r'\bwants\b',	r'\bwas\b', 	     r'\bwe\b',		r'\bwere\b',
		r'\bwhat\b',	r'\bwhen\b',		r'\bwhere\b',	    r'\bwhich\b',	r'\bwhile\b',	     r'\bwho\b',	r'\bwhom\b',
		r'\bwhy\b',	r'\bwill\b',		r'\bwith\b',	    r'\bwould\b',	r'\byet\b',	     r'\byou\b',	r'\byour\b',
		r'\byours\b', 	r'\byourself\b',	r'\byourselves\b']


punctuation = "().,:;!?&-/0123456789\"|"


# parameters for the Rocchio algorithm
alpha = 1
beta = 0.50
gamma = 0.50


# we need to delete puntuations and stop words(these are not typically used as search words)
# input : raw string
# output : clear string
def clear(value):
	value = value.strip().lower()
	# delete the puctuations
	for item in punctuation:
		value = value.replace(item, '')
	# delete stop words
	for item in stopWords:
		value = re.sub(item,'', value)
	return value

# using tf-idf to set weight for each word
# input: weight frequency, relevant document frequency, irrelevant document frequency
# output: weight
def getWeight(tf, rdf, irdf):
	weight = {}
	for item in rdf.keys():	
		weight[item] = tf[item] * math.log((float)(10/(rdf[item] + irdf[item])))
	return weight

#set flag for the old query, and when the word is in the query, we set it as 1, otherwise 0
# input: tf (dict for 10 documents words)
# output: words vector
def createQuery(tf, query):
	q = {}
	for word in tf.keys():
		if word in query:
		    q[word] = 1
		else:
			q[word] = 0
	return q

# run Rocchio algorithm
# input: old word vector, # of relevant document, termweight, # of appearance in relevant document, # of appearance in irrelevant document
# output: new word vector
def runEq(oldQuery, Cr, termWeight, reDocFreq, irreDocFreq):
	q = {}
	for item in oldQuery.keys():
		q[item] = oldQuery[item]*alpha 
		if reDocFreq[item] > 0:
			q[item] += termWeight[item]*beta/Cr
		if irreDocFreq[item] > 0:
			q[item] -= termWeight[item]*gamma/(10-Cr)
	return q

# find the two words need be added to query according to their weight
# input: new word vector, current query
# output: two words (as string)
def findMax(q, query):
	maxOccur = 0
	secondOccur = 0
	r1 = ""
	r2 = ""
	for word in q.keys():
		if q[word] > secondOccur and word not in query:
			if (maxOccur < q[word]):
				secondOccur = maxOccur
				r2 = r1
				maxOccur = q[word]
				r1 = word
			else:
				secondOccur = q[word]
				r2 = word
	print r1, q[r1]
	print r2, q[r2]
	return r1 + " " + r2


def main():
	global accountKey
	global limitWords
	accountKey = sys.argv[1]
	query = sys.argv[3]
	targetPrecision = float(sys.argv[2])
	expandedQuery = query
	iteration = 0
	precision = 0
	while True:
		key = accountKey
		addWords = ""
		# number of the docs contains the relevant terms
		reDocFreq = {}
		# number of the docs contains the irrelevant terms
		irreDocFreq = {}
		# termFrequency
		termFreq = {}


		response, url = bing_search(expandedQuery)
		if iteration >= 1:
			print "====================" + "\n" + "FEEDBACK SUMMARY" + "\n" + "Query " + query
			query = expandedQuery
			print "Precision ", ((float)(precision))/10
			print "Still below the desired precision of ", targetPrecision
			print "Indexing results .... " + "\n" + "Indexing results .... " 
			print "Augmenting by ", addWords
			addWords = ""
			precision = 0
		print "Parameters: " + "\n" + "Client Key = " + key + "\n" "Query = " + expandedQuery + "\n" + "Precision = ", targetPrecision, \
			"\n" + "URL: " + url + "\n" + "Total no of results : 10" + "\n" + "Bing Search Results: " + "\n" + \
			"===================="
		resultNum = 1
		iteration += 1
		
		for result in json.loads(response)['d']['results']:
			print "Result", resultNum, "\n" + "["
			print "URL:", result["Url"]
			print "Title:", result["Title"].encode("utf-8")
			print "Summary:", result["Description"].encode("utf-8"), "\n" + "]" + "\n"
			releResponse = raw_input("Relevant (Y/N)?")

			# the set of words in a single doc result
			localDoc = set()
			if releResponse == 'y' or releResponse == 'Y':
				precision += 1

				for key, value in result.iteritems():
					if key == "Description" or key == "Title":
						value = clear(value)
						wordList = value.split()
						for word in wordList:
							word = word.lower()
							if word in termFreq:
								termFreq[word] += 1
							else:
								termFreq[word] = 1
							localDoc.add(word)

						
				for word in localDoc:
					if word in reDocFreq:
						reDocFreq[word] += 1
					else:
						reDocFreq[word] = 1
					if word not in irreDocFreq:
						irreDocFreq[word] = 0
			else:
				for key, value in result.iteritems():
					if key == "Description" or key == "Title":
						value = clear(value)
						wordList = value.split()
						for word in wordList:
							word = word.lower()
							if word in termFreq:
								termFreq[word] += 1
							else:
								termFreq[word] = 1
							localDoc.add(word)
				#print localDoc
				for word in localDoc:
					if word in irreDocFreq:
						irreDocFreq[word] += 1
					else:
						irreDocFreq[word] = 1
					if word not in reDocFreq:
						reDocFreq[word] = 0
			resultNum += 1
		
		if precision == 0:
			print "Sorry! There is no relevant result. The program is terminated!"
			break
		if resultNum < 10:
			print "Sorry! There are less than 10 results found. The program is terminated!"
			break
		if  ((float)(precision))/10 >= targetPrecision:
			print "====================" + "\n" + "FEEDBACK SUMMARY" + "\n" + "Query " + expandedQuery
			print "Precision", ((float)(precision))/10
			print "Desired precision reached, done"
			break

		Cr = precision
		Cnr = 10 - precision
		termWeight = getWeight(termFreq, reDocFreq, irreDocFreq)
		oldQuery = createQuery(termFreq, query)
		newQuery = runEq(oldQuery, Cr, termWeight, reDocFreq, irreDocFreq)
		addWords = findMax(newQuery, query)
		expandedQuery = expandedQuery + " " + addWords
		print expandedQuery


# do search by bing research
def bing_search(query, **kwargs):
	baseURL = 'https://api.datamarket.azure.com/Bing/Search/'
	query = urllib.quote(query)
	# create credential for authentication
	user_agent = 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; FDM; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 1.1.4322)'
	credentials = (':%s' % accountKey).encode('base64')[:-1]
	auth = 'Basic %s' % credentials
	url = baseURL+'Web?Query=%27'+query+'%27&$top=10&$format=json'
	request = urllib2.Request(url)
	request.add_header('Authorization', auth)
	request.add_header('User-Agent', user_agent)
	request_opener = urllib2.build_opener()
	response = request_opener.open(request)
	response_data = response.read()
	return response_data, url
if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		print "\n"
		exit()
	
