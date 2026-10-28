# GRE Context Lab

一个面向 GRE General Verbal 的个人词汇学习系统：先从语境推断词义，再做近义词辨析，最后用原创 Sentence Equivalence（SE）练习检验。题目均为原创练习，不是 ETS 官方真题。

## 当前版本

- 语境学习、近义词辨析、原创 SE、间隔复习与学习统计。
- 学习状态保存在当前浏览器；支持完整备份、进度同步记录导出、词包导入与进度恢复。
- `docs/packs/starter.json` 是网站运行时的主词库/题库数据包。更新后，在线网站会尝试加载新版数据，并把它合并到本地内容中；远程内容优先覆盖相同 ID 的旧内容，用户导入的额外 ID 会保留。
- `tools/desktop_sync.py` 将网页导出的学习记录同步到仓库，归档历史快照，并按到期复习与错误记录生成 `docs/mobile/review-pack.json`。
- `tools/validate_pack.py` 检查词库/题库 JSON 的结构、ID 唯一性、词汇引用和答案索引；Pages 部署前会运行它。
- GitHub Actions 会尝试将 `docs/` 发布到 GitHub Pages。

## 运行网站

直接访问 GitHub Pages（首次发布成功后，地址通常是 `https://vmoonaurav.github.io/backup-04/`）。本地开发可在仓库根目录运行：

```bash
python -m http.server 8000 --directory docs
```

然后打开 `http://localhost:8000/`。浏览器需要通过 HTTP/HTTPS 才能正常使用 Service Worker 和 PWA 缓存。

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

## 更新词库与题库

编辑 `docs/packs/starter.json`，保持 `words`、`comparisons` 和 `se` 三个数组的结构。ID 应稳定且唯一；不要把已有 ID 改成另一个词义。网站会在联网时获取新版本并合并本地内容。提交 `docs/` 下的变化后，GitHub Actions 会重新部署网站。

## 内容说明

初始词库规模较小，用于验证学习流程。后续可以依据真实学习记录持续扩充高频 GRE 词汇、近义词辨析与原创 TC/SE 练习。自动生成的复习包是学习建议，不应替代对题目正确性和词义准确性的人工检查。
