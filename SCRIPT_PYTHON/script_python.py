# IMPORTS 
import pandas as pd
import numpy as np
import nltk
import boto3
import boto3.session

from nltk.corpus import stopwords #using ntlk stopwords and not gensim because SW list is easier to configure. 
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.tokenize.treebank import TreebankWordDetokenizer
from sklearn.model_selection import train_test_split
from collections import Counter


#from sklearn.naive_bayes import GaussianNB
#from sklearn.linear_model import SGDClassifier
from sklearn.linear_model import LogisticRegression
#from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report
from sklearn.metrics.pairwise import cosine_similarity


nltk.download('stopwords')
nltk.download('punkt')

pd.set_option("display.max_colwidth", -1)
stopwords_list = stopwords.words('english') #CREATING A LIST FOR STOPWORDS AVOID OPENING LIBRARY EVERYTIME AND WINS A LOT OF TIME
stopwords_list.append('also') #ALSO was missing in stopwords
vectorizer = TfidfVectorizer()
#naive = GaussianNB()#not used anymore
#svm = SGDClassifier(loss= "hinge", max_iter = 10000)#not used anymore
log_reg = LogisticRegression(random_state=0, C=5, penalty='l2',max_iter=2000)


# READING INPUTS FROM S3

print("Pour accéder aux données sur le bucket S3, vous devez renseigner votre id utilisateur aws, votre clé secrète et votre token d'accès sécurisé. \n")
id_key = input("clé d'utilisateur aws: ")
secret_key = input("clé secrète aws: ")
token = input("token aws: ")

session = boto3.session.Session(
    region_name='us-east-1',
    aws_access_key_id=id_key,
    aws_secret_access_key=secret_key,
    aws_session_token=token
    )
s3 = session.resource('s3')
bucket = s3.Bucket('rrt-data-storage-1')


print("\n=== File reading... \n")

s3.Object(bucket.name, 'categories_string').download_file('categories_string')
s3.Object(bucket.name, 'label').download_file('label')
s3.Object(bucket.name, 'data').download_file('data')

df = pd.read_json(r'data')
jobs = pd.read_csv('categories_string')
link_matrix = pd.read_csv('label')


df_split = pd.DataFrame(df.loc[df['Id'] < 5000]) #fetching only x first rows by Id. 
link_matrix = pd.DataFrame(pd.merge(link_matrix, jobs, how='left', left_on="Category", right_on='1'))
linked_data = pd.DataFrame(pd.merge(df_split, link_matrix, how ='left', on='Id'))

df_split = pd.DataFrame({"id" : linked_data["Id"],
                         "job_id" : linked_data["Category"],
                         "job_name" : linked_data["0"],
                         "description" : linked_data["description"]
                         })
#TEXT PROCESSING
print("=== Reading done. Text processing in progress... \n")

df_split['description'] = df_split['description'].apply(word_tokenize) #TOKENIZING SENTENCE 
df_split['description'] = df_split['description'].apply(lambda x: [word.lower() for word in x if word.isalpha()]) #REMOVING PUNCTUATION AND NUMBERS
df_split['description'] = df_split['description'].apply(lambda x: [word for word in x if not word in stopwords_list]) # REMOVING STOPWORS + LOWER CASING
df_split['for_vectorize'] = df_split['description'].apply(TreebankWordDetokenizer().detokenize)# DETOKENIZE FOR VECTORIZER

print("=== Text processed. Preparing samples... \n")
train_X,test_X,train_Y,test_Y = train_test_split(df_split['for_vectorize'], df_split['job_name'], test_size = 0.2) #SAMPLING

test_X_save = test_X #SAVE BEFORE VECTORIZE TO USE IT IN EXIT FILE
vectorizer.fit(train_X)
train_X = vectorizer.transform(train_X) #VECTORIZING THE SAMPLES
test_X = vectorizer.transform(test_X)


print("Train Y : \n", train_Y.describe(), "\n") #WRITING INFORMATION ABOUT OUR SAMPLES BEFORE FITTING THE MODEL
print("Test Y : \n", test_Y.describe(), "\n\n")


print("=== Samples are ready. Training data, may take a while... \n")
log_reg.fit(train_X, train_Y) #FIT THE MODEL IS WHAT TAKES MORE TIME
print("=== Model trained. Prediction on the way... \n")
logreg_prediction = log_reg.predict(test_X) #DOING PREDICATION BASED ON FITTING

#print("Logistic Regression accuracy score : ", accuracy_score(logreg_prediction, test_Y))


