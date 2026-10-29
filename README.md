# GRE Context Lab

一个面向 GRE General Verbal 的个人词汇学习系统：先从语境推断词义，再做近义词辨析，最后用原创 Sentence Equivalence（SE）练习检验。题目均为原创练习，不是 ETS 官方真题。

## 当前版本

- 语境学习、近义词辨析、原创 SE、间隔复习与学习统计。
- 学习状态保存在当前浏览器；支持完整备份、进度同步记录导出、词包导入与进度恢复。
- `docs/packs/starter.json` 是网站运行时的主词库/题库数据包。更新后，在线网站会尝试加载新版数据，并把它合并到本地内容中；远程内容优先覆盖相同 ID 的旧内容，用户导入的额外 ID 会保留。
- `tools/desktop_sync.py` 将网页导出的学习记录同步到仓库，归档历史快照，并按到期复习与错误记录生成 `docs/mobile/review-pack.json`。
- `tools/validate_pack.py` 检查词库/题库 JSON 的结构、ID 唯一性、词汇引用和答案索引；Pages 部署前会运行它。
- GitHub Actions 会尝试将 `docs/` 发布到 GitHub Pages。

## 首次启用网站发布

在仓库的 **Settings → Pages → Build and deployment → Source** 中选择 **GitHub Actions**。GitHub Actions 的默认令牌没有权限替仓库首次开启 Pages，因此这一步需要仓库管理员手动设置一次。设置完成后，到 **Actions** 中重新运行最新的 “Deploy GRE Context Lab to GitHub Pages” 工作流。

## 一键启动（Windows，推荐）

1. 安装 [Git for Windows](https://git-scm.com/download/win) 和 [Python 3](https://www.python.org/downloads/windows/)（安装 Python 时勾选 Add Python to PATH）。
2. 双击仓库根目录的 `Start-GRE-Context-Lab.bat`。
3. 如果你是从 GitHub 的 **Download ZIP** 进入，启动器会在 `%LOCALAPPDATA%\\GRE-Context-Lab\\backup-04` 自动克隆一份带 Git 历史的工作副本；如果你已经 `git clone` 了仓库，则直接启动当前副本。
4. 启动器会打开浏览器并运行本地服务。保持服务窗口打开即可学习；关闭窗口会停止服务。
5. 在「学习记录」中使用 **同步到 GitHub** 或 **从 GitHub 恢复**。首次推送时，Git 可能要求你完成 Git Credential Manager 登录；必须拥有该仓库写入权限。

启动器通过 `tools/desktop_app.py` 在 `127.0.0.1:8766` 运行本地服务。GitHub 凭据只由本机 Git 使用，不会传给网页。该本地 API 只接受本地网页发起的请求。

## 手动运行网站

首次发布成功后，网站地址通常是 `https://vmoonaurav.github.io/backup-04/`。如需手动预览，可在仓库根目录运行：

```bash
python -m http.server 8000 --directory docs
```

然后打开 `http://localhost:8000/`。这种简易静态服务器仅适合学习与预览；GitHub 自动同步按钮需要使用 `Start-GRE-Context-Lab.bat` 启动的本地服务。

## 电脑端学习记录同步

1. 在网页「学习记录」中点击 **导出同步记录（JSON）**，保存 `context-lab-progress-YYYY-MM-DD.json`。也可以用顶部的「同步记录」按钮。
2. 将本仓库克隆到电脑，并确保 Git 已配置好可推送到 `VMoonAuraV/backup-04` 的凭据：

   ```bash
   git clone https://github.com/VMoonAuraV/backup-04.git
   cd backup-04
   ```

3. 在仓库目录运行：

   ```bash
   python tools/desktop_sync.py push "C:\\path\\to\\context-lab-progress-YYYY-MM-DD.json"
   ```

   脚本会先 `git pull --rebase`，检查记录时间戳以避免静默覆盖较新的远程进度，然后更新 `progress/latest.json`、追加 `progress/history/` 快照、生成手机复习包并执行 Git commit/push。也可在 Windows 中使用 `sync-progress.bat "完整文件路径"`。

4. 如果换电脑，需要先 `git pull` 获取最新仓库文件，再在网页「学习记录」里选择 **导入 GitHub 学习记录**，导入 `progress/latest.json`。这会覆盖当前浏览器的学习状态，应用会在导入前二次确认。建议先导出完整备份。

**重要：** 本仓库目前是公开仓库，`progress/` 中的学习记录和 Git 历史都可被任何人查看。同步程序使用电脑本地 Git 凭据，不把 GitHub token 放进网页或仓库。不要在学习记录中放密码、访问令牌等秘密。

## 多例句与本地模型接口

每个词汇可继续使用旧的 `example` 字段，也可增加 `examples` 数组；网站会展示多个例句。结构与调用约定见 [本地例句提供器接口文档](docs/LOCAL_EXAMPLE_PROVIDER.md)。

本地模型接入点已经预留，不包含在线生成服务：

1. 在本地创建 `docs/local-example-provider.local.js`。
2. 定义 `window.GREContextLabExampleProvider`，实现 `apiVersion: 1`、`isConfigured: true` 和异步方法 `generateExamples(request)`。
3. 方法返回 `[{ text, kind, note, id? }]` 形式的候选例句。网页会去重并保存到浏览器本地，标记为“尚未审核”。
4. 本地适配文件已加入 `.gitignore`，不会被提交到仓库，也不会随常规 Git 更新覆盖。它只在本地网站运行时加载。
5. 候选例句包含在“完整备份”中，但不会通过“同步到 GitHub”自动上传。

## 更新词库与题库

编辑 `docs/packs/starter.json`，保持 `words`、`comparisons` 和 `se` 三个数组的结构。ID 应稳定且唯一；不要把已有 ID 改成另一个词义。网站会在联网时获取新版本并合并本地内容。提交 `docs/` 下的变化后，GitHub Actions 会重新部署网站。

## 内容说明

初始词库规模较小，用于验证学习流程。后续可以依据真实学习记录持续扩充高频 GRE 词汇、近义词辨析与原创 TC/SE 练习。自动生成的复习包是学习建议，不应替代对题目正确性和词义准确性的人工检查。
