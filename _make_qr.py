#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
根据 _site_url.txt 里的网页地址，为 13 个单元生成二维码 PNG。
每个二维码指向 网页地址#锚点 ，扫码后手机自动跳到对应单元。
"""
import os, json
import qrcode

BUILD_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(BUILD_DIR, "二维码")
os.makedirs(OUT_DIR, exist_ok=True)

# (文件名, 锚点, 显示名)
UNITS = [
    ("二维码_Hello", "hello", "Hello 入门"),
    ("二维码_U1", "u1", "Unit 1"),
    ("二维码_U2", "u2", "Unit 2"),
    ("二维码_U3", "u3", "Unit 3"),
    ("二维码_U4", "u4", "Unit 4"),
    ("二维码_U5", "u5", "Unit 5"),
    ("二维码_U6", "u6", "Unit 6"),
    ("二维码_U7", "u7", "Unit 7"),
    ("二维码_U8", "u8", "Unit 8"),
    ("二维码_U9", "u9", "Unit 9"),
]

def main():
    url_file = os.path.join(BUILD_DIR, "_site_url.txt")
    if not os.path.exists(url_file):
        print("❌ 找不到 _site_url.txt，请先运行 _deploy.py 部署网页")
        return
    with open(url_file, "r") as f:
        base = f.read().strip().rstrip("/")
    print(f"网页地址: {base}")

    count = 0
    for fname, anchor, label in UNITS:
        link = f"{base}#{anchor}"
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        qr.add_data(link)
        qr.make(fit=True)
        img = qr.make_image(fill_color="#2b2b3a", back_color="white")
        # 在二维码下方留白处写入单元名（用注释方式：把名存为同目录 txt 方便对照）
        out_path = os.path.join(OUT_DIR, f"{fname}.png")
        img.save(out_path)
        # 同时写一份对照表，方便打印时对应
        with open(os.path.join(OUT_DIR, f"{fname}.txt"), "w") as t:
            t.write(f"{label}\n{link}\n")
        count += 1
        print(f"  ✅ {label}: {out_path}")

    print(f"\n共生成 {count} 个二维码，保存在: {OUT_DIR}")

if __name__ == "__main__":
    main()
