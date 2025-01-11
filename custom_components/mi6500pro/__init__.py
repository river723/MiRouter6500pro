"""初始化 Mi6500Pro 组件."""

import datetime
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_time_interval

from .const import DOMAIN
from .device_tracker import RouterDeviceScanner

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """通过 Config Flow 设置设备跟踪器."""

    _LOGGER.debug("开始初始化 Mi6500Pro")
    config = entry.data  # 获取 Config Flow 中的配置数据
    host = config["host"]
    password = config["password"]
    scan_interval = config["scan_interval"]

    # 定义 see 回调函数
    async def see(mac, dev_id, host_name, source_type, attributes):
        hass.states.async_set(
            f"device_tracker.{dev_id}",  # 实体 ID
            host_name,  # 设备名称
            attributes,  # 设备属性
        )

    # 初始化设备扫描器
    scanner = RouterDeviceScanner(host, "admin", password, see)
    _LOGGER.debug("初始化 RouterDeviceScanner 完成")

    # 启动定期更新设备信息的任务
    async def _update(_):
        _LOGGER.debug("开始更新设备信息")
        await scanner.async_update_info()

    scan_interval = datetime.timedelta(seconds=60)  # 扫描间隔
    async_track_time_interval(hass, _update, scan_interval)

    # 将设备扫描器添加到 hass 数据中，以便其他组件使用
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = scanner

    # 返回 True 表示初始化成功
    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    """卸载配置条目."""
    hass.data[DOMAIN].pop(config_entry.entry_id)
    return True
