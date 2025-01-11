"""mi6500pro config flow."""

import datetime

import voluptuous as vol

from homeassistant import config_entries
import homeassistant.helpers.config_validation as cv

from .const import CONF_HOST, CONF_PASSWORD, CONF_SCAN_INTERVAL, DOMAIN

DEFAULT_SCAN_INTERVAL = datetime.timedelta(seconds=60).total_seconds()

DEVICE_TRACKER_SCHEMA = vol.Schema(
    {
        # 路由器IP地址配置项
        vol.Required(CONF_HOST): cv.string,
        # 路由器密码配置项
        vol.Required(CONF_PASSWORD): cv.string,
        vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(
            int, vol.Range(min=1)
        ),
    }
)


class mi6500proConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """mi6500pro config flow."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_PUSH

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        if user_input is not None:
            return self.async_create_entry(title=user_input[CONF_HOST], data=user_input)
        return self.async_show_form(
            step_id="user",
            data_schema=DEVICE_TRACKER_SCHEMA,
        )
