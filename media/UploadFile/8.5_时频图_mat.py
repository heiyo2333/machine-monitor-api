import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import pywt
from scipy import io

# 指定要遍历的文件夹路径和保存的位置
folder_path = "D:/2023-7铣刀/Cleansed data/G06/"
save_folder = "C:/Users/wzy/Desktop/频谱图/特征提取/时频特征_小波包分析"

# 确保保存文件夹存在
if not os.path.exists(save_folder):
    os.makedirs(save_folder)


def plot_wavelet_transform(data, title, save_folder):
    scales = np.arange(1, 50)
    coef, freqs = pywt.cwt(data, scales, 'morl')

    plt.figure(figsize=(10, 6))
    plt.imshow(np.abs(coef), extent=[0, len(data), 1, 50], aspect='auto', cmap='jet')
    plt.title(title)
    plt.xlabel('Sample')
    plt.ylabel('Scale')
    plt.colorbar(label='Magnitude')
    plt.savefig(os.path.join(save_folder, f'{title}_wavelet_transform_scales.png'))
    plt.close()

    return coef  # Return without adding extra dimensions


def extract_and_process_data(data, ratios, save_folder):
    dataX = []
    dataY = []
    for ratio in ratios:
        number = int(len(data) * ratio)
        data_segment_length = min(5000, len(data) - number)
        data_segment = data[number:number + data_segment_length]

        wavelet_data = plot_wavelet_transform(data_segment, f"Wavelet Transform Ratio {ratio}", save_folder)
        dataX.append(wavelet_data[:, :, np.newaxis])  # Add new axes if necessary
        dataY.append([ratio])

    return np.array(dataX), np.array(dataY)


# 遍历文件夹中的每个文件
for file_name in os.listdir(folder_path):
    # 检查文件是否为 CSV 文件
    if file_name.endswith('.csv'):
        # 构造完整的文件路径
        file_path = os.path.join(folder_path, file_name)

        # 读取 CSV 文件里面的数据（这里假设第一列是要分析的数据）
        data = pd.read_csv(file_path)
        data_array = np.array(data.iloc[:, 0])

        # 定义不同的比例
        ratios = [0.1, 0.5, 0.9]

        # 提取并处理不同比例的数据段
        dataX, dataY = extract_and_process_data(data_array, ratios, save_folder)

        # 保存为.mat文件
        file_name_without_extension = os.path.splitext(file_name)[0]
        mat_file_path = os.path.join(save_folder, f'{file_name_without_extension}.mat')
        io.savemat(mat_file_path, {'dataX': dataX, 'dataY': dataY})

        print(f"Processed {file_name}, saved as {mat_file_path}")

print("All processing completed.")
