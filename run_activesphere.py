#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ActiveSphere - ตัวรันแอปบนเครื่อง (local web server)
=====================================================
รันไฟล์นี้แล้วแอปจะเปิดในเบราว์เซอร์ที่ http://localhost:8000/activesphere.html

ทำไมต้องใช้ไฟล์นี้:
  - การเปิด activesphere.html แบบดับเบิลคลิกตรง ๆ (file://) เบราว์เซอร์จะ "บล็อก GPS"
  - แต่ถ้าเปิดผ่าน http://localhost (ด้วยสคริปต์นี้) เบราว์เซอร์ถือว่าปลอดภัย -> ใช้ GPS ได้จริง
  - แผนที่จริงและข้อมูลสวนทั่วประเทศจาก OpenStreetMap ก็จะโหลดได้ครบ

วิธีใช้:
  1) วางไฟล์นี้ (run_activesphere.py) ไว้ "โฟลเดอร์เดียวกัน" กับ activesphere.html
  2) ติดตั้ง Python 3 (ถ้ายังไม่มี: python.org/downloads)
  3) เปิดได้ 2 วิธี:
       - ดับเบิลคลิกไฟล์นี้  หรือ
       - เปิด Terminal/Command Prompt ในโฟลเดอร์นี้แล้วพิมพ์:  python run_activesphere.py
  4) เบราว์เซอร์จะเปิดเองอัตโนมัติ -> กด "อนุญาต/Allow" ตอนถามตำแหน่ง
  5) กด Ctrl+C ในหน้าต่าง Terminal เพื่อหยุดเซิร์ฟเวอร์

ใช้เฉพาะไลบรารีมาตรฐานของ Python (ไม่ต้องติดตั้งอะไรเพิ่ม)
"""

import http.server
import socketserver
import socket
import webbrowser
import threading
import time
import os
import sys

APP_FILE = "activesphere.html"
START_PORT = 8000


def find_free_port(start: int) -> int:
    """หาพอร์ตว่าง เริ่มจาก start (เผื่อพอร์ตถูกใช้อยู่)"""
    port = start
    for _ in range(30):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return port
        port += 1
    return start


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    """เสิร์ฟไฟล์จากโฟลเดอร์ปัจจุบัน + ปิด cache + ไม่พิมพ์ log รก ๆ"""

    def end_headers(self):
        self.send_header("Cache-Control", "no-store, max-age=0")
        super().end_headers()

    def log_message(self, *args):
        pass


def main():
    # ย้าย working directory ไปที่โฟลเดอร์ของสคริปต์นี้
    here = os.path.dirname(os.path.abspath(__file__)) or "."
    os.chdir(here)

    if not os.path.exists(APP_FILE):
        print("=" * 52)
        print(f"  ไม่พบไฟล์ '{APP_FILE}'")
        print("  กรุณาวางไฟล์ run_activesphere.py นี้")
        print("  ไว้โฟลเดอร์เดียวกับ activesphere.html")
        print("=" * 52)
        input("กด Enter เพื่อปิด...")
        sys.exit(1)

    port = find_free_port(START_PORT)
    url = f"http://localhost:{port}/{APP_FILE}"

    # เปิดเบราว์เซอร์ให้อัตโนมัติ (หน่วง 1 วิให้เซิร์ฟเวอร์พร้อมก่อน)
    def open_browser():
        time.sleep(1.0)
        try:
            webbrowser.open(url)
        except Exception:
            pass

    threading.Thread(target=open_browser, daemon=True).start()

    print("=" * 52)
    print("  ActiveSphere กำลังทำงานแล้ว!")
    print("  เปิดที่:  " + url)
    print("")
    print("  - GPS ใช้ได้บน localhost (กด 'อนุญาต' เมื่อถาม)")
    print("  - กด Ctrl + C เพื่อหยุดเซิร์ฟเวอร์")
    print("=" * 52)

    # allow_reuse_address กันปัญหาพอร์ตค้างตอนรันซ้ำ
    socketserver.TCPServer.allow_reuse_address = True
    try:
        with socketserver.TCPServer(("", port), QuietHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nปิดเซิร์ฟเวอร์เรียบร้อยแล้ว ขอบคุณที่ใช้งาน ActiveSphere")
    except OSError as e:
        print(f"\nเปิดเซิร์ฟเวอร์ไม่ได้: {e}")
        input("กด Enter เพื่อปิด...")


if __name__ == "__main__":
    main()
