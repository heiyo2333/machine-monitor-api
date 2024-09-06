# 本代码用于从Z方向力信号中提取出0.15-0.25、0.55-0.65、0.85-0.95范围内各100个样本，总计300个样本。
import os
import numpy as np
import pandas as pd

original_signal_path = "D:/2023-7铣刀/Cleansed data/ALL_Z_Forced_Signal_Wet/"
processed_signal_path = "D:/2023-7铣刀/Cleansed data/Z_Signal_Wet_data_make"

if not os.path.exists(processed_signal_path):
    os.makedirs(processed_signal_path)

ratios_0_2 = np.linspace(0.15, 0.25, 100)
ratios_0_6 = np.linspace(0.55, 0.65, 100)
ratios_0_9 = np.linspace(0.85, 0.95, 100)
ratios = np.concatenate((ratios_0_2, ratios_0_6, ratios_0_9))
Fs = 10000

for file_name in os.listdir(original_signal_path):
    if file_name.endswith(".csv"):
        filename = file_name.split(".")[0]
        file_path = os.path.join(original_signal_path, file_name)
        data = pd.read_csv(file_path)
        data_array = data.iloc[:, 0].to_numpy()
        data_numbers = len(data_array)
        data_array = data_array - np.mean(data_array)
        for ratio in ratios:
            numbers = int(data_numbers * ratio)
            data_segment = data_array[numbers: numbers+2000]
            # 将numpy数组转换为pandas Series
            data_segment_series = pd.Series(data_segment)
            save_ratio = f'{ratio:.3f}'
            save_filename = filename + "_" + save_ratio + ".csv"
            save_path = os.path.join(processed_signal_path, save_filename)
            data_segment_series.to_csv(save_path, index=False)
            print(save_filename + " already made")
