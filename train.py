import neptune

neptune.init(project_qualified_name='shared/github-actions', api_token='ANONYMOUS')

neptune.create_experiment(params={'lr': 0.3, 'epoch_nr': 11})
# neptune.append_tag('baseline')

neptune.log_metric('accuracy', 0.99)
neptune.log_metric('f1_score', 0.69)
