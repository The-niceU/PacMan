<a id="top"></a>

# 👾 PacMan 期末大作业

> 使用 `Python + pygame` 实现的 PacMan GUI 小游戏，包含双关卡、素材动画、蓝色线条迷宫、生命系统与道具机制。

<p align="left">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white">
  <img alt="Pygame" src="https://img.shields.io/badge/Pygame-2.x-22A559?logo=pygame&logoColor=white">
  <img alt="Platform" src="https://img.shields.io/badge/Platform-Windows-blue">
  <img alt="Status" src="https://img.shields.io/badge/Status-Completed-success">
</p>

<p>
  <img src="/preview1.png" alt="PacMan Cover" width="400" />
</p>

---

<a id="table-of-contents"></a>

## 📚 目录

- [✨ 项目亮点](#highlights)
- [🖼 演示图](#demo)
- [🧠 架构图](#architecture)
- [🔄 玩法流程](#flow)
- [🎮 游戏规则](#rules)
- [✅ 特性对照](#features)
- [🧩 项目结构](#structure)
- [🚀 快速开始](#quickstart)
- [🎯 操作说明](#controls)
- [🛠 技术实现概览](#tech)
- [🗺 路线图](#roadmap)
- [❓ FAQ](#faq)

---

<a id="highlights"></a>

## ✨ 项目亮点

- **双关卡递进**：至少 2 关，清空豆点后自动进入下一关。
- **素材动画完整接入**：PacMan、Ghost、GhostScared、FrightFruit 全部来自 `images/`。
- **迷宫风格贴近题图**：墙体采用蓝色直线与圆角连接的线框式绘制。
- **手感优化**：PacMan 支持拐角吸附转向，减少卡拐角。
- **碰撞机制更合理**：
  - 红色 Ghost：碰到后仅扣 1 条命，角色位置保持不变。
  - 蓝色 Ghost：与 PacMan 相遇互相无视，PacMan 不能吃 Ghost。
- **仓库展示增强**：支持封面图、演示图、目录锚点与可视化架构图。


---


<a id="rules"></a>

## 🎮 游戏规则

1. 使用方向键控制 PacMan 移动。
2. 吃掉普通豆点可获得分数。
3. 吃到 `FrightFruit` 后，Ghost 进入短暂蓝色状态。
4. 蓝色状态期间，PacMan 与 Ghost 互不影响。
5. 撞到红色 Ghost 会损失生命值，但游戏不会重置角色位置。
6. 当前关卡所有豆点吃完后进入下一关。


---

<a id="features"></a>

## ✅ 特性对照

| 功能项                | 当前状态  | 说明                       |
| --------------------- | --------- | -------------------------- |
| 至少 2 关卡           | ✅ 已实现 | 清空当前关豆点后自动下一关 |
| PacMan 动画           | ✅ 已实现 | 按方向切换不同帧贴图       |
| Ghost 正常/害怕状态   | ✅ 已实现 | 红色与蓝色两种视觉状态     |
| FrightFruit 道具      | ✅ 已实现 | 触发短暂蓝色无视状态       |
| 拐角顺滑转向          | ✅ 已实现 | 网格吸附 + 预输入方向      |
| 红 Ghost 碰撞扣血继续 | ✅ 已实现 | 不重置角色位置             |
| 蓝 Ghost 可被吃掉     | ❌ 不启用 | 按当前规则设定为互相无视   |


---

<a id="structure"></a>

## 🧩 项目结构

```text
.
├─ docs/
│  └─ assets/
│     ├─ cover.svg
│     ├─ demo.svg
│     ├─ architecture.svg
│     └─ game-flow.svg
├─ images/                  # 游戏素材资源
│  ├─ PacMan*.gif
│  ├─ Ghost*.gif
│  └─ FrightFruit.png
├─ src/
│  ├─ main.py               # 程序入口
│  └─ game.py               # 核心逻辑（实体、渲染、关卡、碰撞）
├─ requirements.txt         # 依赖
├─ REPORT.md                # 课程报告
└─ README.md
```


---

<a id="quickstart"></a>

## 🚀 快速开始

### 1) 安装依赖

```bash
pip install -r requirements.txt
```

### 2) 运行项目

```bash
python src/main.py
```

### 3) 可选：创建虚拟环境

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```


---

<a id="controls"></a>

## 🎯 操作说明

- `↑`：向上移动
- `↓`：向下移动
- `←`：向左移动
- `→`：向右移动
- `Esc`：退出游戏


---

<a id="tech"></a>

## 🛠 技术实现概览

- **核心框架**：`pygame`
- **地图表示**：字符矩阵生成墙体、豆点、Ghost 出生点和道具点位
- **碰撞检测**：矩形碰撞 + 圆形接触判定
- **墙体绘制**：预渲染 `maze_surface`，提升视觉统一性与性能
- **角色动画**：按方向与状态切换帧动画
- **状态系统**：分数、生命、无敌时间、害怕时间、关卡推进


---

<a id="roadmap"></a>

## 🗺 路线图

- [ ] 增加第 3、4 关并引入不同地图主题
- [ ] 加入真实游戏录屏 `demo.gif`
- [ ] 增加开始菜单与暂停菜单
- [ ] 加入音效与背景音乐开关
- [ ] 支持本地最高分记录


---

<a id="faq"></a>

## ❓ FAQ

**Q1：运行时报 `No module named pygame` 怎么办？**  
A：执行 `pip install -r requirements.txt` 安装依赖。

**Q2：为什么蓝色 Ghost 碰到 PacMan 没反应？**  
A：这是当前规则设计，蓝色状态下双方互相无视。

**Q3：如何替换素材？**  
A：保留 `images/` 内原文件名，直接覆盖即可。

---

<p align="center">
  如果这个项目对你有帮助，欢迎 ⭐ Star 支持一下！
</p>

<p align="right"><a href="#top">⬆ 返回顶部</a></p>
