import neptune

neptune.init(project_qualified_name='shared/github-actions', api_token='ANONYMOUS')

neptune.create_experiment(params={'lr': 0.3, 'epoch_nr': 24})

neptune.log_metric('accuracy', 0.667)
neptune.log_metric('f1_score', 0.764)

import os
os.environ["NEPTUNE_EXPERIMENT_ID"] = neptune.get_experiment().id
