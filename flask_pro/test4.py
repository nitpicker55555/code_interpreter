# -*- coding: utf-8 -*-
from flask import Flask, render_template
import folium

app = Flask(__name__)


@app.route('/')
def index():
    start_coords = (46.9540700, 142.7360300)
    folium_map = folium.Map(location=start_coords, zoom_start=14)

    # 用于跟踪tooltip信息的列表
    tooltips_info = []

    # 添加第一个marker和tooltip
    folium.Marker([46.9540700, 142.7360300],
                  tooltip='Tooltip 类型A',
                  popup='Popup A').add_to(folium_map)
    tooltips_info.append('类型A')

    # 添加第二个marker和tooltip
    folium.Marker([46.9580700, 142.7360300],
                  tooltip='Tooltip 类型B',
                  popup='Popup B').add_to(folium_map)
    tooltips_info.append('类型B')

    # 确保没有重复的tooltip类型
    unique_tooltips = list(set(tooltips_info))

    map_html = folium_map._repr_html_()

    # 传递地图HTML和tooltip类型信息给模板
    return render_template("index2.html", map_html=map_html, tooltips=unique_tooltips)


if __name__ == '__main__':
    app.run(debug=True)
