import nltk
import requests
import math
import urllib2

from apiclient.discovery import build



FILE_NAME='review.txt'
API_KEY_BING=''
API_KEY_GOOGLE=''
USE_GOOGLE = False 

"""
Class that implements the search through Google Custom Search (100 Query/day free)
"""

class GoogleApi:
    def __init__(self):
        self.service = build("customsearch", "v1", developerKey=API_KEY_GOOGLE)


    def count(self,query):
        res = self.service.cse().list(
      q=query,
      cx='017576662512468239146:omuauf_lfve',
        ).execute()
        if 'nextPage' in  res['queries']:
            return float(res['queries']['nextPage'][0]['totalResults'])
        else:
            return float(res['queries']['request'][0]['totalResults'])

"""
Class that implements the matcher through token triples
"""        

class TokenMatcher:
    def __init__(self):
        self.pattern_anything = [['JJ','NN'],['JJ','NNS'],
                        ['RB','VD'],['RB','VBD'],['RB','VBN'],['RB','VBG'],
                        ['RBR','VD'],['RBR','VBD'],['RBR','VBN'],['RBR','VBG'],
                        ['RBS','VD'],['RBS','VBD'],['RBS','VBN'],['RBS','VBG']]
        self.pattern_no_NN_or_NNS= [['RB','JJ'],['RBR','JJ'],['RBS','JJ'],['JJ','JJ'],
                                    ['NN','JJ'],['NNS','JJ']]
    """
    Methon that match triple pattern
    input = sentence
    output = couples of words that have a match
    """  
    
    def evaluate_phrase(self, sentences):
        for index in range(len(sentences)-2):
            if self.matcher(sentences[index:index+3]):
                yield (sentences[index]['word']+" "+sentences[index+1]['word'])
        
    
    
    def matcher(self, triple):
        match = False
        for test in self.pattern_anything:
            if triple[0]['pos'] == test[0] and triple[1]['pos'] == test[1]:
                match= True
        for test in self.pattern_no_NN_or_NNS:
            if not match and triple[0]['pos'] == test[0] and triple[1]['pos'] == test[1] and triple[2] <> 'NN' and triple[2] <> 'NNS':
                match= True
        return match

"""
Method that implements the search through Bing
"""

def request_bing(query, **params):
    URL_BING = 'https://api.datamarket.azure.com/Bing/Search/v1/Composite?Sources=%(source)s&Query=%(query)s&$top=50&$format=json'
    url = URL_BING % {'source': urllib2.quote("'web'"),
                 'query': urllib2.quote("'"+query+"'")}
    r = requests.get(url, auth=('', API_KEY_BING))
    return float(r.json()['d']['results'][0]['WebTotal'])




# return true if a word ia a stopword
def is_stopword(string):
    if string.lower() in nltk.corpus.stopwords.words('english'):
        return True
    else:
        return False

# return true if a string is punctation    
def is_punctuation(string):
    for char in string:
        if char.isalpha() or char.isdigit():
            return False
    return True




#Tokenization

def tokenizer(tweet):    
    sents = nltk.sent_tokenize(tweet)
    sentence = []
    for sent in sents:
        
        tokens = nltk.word_tokenize(sent)
        tag_tuples = nltk.pos_tag(tokens)
        for (string, tag) in tag_tuples:
            if not is_punctuation(string):
                token = {'word':string, 'pos':tag}            
                sentence.append(token)    
    return sentence

"""
input -> plain text
output -> list of phrases
"""    

def list_phrases(textImput):
    sent_tokenizer=nltk.data.load('tokenizers/punkt/english.pickle')
    text = open(textImput).read()
    sents = sent_tokenizer.tokenize(text)
    return sents
    


def main():
    t = TokenMatcher()
    if USE_GOOGLE:
        g = GoogleApi()
    text = list_phrases(FILE_NAME)
    
    excellent_BING=request_bing("excellent")
    poor_BING=request_bing("poor")
    if g is not None:
        excellent_GOOGLE=g.count("excellent")
        poor_GOOGLE=g.count("poor")
    
    avg_pmi_BING=0
    avg_pmi_GOOGLE=0
    count=0
    
    for phrase in text:
        for a in t.evaluate_phrase(tokenizer(phrase.encode('ascii', 'ignore'))):
            print a
            term1_term2_e = request_bing(a+" excellent")
            term2= request_bing(a)
            term1_term2_p = request_bing(a+" poor")
#             pmi_excelent =math.log( float(pygoogle(a+" excellent").get_result_count()) / float(pygoogle("excellent").get_result_count()) * float(pygoogle(a).get_result_count()),2)
            
            print "---BING"
            
            print 'excellent : '+str(excellent_BING)
            print 'poor : '+str(poor_BING)
            print 'only phrase : '+str(term2)
            print ' + excellent :'+str(term1_term2_e)
            print ' + poor :'+str(term1_term2_p)
            
            pmi_excelent =math.log( (term1_term2_e / (excellent_BING * term2)) ,2)
            pmi_poor =math.log( (term1_term2_p / (poor_BING * term2)) ,2)
            
            print 'pmi excellent : '+str(pmi_excelent)
            print 'pmi poor : '+str(pmi_poor)
            
            pmi_sentence_BING = pmi_excelent - pmi_poor
            
            avg_pmi_BING = avg_pmi_BING + pmi_sentence_BING
            
            count = count +1
            
            print 'pmi sentence : '+str(pmi_sentence_BING)
            
            print ''
            
            if g is not None:
                term1_term2_e = g.count(a+" excellent")
                term2= g.count(a)
                term1_term2_p = g.count(a+" poor")
                print "---GOOGLE"
            
                print 'excellent : '+str(excellent_GOOGLE)
                print 'poor : '+str(poor_GOOGLE)
                print 'only phrase : '+str(term2)
                print ' + excellent :'+str(term1_term2_e)
                print ' + poor :'+str(term1_term2_p)
            
                pmi_excelent =math.log( (term1_term2_e / (excellent_GOOGLE * term2)) ,2)
                pmi_poor =math.log( (term1_term2_p / (poor_GOOGLE * term2)) ,2)
            
                print 'pmi excellent : '+str(pmi_excelent)
                print 'pmi poor : '+str(pmi_poor)
            
                pmi_sentence_GOOGLE = pmi_excelent - pmi_poor
            
                avg_pmi_GOOGLE = avg_pmi_GOOGLE + pmi_sentence_GOOGLE
            
            
                print 'pmi sentence : '+str(pmi_sentence_GOOGLE)
            
                print ''
            
    print 'BING       sentence text : '+str(avg_pmi_BING / count)
    print 'GOOGLE     sentence text : '+str(avg_pmi_GOOGLE / count)
            

if __name__ == '__main__':
    main()