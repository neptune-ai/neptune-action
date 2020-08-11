import os
print(os.getenv('GITHUB_REF'))
exit()

import lightgbm as lgb
import matplotlib.pyplot as plt
import neptune
from neptunecontrib.monitoring.lightgbm import neptune_monitor
from scikitplot.metrics import plot_roc, plot_confusion_matrix, plot_precision_recall
from sklearn.datasets import load_wine
from sklearn.metrics import f1_score, accuracy_score
from sklearn.model_selection import train_test_split

# Connect your script to Neptune
# To do that you need to specify which user (NEPTUNE_API_TOKEN) and project (NEPTUNE_PROJECT_NAME) is it.
PROJECT_NAME = os.getenv('NEPTUNE_PROJECT_NAME')
API_TOKEN = os.getenv('NEPTUNE_API_TOKEN')

neptune.init(api_token=API_TOKEN, project_qualified_name=PROJECT_NAME)

PARAMS = {'boosting_type': 'gbdt',
          'objective': 'multiclass',
          'num_class': 3,
          'num_leaves': 8,
          'learning_rate': 0.01,
          'feature_fraction': 0.9
          }
NUM_BOOSTING_ROUNDS = 10

# Create an experiment in Neptune and log hyperparameters
neptune.create_experiment('lightGBM-on-wine',
                          params={**PARAMS,
                                  'num_boosting_round': NUM_BOOSTING_ROUNDS})

data = load_wine()
X_train, X_test, y_train, y_test = train_test_split(data.data,
                                                    data.target,
                                                    test_size=0.25)
lgb_train = lgb.Dataset(X_train, y_train)
lgb_eval = lgb.Dataset(X_test, y_test, reference=lgb_train)

# Train model and monitor learning curves during training
gbm = lgb.train(PARAMS,
                lgb_train,
                num_boost_round=NUM_BOOSTING_ROUNDS,
                valid_sets=[lgb_train, lgb_eval],
                valid_names=['train', 'valid'],
                callbacks=[neptune_monitor()],
                )

# Get predictions on test dataset
y_test_pred = gbm.predict(X_test)

# Calculate evaluation metrics and log them to Neptune
f1 = f1_score(y_test, y_test_pred.argmax(axis=1), average='macro')
accuracy = accuracy_score(y_test, y_test_pred.argmax(axis=1))

neptune.log_metric('accuracy', accuracy)
neptune.log_metric('f1_score', f1)

# Create performance charts and log them to Neptune
fig_roc, ax = plt.subplots(figsize=(12, 10))
plot_roc(y_test, y_test_pred, ax=ax)

fig_cm, ax = plt.subplots(figsize=(12, 10))
plot_confusion_matrix(y_test, y_test_pred.argmax(axis=1), ax=ax)

fig_pr, ax = plt.subplots(figsize=(12, 10))
plot_precision_recall(y_test, y_test_pred, ax=ax)

neptune.log_image('performance charts', fig_roc)
neptune.log_image('performance charts', fig_cm)
neptune.log_image('performance charts', fig_pr)

# Handle CI pipeline details if inside of the Gitub Actions Workflow
if os.getenv('CI') == "true":
    neptune.append_tag('ci-pipeline')
    with open('experiment_id.txt', 'w+') as f:
        f.write(neptune.get_experiment().id)
