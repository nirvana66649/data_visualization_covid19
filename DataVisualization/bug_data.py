# import pandas as pd
# import os
#
# # 确保保存目录存在（自动创建）
# save_path = r'D:\数据可视化'
# os.makedirs(save_path, exist_ok=True)
#
# # 读取 CSV 文件
# df = pd.read_csv(r"D:\Download\DXYArea.csv")
#
# # 过滤出 countryName 是 “中国” 的行
# china_df = df[df['countryName'] == '中国']
#
# # 显示前几行
# print(china_df[['continentName', 'countryName', 'provinceName', 'cityName',
#                 'province_confirmedCount', 'province_curedCount', 'province_deadCount', 'updateTime']].head())
#
# # 保存为新文件
# china_df.to_csv(os.path.join(save_path, "china_data.csv"), index=False, encoding='utf_8_sig')
# print("文件已保存到:", os.path.join(save_path, "china_data.csv"))

import pandas as pd

# 原始文件路径
input_path = r"D:\Download\20221229.csv"

# 输出文件路径
output_path = r"D:\数据可视化\数据\20221229.csv"

# 读取 CSV 文件
df = pd.read_csv(input_path)

# 过滤出中国的数据
china_df = df[df['countryName'] == '中国']

# 只保留指定列，并去重（同一省份可能会因为不同城市多次出现）
province_df = china_df[['provinceName', 'province_confirmedCount', 'province_curedCount', 'province_deadCount', 'updateTime']]
province_df = province_df.drop_duplicates(subset=['provinceName'])

# 保存到新文件
province_df.to_csv(output_path, index=False, encoding='utf_8_sig')

print("保存成功，路径：", output_path)
