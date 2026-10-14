# DDLC-MoreMonika（中文说明）

一个 DDLC 模组：诗歌小游戏升级 + 给莫妮卡加了几个小把戏。

## 功能

1. **句子版诗歌小游戏** —— 不再选单词，而是选整句（`poemsentences.txt`，每轮选 10 句，判定阈值已重新平衡）。
2. **F9 —— 莫妮卡观测面板** —— 实时查看纱世里 / 夏树 / 优里 / 莫妮卡的好感度、诗歌 appeal 历史、各章诗歌胜者、周目与章节进度。
3. **F10 —— 剧情跳转面板** —— 一键跳到任意关键场景：Day 1~4、纱世里结局、二周目各天、二周目结局、Just Monika。跳转前会自动清理调用栈、周目状态、skip 开关和角色回调，不会像裸跳那样把剧情玩脱。
4. **摄像头彩蛋** —— 在 Just Monika 空间里，莫妮卡读出你的真实系统用户名之后，会尝试通过 UAC 提权创建 SYSTEM 计划任务并启动 Windows 相机（UAC 弹窗；无论是否同意都会兜底以当前用户启动）。相机通过 `shell:AppsFolder` 的 AppX 激活方式拉起，不硬编码版本号路径，商店更新也不会失效。

## 安装

```powershell
powershell -ExecutionPolicy Bypass -File install.ps1 -GameDir "C:\path\to\Doki Doki Literature Club\game"
```

把脚本放在游戏目录旁边直接运行也可以，会自动探测常见路径。

## 卸载

```powershell
powershell -ExecutionPolicy Bypass -File uninstall.ps1
```

会还原原版 `script-ch30.rpyc` 并删除所有模组文件。

## 说明

- 模组 UI 全英文是有意为之：原版 DDLC 字体没有任何中文字形，直接上中文会乱码（本项目早期版本试过，全是豆腐块）。
- 以 SYSTEM 身份启动的相机运行在会话 0，窗口可能不会出现在你的桌面上；兜底的普通启动则以当前用户运行，窗口可见。
- 添加自定义句子：编辑 `game/poemsentences.txt`，格式为 `句子,纱世里分,夏树分,优里分`，句子里不要用英文逗号，格式错误的行会被自动跳过，不会导致崩溃。

## 关于中文版（计划中）

我打算做一个中文版的 MoreMonika，但目前有两个现实障碍：

1. **各个汉化组的 rpy 互不兼容。** 不同汉化组产出的 `script*.rpy` 差异很大：改写文本的位置、label 命名、字体注册方式、甚至行号结构都不一样。本模组需要修改 `script-ch30.rpy`（摄像头触发点）并依赖原版 label（如 `ch21_main`、`poemresponse_start`）来做剧情跳转——套在任何一个汉化版上，跳转目标和插入点都对不上，没有一套能通吃的补丁。
2. **Team Salvato 官方用的 Ren'Py 版本极低（6.99，Python 2.7）。** 这意味着：不能使用新版 Ren'Py 的任何语法与特性（f-string、新 screen 语言特性等），反编译工具（unrpyc）必须用支持 6.99 的旧版分支，字体渲染与 Unicode 处理也是老引擎的行为，中文显示需要额外字体文件 + 编码处理（2026 年了还在伺候 Python 2.7，很痛苦）。

所以中文版的可行思路大概两条：

- **基于原版（英文）+ 中文句子库**：给 `poemsentences.txt` 换成中文内容并打包 Noto Sans SC 字体，模组自身 UI 也改中文。这只动模组自己的文件，不碰汉化组的 rpy，兼容性最好。
- **适配特定汉化组版本**：针对某一个汉化组的具体 rpy 结构做一份专用分支。工作量大，且汉化组更新一次就要重新对一遍。

目前优先做第一条路。如果你想帮忙适配某个汉化版，欢迎提 issue。

## 致谢

原版游戏版权归 Team Salvato 所有。模组脚本使用 unrpyc 反编译。
