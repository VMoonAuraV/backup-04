#!/usr/bin/env python3
"""Local desktop host for GRE Context Lab.

Binds only to 127.0.0.1. The browser never receives Git credentials; the helper
invokes the local Git CLI for sync. POST endpoints accept same-origin JSON only.
"""
from __future__ import annotations
import json
import subprocess
import sys
import tempfile
import threading
import time
import webbrowser
from datetime import datetime, timezone
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
HOST = "127.0.0.1"
PORT = 8766
ORIGINS = {f"http://{HOST}:{PORT}", f"http://localhost:{PORT}"}


def git(*args: str) -> str:
    p = subprocess.run(["git", *args], cwd=ROOT, text=True, encoding="utf-8",
                       errors="replace", capture_output=True, timeout=60)
    if p.returncode:
        raise RuntimeError((p.stderr or p.stdout or "Git command failed").strip())
    return p.stdout.strip()


def json_response(handler, status, payload):
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Cache-Control", "no-store")
    handler.end_headers()
    handler.wfile.write(body)


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DOCS), **kwargs)

    def log_message(self, fmt, *args):
        print("[%s] %s" % (self.log_date_time_string(), fmt % args))

    def do_GET(self):
        path = urlsplit(self.path).path
        if path == "/api/status":
            try:
                branch = git("branch", "--show-current")
                remote_ok = bool(git("remote"))
                json_response(self, 200, {
                    "ok": True, "gitRepository": (ROOT / ".git").exists(),
                    "branch": branch, "remoteConfigured": remote_ok,
                    "repoPath": str(ROOT),
                })
            except Exception as exc:
                json_response(self, 200, {
                    "ok": False, "gitRepository": (ROOT / ".git").exists(),
                    "error": str(exc), "repoPath": str(ROOT),
                })
            return
        super().do_GET()

    def do_POST(self):
        path = urlsplit(self.path).path
        origin = self.headers.get("Origin", "")
        if origin not in ORIGINS:
            json_response(self, 403, {"ok": False, "error": "拒绝非本地网页发起的请求。请通过启动器打开本地网站。"})
            return
        if self.headers.get_content_type() != "application/json":
            json_response(self, 415, {"ok": False, "error": "请求必须使用 application/json。"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > 10_000_000:
                raise ValueError("请求内容为空或过大。")
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            if path == "/api/sync":
                if payload.get("type") != "context-lab-progress":
                    raise ValueError("无效的学习记录格式。")
                if not (ROOT / ".git").exists():
                    raise RuntimeError("当前目录不是 Git 仓库。请通过启动器重新安装/克隆仓库。")
                with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False) as f:
                    temp_path = Path(f.name)
                    json.dump(payload, f, ensure_ascii=False)
                try:
                    p = subprocess.run(
                        [sys.executable, str(ROOT / "tools" / "desktop_sync.py"), "push", str(temp_path)],
                        cwd=ROOT, text=True, encoding="utf-8", errors="replace",
                        capture_output=True, timeout=180,
                    )
                finally:
                    temp_path.unlink(missing_ok=True)
                if p.returncode:
                    raise RuntimeError((p.stderr or p.stdout or "GitHub 同步失败").strip())
                json_response(self, 200, {"ok": True, "message": (p.stdout or "同步完成。").strip()})
                return
            if path == "/api/pull":
                if not (ROOT / ".git").exists():
                    raise RuntimeError("当前目录不是 Git 仓库。")
                git("pull", "--rebase")
                latest = ROOT / "progress" / "latest.json"
                if not latest.exists():
                    json_response(self, 404, {"ok": False, "error": "GitHub 上还没有学习记录。请先在另一台设备同步一次。"})
                    return
                data = json.loads(latest.read_text(encoding="utf-8"))
                json_response(self, 200, {"ok": True, "progress": data, "message": "已从 GitHub 获取最新学习记录。"})
                return
            json_response(self, 404, {"ok": False, "error": "未知的本地 API 路径。"})
        except Exception as exc:
            json_response(self, 400, {"ok": False, "error": str(exc)})


def main():
    if not DOCS.is_dir():
        raise SystemExit(f"找不到网站目录：{DOCS}")
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    url = f"http://{HOST}:{PORT}/"
    print("=" * 60)
    print("GRE Context Lab 本地学习服务")
    print(f"网站地址：{url}")
    print(f"仓库目录：{ROOT}")
    print("保持此窗口打开即可学习；关闭窗口会停止服务。")
    print("通过网页中的“同步到 GitHub”按钮推送学习记录。")
    print("首次同步需要本机 Git 已登录并拥有仓库写入权限。")
    print("按 Ctrl+C 退出。")
    print("=" * 60)
    threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n正在关闭 GRE Context Lab…")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
