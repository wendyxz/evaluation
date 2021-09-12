import pandas as pd
import numpy as np

# column headers of detection file
col_list = ['frameNumber', 'tracks_entering_interval', 'tracks_entering_total',
            'tracks_exiting_interval','tracks_exiting_total',
            'trackId', 'rectsSize', 'attribRectsSize', 'confClassId',
            'countedAs', 'trackCrossingStatus', 'bordersSize', 'attribRectsX',
            'attribRectsY', 'attribRectsWidth','attribRectsHeight',
            'border_0_crossingStatus', 'border_0_areaChange',
            'border_0_touchesBorder', 'border_0_percentArea']

# path to detection file
file_path = '/Users/wendyzhang/Downloads/detections_bei_release_4.csv'

df = pd.read_csv(file_path, usecols=col_list, low_memory=False,
                 error_bad_lines=False, index_col=False, dtype='unicode')

# list of indices of repetitive row entries that need to be removed from
#   dataframe
rows_to_remove = []

# dictionary of pairs, indicating frames whose total entering count need to be
#   updated after removal (max value is selected for mutiple entries)
enter_update = {}
last_frame = 'a'
last_enter = 0
last_exit = 0

# determines rows to be deleted, and leaves rows to be updated after deletion
for index, row in df.iterrows():
    if row['frameNumber'] == last_frame:
        if row['tracks_exiting_total'] > last_exit:
            if row['tracks_entering_total'] >= last_enter:
                rows_to_remove.append(index - 1)
            else:
                enter_update[row['frameNumber']] = last_enter
                rows_to_remove.append(index - 1)
            last_frame = row['frameNumber']
            last_enter = row['tracks_entering_total']
            last_exit = row['tracks_exiting_total']
        else:
            rows_to_remove.append(index)
            if row['tracks_entering_total'] > last_enter:
                enter_update[row['frameNumber']] = row['tracks_entering_total']
            last_frame = row['frameNumber']
            last_enter = row['tracks_entering_total']
            last_exit = row['tracks_exiting_total']
    else:
        last_frame = row['frameNumber']
        last_enter = row['tracks_entering_total']
        last_exit = row['tracks_exiting_total']

# contains unique frames only
modified_df = df.drop(rows_to_remove)

# update entering count to maximum for specific frame
for key in enter_update:
    frame = key
    total_enter = enter_update[key]
    modified_df.loc[modified_df['frameNumber'] == frame,
                    'tracks_entering_total'] = total_enter

new_file = '/Users/wendyzhang/Documents/reduced_bei_release_4.csv'

modified_df.reset_index(inplace=True)

modified_df.to_csv(new_file)

counts = modified_df[["tracks_entering_total", "tracks_exiting_total"]].to_numpy()
total_counts_per_minute = counts[::1500,:]
total_counts_per_minute = np.array([list(map(int, i)) for i in
                          total_counts_per_minute])

per_minute_counts = np.diff(total_counts_per_minute.transpose())

# read file with ground truth data to dataframe
gt_df = pd.read_csv('/Users/wendyzhang/Documents/bei_gt.csv',
                    usecols=['Interval', 'Entering', 'Exiting'],
                    low_memory=False)

my_counts = gt_df[['Entering', 'Exiting']].to_numpy()

gt_counts_per_minute = my_counts.transpose()

df_counts = pd.DataFrame(np.array(per_minute_counts.transpose()),
                         columns=['Entering', 'Exiting'])

df_counts.to_csv('/Users/wendyzhang/Documents/bei_release_4_counts.csv')

# list of intervals by minute
intervals = gt_df['Interval'].tolist()

df_counts.insert(0, 'Interval', intervals, True)

# calculate average accuracy and error per minute
mean_error_per_minute = np.mean(abs(gt_counts_per_minute - per_minute_counts) /
                                np.add(gt_counts_per_minute,1e-15),axis = 1)
mean_accuracy_per_minute = (1 - mean_error_per_minute) * 100

print(mean_error_per_minute)
print(mean_accuracy_per_minute)






