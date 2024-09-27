from pydantic import BaseModel
from nonebot.plugin import PluginMetadata

from zhenxun.models.plugin_info import PluginInfo
from zhenxun.configs.path_config import IMAGE_PATH

SUPERUSER_HELP_IMAGE = IMAGE_PATH / "SUPERUSER_HELP.png"
if SUPERUSER_HELP_IMAGE.exists():
    SUPERUSER_HELP_IMAGE.unlink()


class PluginData(BaseModel):
    """
    插件信息
    """

    plugin: PluginInfo
    """插件信息"""
    metadata: PluginMetadata
    """元数据"""

    class Config:
        arbitrary_types_allowed = True
