import os

import neptune

PROJECT_NAME = os.getenv('NEPTUNE_PROJECT_NAME')
API_TOKEN = os.getenv('NEPTUNE_API_TOKEN')

neptune.init(project_qualified_name=PROJECT_NAME, api_token=API_TOKEN)

neptune.create_experiment(params={'lr': 0.3, 'epoch_nr': 16})

neptune.log_metric('accuracy', 0.14)
neptune.log_metric('f1_score', 0.58)

if os.getenv('CI_PIPELINE') == "true":
    neptune.append_tag('ci-pipeline')
    with open('experiment_id.txt', 'w+') as f:
        f.write(neptune.get_experiment().id)
