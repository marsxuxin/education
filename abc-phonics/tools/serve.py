#!/usr/bin/env python3
"""本地预览 dist/ 的静态服务器（绕开 http.server -m 模式对 cwd 的依赖）。"""
import functools
import http.server
import os

DIST = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "dist"))
handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=DIST)
print(f"serving {DIST} at http://127.0.0.1:8642")
http.server.ThreadingHTTPServer(("127.0.0.1", 8642), handler).serve_forever()
