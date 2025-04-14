import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn import svm
from sklearn import metrics


dataset=np.load('dataset_bin.npz')
test_test_size=np.arange(0.1,0.5,0.1)
from sklearn.model_selection import GridSearchCV


X_train, X_test, y_train, y_test = train_test_split(dataset['data'],dataset['target'], test_size=0.1,random_state=42)
clf = svm.SVC()
param_grid = [
  {'C': [500,800,1000], 'gamma': [0.008,0.0009,0.001,0.0011], 'kernel': ['rbf']},
 ]
grid = GridSearchCV(clf, param_grid, cv=10, scoring='accuracy')
grid.fit(X_train, y_train)
results = pd.DataFrame(grid.cv_results_)

display_columns = [
    'mean_test_score', 'std_test_score', 'rank_test_score', 'params'
]
print(results[display_columns].to_string(index=False))