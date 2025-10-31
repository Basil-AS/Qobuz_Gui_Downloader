"""
Модуль для работы с API Qobuz
Адаптировано из qobuz-dl/qobuz_dl/qopy.py и bundle.py
"""
import hashlib
import time
import requests
import base64
import re
from collections import OrderedDict


class QobuzAPIException(Exception):
    """Базовое исключение API Qobuz"""
    pass


class AuthenticationError(QobuzAPIException):
    """Ошибка аутентификации"""
    pass


class InvalidAppIdError(QobuzAPIException):
    """Неверный App ID"""
    pass


class InvalidAppSecretError(QobuzAPIException):
    """Неверный App Secret"""
    pass


class InvalidQuality(QobuzAPIException):
    """Неверное качество"""
    pass


class IneligibleError(QobuzAPIException):
    """Аккаунт не подходит"""
    pass


class Bundle:
    """Класс для получения app_id и secrets с сайта Qobuz"""
    
    _SEED_TIMEZONE_REGEX = re.compile(
        r'[a-z]\.initialSeed\("(?P<seed>[\w=]+)",window\.utimezone\.(?P<timezone>[a-z]+)\)'
    )
    _INFO_EXTRAS_REGEX = r'name:"\w+/(?P<timezone>{timezones})",info:"(?P<info>[\w=]+)",extras:"(?P<extras>[\w=]+)"'
    _APP_ID_REGEX = re.compile(
        r'production:{api:{appId:"(?P<app_id>\d{9})",appSecret:"\w{32}"'
    )
    _BUNDLE_URL_REGEX = re.compile(
        r'<script src="(/resources/\d+\.\d+\.\d+-[a-z]\d{3}/bundle\.js)"></script>'
    )
    _BASE_URL = "https://play.qobuz.com"
    
    def __init__(self):
        self._session = requests.Session()
        
        response = self._session.get(f"{self._BASE_URL}/login")
        response.raise_for_status()
        
        bundle_url_match = self._BUNDLE_URL_REGEX.search(response.text)
        if not bundle_url_match:
            raise NotImplementedError("Bundle URL not found")
        
        bundle_url = bundle_url_match.group(1)
        
        response = self._session.get(self._BASE_URL + bundle_url)
        response.raise_for_status()
        
        self._bundle = response.text
        
    def get_app_id(self):
        """Получение App ID"""
        match = self._APP_ID_REGEX.search(self._bundle)
        if not match:
            raise NotImplementedError("Failed to match APP ID")
        return match.group("app_id")
    
    def get_secrets(self):
        """Получение списка секретов"""
        seed_matches = self._SEED_TIMEZONE_REGEX.finditer(self._bundle)
        secrets = OrderedDict()
        
        for match in seed_matches:
            seed, timezone = match.group("seed", "timezone")
            secrets[timezone] = [seed]
        
        keypairs = list(secrets.items())
        secrets.move_to_end(keypairs[1][0], last=False)
        info_extras_regex = self._INFO_EXTRAS_REGEX.format(
            timezones="|".join([timezone.capitalize() for timezone in secrets])
        )
        info_extras_matches = re.finditer(info_extras_regex, self._bundle)
        for match in info_extras_matches:
            timezone, info, extras = match.group("timezone", "info", "extras")
            secrets[timezone.lower()] += [info, extras]
        
        for secret_pair in secrets:
            secrets[secret_pair] = base64.standard_b64decode(
                "".join(secrets[secret_pair])[:-44]
            ).decode("utf-8")
        
        return secrets


