import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. 解决PyCharm显示问题
try:
    import matplotlib

    matplotlib.use('TkAgg')  # 使用TkAgg后端替代PyCharm默认后端
except ImportError:
    pass

# 2. 设置中文显示和字体问题
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']  # 添加备用字体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 3. 读取数据
path = r"D:\数据可视化\工作簿1.xlsx"
# 读取数据（这里假设数据已经在剪贴板中）
df = pd.read_excel(path)

# 4. 修正列名拼写错误
df = df.rename(columns={'2020_10_19_Deadarte': '2020_10_19_Deadrate'})

# 5. 提取日期列
date_columns = [col for col in df.columns if col.endswith('Confirmed')]

# 6. 创建死亡率数据框
mortality_df = pd.DataFrame()

for date_col in date_columns:
    date_str = '_'.join(date_col.split('_')[:3])
    rate_col = date_col.replace('Confirmed', 'Deadrate')

    if rate_col not in df.columns:
        print(f"警告：列 {rate_col} 不存在，跳过")
        continue

    temp_df = pd.DataFrame({
        'Date': pd.to_datetime(date_str, format='%Y_%m_%d'),
        'Province': df['Province'],
        'Mortality Rate': df[rate_col]
    })
    mortality_df = pd.concat([mortality_df, temp_df])

# 7. 数据处理
mortality_df = mortality_df.dropna()

# 8. 可视化
plt.figure(figsize=(14, 8))

# 选择变化较大的前10个省份
top_provinces = mortality_df.groupby('Province')['Mortality Rate'].max().nlargest(10).index

for province in top_provinces:
    province_data = mortality_df[mortality_df['Province'] == province]
    plt.plot(province_data['Date'], province_data['Mortality Rate'],
             marker='o', label=province, linewidth=2)

plt.title('各省份COVID-19死亡率随时间变化趋势', fontsize=16)
plt.xlabel('日期', fontsize=14)
plt.ylabel('死亡率', fontsize=14)
plt.xticks(rotation=45)
plt.yscale('log')
plt.grid(True, which="both", ls="--")
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()

# 9. 保存图像和显示
plt.savefig('mortality_rate_trend.png', dpi=300, bbox_inches='tight')
plt.show()