print("=== Prediction done. Now calculating the cosine similarity... \n")
cosine_dict = {'pastor' : [],'model' : [],'yoga_teacher' : [],'teacher' : [],'personal_trainer' : [],'painter' : [],'journalist' : [],'interior_designer' : [],'surgeon' : [],'accountant' : [],'dj' : [],'physician' : [],'comedian' : [],'software_engineer' : [],'nurse' : [],'poet' : [],'dentist' : [],'chiropractor' : [],'filmmaker' : [],'professor' : [],'photographer' : [],'rapper' : [],'psychologist' : [],'paralegal' : [],'architect' : [],'composer' : [],'attorney' : [],'dietitian' : []}# CREATING THE DICTIONARY

for key in cosine_dict:#POUR CHAQUE METIER 
    words_list = []
    for desc in df_split[df_split['job_name'] == key]['description']: #POUR CHAQUE CV DANS LA LISTE DU METIER
        words_list.append(desc) #ADD THE DESCRIPTION 
    flatten_list = [item for sublist in words_list for item in sublist] #LIST OF LISTS BECOMES A 1 DIMENSION LIST FOR EACH JOB
    countered = Counter(flatten_list) #INITIATING THE COUNTER
    occuring_most = countered.most_common(25)#FETCHING THE 25 MOST COMMONLY USED WORD IN THIS LIST
    occuring_most_words = [tuple_a[0] for tuple_a in occuring_most]#KEEPING ONLY WORD AND NOT NUMBER
    occuring_most_words = TreebankWordDetokenizer().detokenize(occuring_most_words)#DETOKENIZE SO WE CAN VECTORIZE FOR COSINE
    cosine_dict[key].append(occuring_most_words)#add list of more used words
    

words_df = pd.DataFrame(columns = ["job_name", "top1", "top1n", "top2", "top2n", "top3", "top3n", "top4", "top4n", "top5", "top5n"])
 
for key in cosine_dict:#POUR CHAQUE METIER 
    words_list = []
    for desc in df_split[df_split['job_name'] == key]['description']: #POUR CHAQUE CV DANS LA LISTE DU METIER
        words_list.append(desc) #ADD THE DESCRIPTION 
    flatten_list = [item for sublist in words_list for item in sublist] #LIST OF LISTS BECOMES A 1 DIMENSION LIST FOR EACH JOB
    countered = Counter(flatten_list) #INITIATING THE COUNTER
    occuring_most = countered.most_common(5)#FETCHING THE 25 MOST COMMONLY USED WORD IN THIS LIST
    occuring_most_words = [tuple_a[0] for tuple_a in occuring_most]
    occuring_most_numbers = [tuple_a[1] for tuple_a in occuring_most]
    new_occuring_list = [key]
    for k in range(0,5): # CREATING A LIST OR BOTH TO PUT THEM IN A DATAFRAME
        new_occuring_list.append(occuring_most_words[k])
        new_occuring_list.append(occuring_most_numbers[k])
    words_df.loc[len(words_df)] = new_occuring_list #LIST OF WORDS IN A DATAFRAME

#print(words_df)

cosine_list = []
for cv in test_X: #CALCULATING ALL COSINE SIMILARITIES
    job_to_keep = ''
    result = 0
    for key in cosine_dict:
        cosine = cosine_similarity(cv, vectorizer.transform(cosine_dict[key]))
        if cosine >= result:
            job_to_keep = key
            result = cosine
    cosine_list.append(job_to_keep) #Appening to list of cosines that will be used in predictions list
 

#df_newdata = read_csv('new_cv.csv')
#df_newdata['prediction'] = log_reg.predict(df_newdata['cv'])    
#.to_csv('botte.csv')       


#OUTPUTS FOR DATA VISUALISATION
learning_df = pd.DataFrame({
    "resume" : test_X_save,
    "expected" : test_Y,
    "prediction" : logreg_prediction,
    "cosine_similarity" : cosine_list
    })

print("Cosine calculated. Now printing into .CSV files...")

report = classification_report(test_Y, logreg_prediction, output_dict=True)
report_df = pd.DataFrame(report).transpose()
report_df['job_name'] = report_df.index

learning_df.to_csv('predictions.csv')
report_df.to_csv('classification_report.csv')
words_df.to_csv('words.csv')

print("=== Sending files to S3....")
s3.Object(bucket.name, 'predictions').upload_file('predictions.csv')
s3.Object(bucket.name, 'classification_report').upload_file('classification_report.csv')
s3.Object(bucket.name, 'words').upload_file('words.csv')

print("All complete")
