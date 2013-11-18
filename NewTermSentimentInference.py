import csv
import sys

twitterData = sys.argv[1] # csv file

def tweet_dict(twitterData):  
    ''' (file) -> list of dictionaries
    This method should take your csv file
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
        term, score  = line.split("\t")  # The file is tab-delimited. "\t" means "tab character"
        scores[term] = float(score)  # Convert the score to an integer.   
    return scores # Print every (term, score) pair in the dictionary


def main():

    tweets = tweet_dict(twitterData)
    sentiment = sentiment_dict("AFINN-111.txt")
    accum_term = dict()
    
    """Calculating sentiment scores for the whole tweet with unknown terms set to score of zero
    See -> DeriveTweetSentimentEasy
    """

    for index in range(len(tweets)):
        
        tweet_word = tweets[index].split()
        sent_score = 0 # sentiment of the sentence
        term_count = {}
        term_list = []
        
        for word in tweet_word:
            word = word.rstrip('?:!.,;"!@')
            word = word.replace("\n", "")
            if not (word.encode('utf-8', 'ignore') == ""):
                if word.encode('utf-8') in sentiment.keys():
                    sent_score = sent_score + float(sentiment[word])    
                else:
                    sent_score = sent_score
                    accum_term[word] = []
                    term_list.append(word) #inverted index
                    if word.encode('utf-8') in term_count.keys():
                        term_count[word] = term_count[word] + 1
                    else:
                        term_count[word] = 1

        for word in term_list:
            accum_term[word].append(sent_score) # for each new word assign to this word the sentiment of the tweet

    """Derive the sentiment of new terms
    """

    for key in accum_term.keys():
        adjusted_score = 0
        term_value = 0
        total_sum = 0
        for score in accum_term[key]:
            total_sum = total_sum + score
        
        """if a word is present in more tweet -> to the word is assigned the average of the sentiment of the tweets that contain it 
        """
                    
        term_value = (total_sum)/len(accum_term[key]) 
        
        adjusted_score = "%.3f" %term_value
        print key.encode('utf-8') + " " + adjusted_score



if __name__ == '__main__':
    main()