class QobuzClient:
    """Клиент для работы с API Qobuz"""
    
    def __init__(self, email, password, app_id, secrets):
        self.secrets = secrets
        self.id = str(app_id)
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0",
            "X-App-Id": self.id,
            "Content-Type": "application/json;charset=UTF-8"
        })
        self.base = "https://www.qobuz.com/api.json/0.2/"
        self.sec = None
        self.auth(email, password)
        self.cfg_setup()
        
    def api_call(self, epoint, **kwargs):
        """Выполнение API запроса"""
        if epoint == "user/login":
            params = {
                "email": kwargs["email"],
                "password": kwargs["pwd"],
                "app_id": self.id,
            }
        elif epoint == "track/get":
            params = {"track_id": kwargs["id"]}
        elif epoint == "album/get":
            params = {"album_id": kwargs["id"]}
        elif epoint == "playlist/get":
            params = {
                "extra": "tracks",
                "playlist_id": kwargs["id"],
                "limit": 500,
                "offset": kwargs.get("offset", 0),
            }
        elif epoint == "artist/get":
            params = {
                "app_id": self.id,
                "artist_id": kwargs["id"],
                "limit": 500,
                "offset": kwargs.get("offset", 0),
                "extra": "albums",
            }
        elif epoint == "label/get":
            params = {
                "label_id": kwargs["id"],
                "limit": 500,
                "offset": kwargs.get("offset", 0),
                "extra": "albums",
            }
        elif epoint == "track/getFileUrl":
            unix = time.time()
            track_id = kwargs["id"]
            fmt_id = kwargs["fmt_id"]
            if int(fmt_id) not in (5, 6, 7, 27):
                raise InvalidQuality("Invalid quality id: choose between 5, 6, 7 or 27")
            r_sig = "trackgetFileUrlformat_id{}intentstreamtrack_id{}{}{}".format(
                fmt_id, track_id, unix, kwargs.get("sec", self.sec)
            )
            r_sig_hashed = hashlib.md5(r_sig.encode("utf-8")).hexdigest()
            params = {
                "request_ts": unix,
                "request_sig": r_sig_hashed,
                "track_id": track_id,
                "format_id": fmt_id,
                "intent": "stream",
            }
        else:
            params = kwargs
            
        r = self.session.get(self.base + epoint, params=params)
        
        if epoint == "user/login":
            if r.status_code == 401:
                raise AuthenticationError("Invalid credentials")
            elif r.status_code == 400:
                raise InvalidAppIdError("Invalid app id")
        elif epoint == "track/getFileUrl" and r.status_code == 400:
            raise InvalidAppSecretError(f"Invalid app secret: {r.json()}")
        
        r.raise_for_status()
        return r.json()
    
    def auth(self, email, pwd):
        """Авторизация пользователя"""
        usr_info = self.api_call("user/login", email=email, pwd=pwd)
        if not usr_info["user"]["credential"]["parameters"]:
            raise IneligibleError("Free accounts are not eligible to download tracks")
        self.uat = usr_info["user_auth_token"]
        self.session.headers.update({"X-User-Auth-Token": self.uat})
        self.label = usr_info["user"]["credential"]["parameters"]["short_label"]
        self.user_info = usr_info
        
    def test_secret(self, sec):
        """Тестирование секрета"""
        try:
            self.api_call("track/getFileUrl", id=5966783, fmt_id=5, sec=sec)
            return True
        except InvalidAppSecretError:
            return False
    
    def cfg_setup(self):
        """Настройка конфигурации (поиск валидного секрета)"""
        for secret in self.secrets.values():
            if not secret:
                continue
            if self.test_secret(secret):
                self.sec = secret
                break
        
        if self.sec is None:
            raise InvalidAppSecretError("Can't find any valid app secret")
    
    def get_album_meta(self, album_id):
        """Получение метаданных альбома"""
        return self.api_call("album/get", id=album_id)
    
    def get_track_meta(self, track_id):
        """Получение метаданных трека"""
        return self.api_call("track/get", id=track_id)
    
    def get_track_url(self, track_id, fmt_id):
        """Получение URL для скачивания трека"""
        return self.api_call("track/getFileUrl", id=track_id, fmt_id=fmt_id)
    
    def get_playlist_meta(self, playlist_id):
        """Получение метаданных плейлиста"""
        return self.api_call("playlist/get", id=playlist_id, offset=0)


# Глобальные переменные для кеширования
_cached_app_id = None
_cached_secrets = None


def get_app_credentials():
    """Получение app_id и secrets (с кешированием)"""
    global _cached_app_id, _cached_secrets
    
    if _cached_app_id and _cached_secrets:
        return _cached_app_id, _cached_secrets
    
    bundle = Bundle()
    _cached_app_id = bundle.get_app_id()
    _cached_secrets = bundle.get_secrets()
    
    return _cached_app_id, _cached_secrets


def get_qobuz_client(email, password):
    """Создание клиента Qobuz"""
    app_id, secrets = get_app_credentials()
    return QobuzClient(email, password, app_id, secrets)
