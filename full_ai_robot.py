import json
import rclpy
import threading
import time
from rclpy.node import Node
from pymoveit2 import MoveIt2
from openai import OpenAI

# ================= 1. 大模型大脑配置 =================
# 👇 这里换成你真实的 Key
API_KEY = "YOUR_DEEPSEEK_API_KEY_HERE" 

# 注意这里加了 /v1
client = OpenAI(api_key=API_KEY, base_url="https://api.deepseek.com/v1")

def get_coordinates_from_ai(command):
    print(f"\n🧠 正在呼叫大模型，解析指令: '{command}' ...")
    try:
        response = client.chat.completions.create(
            model="deepseek-flash",
            messages=[
                # 👇 确保这里面的内容都在！
                {"role": "system", "content": "你是一个机械臂控制器。请将用户指令转换为JSON格式的三维坐标，格式为 {\"x\": 0.3, \"y\": 0.0, \"z\": 0.3}。坐标范围x在0.2-0.6，y在-0.4-0.4，z在0.1-0.5之间。只输出JSON，绝对不要输出其他文字。"},
                {"role": "user", "content": command}
            ],
            temperature=0.1
        )
        result_text = response.choices[0].message.content
        # 清理可能出现的 markdown 符号
        result_text = result_text.replace('```json', '').replace('```', '').strip()
        
        coords = json.loads(result_text)
        print(f"✅ 解析成功！目标坐标 -> X:{coords['x']}, Y:{coords['y']}, Z:{coords['z']}")
        return coords
    except Exception as e:
        print(f"❌ 大模型返回的格式有误: {e}")
        return None

# ================= 2. 后台 ROS 2 通信线程 =================
def ros_spin_thread(node):
    try:
        rclpy.spin(node) 
    except Exception:
        pass

def main():
    rclpy.init()
    my_node = Node('ai_robot_controller') 
    
    spin_thread = threading.Thread(target=ros_spin_thread, args=(my_node,), daemon=True)
    spin_thread.start()

    moveit2 = MoveIt2(
        node=my_node,
        joint_names=['panda_joint1', 'panda_joint2', 'panda_joint3', 'panda_joint4', 'panda_joint5', 'panda_joint6', 'panda_joint7'],
        base_link_name='panda_link0',
        end_effector_name='panda_hand',
        group_name='panda_arm',
    )
    
    print("🤖 机械臂控制系统已启动，等待指令...")
    
    while True:
        cmd = input("\n🗣️ 请输入指令 (例如: '把机械臂往右边移一点', 输入 'q' 退出): ")
        if cmd.lower() == 'q':
            break
            
        coords = get_coordinates_from_ai(cmd)
        
        if coords:
            print("🚀 正在发送指令给 MoveIt2，开始规划路径...")
            target_pose = {
                "position": [float(coords['x']), float(coords['y']), float(coords['z'])],
                "quat_xyzw": [0.0, 0.0, 0.0, 1.0] 
            }
            
            moveit2.move_to_pose(**target_pose)
            print("⏳ 等待规划与执行 (请观察 RViz 画面)...")
            time.sleep(3.0) 
            print("✅ 动作发送完毕！")
            
    my_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
