import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import psutil
import ujson as json
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from nonebot.utils import run_sync

from configs.config import Config
from configs.path_config import (
    DATA_PATH,
    FONT_PATH,
    IMAGE_PATH,
    LOG_PATH,
    RECORD_PATH,
    TEMP_PATH,
    TEXT_PATH,
)

from .base_model import SystemFolderSize, SystemStatus, User

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login")

token_file = DATA_PATH / "web_ui" / "token.json"
token_file.parent.mkdir(parents=True, exist_ok=True)
token_data = {"token": []}
if token_file.exists():
    try:
        token_data = json.load(open(token_file, "r", encoding="utf8"))
    except json.JSONDecodeError:
        pass


def get_user(uname: str) -> Optional[User]:
    """获取账号密码

    参数:
        uname: uname

    返回:
        Optional[User]: 用户信息
    """
    username = Config.get_config("web-ui", "username")
    password = Config.get_config("web-ui", "password")
    if username and password and uname == username:
        return User(username=username, password=password)


def create_token(user: User, expires_delta: Optional[timedelta] = None):
    """创建token

    参数:
        user: 用户信息
        expires_delta: 过期时间.
    """
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    return jwt.encode(
        claims={"sub": user.username, "exp": expire},
        key=SECRET_KEY,
        algorithm=ALGORITHM,
    )


def authentication():
    """权限验证


    异常:
        JWTError: JWTError
        HTTPException: HTTPException
    """
    # if token not in token_data["token"]:
    def inner(token: str = Depends(oauth2_scheme)):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username, expire = payload.get("sub"), payload.get("exp")
            user = get_user(username)  # type: ignore
            if user is None:
                raise JWTError
        except JWTError:
            raise HTTPException(status_code=400, detail="登录验证失败或已失效, 踢出房间!")

    return Depends(inner)


def _get_dir_size(dir_path: Path) -> float:
    """
    说明:
        获取文件夹大小
    参数:
        :param dir_path: 文件夹路径
    """
    size = 0
    for root, dirs, files in os.walk(dir_path):
        size += sum([os.path.getsize(os.path.join(root, name)) for name in files])
    return size


@run_sync
def get_system_status() -> SystemStatus:
    """
    说明:
        获取系统信息等
    """
    cpu = psutil.cpu_percent()
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent
    return SystemStatus(
        cpu=cpu,
        memory=memory,
        disk=disk,
        check_time=datetime.now().replace(microsecond=0),
    )


@run_sync
def get_system_disk(
    full_path: Optional[str],
) -> List[SystemFolderSize]:
    """
    说明:
        获取资源文件大小等
    """
    base_path = Path(full_path) if full_path else Path()
    other_size = 0
    data_list = []
    for file in os.listdir(base_path):
        f = base_path / file
        if f.is_dir():
            size = _get_dir_size(f) / 1024 / 1024
            data_list.append(SystemFolderSize(name=file, size=size, full_path=str(f), is_dir=True))
        else:
            other_size += f.stat().st_size / 1024 / 1024
    if other_size:
        data_list.append(SystemFolderSize(name='other_file', size=other_size, full_path=full_path, is_dir=False))
    return data_list
    # else:
    #     if type_ == "image":
    #         dir_path = IMAGE_PATH
    #     elif type_ == "font":
    #         dir_path = FONT_PATH
    #     elif type_ == "text":
    #         dir_path = TEXT_PATH
    #     elif type_ == "record":
    #         dir_path = RECORD_PATH
    #     elif type_ == "data":
    #         dir_path = DATA_PATH
    #     elif type_ == "temp":
    #         dir_path = TEMP_PATH
    #     else:
    #         dir_path = LOG_PATH
    #     dir_map = {}
    #     other_file_size = 0
    #     for file in os.listdir(dir_path):
    #         file = Path(dir_path / file)
    #         if file.is_dir():
    #             dir_map[file.name] = _get_dir_size(file) / 1024 / 1024
    #         else:
    #             other_file_size += os.path.getsize(file) / 1024 / 1024
    #     dir_map["其他文件"] = other_file_size
    #     dir_map["check_time"] = datetime.now().replace(microsecond=0)
    #     return dir_map
