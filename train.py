import os

import neptune
from sklearn.datasets import load_breast_cancer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, f1_score
from sklearn.model_selection import train_test_split

PROJECT_NAME = os.getenv('NEPTUNE_PROJECT_NAME')
API_TOKEN = os.getenv('NEPTUNE_API_TOKEN')

PARAMS = {'n_estimators': 40,
          'max_depth': 20,
          'max_features': 60,
          }

neptune.init(project_qualified_name=PROJECT_NAME, api_token=API_TOKEN)
neptune.create_experiment('random-forest-on-wine', params=PARAMS)

data = load_breast_cancer()
X_train, X_test, y_train, y_test = train_test_split(data.data, data.target, test_size=0.1)

rf = RandomForestClassifier(**PARAMS)
rf.fit(X_train, y_train)

y_test_pred = rf.predict_proba(X_test)
roc_auc = roc_auc_score(y_test, y_test_pred[:, 1])
f1_score = f1_score(y_test, y_test_pred[:, 1] > 0.5)

neptune.log_metric('roc_auc', roc_auc)
neptune.log_metric('f1_score', f1_score)

# CI
if os.getenv('CI') == "true":
    neptune.append_tag('ci-pipeline')
    with open('experiment_id.txt', 'w+') as f:
        f.write(neptune.get_experiment().id)
