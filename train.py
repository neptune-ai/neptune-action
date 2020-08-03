import neptune

neptune.init(project_qualified_name='shared/github-actions', api_token='ANONYMOUS')

neptune.create_experiment(params={'lr': 0.3, 'epoch_nr': 173})

neptune.log_metric('accuracy', 0.72)
neptune.log_metric('f1_score', 0.62)


with open('experiment_id.txt', 'w+') as f:
    f.write(neptune.get_experiment().id)