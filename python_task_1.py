import pandas as pd
import numpy as np

def generate_car_matrix(dataset):
  
    df = pd.read_csv(dataset)
    
   
    result_df = df.pivot_table(index='id_1', columns='id_2', values='car', fill_value=0)
    
  
    np.fill_diagonal(result_df.values, 0)
    
    return result_df


def get_type_count(dataset):
    df = pd.read_csv(dataset)
    
  
    df['car_type'] = pd.cut(df['car'], bins=[-float('inf'), 15, 25, float('inf')],
                            labels=['low', 'medium', 'high'], right=False)
    
    
    type_count = df['car_type'].value_counts().to_dict()
    
  
    sorted_type_count = dict(sorted(type_count.items()))
    
    return sorted_type_count





def get_bus_indexes(dataset):
    df = pd.read_csv(dataset)
    
 
    mean_bus_value = df['bus'].mean()
    
   
    bus_indexes = df[df['bus'] > 2 * mean_bus_value].index.tolist()
    
   
    bus_indexes.sort()
    
    return bus_indexes


def filter_routes(dataset):
    df = pd.read_csv(dataset)
    
    
    avg_truck_per_route = df.groupby('route')['truck'].mean()
    
   
    selected_routes = avg_truck_per_route[avg_truck_per_route > 7].index.tolist()
    
  
    selected_routes.sort()
    
    return selected_routes


def multiply_matrix(result_df):
    modified_df = result_df.applymap(lambda x: x * 0.75 if x > 20 else x * 1.25)
    
 
    modified_df = modified_df.round(1)
    
    return modified_df

def check_time_completeness(dataset):
   
    df = pd.read_csv(dataset)

   
    df['start_datetime'] = pd.to_datetime(df['startDay'] + ' ' + df['startTime'])

    
    df['end_datetime'] = pd.to_datetime(df['endDay'] + ' ' + df['endTime'])

   
    completeness_check = df.groupby(['id', 'id_2']).apply(lambda group: (
        group['start_datetime'].min() == pd.to_datetime('00:00:00')) and
        (group['end_datetime'].max() == pd.to_datetime('23:59:59')) and
        (group['start_datetime'].dt.dayofweek.nunique() == 7)
    )

    return completeness_check