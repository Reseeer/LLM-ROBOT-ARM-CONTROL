# LLM-Robot-Arm-Control

基于大语言模型（DeepSeek-flash）与 ROS 2 的具身智能机械臂控制系统。

## 核心功能
用户输入自然语言，大模型解析为 JSON 坐标，底层驱动 MoveIt 2 实现无碰撞的机械臂运动规划。

## 难点攻克
1. 多线程分离，解决 Python `input` 阻塞 ROS 2 通信。
2. 修改 SRDF 的 `disable_collisions`，解决底层物理自碰撞报错。

## 技术栈
Python, ROS 2, MoveIt 2, DeepSeek API
