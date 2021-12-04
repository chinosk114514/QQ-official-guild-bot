import requests
import json
from . import structs
import typing as t


class ColorfulPrint:
    class Style:
        DEFAULT = 0
        BOLD = 1
        ITALIC = 3
        UNDERLINE = 4
        ANTIWHITE = 7

    class Color:
        DEFAULT = 39
        BLACK = 30
        RED = 31
        GREEN = 32
        YELLOW = 33
        BLUE = 34
        PURPLE = 35
        CYAN = 36
        WHITE = 37
        LIGHTBLACK_EX = 90
        LIGHTRED_EX = 91
        LIGHTGREEN_EX = 92
        LIGHTYELLOW_EX = 93
        LIGHTBLUE_EX = 94
        LIGHTMAGENTA_EX = 95
        LIGHTCYAN_EX = 96
        LIGHTWHITE_EX = 97

    class BGColor:
        DEFAULT = 49
        BLACK = 40
        RED = 41
        GREEN = 42
        YELLOW = 43
        BLUE = 44
        PURPLE = 45
        CYAN = 46
        WHITE = 47
        LIGHTBLACK_EX = 100
        LIGHTRED_EX = 101
        LIGHTGREEN_EX = 102
        LIGHTYELLOW_EX = 103
        LIGHTBLUE_EX = 104
        LIGHTMAGENTA_EX = 105
        LIGHTCYAN_EX = 106
        LIGHTWHITE_EX = 107

    @staticmethod
    def printout(content, color=Color.DEFAULT, bgcolor=BGColor.DEFAULT, style=Style.DEFAULT):
        print("\033[{};{};{}m{}\033[0m".format(style, color, bgcolor, content))


