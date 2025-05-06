import matplotlib

matplotlib.use('TkAgg')  # 使用 TkAgg 后端以启用交互功能

import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import mplcursors
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
import numpy as np

# 中文支持设置
plt.rcParams['font.sans-serif'] = ['SimHei']  # 中文字体
plt.rcParams['axes.unicode_minus'] = False  # 正确显示负号

# 加载 shapefile 地图数据
shp_path = "D:\\数据可视化\\china_SHP\\省界_Project.shp"
china_map = gpd.read_file(shp_path)

# 加载 COVID-19 数据
covid_data_path = "D:\\数据可视化\\数据\\20221229_clustered.csv"
df_covid = pd.read_csv(covid_data_path)

# 映射省份名以匹配地图数据中的名称
province_mapping_full = {
    '北京': '北京市', '上海': '上海市', '广东': '广东省', '江苏': '江苏省', '浙江': '浙江省', '四川': '四川省',
    '海南': '海南省', '贵州': '贵州省', '甘肃': '甘肃省', '青海': '青海省', '宁夏': '宁夏回族自治区',
    '新疆': '新疆维吾尔自治区', '湖北': '湖北省', '福建': '福建省', '山东': '山东省', '河南': '河南省',
    '湖南': '湖南省', '安徽': '安徽省', '河北': '河北省', '辽宁': '辽宁省', '江西': '江西省', '重庆': '重庆市',
    '云南': '云南省', '广西': '广西壮族自治区', '山西': '山西省', '内蒙古': '内蒙古自治区', '黑龙江': '黑龙江省',
    '吉林': '吉林省', '天津': '天津市', '西藏': '西藏自治区', '陕西': '陕西省', '香港': '香港特别行政区',
    '澳门': '澳门特别行政区', '台湾': '台湾省'
}

# 映射数据中的省份名称为全称
df_covid['province'] = df_covid['Province'].map(province_mapping_full)

# 重命名地图数据的省份列名以便合并
china_map.rename(columns={'NAME': 'province'}, inplace=True)

# 合并地图和疫情数据
merged = china_map.set_index('province').join(df_covid.set_index('province'))
merged.reset_index(inplace=True)  # 重置索引以便后续访问

# 创建图形
fig, ax = plt.subplots(1, 1, figsize=(12, 10))

# 绘制基础地图
patches = []
for idx, geom in enumerate(merged.geometry):
    if geom.geom_type == 'Polygon':
        patches.append(Polygon(np.array(geom.exterior.coords)))
    elif geom.geom_type == 'MultiPolygon':
        for poly in geom.geoms:
            patches.append(Polygon(np.array(poly.exterior.coords)))

# 创建颜色映射
colors = plt.cm.Reds(np.linspace(0.3, 1, len(merged['Cluster'].unique())))
color_dict = {k: colors[i] for i, k in enumerate(sorted(merged['Cluster'].unique()))}

# 绘制省份
pc = PatchCollection(patches, edgecolor='black', linewidth=0.8)
pc.set_array(np.array(merged['Cluster']))
pc.set_cmap('Reds')
ax.add_collection(pc)

# 添加颜色条
cbar = plt.colorbar(pc, ax=ax)
cbar.set_label('风险等级')

# 准备悬停数据
hover_data = []
for idx, row in merged.iterrows():
    hover_data.append({
        'province': row['province'],
        'confirmed': row['Confirmed'],
        'cured': row['Cured'],
        'dead': row['Dead'],
        'cluster': row['Cluster']
    })

# 设置悬停交互
cursor = mplcursors.cursor(pc, hover=True)
highlight = None


@cursor.connect("add")
def on_hover(sel):
    global highlight

    idx = sel.index[0]  # 修复关键点：取元组第一个元素作为索引

    data = hover_data[idx]

    sel.annotation.set_text(
        f"省份: {data['province']}\n"
        f"确诊: {data['confirmed']}\n"
        f"治愈: {data['cured']}\n"
        f"死亡: {data['dead']}\n"
        f"风险等级: {data['cluster']}"
    )

    sel.annotation.get_bbox_patch().set(
        boxstyle="round,pad=0.5",
        fc="lightyellow",
        alpha=0.9
    )

    if highlight is not None:
        highlight.remove()

    geom = merged.geometry.iloc[idx]
    if geom.geom_type == 'Polygon':
        highlight_poly = Polygon(np.array(geom.exterior.coords), fill=False, edgecolor='blue', linewidth=2)
        highlight = ax.add_patch(highlight_poly)
    else:  # MultiPolygon
        polys = [Polygon(np.array(poly.exterior.coords)) for poly in geom.geoms]
        highlight_poly = PatchCollection(polys, facecolor='none', edgecolor='blue', linewidth=2)
        highlight = ax.add_collection(highlight_poly)

    fig.canvas.draw_idle()


# 添加图表标题与美化
ax.set_title("中国各省市COVID-19疫情风险聚类", fontsize=18, pad=20)
ax.autoscale_view()
ax.set_axis_off()
plt.tight_layout()
plt.show()
