from pydantic import BaseModel, Extra
from nonebot import get_driver, logger
from pathlib import Path


class PluginConfig(BaseModel, extra=Extra.ignore):
    image_path: Path = Path(__file__).parent / "resource"


config = get_driver().config.dict()
image_config: PluginConfig = PluginConfig.parse_obj(config)

if 'group_id_on' not in config:
    logger.warning('未发现配置项 `group_id_on` , 采用默认值: []')

group_id_on = config.get('group_id_on', [])
