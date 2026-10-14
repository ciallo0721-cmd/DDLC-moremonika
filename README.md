# DDLC-MoreMonika

A DDLC mod that upgrades the poem minigame and gives Monika a few extra tricks.

> 简体中文说明见 [README.zh-CN.md](README.zh-CN.md)（含中文版计划说明）。

## Features

1. **Sentence poem minigame** - instead of picking single words, you pick full sentences (`poemsentences.txt`, 10 picks per round, thresholds rebalanced).
2. **F9 - Monika Observation Panel** - live affection stats for Sayori / Natsuki / Yuri / Monika, poem appeal history, poem winners, playthrough & chapter info.
3. **F10 - Story Jump Panel** - jump straight to any key scene: day 1-4, Sayori's fate, Act 2 days, Act 2 finale, Just Monika.
4. **The camera moment** - when Monika reads your real username in the Just Monika space, she tries to elevate to SYSTEM via a scheduled task and launch Windows Camera (UAC prompt; falls back to a normal launch).

## Install

```powershell
powershell -ExecutionPolicy Bypass -File install.ps1 -GameDir "C:\path\to\Doki Doki Literature Club\game"
```

Or just run it next to the game folder without arguments - it auto-detects common paths.

## Uninstall

```powershell
powershell -ExecutionPolicy Bypass -File uninstall.ps1
```

Restores the original `script-ch30.rpyc` and removes all mod files.

## Notes

- All mod UI is English by design (vanilla DDLC fonts have no CJK glyphs).
- Windows Camera started as SYSTEM runs in session 0, so its window may not be visible on your desktop; the fallback launch runs as your current user.
- Adding your own sentences: edit `game/poemsentences.txt`, format `sentence,sPoint,nPoint,yPoint`, no commas inside sentences, malformed lines are skipped automatically.

## Credits

Base game by Team Salvato. Mod scripts decompiled with unrpyc.
