# Columbia Bulletin Scraper (BeautifulSoup)

用 `requests + BeautifulSoup` 抓取 Columbia Engineering Bulletin 专业页面的“要求小节 + 课程代码”信息。默认示例抓取 **Computer Science (BS)** 页面。

## 一键跑通（GitHub Codespaces）
1. 新建 GitHub 仓库（建议名：`columbia-bulletin-scraper`），把本项目所有文件上传（或直接上传 zip 解压）。
2. 打开仓库 → 绿色 **Code** 按钮 → **Create codespace on main**。
3. 在 Codespaces 终端执行：
   ```bash
   pip install -r requirements.txt
   python scrape_bulletin.py
   ```
4. 运行后输出：
   - `data/cs_bs_sections.csv`：每个小节的合并纯文本
   - `data/cs_bs_courses.csv`：抽取到的课程代码清单（去重）

## 本地运行
```bash
python -m venv .venv
source .venv/bin/activate  # Windows 用 .venv\Scripts\activate
pip install -r requirements.txt
python scrape_bulletin.py
```

## 修改为其它专业页面
- 编辑 `scrape_bulletin.py` 顶部的 `URLS` 列表，添加你要抓的 Bulletin 页面（一个或多个）。
- 结构类似的页面都可以直接复用这套解析逻辑。

## 注意
- 仅作学习用途，控制访问频率（脚本内已加简单 sleep）；如需大规模抓取请先阅读对方站点的 robots/条款。
- 某些页面可能包含 PDF 或动态内容，优先抓 HTML；必要时再扩展 PDF 解析或 Selenium。

