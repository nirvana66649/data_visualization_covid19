import pandas as pd
import numpy as np
import plotly.express as px
import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc

# Load the data
file_path = r"D:\数据可视化\数据\merged_province_data.csv"
df = pd.read_csv(file_path)

# Process the data
# Convert column names to readable dates
date_columns = [col for col in df.columns if col != 'Province']
time_points = sorted(
    list(set([col.split('_')[0] + '_' + col.split('_')[1] + '_' + col.split('_')[2] for col in date_columns])))

# Create dictionaries to map original columns to readable names
confirmed_cols = {date: f"{date}_Confirmed" for date in time_points}
death_cols = {date: f"{date}_Dead" for date in time_points}

# Prepare data for visualization
provinces = sorted(df['Province'].unique())

# Initialize the Dash app with a modern theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])

# Define custom styles
COLORS = {
    'background': '#f8f9fa',
    'text': '#343a40',
    'primary': '#2c3e50',
    'secondary': '#18bc9c',
    'light': '#ecf0f1',
    'dark': '#343a40',
    'border': '#dee2e6'
}

# Custom CSS
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>中国新冠疫情数据可视化</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                background-color: ''' + COLORS['background'] + ''';
                color: ''' + COLORS['text'] + ''';
                font-family: "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            }
            .card {
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                margin-bottom: 20px;
                transition: transform 0.3s ease;
            }
            .card:hover {
                transform: translateY(-5px);
            }
            .chart-card {
                background-color: white;
                padding: 15px;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            }
            .header {
                background: linear-gradient(135deg, #18bc9c 0%, #2c3e50 100%);
                color: white;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 30px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            }
            .control-panel {
                background-color: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                margin-bottom: 20px;
            }
            .table-container {
                background-color: white;
                padding: 15px;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            }
            .footer {
                text-align: center;
                padding: 20px;
                margin-top: 30px;
                color: ''' + COLORS['text'] + ''';
                font-size: 0.9rem;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
            <div class="footer">
                中国新冠疫情数据可视化 | 数据截至2022年12月
            </div>
        </footer>
    </body>
</html>
'''

# Define the layout with styled components
# Define the layout with styled components
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.Div([
            html.H1("中国新冠疫情数据可视化", className="text-center"),
            html.P("交互式仪表板 - 选择省份、图表类型和时间范围进行数据探索", className="text-center text-light")
        ], className="header"), width=12)
    ]),

    dbc.Row([
        dbc.Col([
            dbc.Row([
                dbc.Col(html.H1("中国新冠疫情数据可视化", className="text-center mt-4 mb-4"), width=12)
            ]),

            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H4("控制面板", className="mb-4 text-primary"),
                        dbc.Row([
                            dbc.Col([
                                html.H5("选择省份:", className="mb-2"),
                                dcc.Dropdown(
                                    id='province-dropdown',
                                    options=[{'label': province, 'value': province} for province in provinces],
                                    value=provinces[:5],  # Default to first 5 provinces
                                    multi=True,
                                    style={"borderRadius": "8px"}
                                ),
                            ], width=12, className="mb-4"),

                            dbc.Col([
                                html.H5("选择图表类型:", className="mb-2"),
                                dcc.RadioItems(
                                    id='chart-type',
                                    options=[
                                        {'label': '确诊病例折线图', 'value': 'line-confirmed'},
                                        {'label': '死亡病例折线图', 'value': 'line-dead'},
                                        {'label': '确诊病例柱状图', 'value': 'bar-confirmed'},
                                        {'label': '死亡病例柱状图', 'value': 'bar-dead'},
                                        {'label': '热力图 (所有省份)', 'value': 'heatmap'},
                                        {'label': '致死率分析', 'value': 'mortality-rate'},
                                        {'label': '增长率图', 'value': 'growth-rate'},
                                        {'label': '确诊/死亡散点图', 'value': 'scatter'},
                                        {'label': '数据占比饼图', 'value': 'pie'},
                                    ],
                                    value='line-confirmed',
                                    labelStyle={'display': 'block', 'margin': '8px 0', 'cursor': 'pointer'},
                                    inputStyle={"marginRight": "10px"},
                                    className="radio-items"
                                ),
                            ], width=12, className="mb-4"),

                            dbc.Col([
                                html.H5("选择时间范围:", className="mb-2"),
                                dcc.RangeSlider(
                                    id='time-slider',
                                    min=0,
                                    max=len(time_points) - 1,
                                    step=1,
                                    marks={i: {"label": time_points[i].replace('_', '/'),
                                               "style": {"transform": "rotate(45deg)", "white-space": "nowrap"}}
                                           for i in range(0, len(time_points), max(1, len(time_points) // 8))},
                                    value=[0, len(time_points) - 1],  # Default to all time points
                                    tooltip={"placement": "bottom", "always_visible": True}
                                ),
                            ], width=12),
                        ]),
                    ], className="control-panel"),
                ], width=12),
            ]),

            dbc.Row([
                dbc.Col([
                    html.Div([
                        dcc.Graph(id='covid-chart', style={"height": "600px"})
                    ], className="chart-card")
                ], width=12, className="mb-4"),
            ]),

            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H4("比较分析图表", className="mb-3 text-primary"),
                        dcc.Graph(id='additional-chart', style={"height": "500px"})
                    ], className="chart-card")
                ], width=12, className="mb-4"),
            ]),

            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H4("数据表格", className="mb-3 text-primary"),
                        html.Div(id='data-table')
                    ], className="table-container")
                ], width=12, className="mb-4"),
            ]),
        ], width=12)
    ])
], fluid=True)


# Define callback to update main chart
@app.callback(
    Output('covid-chart', 'figure'),
    [Input('province-dropdown', 'value'),
     Input('chart-type', 'value'),
     Input('time-slider', 'value')]
)
def update_chart(selected_provinces, chart_type, time_range):
    if not selected_provinces and chart_type != 'heatmap':
        return {}

    # Filter time points based on range slider
    selected_time_points = time_points[time_range[0]:time_range[1] + 1]

    # Special chart types
    if chart_type == 'heatmap':
        # Create heatmap for all provinces
        heatmap_data = []
        for _, row in df.iterrows():
            province = row['Province']
            for date in selected_time_points:
                heatmap_data.append({
                    'Province': province,
                    'Date': date.replace('_', '/'),
                    'Confirmed': row[confirmed_cols[date]],
                    'Dead': row[death_cols[date]]
                })

        df_heatmap = pd.DataFrame(heatmap_data)

        # Use log scale for better visualization
        df_heatmap['LogConfirmed'] = np.log1p(df_heatmap['Confirmed'])

        fig = px.imshow(
            df_heatmap.pivot(index='Province', columns='Date', values='LogConfirmed'),
            labels=dict(x="日期", y="省份", color="确诊病例数(对数)"),
            title="中国各省份新冠确诊病例热力图 (对数比例)",
            color_continuous_scale="Viridis"
        )
        fig.update_layout(height=800)
        return fig

    elif chart_type == 'mortality-rate':
        # Create mortality rate chart
        mortality_data = []
        for province in selected_provinces:
            province_data = df[df['Province'] == province]

            if len(province_data) > 0:
                for date in selected_time_points:
                    confirmed = province_data[confirmed_cols[date]].values[0]
                    deaths = province_data[death_cols[date]].values[0]

                    # Calculate mortality rate (avoid division by zero)
                    mortality_rate = (deaths / confirmed * 100) if confirmed > 0 else 0

                    mortality_data.append({
                        'Province': province,
                        'Date': date.replace('_', '/'),
                        'MortalityRate': mortality_rate
                    })

        df_mortality = pd.DataFrame(mortality_data)

        fig = px.line(
            df_mortality,
            x='Date',
            y='MortalityRate',
            color='Province',
            title="中国各省份新冠致死率变化趋势 (%)",
            labels={'MortalityRate': '致死率 (%)', 'Date': '日期', 'Province': '省份'}
        )

        fig.update_layout(
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=40, r=40, t=60, b=60)
        )

        return fig

    elif chart_type == 'growth-rate':
        # Create growth rate chart
        growth_data = []

        for province in selected_provinces:
            province_data = df[df['Province'] == province]

            if len(province_data) > 0:
                # Get confirmed cases for each date
                confirmed_values = [province_data[confirmed_cols[date]].values[0] for date in selected_time_points]

                # Calculate growth rates
                for i in range(1, len(confirmed_values)):
                    prev_value = confirmed_values[i - 1]
                    curr_value = confirmed_values[i]

                    # Calculate percentage growth
                    growth_pct = ((curr_value - prev_value) / prev_value * 100) if prev_value > 0 else 0

                    growth_data.append({
                        'Province': province,
                        'Date': selected_time_points[i].replace('_', '/'),
                        'GrowthRate': growth_pct
                    })

        df_growth = pd.DataFrame(growth_data)

        fig = px.bar(
            df_growth,
            x='Date',
            y='GrowthRate',
            color='Province',
            title="中国各省份新冠确诊病例增长率 (%)",
            labels={'GrowthRate': '增长率 (%)', 'Date': '日期', 'Province': '省份'},
            barmode='group'
        )

        fig.update_layout(
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=40, r=40, t=60, b=60)
        )

        return fig

    elif chart_type == 'scatter':
        # Create scatter plot of confirmed vs deaths
        scatter_data = []

        for province in selected_provinces:
            province_data = df[df['Province'] == province]

            if len(province_data) > 0:
                for date in selected_time_points:
                    confirmed = province_data[confirmed_cols[date]].values[0]
                    deaths = province_data[death_cols[date]].values[0]

                    scatter_data.append({
                        'Province': province,
                        'Date': date.replace('_', '/'),
                        'Confirmed': confirmed,
                        'Deaths': deaths
                    })

        df_scatter = pd.DataFrame(scatter_data)

        fig = px.scatter(
            df_scatter,
            x='Confirmed',
            y='Deaths',
            color='Province',
            size='Confirmed',
            hover_data=['Date'],
            title="确诊病例数与死亡病例数相关性分析",
            labels={'Confirmed': '确诊病例数', 'Deaths': '死亡病例数', 'Province': '省份'},
            log_x=True  # 使用对数刻度以便更好地显示小值和大值
        )

        # Add a trend line
        fig.update_layout(
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=40, r=40, t=60, b=60)
        )

        return fig

    elif chart_type == 'pie':
        # Create pie chart for last selected time point
        last_time_point = selected_time_points[-1]

        pie_data = []
        for province in selected_provinces:
            province_data = df[df['Province'] == province]

            if len(province_data) > 0:
                confirmed = province_data[confirmed_cols[last_time_point]].values[0]

                pie_data.append({
                    'Province': province,
                    'Confirmed': confirmed
                })

        df_pie = pd.DataFrame(pie_data)

        # Sort by value
        df_pie = df_pie.sort_values('Confirmed', ascending=False)

        # If too many provinces, keep top 10 and group others
        if len(df_pie) > 10:
            top_n = df_pie.head(10)
            others = pd.DataFrame([{
                'Province': '其他省份',
                'Confirmed': df_pie.iloc[10:]['Confirmed'].sum()
            }])
            df_pie = pd.concat([top_n, others], ignore_index=True)

        fig = px.pie(
            df_pie,
            values='Confirmed',
            names='Province',
            title=f"{last_time_point.replace('_', '/')} 确诊病例省份分布",
            hole=0.3  # Make it a donut chart
        )

        return fig

    # Regular chart types
    chart_data = []

    for province in selected_provinces:
        province_data = df[df['Province'] == province]

        if 'confirmed' in chart_type:
            data_type = 'confirmed'
            y_title = '确诊病例数'
            columns = [confirmed_cols[date] for date in selected_time_points]
        else:  # 'dead'
            data_type = 'dead'
            y_title = '死亡病例数'
            columns = [death_cols[date] for date in selected_time_points]

        if len(province_data) > 0:
            row_data = province_data[['Province'] + columns].iloc[0]

            for date, col in zip(selected_time_points, columns):
                chart_data.append({
                    'Province': row_data['Province'],
                    'Date': date.replace('_', '/'),
                    'Value': row_data[col]
                })

    df_plot = pd.DataFrame(chart_data)

    # Create the plot
    if 'line' in chart_type:
        fig = px.line(
            df_plot,
            x='Date',
            y='Value',
            color='Province',
            title=f'中国各省份 {y_title} 趋势图',
            labels={'Value': y_title, 'Date': '日期', 'Province': '省份'}
        )
    else:  # 'bar'
        fig = px.bar(
            df_plot,
            x='Date',
            y='Value',
            color='Province',
            barmode='group',
            title=f'中国各省份 {y_title} 对比图',
            labels={'Value': y_title, 'Date': '日期', 'Province': '省份'}
        )

    # Update layout
    fig.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=60, b=60)
    )

    return fig


# Define callback for additional chart
@app.callback(
    Output('additional-chart', 'figure'),
    [Input('province-dropdown', 'value'),
     Input('time-slider', 'value')]
)
def update_additional_chart(selected_provinces, time_range):
    if not selected_provinces:
        return {}

    # Filter time points based on range slider
    selected_time_points = time_points[time_range[0]:time_range[1] + 1]
    first_time = selected_time_points[0]
    last_time = selected_time_points[-1]

    # Prepare data for visualization - comparing first and last time point
    comparison_data = []

    for province in selected_provinces:
        province_data = df[df['Province'] == province]

        if len(province_data) > 0:
            first_confirmed = province_data[confirmed_cols[first_time]].values[0]
            last_confirmed = province_data[confirmed_cols[last_time]].values[0]

            # Calculate percentage change
            pct_change = ((last_confirmed - first_confirmed) / first_confirmed * 100) if first_confirmed > 0 else 0

            comparison_data.append({
                'Province': province,
                'FirstConfirmed': first_confirmed,
                'LastConfirmed': last_confirmed,
                'PercentageChange': pct_change
            })

    df_comparison = pd.DataFrame(comparison_data)

    # Sort by percentage change
    df_comparison = df_comparison.sort_values('PercentageChange', ascending=False)

    # Create the bar chart
    fig = px.bar(
        df_comparison,
        x='Province',
        y='PercentageChange',
        title=f"各省份确诊病例从 {first_time.replace('_', '/')} 到 {last_time.replace('_', '/')} 的增长百分比",
        labels={'PercentageChange': '增长百分比 (%)', 'Province': '省份'},
        text='PercentageChange',
        color='PercentageChange',
        color_continuous_scale='RdYlGn_r'  # Red for high values, green for low
    )

    # Format percentage labels
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')

    # Update layout
    fig.update_layout(
        xaxis={'categoryorder': 'total descending'},
        margin=dict(l=40, r=40, t=60, b=60)
    )

    return fig


# Define callback to update data table
@app.callback(
    Output('data-table', 'children'),
    [Input('province-dropdown', 'value'),
     Input('time-slider', 'value')]
)
def update_table(selected_provinces, time_range):
    if not selected_provinces:
        return html.Div("请选择至少一个省份")

    # Filter time points based on range slider
    selected_time_points = time_points[time_range[0]:time_range[1] + 1]

    # Get columns for both confirmed and dead
    confirmed_columns = [confirmed_cols[date] for date in selected_time_points]
    death_columns = [death_cols[date] for date in selected_time_points]

    # Filter dataframe
    filtered_df = df[df['Province'].isin(selected_provinces)][['Province'] + confirmed_columns + death_columns]

    # Create table
    table_header = [
        html.Thead(html.Tr([html.Th("省份")] +
                           [html.Th(f"{date.replace('_', '/')} 确诊") for date in selected_time_points] +
                           [html.Th(f"{date.replace('_', '/')} 死亡") for date in selected_time_points]))
    ]

    rows = []
    for _, row in filtered_df.iterrows():
        province_row = [html.Td(row['Province'])]
        for col in confirmed_columns:
            province_row.append(html.Td(row[col]))
        for col in death_columns:
            province_row.append(html.Td(row[col]))
        rows.append(html.Tr(province_row))

    table_body = [html.Tbody(rows)]

    return dbc.Table(table_header + table_body, bordered=True, striped=True, hover=True, responsive=True)


if __name__ == '__main__':
    app.run(debug=True)
