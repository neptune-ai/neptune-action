# import neptune
#
# neptune.init(project_qualified_name='shared/github-actions', api_token='ANONYMOUS')
#
# neptune.create_experiment(params={'lr': 0.3, 'epoch_nr': 40})
#
# neptune.log_metric('accuracy', 0.81)
# neptune.log_metric('f1_score', 0.66)

weird_text="234234234"

import os
os.environ["NEPTUNE_EXPERIMENT_ID"] = "GIT-6" #neptune.get_experiment().id
