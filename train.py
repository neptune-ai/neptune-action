import os

import lightgbm as lgb
import matplotlib.pyplot as plt
import neptune
from neptunecontrib.monitoring.lightgbm import neptune_monitor
from scikitplot.metrics import plot_roc, plot_confusion_matrix, plot_precision_recall
from sklearn.datasets import load_wine
from sklearn.metrics import f1_score, accuracy_score
from sklearn.model_selection import train_test_split

PARAMS = {'boosting_type': 'gbdt',
          'objective': 'multiclass',
          'num_class': 3,
          'num_leaves': 8,
          'learning_rate': 0.01,
          'feature_fraction': 0.9,
          'seed': 1234
          }
NUM_BOOSTING_ROUNDS = 10

data = load_wine()
X_train, X_test, y_train, y_test = train_test_split(data.data,
                                                    data.target,
                                                    test_size=0.25,
                                                    random_state=1234)
lgb_train = lgb.Dataset(X_train, y_train)
lgb_eval = lgb.Dataset(X_test, y_test, reference=lgb_train)

# Connect your script to Neptune
neptune.init(api_token=os.getenv('NEPTUNE_API_TOKEN'),
             project_qualified_name=os.getenv('NEPTUNE_PROJECT_NAME'))

# Create an experiment and log hyperparameters
neptune.create_experiment('lightGBM-on-wine',
                          params={**PARAMS,
                                  'num_boosting_round': NUM_BOOSTING_ROUNDS})

gbm = lgb.train(PARAMS,
                lgb_train,
                num_boost_round=NUM_BOOSTING_ROUNDS,
                valid_sets=[lgb_train, lgb_eval],
                valid_names=['train', 'valid'],
                callbacks=[neptune_monitor()],  # monitor learning curves
                )
y_test_pred = gbm.predict(X_test)

f1 = f1_score(y_test, y_test_pred.argmax(axis=1), average='macro')
accuracy = accuracy_score(y_test, y_test_pred.argmax(axis=1))

# Log metrics to Neptune
neptune.log_metric('accuracy', accuracy)
neptune.log_metric('f1_score', f1)

fig_roc, ax = plt.subplots(figsize=(12, 10))
plot_roc(y_test, y_test_pred, ax=ax)

fig_cm, ax = plt.subplots(figsize=(12, 10))
plot_confusion_matrix(y_test, y_test_pred.argmax(axis=1), ax=ax)

fig_pr, ax = plt.subplots(figsize=(12, 10))
plot_precision_recall(y_test, y_test_pred, ax=ax)

# Log performance charts to Neptune
neptune.log_image('performance charts', fig_roc)
neptune.log_image('performance charts', fig_cm)
neptune.log_image('performance charts', fig_pr)

# Handle CI pipeline details
if os.getenv('CI') == "true":
    neptune.append_tag('ci-pipeline', os.getenv('NEPTUNE_EXPERIMENT_TAG_ID'))
