#!/usr/bin/env python 
# -*- coding:utf-8 -*-
"""
A component which allows you to parse maoyan site get movie rank info

For more details about this component, please refer to the documentation at
https://github.com/zrincet/movie_box-office_query/

"""
import logging
import asyncio
import voluptuous as vol
from datetime import timedelta
from homeassistant.helpers.entity import Entity
import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import (PLATFORM_SCHEMA)
from requests import request
from requests.exceptions import (
    ConnectionError as ConnectError, HTTPError, Timeout)
from bs4 import BeautifulSoup
import json

__version__ = '0.1.0'
_LOGGER = logging.getLogger(__name__)

REQUIREMENTS = ['requests', 'beautifulsoup4']

COMPONENT_REPO = 'https://github.com/zrincet/movie_box-office_query/'
SCAN_INTERVAL = timedelta(seconds=120)
CONF_OPTIONS = "options"
CONF_NUM = 'movie_num'
ATTR_UPDATE_TIME = "更新时间"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_NUM, default=20): cv.string,
    #vol.Required(CONF_OPTIONS, default=[]): vol.All(cv.ensure_list, [vol.In(OPTIONS)]),
})


@asyncio.coroutine
def async_setup_platform(hass, config, async_add_devices, discovery_info=None):
    _LOGGER.info("async_setup_platform sensor movie_box-office_query")
    dev = []
    #for option in config[CONF_OPTIONS]:
    dev.append(MovieBoxOfficeSensor(config[CONF_NUM]))

    async_add_devices(dev, True)


class MovieBoxOfficeSensor(Entity):
    def __init__(self, movie_num):
        self._movieNum = int(movie_num)
        self._state = None

        self._ele = None
        self._price = None
        self._updateTime = None
        self._roomName = None
        self._entries = []

        self._object_id = 'movie_box_office'
        self._friendly_name = '票房大盘'
        self._icon = 'mdi:movie-roll'
        self._unit_of_measurement = None

        self._showCountDesc = None
        self._viewCountDesc = None
        #self._type = option

    def update(self):
        import time
        _LOGGER.info("MovieBoxOfficeSensor start updating data.")
        self._entries.clear()
        header = {
            'Content-Type': 'application/json; charset=utf-8',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; MI 8 UD Build/QKQ1.190828.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/67.0.3396.87 XWEB/1179 MMWEBSDK/200201 Mobile Safari/537.36 MMWEBID/9993 MicroMessenger/7.0.12.1620(0x27000C35) Process/tools NetType/WIFI Language/zh_CN ABI/arm64'
        }
        url = 'https://piaofang.maoyan.com/dashboard-ajax?orderType=0&riskLevel=71&optimusCode=10'
        url_detail = 'https://piaofang.maoyan.com/dashboard/ajax-moviedetail'
        try:
            response = request('GET', url, headers=header)
            response.encoding = 'utf-8'
            re_json = json.loads(response.text)
        except (ConnectError, HTTPError, Timeout, ValueError) as error:
            time.sleep(0.01)
            _LOGGER.error("Unable to connect to maoyan site. %s", error)

        try:
            import time
            time_stamp = re_json['movieList']['data']['updateInfo']['updateTimestamp'] / 1000
            time_array = time.localtime(time_stamp)
            self._updateTime = time.strftime("%Y-%m-%d %H:%M:%S", time_array)
            tmp_date = time.strftime("%Y%m%d", time_array)

            movie_list = re_json['movieList']['data']['list']
            tmp_num = 0
            if len(list(movie_list)) > self._movieNum:
                tmp_num = self._movieNum
            else:
                tmp_num = len(list(movie_list))
            for i in range(0, tmp_num):
                movie_info = {}
                movie_info['name'] = movie_list[i]['movieInfo']['movieName']
                movie_info['boxUnit'] = float(movie_list[i]['boxSplitUnit']['num'])
                movie_info['boxRate'] = movie_list[i]['boxRate']
                movie_info['showCount'] = movie_list[i]['showCount']
                movie_info['showCountRate'] = movie_list[i]['showCountRate']
                movie_info['avgShowView'] = int(movie_list[i]['avgShowView'])
                movie_info['avgSeatView'] = movie_list[i]['avgSeatView']
                movie_info['sumBoxDesc'] = movie_list[i]['sumBoxDesc']

                data = {'showDate': tmp_date, 'movieId': movie_list[i]['movieInfo']['movieId']}
                try:
                    response = request('GET', url_detail, headers=header, params=data)
                    response.encoding = 'utf-8'
                    movie_info_detail_json = json.loads(response.text)
                    movie_info['imgUrl'] = str(movie_info_detail_json['movieInfo']['imgUrl']).replace('w.h/', '')
                except Exception as e:
                    _LOGGER.error("Something wrong in movie box-office. with get imgUrl %s", e)

                self._entries.append(movie_info)

            self._showCountDesc = re_json['movieList']['data']['nationBoxInfo']['showCountDesc']
            self._viewCountDesc = re_json['movieList']['data']['nationBoxInfo']['viewCountDesc']

            self._state = re_json['movieList']['data']['nationBoxInfo']['nationBoxSplitUnit']['num']
            self._unit_of_measurement = re_json['movieList']['data']['nationBoxInfo']['nationBoxSplitUnit']['unit']
        except Exception as e:
            _LOGGER.error("Something wrong in movie box-office. %s", e)

    @property
    def name(self):
        return self._friendly_name

    @property
    def state(self):
        return self._state

    @property
    def icon(self):
        return self._icon
    @property
    def unique_id(self):
        return self._object_id

    @property
    def unit_of_measurement(self):
        return self._unit_of_measurement

    @property
    def device_state_attributes(self):
        return {
            '总场次': self._showCountDesc,
            '总出票': self._viewCountDesc,
            'entries': self._entries,
            ATTR_UPDATE_TIME: self._updateTime,
        }
