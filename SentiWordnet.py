import sys
import csv
import nltk
from nltk.corpus import wordnet
import re
import codecs

twitterData = sys.argv[1] # tweet input file (.csv)



class SentiWordNetCorpusReader:
    def __init__(self, filename):
        """
        Argument:
        filename -- the name of the text file containing the
                    SentiWordNet database
        """        
        self.filename = filename
        self.db = {}
        self.parse_src_file()

    def parse_src_file(self):
        lines = codecs.open(self.filename, "r", "utf8").read().splitlines()
        lines = filter((lambda x : not re.search(r"^\s*#", x)), lines)
        for i, line in enumerate(lines):
            fields = re.split(r"\t+", line)
            fields = map(unicode.strip, fields)
            try:            
                pos, offset, pos_score, neg_score, synset_terms, gloss = fields
            except:
                sys.stderr.write("Line %s formatted incorrectly: %s\n" % (i, line))
            if pos and offset:
                offset = int(offset)
                self.db[(pos, offset)] = (float(pos_score), float(neg_score))

    def senti_synset(self, *vals):        
        if tuple(vals) in self.db:
            pos_score, neg_score = self.db[tuple(vals)]
            pos, offset = vals
            synset = wordnet._synset_from_pos_and_offset(pos, offset)
            return SentiSynset(pos_score, neg_score, synset)
        else:
            synset = wordnet.synset(vals[0])
            pos = synset.pos
            offset = synset.offset
            if (pos, offset) in self.db:
                pos_score, neg_score = self.db[(pos, offset)]
                return SentiSynset(pos_score, neg_score, synset)
            else:
                return None

    def senti_synsets(self, string, pos=None):
        sentis = []
        synset_list = wordnet.synsets(string, pos)
        for synset in synset_list:
            sentis.append(self.senti_synset(synset.name))
        sentis = filter(lambda x : x, sentis)
        return sentis

    def all_senti_synsets(self):
        for key, fields in self.db.iteritems():
            pos, offset = key
            pos_score, neg_score = fields
            synset = wordnet._synset_from_pos_and_offset(pos, offset)
            yield SentiSynset(pos_score, neg_score, synset)

######################################################################
            
class SentiSynset:
    def __init__(self, pos_score, neg_score, synset):
        self.pos_score = pos_score
        self.neg_score = neg_score
        self.obj_score = 1.0 - (self.pos_score + self.neg_score)
        self.synset = synset

    def __str__(self):
        """Prints just the Pos/Neg scores for now."""
        s = ""
        s += self.synset.name + "\t"
        s += "PosScore: %s\t" % self.pos_score
        s += "NegScore: %s" % self.neg_score
        return s

    def __repr__(self):
        return "Senti" + repr(self.synset)


def tweet_dict(twitterData):  
    ''' (file) -> list of dictionaries
    This method should take your output.txt
    file and create a list of dictionaries.
    '''
    twitter_list_dict = []    
    twitterfile = open(twitterData)
    twitterreader = csv.reader(twitterfile)
    for line in twitterreader:
        twitter_list_dict.append(line[0])
    return twitter_list_dict


def sentiment_dict(sentimentData):
    ''' (file) -> dictionary
    This method should take your sentiment file
    and create a dictionary in the form {word: value}
    '''
    afinnfile = open(sentimentData)
    scores = {} # initialize an empty dictionary
    for line in afinnfile:
        pos, id, posScore, negScore,synsetTerms, gloss  = line.split("\t")  # The file is tab-delimited. "\t" means "tab character"
        try:
            score=0
            if float(negScore) <> 0:
                score = float(posScore)
            else:
                score = -float(posScore) 
            scores[pos+synsetTerms] = score  # Convert the score to an integer.
        except:
            pass
    return scores # Print every (term, score) pair in the dictionary

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

# 
def wordnet_pos_code(tag):
    if tag.startswith('NN'):
        return wordnet.NOUN
    elif tag.startswith('VB'):
        return wordnet.VERB
    elif tag.startswith('JJ'):
        return wordnet.ADJ
    elif tag.startswith('RB'):
        return wordnet.ADV
    else:
        return ''

