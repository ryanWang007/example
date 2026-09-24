# Mini Lookbook：最小穿搭收藏 CRUD

给 Flask 初学者的完整、可运行练习。这是独立的简化例子，不是 LookForge 的官方实现。

你可以保存一套穿搭的名称、场合和备注，然后查看、修改、删除它。例如：

- 名称：周末休闲装
- 场合：周末出门
- 备注：白色 T 恤 + 蓝色牛仔裤 + 白色运动鞋

技术：Python + Flask（后端）、HTML/Jinja + CSS（页面）、少量 JavaScript（删除确认）、SQLite（数据库）。没有登录、图片上传、AI 推荐。先学通一次完整的 CRUD。

## 1. 在 Windows / VS Code 启动

先安装 Python 3.10 或更新版本，安装时勾选 Add Python to PATH。VS Code 可以安装 Microsoft 的 Python 扩展，扩展不能代替 Python 本体。

1. 解压 ZIP。
2. VS Code → File → Open Folder，打开里面的 `mini-lookbook` 文件夹。左侧应直接看到 `app.py`。
3. Terminal → New Terminal，打开 PowerShell 终端，确认当前目录是这个项目目录。
4. 按顺序运行：

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

这里直接使用虚拟环境内的 Python，不需要激活环境，也无需修改 PowerShell 执行策略。

5. 保持终端运行，在浏览器打开 http://127.0.0.1:5000 （也可以 http://localhost:5000）。
6. 点击“新增穿搭”，保存一条记录，再试试“编辑”“删除”。
7. 终端按 Ctrl+C 停止。下次只需运行最后一条命令，数据还在。

若 `py` 无法识别，但 `python --version` 正常，可将第一条命令改为 `python -m venv .venv`。

macOS / Linux：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python app.py
```

## 2. Repo 里每个文件做什么

| 路径 | 作用 | 放 GitHub？ |
|---|---|---|
| `app.py` | 启动 Flask、接收请求、执行 SQL、返回页面 | 是 |
| `templates/base.html` | 公共页面外壳，引用 CSS / JS | 是 |
| `templates/index.html` | 首页：读取并显示所有穿搭 | 是 |
| `templates/form.html` | 新增和编辑共用的表单 | 是 |
| `static/style.css` | 颜色、布局、按钮等样式 | 是 |
| `static/app.js` | 删除前弹出确认框 | 是 |
| `requirements.txt` | 第三方 Python 依赖清单 | 是 |
| `.gitignore` | 告诉 Git 哪些文件不上传 | 是 |
| `test_app.py` | 自动验证 CRUD 和输入检查 | 是 |
| `README.md` | 本说明 | 是 |
| `.venv/` | 安装后生成的 Python 虚拟环境 | 否 |
| `instance/lookbook.db` | 首次访问首页后自动生成的数据库 | 否 |
| `__pycache__/` | Python 自动生成的缓存 | 否 |

Flask 默认从 `templates/` 找 HTML，从 `static/` 提供 CSS 和 JS，所以保留这两个目录名称。

## 3. 一次保存穿搭究竟发生了什么

1. 浏览器打开 `/outfits/new`，Flask 的 `create()` 返回 `form.html`。
2. 你填完表单点击保存，浏览器用 POST 把 `title`、`occasion`、`notes` 发给 Flask。
3. `request.form` 获取输入；`read_form()` 检查是否为空、是否超长。
4. `db.execute(...)` 执行 INSERT，`db.commit()` 提交到 SQLite 文件。
5. Flask 重定向回 `/`，`index()` 用 SELECT 重新读取数据。
6. `index.html` 用 `{% for outfit in outfits %}` 把每条记录显示成一张卡片。

HTML 里的 `{{ ... }}` 和 `{% ... %}` 是 Jinja 模板语法，Flask 在服务器端把它们转换成普通 HTML。不要用 Live Server 或双击 HTML 文件启动本项目；必须先运行 Python。

## 4. CRUD 对照

| CRUD | 操作 | 请求 | Python 函数 | SQL |
|---|---|---|---|---|
| Create | 新增 | `POST /outfits/new` | `create()` | INSERT |
| Read | 查看列表 | `GET /` | `index()` | SELECT |
| Update | 修改 | `POST /outfits/1/edit` | `edit(1)` | UPDATE |
| Delete | 删除 | `POST /outfits/1/delete` | `delete(1)` | DELETE |

另外，`GET /outfits/new` 显示空表单；`GET /outfits/1/edit` 显示记录 1 的编辑表单。URL 中的 1 是示例 ID。

这里使用传统 HTML 表单，因此更新和删除也使用 POST；不需要为这个小练习再拆出 JSON API。

## 5. SQLite 数据库

Python 内置 `sqlite3`，无需单独安装数据库服务。数据库是 `instance/lookbook.db`，关闭浏览器或停止 Flask 后数据仍在。

`get_db()` 自动创建的表相当于：

```sql
CREATE TABLE IF NOT EXISTS outfits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    occasion TEXT NOT NULL,
    notes TEXT NOT NULL DEFAULT ''
);
```

`id` 自动生成；`title` 是名称；`occasion` 是场合；`notes` 是备注。

SQL 中的 `?` 是参数占位符，用户输入通过另外的参数传入，不要用字符串拼接 SQL。

`.gitignore` 忽略数据库，所以队友 clone repo 后第一次打开首页会得到自己的空数据库。GitHub 保存代码，不会自动同步大家的穿搭记录。

## 6. 验证项目

Windows：

```powershell
.\.venv\Scripts\python.exe -m unittest -v
```

macOS / Linux：

```bash
.venv/bin/python -m unittest -v
```

测试使用独立临时数据库，不会修改你的穿搭。覆盖新增、读取、修改、删除、跨请求保存、空值/超长输入、HTML 转义、CSRF 校验和不存在的记录。

手动试一次：新增“周末休闲装” → 刷新页面 → 编辑名称 → 停止并重启 Flask → 确认记录还在 → 删除并确认。

## 7. 加入 GitHub repo

如果已经 clone 了一个 repo，把本项目内容复制到那个 repo 目录（包括 `.gitignore`），再用 VS Code 的 Source Control 查看更改、填写提交说明、Commit、Push / Sync Changes。

也可打开现有 repo 的终端执行：

```bash
git status
git add .
git commit -m "Add simple Flask SQLite lookbook CRUD"
git push
```

提交前确认 `.venv/` 和 `instance/` 没出现在待提交清单。ZIP 本身不是已连接 GitHub 的 repo；上述 push 假设你已经 clone 并配置了远端。

## 8. 常见问题与学习顺序

- `No module named flask`：使用上面 `.venv` 内的 Python 安装并启动，不要混用解释器。
- 端口被占用：停止另一个 Flask 进程，或将 `app.py` 最后一行的 `port=5000` 改成 `5001`，访问相应端口。
- 修改 Python 后未生效：Ctrl+C 停止并重新启动。
- 表单过期：刷新页面再提交。程序重启会生成新 session 密钥，旧表单会失效。
- 404：记录可能已被删除，回首页再操作。
- SQLite 不需要另外安装。`pip install sqlite3` 不是必需步骤。

建议阅读顺序：`index.html` → `app.py` 的 `index()` → `form.html` → `create()` → `edit()` → `delete()`。`get_db()` 管连接，CSRF 代码保护表单，可以第二遍再细读。

这是本机单人学习版本，绑定 `127.0.0.1`，没有账户隔离，Flask 开发服务器不用于正式公网部署。

官方参考：
- https://flask.palletsprojects.com/en/stable/tutorial/database/
- https://flask.palletsprojects.com/en/stable/tutorial/templates/
