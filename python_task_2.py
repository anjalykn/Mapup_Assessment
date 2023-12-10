import pandas as pd
from itertools import permutations
import datetime


def calculate_distance_matrix(input_file):
    df = pd.read_csv(input_file)
    locations = df['ID'].unique()
    distance_matrix = pd.DataFrame(index=locations, columns=locations)

    for start, end in permutations(locations, 2):
        route1 = df[(df['ID'] == start) & (df['ID_to'] == end)]['Distance'].sum()
        route2 = df[(df['ID'] == end) & (df['ID_to'] == start)]['Distance'].sum()
        total_distance = route1 + route2
        distance_matrix.loc[start, end] = total_distance
        distance_matrix.loc[end, start] = total_distance

    distance_matrix.fillna(0, inplace=True)
    return distance_matrix.astype(float)

def unroll_distance_matrix(distance_matrix):
    unrolled_data = []
    for start, end in permutations(distance_matrix.index, 2):
        distance = distance_matrix.loc[start, end]
        unrolled_data.append({'id_start': start, 'id_end': end, 'distance': distance})

    return pd.DataFrame(unrolled_data)


def find_ids_within_ten_percentage_threshold(distance_data, reference_value):
    average_distance = distance_data[distance_data['id_start'] == reference_value]['distance'].mean()
    threshold = 0.1 * average_distance
    valid_ids = distance_data[(distance_data['distance'] >= average_distance - threshold) & 
                              (distance_data['distance'] <= average_distance + threshold)]['id_start'].unique()
    
    return sorted(valid_ids)


def calculate_toll_rate(distance_data):
    toll_rates = {'moto': 0.8, 'car': 1.2, 'rv': 1.5, 'bus': 2.2, 'truck': 3.6}
    
    for vehicle_type, rate in toll_rates.items():
        distance_data[vehicle_type] = distance_data['distance'] * rate
    
    return distance_data


def calculate_time_based_toll_rates(distance_data):
    discount_factors = {
        'weekday': {'00:00:00-10:00:00': 0.8, '10:00:00-18:00:00': 1.2, '18:00:00-23:59:59': 0.8},
        'weekend': {'00:00:00-23:59:59': 0.7}
    }

    def get_discount_factor(day, time):
        if day in ['Saturday', 'Sunday']:
            return discount_factors['weekend']['00:00:00-23:59:59']
        else:
            for time_range, factor in discount_factors['weekday'].items():
                start_time, end_time = map(datetime.time, map(lambda x: datetime.datetime.strptime(x, "%H:%M:%S").time(), time_range.split('-')))
                if start_time <= time <= end_time:
                    return factor

    distance_data[['start_day', 'start_time']] = distance_data.apply(lambda row: [day, datetime.datetime.strptime(time, "%H:%M:%S").time()] , axis=1, result_type='expand')
    distance_data[['end_day', 'end_time']] = distance_data.apply(lambda row: [day, datetime.datetime.strptime(time, "%H:%M:%S").time()] , axis=1, result_type='expand')
    distance_data['discount_factor'] = distance_data.apply(lambda row: get_discount_factor(row['start_day'], row['start_time']), axis=1)

    for vehicle_type in ['moto', 'car', 'rv', 'bus', 'truck']:
        distance_data[vehicle_type] = distance_data[vehicle_type] * distance_data['discount_factor']

    return distance_data
