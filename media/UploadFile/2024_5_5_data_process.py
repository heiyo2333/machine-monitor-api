import pandas as pd
import numpy as np
from scipy.io import savemat
import os

# 指定要遍历的文件夹路径和保存的位置
folder_path = "D:/2023-7铣刀/Cleansed data/G01/"
save_folder = "C:/Users/wzy/Desktop/频谱图/所有数据/Z向力信号_时域特征_频域特征_0.2s_0.1_0.5_0.95"

# 遍历文件夹中的所有文件
for file_name in os.listdir(folder_path):
    # 检查文件是否为 CSV 文件
    if file_name.endswith('.csv'):
        # 构造完整的文件路径
        file_path = os.path.join(folder_path, file_name)

        # 读取 CSV 文件里面的X向力信号
        data = pd.read_csv(file_path)
        numbers = len(data.iloc[:, 2])

        # 提取不同比例的信号段
        ratios = [0.1, 0.3, 0.5, 0.7, 0.95]
        features_combined = []  # 用于保存特征的列表
        ratios_list = []  # 用于保存比例值的列表
        for ratio in ratios:
            number = int(numbers * ratio)
            data_segment = data.iloc[number:number + 2000, 2]
            data_array = np.array(data_segment)

            # 计算时域特征
            mean_value = np.mean(data_array)
            std_deviation = np.std(data_array)
            rms = np.sqrt(np.mean(data_array ** 2))

            # 进行 FFT 处理
            Fs = 10000
            N = 2000
            data_fft = abs(np.fft.fft(data_array)) / N
            data_fft_half = data_fft[:N // 2]

            # 计算频域特征
            freqs = np.fft.fftfreq(N, 1 / Fs)[:N // 2]
            centroid_freq = np.sum(data_fft_half * freqs) / np.sum(data_fft_half)
            freq_variance = np.sum(data_fft_half * (freqs - centroid_freq) ** 2) / np.sum(data_fft_half)
            mean_freq = np.sum(data_fft_half * freqs) / N

            # 将特征加入列表
            features_combined.append([mean_value, std_deviation, rms, centroid_freq, freq_variance, mean_freq])
            # 保存比例值
            ratios_list.append(ratio)

        # 将列表转换为 NumPy 数组，并按行合并
        features_combined = np.vstack(features_combined)
        ratios_data_combined = np.vstack(ratios_list)
        # 构造保存 MAT 文件的文件名
        file_name_parts = file_name.split('.')
        mat_file_name = f"data_{file_name_parts[0]}_z_0.2s_test.mat"

        # 构造保存 MAT 文件的完整路径
        save_path = os.path.join(save_folder, mat_file_name)

        # 保存为 MAT 文件
        savemat(save_path, {'data': features_combined, 'ratios': ratios_data_combined})
        print(f"已保存文件：{save_path}")
