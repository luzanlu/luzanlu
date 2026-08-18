#!/usr/bin/env python3
"""BBDown WEB QR login fix: save cookies from poll response Set-Cookie headers."""

from __future__ import annotations

import http.cookiejar
import json
import os
from pathlib import Path
import shutil
import struct
import sys
import time
import urllib.parse
import urllib.request
import zlib

from _bbdown_qrcodegen import QrCode

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "BBDown.data"
QR_FILE = BASE_DIR / "qrcode.png"
GENERATE_URL = "https://passport.bilibili.com/x/passport-login/web/qrcode/generate"
POLL_URL = "https://passport.bilibili.com/x/passport-login/web/qrcode/poll"
REQUIRED_COOKIES = ("SESSDATA", "bili_jct", "DedeUserID")
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/140 Safari/537.36",
    "Referer": "https://www.bilibili.com/",
    "Accept": "application/json, text/plain, */*",
}


def _get_json(opener: urllib.request.OpenerDirector, url: str, params: dict[str, str]) -> dict:
    request_url = url + "?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(request_url, headers=HEADERS)
    with opener.open(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def _png_chunk(kind: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)


def _write_qr_png(text: str, path: Path) -> None:
    qr = QrCode.encode_text(text, QrCode.Ecc.MEDIUM)
    border, scale = 4, 8
    size = (qr.get_size() + border * 2) * scale
    rows = bytearray()
    for y in range(size):
        rows.append(0)  # PNG filter: None
        module_y = y // scale - border
        for x in range(size):
            module_x = x // scale - border
            dark = 0 <= module_x < qr.get_size() and 0 <= module_y < qr.get_size() and qr.get_module(module_x, module_y)
            rows.append(0 if dark else 255)
    ihdr = struct.pack(">IIBBBBB", size, size, 8, 0, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n" + _png_chunk(b"IHDR", ihdr) + _png_chunk(b"IDAT", zlib.compress(bytes(rows), 9)) + _png_chunk(b"IEND", b"")
    path.write_bytes(png)


def _cookie_values(jar: http.cookiejar.CookieJar) -> dict[str, str]:
    values: dict[str, str] = {}
    for cookie in jar:
        if "bilibili.com" in cookie.domain:
            values[cookie.name] = cookie.value.replace(",", "%2C")
    return values


def _serialize_cookies(values: dict[str, str]) -> str:
    missing = [name for name in REQUIRED_COOKIES if not values.get(name)]
    if missing:
        raise RuntimeError("登录成功，但响应缺少 Cookie: " + ", ".join(missing))
    priority = ("DedeUserID", "DedeUserID__ckMd5", "SESSDATA", "bili_jct", "sid")
    names = [name for name in priority if name in values]
    names.extend(sorted(name for name in values if name not in names))
    return ";".join(f"{name}={values[name]}" for name in names)


def _save_cookie_data(content: str, target: Path = DATA_FILE) -> Path | None:
    backup = None
    if target.exists():
        stamp = time.strftime("%Y%m%d_%H%M%S")
        backup = target.with_name(f"{target.name}.bak_{stamp}")
        shutil.copy2(target, backup)
    temp = target.with_name(target.name + ".tmp")
    temp.write_text(content, encoding="utf-8", newline="")
    os.replace(temp, target)
    return backup


def create_login() -> tuple[urllib.request.OpenerDirector, http.cookiejar.CookieJar, str, str]:
    jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    payload = _get_json(opener, GENERATE_URL, {"source": "main-fe-header"})
    if payload.get("code") != 0:
        raise RuntimeError("获取二维码失败: " + str(payload))
    data = payload["data"]
    return opener, jar, data["url"], data["qrcode_key"]


def poll_once(opener: urllib.request.OpenerDirector, key: str) -> tuple[int, dict]:
    payload = _get_json(opener, POLL_URL, {"qrcode_key": key, "source": "main-fe-header"})
    if payload.get("code") != 0:
        raise RuntimeError("轮询登录失败: " + str(payload))
    data = payload.get("data") or {}
    return int(data.get("code", -1)), data


def login() -> int:
    opener, jar, login_url, key = create_login()
    _write_qr_png(login_url, QR_FILE)
    print(f"二维码已生成: {QR_FILE}")
    print("请用哔哩哔哩 APP 扫码并确认。")
    try:
        os.startfile(QR_FILE)  # type: ignore[attr-defined]
    except OSError:
        print("无法自动打开图片，请手动打开 qrcode.png。")

    scanned = False
    deadline = time.monotonic() + 180
    while time.monotonic() < deadline:
        code, data = poll_once(opener, key)
        if code == 86101:
            time.sleep(1)
            continue
        if code == 86090:
            if not scanned:
                print("扫码成功，请在手机上确认...")
                scanned = True
            time.sleep(1)
            continue
        if code == 86038:
            raise RuntimeError("二维码已过期，请重新运行。")
        if code != 0:
            raise RuntimeError(f"未知登录状态 {code}: {data.get('message', '')}")

        content = _serialize_cookies(_cookie_values(jar))
        backup = _save_cookie_data(content)
        QR_FILE.unlink(missing_ok=True)
        print("WEB 登录成功，已生成有效 BBDown.data。")
        if backup:
            print(f"旧文件已备份: {backup.name}")
        print("Cookie 字段: " + ", ".join(part.split("=", 1)[0] for part in content.split(";")))
        return 0
    raise RuntimeError("登录等待超时，请重新运行。")


def self_test() -> int:
    sample = {
        "SESSDATA": "abc,def",
        "bili_jct": "csrf",
        "DedeUserID": "123",
        "DedeUserID__ckMd5": "hash",
    }
    content = _serialize_cookies({k: v.replace(",", "%2C") for k, v in sample.items()})
    assert "SESSDATA=abc%2Cdef" in content
    _write_qr_png("https://example.com/login?qrcode_key=self-test", QR_FILE)
    assert QR_FILE.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
    QR_FILE.unlink()
    print("self-test OK")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(self_test() if "--self-test" in sys.argv else login())
    except KeyboardInterrupt:
        print("\n已取消。")
        raise SystemExit(130)
    except Exception as exc:
        print(f"[错误] {exc}")
        raise SystemExit(1)
