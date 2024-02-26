import pandas as pd

def map_results_to_numeric(result):
    mapping = {
        'EXCELLENT': 0,
        'GOOD': 1,
        'FAIR': 2,
        'BORDERLINE': 3,
        'MILD': 4,
        'MODERATE': 5,
        'SEVERE': 6
    }
    return mapping.get(result)

def map_results(df):
    df['Registration_Results_Num'] = df['Results'].apply(map_results_to_numeric)
    return df

def derive_parents_results_num(df, selected_column_name):
    # Each row in the dataframe represents one dog.
    # The Sire and Dam columns contain the ID of the dog's parents, so these are foreign keys.
    # The ID's refer to other row where the Registration column holds the ID, so it's the primary key.
    # The Results_Num column contains the numerical representation of the OFA test results of the dog.

    # Create a dictionary mapping Registration ID to Results_Num value.
    id_to_results = df.set_index('Registration')['Registration_Results_Num'].to_dict()
    # remove the row is the key is nan
    id_to_results = {k: v for k, v in id_to_results.items() if pd.notnull(k)}

    # Create derived column for <selected_column_name>_Results_Num
    # Make sure the Results_Num column stays empty if the corresponding <selected_column_name>_Results_Num column is empty.
    df[selected_column_name + '_Results_Num'] = df[selected_column_name].map(id_to_results)

    return df


def preprocess_parent_data(df, selected_column_name, target):
    # Each row in the dataframe represents one dog.
    # The Sire and Dam columns contain the ID of the dog's parents, so these are foreign keys.
    # The ID's refer to other row where the Registration column holds the ID, so it's the primary key.

    # Create a dictionary mapping Registration ID to Sire and Dam
    id_map = df.set_index('Registration')[target].to_dict()

    # Create new column names for Sire and Dam of the selected column
    target_column_name = selected_column_name + '_' + target

    # Create new columns that hold the Registration values of the sire_column_name and dam_column_name columns
    df[target_column_name] = df[selected_column_name].map(id_map)

    return df

def average_parent_data(df, child_column_name, sire_results_num_column_name, dam_results_num_column_name):
    # Each row in the dataframe represents one dog.
    # The parameters contain references to the columns that hold the numerical representation of the OFA test results of the dog's parents.
    # Determine the average of the 2 values.

    # Create new columns that hold the Registration values of the sire_column_name and dam_column_name columns
    df[child_column_name + '_Parents_Results_Num'] = df[sire_results_num_column_name] + df[dam_results_num_column_name] / 2 

    return df


def average_values(df):
    # The list of columns to be averaged
    ancestor_list = ['Sire_Results_Num', 'Dam_Results_Num', 'Sire_Sire_Results_Num', \
                     'Sire_Dam_Results_Num', 'Dam_Sire_Results_Num', 'Dam_Dam_Results_Num', \
                     'Sire_Sire_Sire_Results_Num', 'Sire_Sire_Dam_Results_Num', \
                     'Sire_Dam_Sire_Results_Num', 'Sire_Dam_Dam_Results_Num', \
                     'Dam_Sire_Sire_Results_Num', 'Dam_Sire_Dam_Results_Num', \
                     'Dam_Dam_Sire_Results_Num', 'Dam_Dam_Dam_Results_Num']
    
    # Create a new column that holds the average of the columns in ancestor_list, but only for the columns that contain a value.
    df['Average_Results_Num'] = df[ancestor_list].mean(axis=1)
      
    return df

def statistics(df, source, target):

    print("Total #records:", df.shape[0])
    # Determine the percentage of missing values in each column
    percentage_filled_in_column = (df[source].count() / df[source].size) * 100
    source_results = "Registration_Results_Num"
    percentage_filled_in_results = (df[source_results].count() / df[source_results].size) * 100
    print(source, " : ", percentage_filled_in_column)
    print(source_results, " : ", percentage_filled_in_results)

    # Create new columns that hold the Registration values of the sire_column_name and dam_column_name columns
    percentage_filled_in_column = (df[target].count() / df[target].size) * 100
    target_results = target + "_Results_Num"
    percentage_filled_in_results = (df[target_results].count() / df[target_results].size) * 100
    print(target, " : ", percentage_filled_in_column)
    print(target_results, " : ", percentage_filled_in_results)


def plot_start_graph(graph_string, child_registration):
    graph_string += '# Graph for ' + child_registration + '\n\n'
    graph_string += '```mermaid\n    graph TD\n'
    return graph_string


def plot_end_graph(graph_string):
    return graph_string + '```\n\n\n'


def plot_results_graph(graph_string,
                       child,
                       child_results_num,
                       sire,
                       sire_results_num,
                       dam,
                       dam_results_num):
    graph_string += '    ' + child + '['+ child + ' ' + str(child_results_num) + ']-->' + sire + '[' + sire + ' ' + str(sire_results_num) + ']\n'
    graph_string += '    ' + child + '-->' + dam + '[' + dam + ' ' + str(dam_results_num) + ']\n'
    return graph_string