def wordnet_pos_label(tag):
    if tag.startswith('NN'):
        return "Noun"
    elif tag.startswith('VB'):
        return "Verb"
    elif tag.startswith('JJ'):
        return "Adjective"
    elif tag.startswith('RB'):
        return "Adverb"
    else:
        return tag

def wordnet_definitions(sentence):
    wnl = nltk.WordNetLemmatizer()
    for token in sentence:
        word = token['word']
        wn_pos = wordnet_pos_code(token['pos'])
        if is_punctuation(word):
            token['punct'] = True
        elif is_stopword(word):
            pass
        elif len(wordnet.synsets(word, wn_pos)) > 0:
            token['wn_lemma'] = wnl.lemmatize(word.lower())
            token['wn_pos'] = wordnet_pos_label(token['pos'])
            defs = [sense.definition for sense in wordnet.synsets(word, wn_pos)]
            token['wn_def'] = "; \n".join(defs) 
        else:
            pass
    return sentence


def tag_tweet(tweet):    
    sents = nltk.sent_tokenize(tweet)
    sentence = []
    for sent in sents:
        tokens = nltk.word_tokenize(sent)
        tag_tuples = nltk.pos_tag(tokens)
        for (string, tag) in tag_tuples:
            token = {'word':string, 'pos':tag}            
            sentence.append(token)    
    return sentence


def word_sense_disambiguate(word, wn_pos, sentence):
    senses = wordnet.synsets(word, wn_pos)
    if len(senses) >0:
        cfd = nltk.ConditionalFreqDist(
               (sense, def_word)
               for sense in senses
               for def_word in sense.definition.split()
               if def_word in sentence)
        best_sense = senses[0] # start with first sense
        for sense in senses:
            try:
                if cfd[sense].max() > cfd[best_sense].max():
                    best_sense = sense
            except: 
                pass                
        return best_sense
    else:
        return None
    

def main():
    tweets = tweet_dict(twitterData)
    sentiment = SentiWordNetCorpusReader("SentiWordNet_3.0.0_20130122.txt")
    for index in range(len(tweets)):
        a = wordnet_definitions(tag_tweet(tweets[index]))
        obj_score = 0 # object score 
        pos_score=0 # positive score
        neg_score=0 #negative score
        count = 0
        for word in a:
            if 'punct' not in word :
                sense = word_sense_disambiguate(word['word'], wordnet_pos_code(word['pos']), tweets[index])
                if sense is not None:
                    sent = sentiment.senti_synset(sense.name)
                    if sent is not None:
                        obj_score = obj_score + float(sent.obj_score)
                        pos_score = pos_score + float(sent.pos_score)
                        neg_score = neg_score + float(sent.neg_score)
                        count=count+1
        print tweets[index]
        avg_obj_score=0
        avg_pos_score=0
        avg_neg_score=0
        if count <> 0:
            avg_obj_score=obj_score/count
            avg_pos_score=pos_score/count
            avg_neg_score=neg_score/count
#         etichetta=""
#         if sent_score <= 0.25:
#             etichetta = "molto negativo"
#         elif sent_score <= 0.40 and sent_score > 0.25:
#             etichetta ="negativo"
#         elif sent_score <= 0.60 and sent_score > 0.40:
#             etichetta ="neutro"
#         elif sent_score <= 0.75 and sent_score > 0.60:
#             etichetta ="positivo"
#         elif sent_score > 0.75:
#             etichetta ="molto positivo"
        print "pos_total : "+str(pos_score)+" - neg_ total: "+str(neg_score)+" - count : "+str(count)+" -> "+(" positivo " if pos_score > neg_score else ("negativo" if pos_score < neg_score else "neutro"))
        print "obj :"+str(avg_obj_score) + " || (CE) pos : "+str(avg_pos_score)+" - (CE) neg : "+str(avg_neg_score)+" -> "+(" positivo " if avg_pos_score > avg_neg_score else ("negativo" if avg_pos_score < avg_neg_score else "neutro"))
#         print "CE score -> pos : "+str(pos_ce)+ " - neg : "+str(neg_ce)+" - pos_score : "+str(score_pos_ce)+" - neg_score : "+str(score_neg_ce) 
        print ""


if __name__ == '__main__':
    main()