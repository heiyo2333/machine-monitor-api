import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import kurtosis, skew, spearmanr, pearsonr

# 指定要遍历的文件夹路径和保存的位置
folder_path = "D:/2023-7铣刀/Cleansed data/G01/"
save_folder = "C:/Users/wzy/Desktop/频谱图/特征提取/X方向力信号_全特征测试_0.5s_归一化处理_相关系数"

# 定义特征名称
feature_names = [
    "Mean Value", "Standard Deviation", "RMS", "Kurtosis", "Skewness",
    "Crest Factor", "Form Factor", "Impulse Factor", "Peak Factor",
    "Centroid Frequency", "Frequency Variance", "Mean Frequency",
    "Mean Square Frequency", "RMS Frequency", "Frequency Std Dev", "Frequency Skewness"
]

# 遍历文件夹中的所有文件
for file_name in os.listdir(folder_path):
    if file_name.endswith('.csv'):
        file_path = os.path.join(folder_path, file_name)
        data = pd.read_csv(file_path)
        numbers = len(data.iloc[:, 0])
        ratios = [i / 40 for i in range(0, 40)]
        features_combined = []  # 用于保存特征的列表
        ratios_list = np.array(ratios)

        for ratio in ratios:
            number = int(numbers * ratio)
            data_segment = data.iloc[number:number + 5000, 0]
            data_array = np.array(data_segment)

            # 计算时域特征
            mean_value = np.mean(data_array)
            std_deviation = np.std(data_array)
            rms = np.sqrt(np.mean(data_array ** 2))
            kurt = kurtosis(data_array)
            skewness = skew(data_array)
            crest_factor = np.max(np.abs(data_array)) / rms
            form_factor = rms / mean_value
            impulse_factor = np.max(data_array) / rms
            peak_factor = np.max(data_array) / mean_value

            # 进行 FFT 处理
            Fs = 10000
            N = 5000
            data_fft = abs(np.fft.fft(data_array)) / N
            data_fft_half = data_fft[:N // 2]

            # 计算频域特征
            freqs = np.fft.fftfreq(N, 1 / Fs)[:N // 2]
            centroid_freq = np.sum(data_fft_half * freqs) / np.sum(data_fft_half)
            freq_variance = np.sum(data_fft_half * (freqs - centroid_freq) ** 2) / np.sum(data_fft_half)
            mean_freq = np.sum(data_fft_half * freqs) / N
            mean_square_freq = np.sum(data_fft_half ** 2 * freqs) / np.sum(data_fft_half ** 2)
            rms_freq = np.sqrt(mean_square_freq)
            indices = np.argsort(np.abs(data_fft_half))[::-1]
            sorted_fft = np.abs(data_fft_half)[indices]
            cumulative_sum = np.cumsum(sorted_fft)
            total_energy = cumulative_sum[-1]
            normalized_cumulative = cumulative_sum / total_energy
            freq_std_dev = np.sqrt(np.sum(normalized_cumulative * (freqs[indices] - np.mean(freqs[indices])) ** 2))
            freq_skewness = (np.sum((3 * normalized_cumulative - 2) * (freqs[indices] - np.mean(freqs[indices])) ** 3) /
                             np.sum((normalized_cumulative - 0.5) ** 2))

            # 将特征加入列表
            features_combined.append([
                mean_value, std_deviation, rms, kurt, skewness, crest_factor, form_factor, impulse_factor,
                peak_factor, centroid_freq, freq_variance, mean_freq, mean_square_freq, rms_freq, freq_std_dev,
                freq_skewness
            ])

        # 将列表转换为 NumPy 数组
        features_combined = np.vstack(features_combined)
        normalized_features = (features_combined - np.nanmin(features_combined, axis=0)) / (
                np.nanmax(features_combined, axis=0) - np.nanmin(features_combined, axis=0))

        # 计算每个特征与磨损度之间的皮尔逊和斯皮尔曼相关系数
        pearson_coeffs = []
        spearman_coeffs = []
        for i in range(normalized_features.shape[1]):
            pc, _ = pearsonr(normalized_features[:, i], ratios_list)
            sc, _ = spearmanr(normalized_features[:, i], ratios_list)
            pearson_coeffs.append(pc)
            spearman_coeffs.append(sc)

        # 创建一个 DataFrame 来存储相关系数和对应的特征名称
        corr_df = pd.DataFrame({
            'Feature': feature_names,
            'Pearson': pearson_coeffs,
            'Spearman': spearman_coeffs
        })

        # 为了确保横坐标标签显示完整，可以增加图形的宽度
        plt.figure(figsize=(15, 6))  # 增加宽度参数

        # 绘制皮尔逊和斯皮尔曼相关系数的条形图，并在每个条形上标注值
        for i, corr_type in enumerate(['Pearson', 'Spearman']):
            plt.subplot(1, 2, i + 1)
            sns.barplot(x='Feature', y=corr_type, data=corr_df)
            plt.title(f'{corr_type} Correlation Coefficients with Feature Names')

            # 调整横坐标标签的字体大小并旋转
            plt.xticks(rotation=45, fontsize=8)  # 减小字体大小

            # 在每个条形上标注相关系数的值
            for index, row in corr_df.iterrows():
                value = getattr(row, corr_type)
                plt.text(index, value, f'{value:.2f}', ha='center', va='bottom')

        # 保存图像
        plt.tight_layout()  # 自动调整子图参数以确保所有内容都可见
        plt.savefig(os.path.join(save_folder, f"{file_name[:-4]}_correlation_with_features.png"))
        plt.close()