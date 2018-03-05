import numpy as np 
import pandas as pd
from scipy.sparse import csr_matrix, hstack, vstack
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import RidgeClassifier
from sklearn.svm import LinearSVC
from collections import Counter
import pickle

def get_formulas(table):
    count = pickle.load(open('./scripts/count.pickle','rb'))
    count_char = pickle.load(open('./scripts/count_char.pickle','rb'))
    forest = pickle.load(open('./scripts/forest.pickle','rb'))
    ridge = pickle.load(open('./scripts/ridge.pickle','rb'))
    logit = pickle.load(open('./scripts/logit.pickle','rb'))
    svc = pickle.load(open('./scripts/svc.pickle','rb'))

    headers = table.pop(0)
    data = pd.DataFrame(table,columns=headers)

    count_text = count.transform(data['Text'])
    count_char_text = count_char.transform(data['Text'])
    X_data = data.drop(['Text','Text_id'],axis=1)
    data_sparse = csr_matrix(X_data)
    data_count = hstack((count_text,count_char_text,data_sparse))

    f_pred = forest.predict(data_count)
    l_pred = logit.predict(data_count)
    svc_pred = svc.predict(data_count)
    r_pred = ridge.predict(data_count)

    for i in range(len(f_pred)):
        if data['First'][i] == 0:
            f_pred[i] = 0
            l_pred[i] = 0
            svc_pred[i] = 0
            r_pred[i] = 0

    cv_cum = np.array([int(round((f_pred[i]*0.25 + r_pred[i]*0.25 + svc_pred[i]*0.25 +
                         l_pred[i]*0.25))) for i in range(len(f_pred))])
    
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
    
