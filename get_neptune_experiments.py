import os

import neptune
import numpy as np

PROJECT_NAME = os.getenv('NEPTUNE_PROJECT_NAME')
API_TOKEN = os.getenv('NEPTUNE_API_TOKEN')

BRANCHES = ['develop', 'master']
EXPERIMENT_IDS = [os.getenv('MASTER_EXPERIMENT_ID'), os.getenv('DEVELOP_EXPERIMENT_ID')]


def get_experiment_data():
    project = neptune.init(project_qualified_name=PROJECT_NAME, api_token=API_TOKEN)

    return project.get_leaderboard(id=EXPERIMENT_IDS)


def find_diff(df):
    selected_cols, cleaned_cols = [], []
    for col in df.columns:
        for name in ['channel_', 'parameter_', 'property_']:
            if name in col and not any(excluded_name in col for excluded_name in ['stderr', 'stdout']):
                selected_cols.append(col)
                cleaned_cols.append(col.replace(name, ''))
    df = df[['id'] + selected_cols]

    different_cols = []
    for col in df.columns:
        vals = df[col].values
        if vals[0] != vals[1]:
            different_cols.append(col)

    return df[different_cols]


def format_data(df):
    data = df.to_dict()

    cleaned_data = {'metrics': {},
                    'parameters': {},
                    'properties': {},
                    'branches': BRANCHES
                    }
    for k, v in data.items():
        if k == 'id':
            cleaned_data[k] = [v[0], v[1]]

        if 'channel_' in k:
            cleaned_data['metrics'][k.replace('channel_', '')] = [v[0], v[1]]
        if 'parameter_' in k:
            cleaned_data['parameters'][k.replace('parameter_', '')] = [v[0], v[1]]
        if 'property_' in k:
            cleaned_data['properties'][k.replace('property_', '')] = [v[0], v[1]]

    return cleaned_data


def create_table(data):
    link = "https://ui.neptune.ai/o/shared/org/github-actions/compare?shortId=%5B%22{}%22%2C%22{}%22%5D".format(
        data['id'][0], data['id'][1])
    table = ["""<a href="{}">See the experiment comparison in Neptune </a>""".format(link)]
    table.append("<table><tr><td></td>")

    # branches
    for branch in data['branches']:
        text = "<td><b>{}</b></td>".format(branch)
        table.append(text)

    # experiment links and id
    table.append("<tr><td>Neptune Experiment</td>")
    user, project = PROJECT_NAME.split('/')
    for exp_id in data['id']:
        text = """<td><a href="https://ui.neptune.ai/o/{0}/org/{1}/e/{2}"><b>{2}</b></a></td>""".format(user, project,
                                                                                                        exp_id)
        table.append(text)
    table.append("</tr>")

    # metrics
    if data['metrics']:
        table.append("""<tr>
            <th colspan=3, style="text-align:left;">
                Metrics
            </th>""")

        for name, values in data['metrics'].items():
            table.append("<tr><td>{}</td>".format(name))
            for value in values:
                value = np.round(float(value), 5)
                table.append("<td>{}</td>".format(value))
            table.append("</tr>")

        table.append("</tr>")

    # parameters
    if data['parameters']:
        table.append("""<tr>
            <th colspan=3, style="text-align:left;">
                Parameters
            </th>""")

        for name, values in data['parameters'].items():
            table.append("<tr><td>{}</td>".format(name))
            for value in values:
                table.append("<td>{}</td>".format(value))
            table.append("</tr>")

        table.append("</tr>")

    # properties

    if data['properties']:
        table.append("""<tr>
            <th colspan=3, style="text-align:left;">
                Properties
            </th>""")

        for name, values in data['properties'].items():
            table.append("<tr><td>{}</td>".format(name))
            for value in values:
                table.append("<td>{}</td>".format(value))
            table.append("</tr>")

        table.append("</tr>")

    table.append("</tr></table>")

    table_text = "".join(table)

    return table_text


if __name__ == "__main__":
    df = get_experiment_data()
    df_diff = find_diff(df)
    data = format_data(df_diff)
    table_text = create_table(data)

    with open("comparison_table.md", "w+") as f:
        f.write(table_text)
