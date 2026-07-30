#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
部署 Power Up L1 配套音频网页到 GitHub Pages。
用法: python3 _deploy.py <令牌文件路径> [仓库名]
  - 令牌从文件读取，不出现在命令行，避免泄露
  - 自动建仓(公开) -> 推送 main 分支 -> 开启 Pages -> 输出公开网址
"""
import os, sys, json, subprocess, urllib.request, urllib.error, time

BUILD_DIR = os.path.dirname(os.path.abspath(__file__))

def redact(s, token):
    if token and token in s:
        return s.replace(token, "***")
    return s

def api(token, method, path, data=None, timeout=30):
    url = "https://api.github.com" + path
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "workbuddy-deploy",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        try:
            payload = json.loads(e.read().decode() or "{}")
        except Exception:
            payload = {}
        return e.code, payload

def main():
    if len(sys.argv) < 2:
        print("用法: python3 _deploy.py <令牌文件路径> [仓库名]")
        sys.exit(1)
    token_file = sys.argv[1]
    repo_name = sys.argv[2] if len(sys.argv) > 2 else "powerup-l1-audio"
    with open(token_file, "r") as f:
        token = f.read().strip()

    # 1) 获取当前登录账号
    st, user = api(token, "GET", "/user")
    if st != 200:
        print("❌ 令牌无效或权限不足:", st, redact(json.dumps(user), token))
        sys.exit(1)
    login = user["login"]
    print(f"✅ 已登录 GitHub 账号: {login}")

    # 2) 建仓(若已存在则跳过)
    st, repo = api(token, "POST", "/user/repos", {
        "name": repo_name,
        "private": False,
        "auto_init": False,
        "description": "Power Up Level 1 配套音频 (Ryan 英式男声)",
    })
    if st == 201:
        print(f"✅ 仓库已创建: https://github.com/{login}/{repo_name}")
    elif st == 422:
        print(f"ℹ️  仓库已存在，继续推送: https://github.com/{login}/{repo_name}")
    else:
        print("❌ 创建仓库失败:", st, redact(json.dumps(repo), token))
        sys.exit(1)

    # 3) 设置 remote 并推送 main 分支
    remote = f"https://{token}@github.com/{login}/{repo_name}.git"
    subprocess.run(["git", "remote", "remove", "origin"], cwd=BUILD_DIR,
                   stderr=subprocess.DEVNULL)
    subprocess.run(["git", "remote", "add", "origin", remote], cwd=BUILD_DIR,
                   check=True)
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0")
    res = subprocess.run(["git", "push", "-u", "origin", "main", "--force"],
                         cwd=BUILD_DIR, capture_output=True, text=True, env=env)
    out = redact(res.stdout, token)
    err = redact(res.stderr, token)
    if out.strip():
        print(out)
    if err.strip():
        print(err)
    if res.returncode != 0:
        print("❌ 推送失败")
        sys.exit(1)
    print("✅ 代码已推送到 GitHub")

    # 4) 开启 GitHub Pages (main 分支根目录)
    st, pages = api(token, "POST", f"/repos/{login}/{repo_name}/pages",
                    {"source": {"branch": "main", "path": "/"}})
    if st in (201, 409):
        # 轮询直到拿到 html_url
        for _ in range(10):
            st2, info = api(token, "GET", f"/repos/{login}/{repo_name}/pages")
            if st2 == 200 and info.get("html_url"):
                url = info["html_url"]
                print(f"✅ GitHub Pages 已开启: {url}")
                with open(os.path.join(BUILD_DIR, "_site_url.txt"), "w") as f:
                    f.write(url)
                return
            time.sleep(3)
        print("⚠️  Pages 已提交，但还未返回公开网址，稍后在仓库 Settings -> Pages 查看")
    else:
        print("⚠️  开启 Pages 返回:", st, redact(json.dumps(pages), token))
        print("    可手动到仓库 Settings -> Pages 选择 main 分支根目录开启")

if __name__ == "__main__":
    main()
