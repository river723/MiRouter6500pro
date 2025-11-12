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
    async def see(mac, dev_id, host_name, source_type,attributes):
        """设备跟踪器 see 回调函数"""
          # 确定设备状态
        online = attributes.get("online", 0) if attributes else 0
        ip= attributes.get("ip", "") if attributes else ""
        
        state = "home" if online == 1 else "not_home"
        # 构建完整的属性字典
        full_attributes = {
            "friendly_name": host_name,
            # "mac": mac,
            # "source_type": "router"
            "online": online,
            "ip": ip,
            "unique_id": dev_id,
            "online_duration": attributes.get("online_duration", "") if attributes else ""
        }
        
        # 合并传入的属性
        if attributes and isinstance(attributes, dict):
            full_attributes.update(attributes)
            
        hass.states.async_set(
            f"device_tracker.{dev_id}",  # 实体 ID
            state,  # 设备状态（主机名）
            full_attributes  # 设备属性
        )


    # 初始化设备扫描器
    scanner = RouterDeviceScanner(host, "admin", password, see)
    _LOGGER.debug("初始化 RouterDeviceScanner 完成")

    # 启动定期更新设备信息的任务
    async def _update(_):
        _LOGGER.debug("开始更新设备信息")
        await scanner.async_update_info()

    scan_interval = datetime.timedelta(seconds=20)  # 扫描间隔
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
