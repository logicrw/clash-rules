# Clash 智能分流配置

**一句话介绍：** 让你上网更聪明——国内网站不绕路，国外网站自动翻。

---

## 📖 什么是分流？

想象你要寄快递：
- 寄到国内 → 用顺丰，又快又便宜
- 寄到国外 → 用 DHL，虽然贵但能送到

**分流就是让电脑自动判断：**
- 打开淘宝 → 直接连，不走代理
- 打开 Google → 自动走代理
- 打开 ChatGPT → 自动选美国线路（避免封号）

**没有分流 = 所有快递都用 DHL = 又慢又费钱**

---

## 🚀 3 分钟上手

### 第 1 步：下载配置文件

点击下载：[clash-verge.yaml](https://raw.githubusercontent.com/logicrw/clash-rules/main/config/clash-verge.yaml)

> 💡 右键 → 另存为，保存到你能找到的地方

### 第 2 步：修改订阅链接

1. 用记事本（或任意文本编辑器）打开下载的文件
2. 按 `Ctrl+F` 搜索 `YOUR_SUBSCRIPTION_URL`
3. 把它替换成你的机场订阅链接：

```
替换前：url: "YOUR_SUBSCRIPTION_URL_1"
替换后：url: "https://你的机场订阅链接"
```

4. 如果只有一个机场，把 `airport2` 整段删掉
5. 保存文件

### 第 3 步：导入 Clash

1. 打开 Clash Verge Rev（[下载地址](https://github.com/clash-verge-rev/clash-verge-rev/releases)）
2. 点左边「订阅」
3. 把你改好的文件**拖进去**，或者点「导入」选择文件
4. 点一下导入的配置让它变亮
5. 打开主界面开关 → 访问 google.com → 成功！🎉

> ✅ **规则会自动更新！** 配置文件里的规则链接指向本项目的 CDN，Clash 会自动拉取最新规则。

---

## 🎛️ 怎么切换线路？

打开 Clash → 点「代理」→ 看到这些组：

| 看到这个 | 它控制什么 | 怎么选 |
|---------|-----------|--------|
| 🚀 节点选择 | 大部分国外网站 | 选「自动选择」最省心 |
| 🤖 OpenAI | ChatGPT | 选 🇺🇸 美国 或 🇯🇵 日本 |
| 💎 Gemini | Google AI | 选 🇺🇸 美国 或 🇯🇵 日本（别选香港）|
| 🌐 Google | 谷歌搜索等 | 随便选 |
| 📹 YouTube | 看视频 | 选速度快的 |
| 💰 Crypto | 币安、OKX | 选 🇸🇬 新加坡 |
| 📺 哔哩哔哩 | B 站 | 保持「直连」|

---

## ❓ 常见问题

**导入后没有节点？**
→ 订阅链接填错了，检查一下

**提示解析错误？**
→ 编辑时格式搞乱了，重新下载再改

**ChatGPT 说地区不支持？**
→ 把「OpenAI」组换成美国节点

---

## 📁 进阶：自定义规则

想添加自己的规则？

1. Fork 本项目
2. 编辑规则文件：
   - `rules/proxy-extra.yaml` — 需要走代理的网站
   - `rules/direct-extra.yaml` — 需要直连的网站
3. **只修改这两个链接**：打开 `config/clash-verge.yaml`，找到 `proxy-extra` 和 `direct-extra` 部分，把里面的 `logicrw` 改成你的用户名（其他规则不要改，保持从本项目更新）
4. 下载修改后的配置文件导入 Clash

规则格式：
```yaml
payload:
  - DOMAIN-SUFFIX,example.com
```


---

## 🛠️ 维护者指南 (Maintainer Guide)

如果你是本项目所有者（`logicrw`），想要新增特殊的分流域名（如 AI、Gemini 或 Crypto）：

### 1. 修改 Surge 规则源仓库 (RuleGo)
项目的 AI、Gemini 和 Crypto 规则集源头在你的另一个仓库 [RuleGo](https://github.com/logicrw/RuleGo)（`patch-1` 分支）中：
- **AI 规则**：`Surge/Ruleset/Extra/AI.list`
- **Gemini 规则**：`Surge/Ruleset/Extra/GenAI/Google.list`
- **Crypto 规则**：`Surge/Ruleset/Extra/Crypto.list`

请**先**在 `logicrw/RuleGo` 仓库的 `patch-1` 分支中修改对应的 `.list` 文件（如直接在 GitHub 网页上修改，或在本地修改后 `git push origin patch-1`）。

### 2. 同步到 clash-rules
修改并推送 `RuleGo` 后，在本项目根目录下运行转换脚本：
```bash
python3 scripts/convert.py
```
这会重新拉取 `RuleGo` 的最新规则并更新 Clash 规则（如 `rules/ai-extra.yaml`）。

然后，将生成的更改提交并推送至本项目的 `main` 分支即可（GitHub Actions 会自动将其发布至 `release` 分支）：
```bash
git add rules/
git commit -m "chore: sync rules from RuleGo"
git push origin main
```

---

## 🙏 致谢

[blackmatrix7](https://github.com/blackmatrix7/ios_rule_script) · [RuleGo](https://github.com/logicrw/RuleGo)