class BotApi:
    def __init__(self, appid: int, token: str, secret: str, debug: bool, sandbox: bool, api_return_pydantic=False):
        self.appid = appid
        self.token = token
        self.secret = secret
        self.base_api = "https://sandbox.api.sgroup.qq.com" if sandbox else "https://api.sgroup.qq.com"
        self.debug = debug
        self.api_return_pydantic = api_return_pydantic

        self.__headers = {
            'Authorization': f'Bot {self.appid}.{self.token}',
            'Content-Type': 'application/json'
        }

        self._cache = {}

    def api_send_reply_message(self, channel_id: str, msg_id="", content="", image_url="", retstr=False) \
            -> t.Union[str, structs.Message, None]:

        url = f"{self.base_api}/channels/{channel_id}/messages"
        if content == "" and image_url == "":
            self.logger("消息为空, 请检查", error=True)
            return None

        _c = {"content": content} if content != "" else None
        _im = {"image": image_url} if image_url != "" else None
        _msgid = {"msg_id": msg_id} if msg_id != "" else None

        def merge_dict(*args) -> dict:
            merged = {}
            for _d in args:
                if _d is not None:
                    merged = {**merged, **_d}

            print(merged)
            return merged

        payload = json.dumps(merge_dict(_c, _im, _msgid))

        response = requests.request("POST", url, headers=self.__headers, data=payload)
        data = json.loads(response.text)
        if "code" in data:
            self.logger(f"发送信息失败: {response.text}", error=True)
            if retstr:
                return response.text
            return None
        elif self.api_return_pydantic and not retstr:
            return structs.Message(**data)
        else:
            return response.text

    def get_guild_info(self, guiid_id, retstr=False) -> t.Union[str, structs.Guild, None]:
        """
        获取频道信息
        :param guiid_id: 频道id
        :param retstr: 强制返回纯文本
        """
        url = f"{self.base_api}/guilds/{guiid_id}"
        response = requests.request("GET", url, headers=self.__headers)
        data = json.loads(response.text)
        if "code" in data:
            self.logger(f"获取频道信息失败: {response.text}", error=True)
            if retstr:
                return response.text
            return None
        elif self.api_return_pydantic and not retstr:
            return structs.Guild(**data)
        else:
            return response.text

    def get_guild_user_info(self, guiid_id, member_id, retstr=False) -> t.Union[str, structs.Member, None]:
        """
        获取频道用户信息
        :param guiid_id: 频道id
        :param member_id: 用户id
        :param retstr: 强制返回纯文本
        """
        url = f"{self.base_api}/guilds/{guiid_id}/members/{member_id}"
        response = requests.request("GET", url, headers=self.__headers)
        data = json.loads(response.text)
        if "code" in data:
            self.logger(f"获取成员信息失败: {response.text}", error=True)
            if retstr:
                return response.text
            return None
        elif self.api_return_pydantic and not retstr:
            try:
                return structs.Member(**data)
            except:
                return response.text
        else:
            return response.text

    def get_channel_info(self, channel_id, retstr=False) -> t.Union[str, structs.Channel, None]:
        """
        获取子频道信息
        :param channel_id: 频道id
        :param retstr: 强制返回纯文本
        """
        url = f"{self.base_api}/channels/{channel_id}"
        response = requests.request("GET", url, headers=self.__headers)
        data = json.loads(response.text)
        if "code" in data:
            self.logger(f"获取子频道信息失败: {response.text}", error=True)
            if retstr:
                return response.text
            return None
        elif self.api_return_pydantic and not retstr:
            return structs.Channel(**data)
        else:
            return response.text

    def get_guild_channel_list(self, guiid_id, retstr=False) -> t.Union[str, t.List[structs.Channel], None]:
        """
        获取频道内子频道列表
        :param guiid_id: 频道id
        :param retstr: 强制返回纯文本
        """
        url = f"{self.base_api}/guilds/{guiid_id}/channels"
        response = requests.request("GET", url, headers=self.__headers)
        data = json.loads(response.text)
        if "code" in data:
            self.logger(f"获取子频道列表失败: {response.text}", error=True)
            if retstr:
                return response.text
            return None
        elif self.api_return_pydantic and not retstr:
            return [structs.Channel(**_c) for _c in data]
        else:
            return response.text

    def get_message(self, channel_id, message_id, retstr=False) -> t.Union[str, structs.Message, None]:
        """
        获取指定消息
        :param channel_id: 子频道id
        :param message_id: 消息id
        :param retstr: 强制返回纯文本
        """
        url = f"{self.base_api}/channels/{channel_id}/messages/{message_id}"
        response = requests.request("GET", url, headers=self.__headers)
        data = json.loads(response.text)
        if "code" in data:
            self.logger(f"获取消息信息失败: {response.text}", error=True)
            if retstr:
                return response.text
            return None
        elif self.api_return_pydantic and not retstr:
            return structs.Message(**data)
        else:
            return response.text

    def get_self_info(self, use_cache=False) -> t.Union[str, structs.User, None]:
        """
        获取Bot自身信息
        """
        if use_cache and "self_info" in self._cache:
            get_response = self._cache["self_info"]
        else:
            url = f"{self.base_api}/users/@me"
            response = requests.request("GET", url, headers=self.__headers)
            get_response = response.text
            self._cache["self_info"] = response.text

        data = json.loads(get_response)
        if "code" in data:
            self.logger(f"获取自身信息失败: {get_response}", error=True)
            return None
        elif self.api_return_pydantic:
            data["bot"] = True
            return structs.User(**data)
        else:
            return get_response

    def get_self_guilds(self, before="", after="", limit="100", use_cache=False, retstr=False) \
            -> t.Union[str, t.List[structs.Guild], None]:
        """
        获取Bot自身加入频道信息
        :param before: 读此id之前的数据(before/after 只能二选一)
        :param after: 读此id之后的数据(before/after 只能二选一)
        :param limit: 每次拉取条数
        :param use_cache: 使用缓存
        :param retstr: 强制返回纯文本
        """
        if use_cache and "get_self_guilds" in self._cache:
            get_response = self._cache["get_self_guilds"]
        else:
            if after != "":
                url = f"{self.base_api}/users/@me/guilds?after={after}&limit={limit}"
            elif before != "":
                url = f"{self.base_api}/users/@me/guilds?before={before}&limit={limit}"
            else:
                url = f"{self.base_api}/users/@me/guilds?limit={limit}"
            response = requests.request("GET", url, headers=self.__headers)
            get_response = response.text
            self._cache["get_self_guilds"] = response.text

        data = json.loads(get_response)
        if "code" in data:
            self.logger(f"获取频道列表失败: {get_response}", error=True)
            if retstr:
                return get_response
            return None
        elif self.api_return_pydantic and not retstr:
            return [structs.Guild(**g) for g in data]
        else:
            return get_response

    # TODO 更多API

    def logger(self, msg, debug=False, warning=False, error=False):
        if error:
            ColorfulPrint.printout(f"[ERROR] {msg}", ColorfulPrint.Color.RED)
        elif warning:
            ColorfulPrint.printout(f"[WARNING] {msg}", ColorfulPrint.Color.LIGHTYELLOW_EX)
        elif debug and self.debug:
            ColorfulPrint.printout(f"[DEBUG] {msg}", ColorfulPrint.Color.BLUE)
        elif not debug:
            ColorfulPrint.printout(f"[INFO] {msg}")
