# movie_box-office_query
 with Home Assistant， 利用maoyan的api，获取当前中国大陆电影票房实时大盘数据
 
 ## install
 在 custom_components/ 文件夹下建立文件夹 movie_box-office_query/ ,将 __init__.py manifest.json sensor.py 放入 movie_box-office_query/ 中  
 在 /config/configuration.yaml 中添加以下语句  
```yaml
  - platform: movie_box-office_query
    movie_num: 15
```
注意：movie_num为将要储存的电影数量，无此参数时默认为20部，如数量超过数据源全部数据的长度，则按照数据源实际的数量储存  
## How to use
利用list-card，显示电影数量
在Lovelace配置中
```yaml
columns:
  - add_link: imgUrl
    field: imgUrl
    title: ''
    type: image
  - field: name
    style:
      - height: 30px
    title: 电影名称
  - field: boxUnit
    title: 实时票房
  - field: boxRate
    title: 票房占比
  - field: showCount
    title: 场次
  - field: showCountRate
    title: 排片占比
  - field: avgShowView
    title: 场均人数
  - field: avgSeatView
    title: 上座率
  - field: sumBoxDesc
    title: 总票房
entity: sensor.piao_fang_da_pan
feed_attribute: entries
title: 电影票房大盘
type: 'custom:list-card'
```
即可展现储存的电影所有属性，可以自由选择要显示的属性
![](https://hozoy-1251133838.cos.ap-shanghai.myqcloud.com/20200722163341.png)
