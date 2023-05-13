from typing import List, Optional

from tortoise import fields
from tortoise.contrib.postgres.functions import Random

from services.db_context import Model


class OpenCasesLog(Model):

    id = fields.IntField(pk=True, generated=True, auto_increment=True)
    """自增id"""
    user_qq = fields.BigIntField()
    """用户id"""
    group_id = fields.BigIntField()
    """群聊id"""
    case_name = fields.CharField(255)
    """箱子名称"""
    name = fields.CharField(255)
    """武器/手套/刀名称"""
    skin_name = fields.CharField(255)
    """皮肤名称"""
    is_stattrak = fields.BooleanField(default=False)
    """是否暗金(计数)"""
    abrasion = fields.CharField(255)
    """磨损度"""
    abrasion_value = fields.FloatField()
    """磨损数值"""
    color = fields.CharField(255)
    """颜色(品质)"""
    price = fields.FloatField(default=0)
    """价格"""
    create_time = fields.DatetimeField(auto_add_now=True)
    """创建日期"""

    class Meta:
        table = "open_cases_log"
        table_description = "开箱日志表"
