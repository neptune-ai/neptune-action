import neptune

PROJECT_NAME = 'shared/github-actions'
API_TOKEN = 'ANONYMOUS'

def get_experiment_data(ids):
    project = neptune.init(project_qualified_name=PROJECT_NAME, api_token=API_TOKEN)
    
    return project.get_leaderboard(id=ids)
    

def find_diff(df):
    
    selected_cols, cleaned_cols = [], []
    for col in df.columns:
        for name in ['channel_', 'parameter_', 'property_']:
            if name in col and not any(excluded_name in col for excluded_name in ['stderr', 'stdout']):
                selected_cols.append(col)
                cleaned_cols.append(col.replace(name,''))
    df = df[['id'] + selected_cols]
        
    different_cols = []
    for col in df.columns:
        vals = df[col].values
        if vals[0] != vals[1]:
            different_cols.append(col)

    return df[different_cols]



def format_data(df):
    
    data = df.to_dict()
    
    cleaned_data = {'metrics':{},
                    'parameters':{},
                    'properties':{},
                    'branches':['master', 'develop']
                   }
    for k,v in data.items():
        if k=='id':
            cleaned_data[k] = [v[0],v[1]] 
            
        if 'channel_' in k:
            cleaned_data['metrics'][k.replace('channel_','')] = [v[0],v[1]]
        if 'parameter_' in k:
            cleaned_data['parameters'][k.replace('parameter_','')] = [v[0],v[1]]
        if 'property_' in k:
            cleaned_data['properties'][k.replace('property_','')] = [v[0],v[1]]
            
    return cleaned_data

def create_table(data):
    table = []
    table.append("<table><tr><td></td>")

    # branches
    for branch in data['branches']:
        text = "<td><b>{}</b></td>".format(branch)
        table.append(text)
    
    # experiment links and id
    table.append("<tr><td>Neptune Experiment</td>")
    user, project = PROJECT_NAME.split('/')
    for exp_id in data['id']:
        text = f"""<td><a href="https://ui.neptune.ai/o/{user}/org/{project}/e/{exp_id}"><b>{exp_id}</b></a></td>"""
        table.append(text)
    table.append("</tr>")

    # metrics
    if data['metrics']:
        table.append("""<tr>
            <th colspan=3, class="section-type", style="text-align:left;background-color:lightblue;">
                Metrics
            </th>""")

        for name, values in data['metrics'].items():
            table.append(f"<tr><td>{name}</td>")
            for value in values:
                table.append(f"<td>{value}</td>")
            table.append("</tr>")

        table.append("</tr>")
    
    # parameters
    if data['parameters']:
        table.append("""<tr>
            <th colspan=3, class="section-type", style="text-align:left;background-color:lightblue;">
                Parameters
            </th>""")

        for name, values in data['parameters'].items():
            table.append(f"<tr><td>{name}</td>")
            for value in values:
                table.append(f"<td>{value}</td>")
            table.append("</tr>")

        table.append("</tr>")
    
    # properties
    
    if data['properties']:
        table.append("""<tr>
            <th colspan=3, class="section-type", style="text-align:left;background-color:lightblue;">
                Properties
            </th>""")

        for name, values in data['properties'].items():
            table.append(f"<tr><td>{name}</td>")
            for value in values:
                table.append(f"<td>{value}</td>")
            table.append("</tr>")

        table.append("</tr>")
    
    table.append("</tr></table>")
    
    table_text = "".join(table)
        
    return table_text

if __name__ == "__main__":

    df = get_experiment_data(['GIT-3', 'GIT-6'])
    df_diff = find_diff(df)
    data = format_data(df_diff)
    table_text = create_table(data)
    
    with open("comparison_table.md", "w+") as f:
        f.write(table_text)