if __name__ == '__main__':
    # load OFA.csv file as dataframe
    df = pd.read_csv('OFA.csv')
    df = map_results(df)

    for parent in ['Sire', 'Dam', 'Sire_Sire', 'Sire_Dam', 'Dam_Sire', 'Dam_Dam']:
        df = derive_parents_results_num(df, parent)
        for target_column in ['Sire', 'Dam']:
            df = preprocess_parent_data(df, parent, target_column)
    df.to_csv('OFA_num_1.csv', index=False)

    for parent in ['Sire_Sire_Sire', 'Sire_Sire_Dam', 'Sire_Dam_Sire', 'Sire_Dam_Dam', 'Dam_Sire_Sire', 'Dam_Sire_Dam', 'Dam_Dam_Sire', 'Dam_Dam_Dam']:
         df = derive_parents_results_num(df, parent)
    df.to_csv('OFA_num_2.csv', index=False)

    for source in ['Registration']:
        for target in ['Sire', 'Dam', 'Sire_Sire', 'Sire_Dam', 'Dam_Sire', 'Dam_Dam', 'Sire_Sire_Sire', 'Sire_Sire_Dam', 'Sire_Dam_Sire', 'Sire_Dam_Dam', 'Dam_Sire_Sire', 'Dam_Sire_Dam', 'Dam_Dam_Sire', 'Dam_Dam_Dam']:
            statistics(df, source, target)

    ancestor_list = [
                        [ 'Registration', 'Sire', 'Dam' ],
                        [ 'Sire', 'Sire_Sire', 'Sire_Dam' ],
                        [ 'Dam', 'Dam_Sire', 'Dam_Dam' ],
                        [ 'Sire_Sire', 'Sire_Sire_Sire', 'Sire_Sire_Dam' ],
                        [ 'Sire_Dam', 'Sire_Dam_Sire', 'Sire_Dam_Dam' ],
                        [ 'Dam_Sire', 'Dam_Sire_Sire', 'Dam_Sire_Dam' ],
                        [ 'Dam_Dam', 'Dam_Dam_Sire', 'Dam_Dam_Dam' ]
                    ]
                                 
    for ancestor in ancestor_list:
        df = average_parent_data(df, ancestor[0], ancestor[1] + '_Results_Num', ancestor[2] + '_Results_Num')

    # columns_to_check = ['Sire', 'Dam', 'Sire_Sire', 'Sire_Dam', 'Dam_Sire', 'Dam_Dam', 'Sire_Sire_Sire', 'Sire_Sire_Dam', 'Sire_Dam_Sire', 'Sire_Dam_Dam', 'Dam_Sire_Sire', 'Dam_Sire_Dam', 'Dam_Dam_Sire', 'Dam_Dam_Dam']
    # df_filtered = df[df[columns_to_check].notnull().all(axis=1)]
    # print("DataFrame after removing rows where all specified columns are filled:")
    # print("complete records with filled in references: ", df_filtered.shape[0])
    # df_filtered.to_csv('OFA_num_3.csv', index=False)

    columns_to_check = ['Sire_Results_Num', 'Dam_Results_Num', 'Sire_Sire_Results_Num', 'Sire_Dam_Results_Num', 'Dam_Sire_Results_Num', 'Dam_Dam_Results_Num', 'Sire_Sire_Sire_Results_Num', 'Sire_Sire_Dam_Results_Num', 'Sire_Dam_Sire_Results_Num', 'Sire_Dam_Dam_Results_Num', 'Dam_Sire_Sire_Results_Num', 'Dam_Sire_Dam_Results_Num', 'Dam_Dam_Sire_Results_Num', 'Dam_Dam_Dam_Results_Num'] 
    df_filtered = df[df[columns_to_check].notnull().all(axis=1)]
    print("DataFrame after removing rows where all specified columns are filled:")
    print("complete records with Results_Num: ", df_filtered.shape[0])
    df_filtered.to_csv('OFA_num_3.csv', index=False)

    graph_string = ''
    for count, row in df_filtered.iterrows():
        graph_string = plot_start_graph(graph_string, row['Registration'])
        for ancestor in ancestor_list:
            graph_string = plot_results_graph(graph_string,
                                              ancestor[0],
                                              row[ancestor[0] + '_Results_Num'],
                                              ancestor[1],
                                              row[ancestor[1] + '_Results_Num'],
                                              ancestor[2],
                                              row[ancestor[2] + '_Results_Num'])
        graph_string = plot_end_graph(graph_string)

    #write graph to file
    with open('graph.md', 'w') as f:
        f.write(graph_string)    

    # Convert the markdown (including the mermaid graphs) file to a pdf file
    # pandoc -o graph.pdf graph.md
    

    # df = average_values(df)
    # df.to_csv('OFA_num_3.csv', index=False)

