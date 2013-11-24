import nltk
import requests
import math
import urllib2

from apiclient.discovery import build



FILE_NAME='review_bad.txt'
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
    if 'g' in locals():
        excellent_GOOGLE=g.count("excellent")
        poor_GOOGLE=g.count("poor")
    
    avg_pmi_BING=0
    avg_pmi_GOOGLE=0
    count=0
    
    for phrase in text:
        for a in t.evaluate_phrase(tokenizer(phrase.encode('ascii', 'ignore'))):
            print a
            term1_term2_e = request_bing(a+" excellent")
            term1_term2_p = request_bing(a+" poor")

            print "---BING"
            
            print 'hits excellent : '+str(excellent_BING)
            print 'hits poor : '+str(poor_BING)
            print 'hits + excellent :'+str(term1_term2_e)
            print 'hits + poor :'+str(term1_term2_p)
            
            if 'accum_ex_bing' not in locals():
                accum_ex_bing=excellent_BING
            else:
                accum_ex_bing=accum_ex_bing*excellent_BING
            if 'accum_po_bing' not in locals():
                accum_po_bing=poor_BING
            else:
                accum_po_bing=accum_po_bing*poor_BING
            if 'accum_tex_bing' not in locals():
                accum_tex_bing=term1_term2_e
            else:
                accum_tex_bing=accum_tex_bing*term1_term2_e
            if 'accum_tpo_bing' not in locals():
                accum_tpo_bing=term1_term2_p
            else:
                accum_tpo_bing=accum_tpo_bing*term1_term2_p
            

            count = count +1

            
            print ''
            
            if 'g' in locals():
                term1_term2_e = g.count(a+" excellent")
                term1_term2_p = g.count(a+" poor")


                print "---GOOGLE"
                
                print 'hits excellent : '+str(excellent_GOOGLE)
                print 'hits poor : '+str(poor_GOOGLE)
                print 'hits + excellent :'+str(term1_term2_e)
                print 'hits + poor :'+str(term1_term2_p)
                
                if 'accum_ex_google' not in locals():
                    accum_ex_google=excellent_GOOGLE
                else:
                    accum_ex_google=accum_ex_google*excellent_GOOGLE
                if 'accum_po_google' not in locals():
                    accum_po_google=poor_GOOGLE
                else:
                    accum_po_google=accum_po_google*poor_GOOGLE
                if 'accum_tex_google' not in locals():
                    accum_tex_google=term1_term2_e
                else:
                    accum_tex_google=accum_tex_google*term1_term2_e
                if 'accum_tpo_google' not in locals():
                    accum_tpo_google=term1_term2_p
                else:
                    accum_tpo_google=accum_tpo_google*term1_term2_p
                
                print ''
    
    
            
    print 'BING       sentence text : '+str(math.log((accum_tex_bing*accum_po_bing)/(accum_ex_bing*accum_tpo_bing),2))
    if 'g' in locals():
        print 'GOOGLE     sentence text : '+str(math.log((accum_tex_google*accum_po_google)/(accum_ex_google*accum_tpo_google),2))
            

if __name__ == '__main__':
    main()