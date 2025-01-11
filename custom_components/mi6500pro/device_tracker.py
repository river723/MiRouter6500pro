"""自定义设备跟踪器组件，用于获取路由器连接的设备信息."""

import datetime
import json
import logging

import aiohttp
import voluptuous as vol

# from homeassistant.components.device_tracker import (
#     CONF_SCAN_INTERVAL,
#     PLATFORM_SCHEMA as DEVICE_TRACKER_PLATFORM_SCHEMA,
# )
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.util import Throttle

from .encrypt import Encrypt

_LOGGER = logging.getLogger(__name__)
# 定义扫描间隔（单位：秒），这里设为60秒，可根据实际调整
DEFAULT_SCAN_INTERVAL = datetime.timedelta(seconds=60)


class RouterDeviceScanner:
    """代表路由器设备扫描器的类，用于获取连接设备信息."""

    def __init__(self, host: str, username: str, password: str, see):
        """初始化相关属性."""
        _LOGGER.debug("初始化 RouterDeviceScanner")
        self.host = host
        self.username = username
        self.password = password
        self.encryptor = Encrypt()
        # 初始化时可以创建Encrypt对象，避免在get_param每次重新创建
        self.param_cache = None
        self.stok = None
        self.see = see
        self.devices = []
        self.last_results = {}

    def _get_param(self):
        if not self.param_cache:
            nonce = self.encryptor.init()
            old_pwd = self.encryptor.old_pwd(self.password)
            self.param_cache = {
                "username": self.username,
                "password": old_pwd,
                "logtype": 2,
                "nonce": nonce,
            }
        return self.param_cache

    async def _get_stok(self, session):
        param = self._get_param()
        loginurl = f"http://{self.host}/cgi-bin/luci/api/xqsystem/login"

        async with session.post(loginurl, data=param) as rsp:
            if rsp.status == 200:
                response_json = json.loads(await rsp.text())
                if response_json.get("code") == 401:
                    _LOGGER.error("登录路由器失败，用户名或密码错误")
                self.stok = response_json.get("token")
            else:
                _LOGGER.error("登录路由器获取 token 失败，状态码: %s", rsp.status)

    def format_time_interval(self, seconds):
        """格式化时间间隔."""
        days, remainder = divmod(seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)

        time_parts = []
        if days > 0:
            time_parts.append(f"{days}天")
        if hours > 0:
            time_parts.append(f"{hours}小时")
        if minutes > 0:
            time_parts.append(f"{minutes}分")
        if seconds > 0 or not time_parts:
            time_parts.append(f"{seconds}秒")

        return " ".join(time_parts)

    async def async_get_device_info(self):
        """异步获取设备详细信息（MAC、IP、名称）."""
        device_info = []

        try:
            async with aiohttp.ClientSession() as session:
                # 这里需要替换为路由器真实的获取设备信息的API地址，假设为 /api/connected_devices_info
                # stok = await self._get_stok(session)
                if self.stok is None:
                    await self._get_stok(session)
                else:
                    url = f"http://{self.host}/cgi-bin/luci/;stok={self.stok}/api/misystem/devicelist?mlo=1"
                    async with session.get(url) as response:
                        if response.status == 200:
                            data = json.loads(await response.text())
                            if "msg" in data and data["msg"] == "Invalid token":
                                _LOGGER.error("获取设备信息失败,token 失效")
                                await self._get_stok(session)
                            else:
                                _LOGGER.debug("获取设备信息成功")
                                device_list = [
                                    device
                                    for device in data["list"]
                                    if device["type"] != 0
                                ]
                                for device in device_list:
                                    mac_address = device["mac"]
                                    ip_address = device["ip"][0]["ip"]
                                    online_duration = int(device["ip"][0]["online"])
                                    device_name = device["name"]
                                    is_online = device["online"]
                                    device_info.append(
                                        {
                                            "mac": mac_address,
                                            "ip": ip_address,
                                            "name": device_name,
                                            "online": is_online,
                                            "online_duration": self.format_time_interval(
                                                online_duration
                                            ),
                                        }
                                    )
                        else:
                            _LOGGER.error(
                                "获取设备信息失败，状态码: %s", response.status
                            )
        except aiohttp.ClientError as e:
            _LOGGER.error("请求出现异常: %s", e)
        return device_info

    @Throttle(DEFAULT_SCAN_INTERVAL)
    async def async_update_info(self):
        """异步更新设备信息，调用获取设备信息方法并保存结果."""
        self.devices = await self.async_get_device_info()
        self.last_results = {device["mac"]: device for device in self.devices}
        for device in self.devices:
            await self.see(
                mac=device["mac"],
                dev_id=device["mac"].replace(":", "_"),
                host_name=device.get("name", "Unknown Device"),
                source_type="router",
                attributes={
                    "friendly_name": device["name"],
                    "online": device["online"],
                    "ip": device["ip"],
                    "online_duration": device["online_duration"],
                },
            )
