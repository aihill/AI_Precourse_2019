
import pandas as pd
import numpy as np
import xgboost as xgb
from xgboost.sklearn import XGBClassifier
from sklearn import cross_validation, metrics
from sklearn.grid_search import GridSearchCV

import matplotlib.pylab as plt
from matplotlib.pylab import rcParams

def modelfit(alg, dtrain, dtest, predictors,useTrainCV=True, cv_folds=5, early_stopping_rounds=50):
    if useTrainCV:
        xgb_param = alg.get_xgb_params()#��ֵ��С��ʧ�����½�ֵ
        xgtrain = xgb.DMatrix(dtrain[predictors].values, label=dtrain[target].values)
        # ����train��target, IDcol���������е�Ԫ��+Disbursed��ֵ
        # xgtest = xgb.DMatrix(dtest[predictors].values)
        # ����test��target, IDcol���������е�Ԫ��
        cvresult = xgb.cv(xgb_param, xgtrain, 
                          num_boost_round=alg.get_params()['n_estimators'],
                          nfold=cv_folds,metrics='auc', 
                          early_stopping_rounds=early_stopping_rounds)
        # ,show_progress=False
        # ��ÿһ�ε�����ʹ�ý�����֤������������ľ���������.�Ƿ���ʾĿǰ��������
        
        alg.set_params(n_estimators=cvresult.shape[0])
    
    #Fit the algorithm on the data ���㷨����������
    alg.fit(dtrain[predictors], dtrain['Disbursed'],eval_metric='auc')
        
    #Predict training set:  Ԥ��ѵ������
    dtrain_predictions = alg.predict(dtrain[predictors])
    dtrain_predprob = alg.predict_proba(dtrain[predictors])[:,1]
        
    #Print model report: ��ӡģ�ͱ��棺
    print ("\nModel Report")
    print ("Accuracy : %.4g" % metrics.accuracy_score(dtrain['Disbursed'].values, dtrain_predictions))
    print ("AUC Score (Train): %f" % metrics.roc_auc_score(dtrain['Disbursed'], dtrain_predprob))
     
    #Predict on testing data:  Ԥ��������ݣ�
    dtest['forecast'] = alg.predict_proba(dtest[predictors])[:,1]
    forecast = dtest[['ID','forecast']]
    forecast.rename(columns={'ID':'userid','forecast':'probability'}, inplace = True)
    forecast.to_csv("forecast_data.csv",index=False,sep=',')
                   
    feat_imp = pd.Series(alg.feature_importances_).sort_values(ascending=False)
    feat_imp.plot(kind='bar', title='Feature Importances')
    plt.ylabel('Feature Importance Score')
    

rcParams['figure.figsize'] = 12, 4

train  =  pd.read_csv ('train_data.csv')
test = pd.read_csv ('test_data.csv')

target='Disbursed'
IDcol = 'ID'

predictors = [x for x in train.columns if x not in [target, IDcol]]
xgb1 = XGBClassifier(
        learning_rate =0.1,
        n_estimators=500,   #���ɭ����������
        max_depth=6,         #����������
        min_child_weight=1,  #������СҶ�ӽڵ�����Ȩ�غ�
        gamma=4,             #ָ���˽ڵ�����������С��ʧ�����½�ֵ
        subsample=0.7,       #���ƶ���ÿ��������������ı���
        colsample_bytree=0.8,#����ÿ�����������������ռ��
        objective= 'binary:logistic',#��������߼��ع飬����Ԥ��ĸ���
        nthread=4,          #���ж��߳̿��ƣ�Ӧ������ϵͳ�ĺ���
        scale_pos_weight=1, #������ʮ�ֲ�ƽ��ʱ���趨Ϊһ����ֵ������ʹ�㷨��������
        seed=27)#,            #�����������
        #booster='gbtree')            
modelfit(xgb1, train, test, predictors)