#Project of Sentiment Analysis for the course of Big Data Analysis of the Department of Computer Engineering of Modena and Reggio Emilia.#


##Library used in the project##




- **Tweepy** - [https://github.com/tweepy/tweepy ](https://github.com/tweepy/tweepy  "Tweepy")



- **Natural Language Toolkit** - [http://nltk.org/install.html](http://nltk.org/install.html "NLTK")

To install additional modules and datasource (Wordnet and other modules are required) launch the following command on a python shell:

    import nltk
	nltk.download()

Download the followings modules:

- Stopword
- Wordnet
- Wordnet_ic
- All the modules in models

##Project usage##

###Tweet###

The script named `ExtractTweet.py` can be used to download tweets in a `csv` file. This script is configurable by this file: `config.json`

The configurable fields are:

- consumer_key
- consumer_secret
- access_token
- access_token\_secret

These fields can be retrieved from  [https://dev.twitter.com](https://dev.twitter.com) after creating an account and an application

- file_name (name of the `cvs` output file)
- count (number of tweet to download)
- filter (a word used to filter the tweet in output)

The CSV file produced in output can be used as arg of the other three script:

- `DeriveTweetSentimentEasy.py`: This script uses AFINN-111.txt as vocabulary to try to assign a sentiment score to a tweet.
- `NewTermSentimentInference.py`: This script try to assign a sentiment score to the words that are not present in AFINN-111.txt based on the sentiment score of a group of tweets.
- `SentiWordnet.py`: This script uses SentiWordNet as vocabulary to try to assign a sentiment score to a tweet. The metrics of the scoring and the annotation process are more complex in this script.

###Document Sentiment Classification###

The script is called `DocumentSentimentClassification.py` and implements a simple method for document sentiment classification.
it possible to set some configuration parameters in the top of Python script:

- FILE_NAME -> name of the file .txt on which you want execute the classification
- API_KEY_BING -> Api Key Bing [http://it.bing.com/dev/en-us/dev-center](Bing Dev)
- API_KEY_GOOGLE -> Api Key for Custom Search Api [https://cloud.google.com/console](Google Api Console)
- USE_GOOGLE -> Enable (True) or Disable (False) the use of the Google Api for Custom Search ( 100 query for day without have to pay )

### ipython ###

For an interactive example with ipython, go into the folder `BDA_Senti_ipython` and launch the command:

	$ ipython notebook --pylab inline
	
###[Slides](http://www.slideshare.net/faigg/tutotial-of-sentiment-analysis)###



