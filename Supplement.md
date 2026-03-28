PacMan 期末大作业

运行说明:

- 安装依赖: `pip install -r requirements.txt`
- 运行: 在项目根目录下执行 `python src\\main.py`

说明:

- 使用 `pygame` 实现一个简化版 PacMan 原型，贴图动画全部来自 `images/` 目录。
- 至少两关 (`Game.levels` 中已准备两个难度)，通关后会依次切换。
- 控制: 方向键控制 PacMan 移动。
- 玩法: 吃掉所有点和能量果实即可过关，同时利用 FrightFruit 让幽灵进入害怕状态。
- 墙体使用蓝色直线段勾勒，与示例截图风格相同，FrightFruit 使用 `images/FrightFruit.png`。
- PacMan 被幽灵撞到只会扣除生命并继续移动，不会重置位置，同时拥有短暂无敌避免连续扣血。
- 害怕 (蓝色) 状态下的幽灵与 PacMan 相遇时彼此无视，玩家无法吃掉幽灵。

资源:

- `images/` 目录下包含学校提供的所有素材 (PacMan1-4、Ghost、GhostScared、FrightFruit 等)。程序会自动加载这些文件，请勿删除或改名，如需替换请保持同名覆盖。
