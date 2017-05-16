import numpy as np 
import pandas as pd
from scipy.sparse import csr_matrix, hstack, vstack
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import RidgeClassifier
from sklearn.svm import LinearSVC
from collections import Counter
import pickle

def get_formulas(table):
    tfidf = pickle.load(open('./scripts/tfidf.pickle','rb'))
    tfidf_char = pickle.load(open('./scripts/tfidf_char.pickle','rb'))
    kmeans = pickle.load(open('./scripts/kmeans.pickle','rb'))
    forest = pickle.load(open('./scripts/forest.pickle','rb'))
    ridge = pickle.load(open('./scripts/ridge.pickle','rb'))
    logit = pickle.load(open('./scripts/logit.pickle','rb'))
    svc = pickle.load(open('./scripts/svc.pickle','rb'))

    headers = table.pop(0)
    data = pd.DataFrame(table,columns=headers)

    tfidf_text = tfidf.transform(data['Text'])
    tfidf_char_text = tfidf_char.transform(data['Text'])
    X_data = data.drop(['Text','Text_id'],axis=1)
    data_sparse = csr_matrix(X_data)
    data_tfidf = hstack((tfidf_text,tfidf_char_text,data_sparse))

    clusters = kmeans.predict(data_tfidf)
    true_clusters = [0 if x else 1 for x in clusters]

    cluster_sparse = csr_matrix(clusters.reshape(-1, 1))
    clust_tfidf = hstack((data_tfidf, cluster_sparse))

    f_pred = forest.predict(clust_tfidf)
    l_pred = logit.predict(clust_tfidf)
    svc_pred = svc.predict(clust_tfidf)
    r_pred = ridge.predict(clust_tfidf)

    for i in range(len(f_pred)):
        if data['First'][i] == 0:
            f_pred[i] = 0
            l_pred[i] = 0
            svc_pred[i] = 0
            r_pred[i] = 0

    cv_cum = np.array([int(round((f_pred[i]*0.2 + r_pred[i]*0.2 +
                         true_clusters[i]*0.2 + svc_pred[i]*0.2 +
                         l_pred[i]*0.2))) for i in range(len(f_pred))])
    
    all_formulas = data[cv_cum == 1]['Text']
    unique_formulas = Counter(all_formulas).most_common()
    
    st1 = ('всего уникальных формул: '+str(len(unique_formulas)),'')
    st2 = (str(round((len(unique_formulas) / len(all_formulas)) * 100,1))+'% всех формул','')
    unique_formulas = [st1,st2] + list(unique_formulas)
    
    final = pd.concat((data[['Text_id','Text']].reset_index(drop=True),
                       pd.DataFrame(cv_cum),
                       pd.DataFrame([x[0] for x in unique_formulas]),
                       pd.DataFrame([x[1] for x in unique_formulas])), axis = 1)

    return final.values.tolist()
    
