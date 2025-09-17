#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import cv2 as cv
import numpy as np
import mediapipe as mp
import copy
import itertools
import time
import screeninfo  # 用于更可靠地获取屏幕分辨率
import socket  # 导入socket库用于UDP通信
import json  # 导入json库用于数据格式化
import multiprocessing as multi_proc  # 导入多进程库
import ctypes  # 用于创建共享内存类型
from model import KeyPointClassifier
from model import PointHistoryClassifier  # 新增历史点分类器
import csv
from collections import deque  # 新增deque用于历史点存储
from collections import Counter  # 新增Counter用于统计

def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--device", type=int, default=0)
    parser.add_argument("--width", help='cap width', type=int, default=960)
    parser.add_argument("--height", help='cap height', type=int, default=540)

    parser.add_argument('--use_static_image_mode', action='store_true')
    parser.add_argument("--min_detection_confidence",
                        help='min_detection_confidence',
                        type=float,
                        default=0.7)
    parser.add_argument("--min_tracking_confidence",
                        help='min_tracking_confidence',
                        type=int,
                        default=0.5)

    args = parser.parse_args()

    return args

def calc_center_point(landmark_list, point_indices=[0, 4, 8, 12, 16, 20]):
    """计算指定关键点的中心坐标"""
    # 如果关键点列表为空，返回None
    if not landmark_list:
        return None
        
    x_sum = 0
    y_sum = 0
    # 遍历指定的关键点索引，计算它们的x和y坐标总和
    for index in point_indices:
        if index < len(landmark_list):
            x_sum += landmark_list[index][0]
            y_sum += landmark_list[index][1]
    
    # 返回这些点的中心坐标（取平均值）
    return [int(x_sum / len(point_indices)), int(y_sum / len(point_indices))]


def pre_process_point_history(image, point_history):
    """
    处理历史点轨迹数据
    
    参数:
        image: 输入图像
        point_history: 历史点列表
    
    返回:
        处理后的历史点列表
    """
    image_width, image_height = image.shape[1], image.shape[0]

    temp_point_history = copy.deepcopy(point_history)

    # 转换为相对坐标
    base_x, base_y = 0, 0
    for index, point in enumerate(temp_point_history):
        if index == 0:
            base_x, base_y = point[0], point[1]

        temp_point_history[index][0] = (temp_point_history[index][0] -
                                        base_x) / image_width
        temp_point_history[index][1] = (temp_point_history[index][1] -
                                        base_y) / image_height

    # 转换为一维列表
    temp_point_history = list(
        itertools.chain.from_iterable(temp_point_history))

    return temp_point_history


# 修改UDP发送函数，使其在单独的进程中运行
def udp_sender_process(shared_data, exit_flag):
    """
    UDP发送进程，循环发送共享数据
    
    参数:
        shared_data: 包含共享状态的字典
        exit_flag: 退出标志
    """
    # 创建UDP套接字
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # 设置目标地址(本地主机)和端口(12345)
    target_addr = ('127.0.0.1', 12345)
    print(f"UDP发送进程已启动，目标地址: {target_addr}")
    
    try:
        while not exit_flag.value:
            # 检查是否需要发送数据
            if shared_data['trigger_send'].value:
                # 创建JSON数据包 
                data = {
                    "x": shared_data['x'].value,
                    "y": shared_data['y'].value,
                    "hand_gesture": shared_data['gesture'].value.decode('utf-8').strip().lower(),
                    "finger_gesture": shared_data['finger_gesture'].value.decode('utf-8').strip().lower()
                }
                
                # 转换为JSON字符串并编码为bytes
                json_data = json.dumps(data).encode('utf-8')
                
                try:
                    # 发送数据包
                    udp_socket.sendto(json_data, target_addr)
                    # 重置触发标志
                    with shared_data['trigger_send'].get_lock():
                        shared_data['trigger_send'].value = False
                except Exception as e:
                    print(f"发送UDP数据包错误: {e}")
            
            # 短暂休眠以减少CPU使用率，但保持响应性
            time.sleep(0.001)
    
    except KeyboardInterrupt:
        pass
    finally:
        # 发送最终退出消息
        try:
            exit_data = {
                "x": shared_data['x'].value,
                "y": shared_data['y'].value,
                "hand_gesture": "exit",
                "finger_gesture": "none"
            }
            udp_socket.sendto(json.dumps(exit_data).encode('utf-8'), target_addr)
        except:
            pass
        
        # 关闭套接字
        udp_socket.close()
        print("UDP发送进程已终止")


def apply_coordinate_filter(new_point, history, smoothing_factor=0.5, history_weight=0.8):
    """
    对坐标进行双重滤波，减少抖动
    
    参数:
        new_point: 新获取的坐标点 [x, y]
        history: 历史坐标点列表
        smoothing_factor: 低通滤波平滑因子 (0-1)，越大越平滑但响应越慢
        history_weight: 历史值权重
    
    返回:
        平滑后的坐标点 [x, y]
    """
    # 如果历史为空，直接返回新点
    if not history:
        return new_point
    
    # 第一步：移动平均滤波 - 计算历史点的平均值
    avg_x = sum(p[0] for p in history) / len(history)
    avg_y = sum(p[1] for p in history) / len(history)
    avg_point = [avg_x, avg_y]
    
    # 第二步：低通滤波 - 将新点与历史平均按权重融合
    # 新坐标 = 历史平均值*历史权重 + 新值*(1-历史权重)
    filtered_x = avg_point[0] * history_weight + new_point[0] * (1 - history_weight)
    filtered_y = avg_point[1] * history_weight + new_point[1] * (1 - history_weight)
    
    # 第三步：应用额外平滑因子，让值更接近历史平均（可选）
    # 进一步平滑 = 当前值*平滑因子 + 新值*(1-平滑因子)
    result_x = filtered_x * smoothing_factor + new_point[0] * (1 - smoothing_factor)
    result_y = filtered_y * smoothing_factor + new_point[1] * (1 - smoothing_factor)
    
    return [int(result_x), int(result_y)]


def main():
    # 创建共享状态变量
    shared_data = {
        'x': multi_proc.Value(ctypes.c_double, 0.5),  # 归一化X坐标，初始为0.5
        'y': multi_proc.Value(ctypes.c_double, 0.5),  # 归一化Y坐标，初始为0.5
        'gesture': multi_proc.Array(ctypes.c_char, b'Idle'.ljust(20)),  # 手势类型，初始为Idle，固定长度20字节
        'finger_gesture': multi_proc.Array(ctypes.c_char, b'None'.ljust(20)),  # 新增：手指轨迹手势
        'trigger_send': multi_proc.Value(ctypes.c_bool, False),  # 新增：发送触发器
    }
    
    # 退出标志
    exit_flag = multi_proc.Value(ctypes.c_bool, False)
    
    # 启动UDP发送进程
    udp_process = multi_proc.Process(target=udp_sender_process, args=(shared_data, exit_flag))
    udp_process.daemon = True  # 设置为守护进程，主进程退出时自动终止
    udp_process.start()
    print("UDP发送进程已启动")
    
    # 获取参考屏幕分辨率
    try:
        monitors = screeninfo.get_monitors()
        screen_width = monitors[0].width  # 主屏幕宽度
        screen_height = monitors[0].height  # 主屏幕高度
    except:         
        # 如果screeninfo失败，设置默认分辨率
        screen_width, screen_height = 1920, 1080
    
    print(f"参考屏幕分辨率: {screen_width}x{screen_height}")
    
    # 修改: 设置更窄的有效操作区域 
    # 这些值表示有效操作区域在整个摄像头视图中的比例
    x_min_range = 0.2  # 左边界 
    x_max_range = 0.8  # 右边界 
    y_min_range = 0.3  # 上边界 
    y_max_range = 0.7 # 下边界 
    
    print(f"有效操作区域: 水平 {x_min_range:.1f}-{x_max_range:.1f}, 垂直 {y_min_range:.1f}-{y_max_range:.1f}")
    
    # 初始化状态变量
    last_hand_gesture = ""  # 上一次检测到的手势
    
    # 添加变量存储最后有效的手部位置 (默认为屏幕中心)
    last_valid_position = (0.5, 0.5)  # 归一化坐标 (0-1)
    last_valid_raw_position = (screen_width // 2, screen_height // 2)  # 原始像素坐标
    
    # 移动平均滤波器参数 (提高平滑度)
    positions_history = []  # 存储历史位置
    history_length = 5  # 增加历史位置数量
    smoothing_factor = 0.6  # 平滑因子 (0-1)，越大越平滑
    history_weight = 0.7   # 历史数据权重
    
    # 添加历史点跟踪 - 类似app.py
    point_history = deque(maxlen=16)  # 存储16个历史点
    finger_gesture_history = deque(maxlen=16)  # 存储手指手势历史

    # Argument parsing #################################################################
    args = get_args()
    cap_device = args.device
    cap_width = args.width
    cap_height = args.height

    # Camera preparation ###############################################################
    cap = cv.VideoCapture(cap_device)
    cap.set(cv.CAP_PROP_FRAME_WIDTH, cap_width)
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, cap_height)
    
    # 获取实际设置的分辨率
    actual_width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
    actual_height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
    print(f"摄像头分辨率: {actual_width}x{actual_height}")

    # 设置摄像头帧率
    cap.set(cv.CAP_PROP_FPS, 60)  # 尝试设置高帧率
    actual_fps = cap.get(cv.CAP_PROP_FPS)
    print(f"摄像头帧率: {actual_fps}")

    # 初始化MediaPipe Hands，调整参数
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=False,  # 动态模式，适合实时视频流
        max_num_hands=1,  # 最多检测一只手
        min_detection_confidence=0.5,  # 最小检测置信度
        min_tracking_confidence=0.5,  # 最小跟踪置信度
        model_complexity=1  # 使用较高复杂度的模型
    )

    # 加载关键点分类器
    keypoint_classifier = KeyPointClassifier()
    
    # 加载历史点分类器
    point_history_classifier = PointHistoryClassifier()

    # 读取标签
    with open('model/keypoint_classifier/keypoint_classifier_label.csv',
              encoding='utf-8-sig') as f:
        keypoint_classifier_labels = csv.reader(f)
        keypoint_classifier_labels = [
            row[0] for row in keypoint_classifier_labels
        ]
        
    # 读取历史点分类器标签
    with open('model/point_history_classifier/point_history_classifier_label.csv',
              encoding='utf-8-sig') as f:
        point_history_classifier_labels = csv.reader(f)
        point_history_classifier_labels = [
            row[0] for row in point_history_classifier_labels
        ]

    # 性能计时器
    frame_count = 0  # 帧计数器
    start_time = time.time()  # 开始时间
    fps = 0  # 帧率

    
    # 添加一个窗口状态标志
    window_visible = True
    
    try:
        while True:
            # 获取帧
            ret, image = cap.read()  # 从摄像头读取一帧图像
            if not ret:
                break  # 如果读取失败，退出循环
            frame_count += 1  # 增加帧计数器
            
            # 计算FPS
            current_time = time.time()
            if (current_time - start_time) > 1:  # 每秒更新一次FPS
                fps = frame_count / (current_time - start_time)
                frame_count = 0  # 重置帧计数器
                start_time = current_time  # 更新开始时间
                
            image = cv.flip(image, 1)  # 镜像显示图像
            
            # 创建调试图像的副本 (仅当窗口可见时)
            if window_visible:
                # 使用浅拷贝而不是深拷贝，提高性能
                debug_image = image.copy()  # 替换copy.deepcopy减少性能开销
            

            # 转换为RGB格式并处理
            image = cv.cvtColor(image, cv.COLOR_BGR2RGB)  # 转换为RGB格式
            image.flags.writeable = False  # 设置为只读以提高性能
            results = hands.process(image)  # 使用MediaPipe Hands处理图像
            image.flags.writeable = True  # 恢复为可写
                
            # 初始化当前帧的手势检测
            current_hand_gesture = ""
            hand_detected = False
                
            # 处理手势识别结果
            if results.multi_hand_landmarks is not None:
                for hand_landmarks, handedness in zip(results.multi_hand_landmarks,
                                                      results.multi_handedness):
                    # 只处理右手
                    if handedness.classification[0].label == 'Right':
                        hand_detected = True
                        # 计算关键点列表 - 优化版本
                        landmark_list = calc_landmark_list(image, hand_landmarks)
                            
                        # 修改：使用索引为0的点(手腕点)而不是中心点
                        wrist_point = None
                        if len(landmark_list) > 0:
                            wrist_point = landmark_list[0]  # 索引0是手腕点
                            
                        # 处理检测到的手腕点
                        if wrist_point:
                            # 归一化坐标 (0-1范围内的原始值)
                            x_ratio = wrist_point[0] / actual_width
                            y_ratio = wrist_point[1] / actual_height
                                
                            # 判断是否在有效操作区域内
                            in_valid_area = (x_min_range <= x_ratio <= x_max_range and 
                                            y_min_range <= y_ratio <= y_max_range)
                                
                            # 将有效区域(0.2-0.8)重新映射为全屏(0-1)
                            # 映射公式: newValue = (value - oldMin) / (oldMax - oldMin)
                            if in_valid_area:
                                # 重新映射x坐标 (0.2-0.8) -> (0-1)
                                x_mapped = (x_ratio - x_min_range) / (x_max_range - x_min_range)
                                # 重新映射y坐标 (0.2-0.8) -> (0-1)
                                y_mapped = (y_ratio - y_min_range) / (y_max_range - y_min_range)
                            else:
                                # 如果在有效区域外，取边界值
                                x_mapped = max(0, min(1, (x_ratio - x_min_range) / (x_max_range - x_min_range)))
                                y_mapped = max(0, min(1, (y_ratio - y_min_range) / (y_max_range - y_min_range)))
                                
                            # 直接计算目标坐标，确保精确性
                            raw_target_x = int(x_mapped * screen_width)
                            raw_target_y = int(y_mapped * screen_height)
                                
                            # 应用坐标滤波减少抖动
                            raw_point = [raw_target_x, raw_target_y]
                                
                            # 添加当前原始点到历史记录
                            positions_history.append(raw_point)
                            # 保持历史记录在指定长度
                            if len(positions_history) > history_length:
                                positions_history.pop(0)
                                    
                            # 应用滤波器获得平滑坐标
                            filtered_point = apply_coordinate_filter(
                                raw_point, 
                                positions_history,
                                smoothing_factor,
                                history_weight
                            )
                                
                            target_x = filtered_point[0]
                            target_y = filtered_point[1]
                                
                            # 发送归一化的坐标值(0-1范围)给Qt程序
                            norm_x = target_x / screen_width
                            norm_y = target_y / screen_height
                                
                            # 更新最后有效位置
                            last_valid_position = (norm_x, norm_y)
                            last_valid_raw_position = (target_x, target_y)
                                
                            # 如果窗口可见，显示原始点和滤波点用于调试
                            if window_visible and wrist_point:
                                # 绘制原始点 (红色)
                                cv.circle(debug_image, (wrist_point[0], wrist_point[1]), 
                                        12, (0, 0, 255), -1)
                                    
                                # 显示文本标注
                                cv.putText(debug_image, "Control Point", (wrist_point[0]+10, wrist_point[1]),
                                        cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv.LINE_AA)
                                    
                                # 显示有效操作区域的边界 (蓝色矩形)
                                area_left = int(x_min_range * actual_width)
                                area_right = int(x_max_range * actual_width)
                                area_top = int(y_min_range * actual_height)
                                area_bottom = int(y_max_range * actual_height)
                                    
                                # 绘制有效操作区域边框
                                cv.rectangle(debug_image, 
                                            (area_left, area_top), 
                                            (area_right, area_bottom), 
                                            (255, 0, 0), 2)
                                    
                                # 添加区域标签
                                cv.putText(debug_image, "Valid Control Area", 
                                              (area_left + 10, area_top + 20),
                                            cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1, cv.LINE_AA)
                                    
                                # 显示是否在有效区域内
                                status_color = (0, 255, 0) if in_valid_area else (0, 0, 255)  # 绿色或红色
                                status_text = "In Control Area" if in_valid_area else "Outside Control Area"
                                cv.putText(debug_image, status_text, 
                                            (wrist_point[0]+10, wrist_point[1]+20),
                                            cv.FONT_HERSHEY_SIMPLEX, 0.5, status_color, 1, cv.LINE_AA)
                                            
                                # 显示滤波后的映射坐标 (绿色)
                                # 将屏幕坐标映射回摄像头坐标空间进行可视化
                                cam_x = int((x_mapped * (x_max_range - x_min_range) + x_min_range) * actual_width)
                                cam_y = int((y_mapped * (y_max_range - y_min_range) + y_min_range) * actual_height)
                                cv.circle(debug_image, (cam_x, cam_y), 
                                        8, (0, 255, 0), -1)
                                    
                                # 显示文本标注
                                cv.putText(debug_image, "Mapped Point", (cam_x+10, cam_y),
                                        cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv.LINE_AA)
                            
                        # 获取手势分类
                        pre_processed_landmark_list = pre_process_landmark(landmark_list)
                        hand_sign_id = keypoint_classifier(pre_processed_landmark_list)
                        current_hand_gesture = keypoint_classifier_labels[hand_sign_id]
                        
                        # 处理历史点 - 类似app.py中的逻辑
                        if hand_sign_id == 2:  # Point gesture - 假设2是指向手势
                            point_history.append(landmark_list[8])  # 使用食指指尖
                        else:
                            point_history.append([0, 0])  # 非指向手势时添加空点
                        
                        # 处理历史点分类
                        pre_processed_point_history_list = pre_process_point_history(image, point_history)
                        finger_gesture_id = 0
                        
                        # 只有当积累了足够的历史点时才进行分类
                        if len(pre_processed_point_history_list) == 32:  # 16点 * 2坐标 = 32
                            finger_gesture_id = point_history_classifier(pre_processed_point_history_list)
                            
                        # 添加到手势历史
                        finger_gesture_history.append(finger_gesture_id)
                        
                        # 获取最常见的手势ID
                        most_common_fg_id = Counter(finger_gesture_history).most_common()
                        if most_common_fg_id:
                            finger_gesture_text = point_history_classifier_labels[most_common_fg_id[0][0]]
                        else:
                            finger_gesture_text = "None"
                            
                        # 更新共享状态中的手指手势
                        with shared_data['finger_gesture'].get_lock():
                            gesture_bytes = finger_gesture_text.encode('utf-8')[:19]
                            shared_data['finger_gesture'].value = gesture_bytes.ljust(20, b' ')
                            
                            
                        # 更新共享状态
                        if wrist_point:  # 只有当检测到手腕点时才更新坐标
                            # 更新所有状态值
                            with shared_data['x'].get_lock():
                                shared_data['x'].value = norm_x
                            with shared_data['y'].get_lock():
                                shared_data['y'].value = norm_y
                            with shared_data['gesture'].get_lock():
                                # 截断并填充字符串，确保固定长度
                                gesture_bytes = current_hand_gesture.encode('utf-8')[:19]
                                shared_data['gesture'].value = gesture_bytes.ljust(20, b' ')
                                
                            # 触发数据发送
                            with shared_data['trigger_send'].get_lock():
                                shared_data['trigger_send'].value = True
                            
                        # 仅当窗口可见时执行绘制操作
                        if window_visible:
                            # 计算边界框
                            brect = calc_bounding_rect(debug_image, hand_landmarks)
                                
                            # 绘制结果
                            debug_image = draw_landmarks(debug_image, landmark_list)
                            debug_image = draw_info_text(
                                debug_image,
                                brect,
                                handedness.classification[0].label,
                                current_hand_gesture,
                                point_history_classifier_labels[most_common_fg_id[0][0]] if most_common_fg_id else "None"
                            )
                            
                            # 绘制历史点轨迹
                            debug_image = draw_point_history(debug_image, point_history)
                
            # 如果没有检测到手，但上次是"Close"状态或需要保持位置状态
            if not hand_detected:
                    
                # 使用最后有效位置
                with shared_data['gesture'].get_lock():
                    idle_bytes = b'Idle'
                    shared_data['gesture'].value = idle_bytes.ljust(20, b' ')
                    
                # 如果窗口可见，显示最后有效位置和有效操作区域
                if window_visible:
                    # 显示有效操作区域的边界 (蓝色矩形)
                    area_left = int(x_min_range * actual_width)
                    area_right = int(x_max_range * actual_width)
                    area_top = int(y_min_range * actual_height)
                    area_bottom = int(y_max_range * actual_height)
                                    
                    # 绘制有效操作区域边框
                    cv.rectangle(debug_image, 
                                (area_left, area_top), 
                                (area_right, area_bottom), 
                                (255, 0, 0), 2)
                                    
                    # 添加区域标签
                    cv.putText(debug_image, "Valid Control Area", 
                                (area_left + 10, area_top + 20),
                                cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1, cv.LINE_AA)
                        
                    # 将最后有效位置显示在画面上 (黄色)
                    # 注意：这里需要反向映射回摄像头坐标空间
                    x_ratio_back = (last_valid_position[0] * (x_max_range - x_min_range) + x_min_range)
                    y_ratio_back = (last_valid_position[1] * (y_max_range - y_min_range) + y_min_range)
                        
                    last_pos_cam_x = int(x_ratio_back * actual_width)
                    last_pos_cam_y = int(y_ratio_back * actual_height)
                        
                    # 绘制最后有效位置点 (黄色，表示保持的位置)
                    cv.circle(debug_image, (last_pos_cam_x, last_pos_cam_y), 
                                15, (0, 255, 255), -1)  # 黄色大圆点
                    cv.putText(debug_image, "Last Position", (last_pos_cam_x+10, last_pos_cam_y),
                                cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1, cv.LINE_AA)
                
                # 添加空点到历史
                point_history.append([0, 0])
                
                # 重置手指手势
                with shared_data['finger_gesture'].get_lock():
                    none_bytes = b'None'
                    shared_data['finger_gesture'].value = none_bytes.ljust(20, b' ')
                
                # 触发数据发送 - 即使没有手也发送当前状态
                with shared_data['trigger_send'].get_lock():
                    shared_data['trigger_send'].value = True
                
            # 更新上一次的手势状态
            last_hand_gesture = current_hand_gesture

            # 只有在窗口可见时才显示图像和信息
            if window_visible:
                # 显示FPS和控制提示
                cv.putText(debug_image, f"FPS: {fps:.1f}", (10, 30), 
                          cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 4, cv.LINE_AA)
                cv.putText(debug_image, f"FPS: {fps:.1f}", (10, 30), 
                           cv.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv.LINE_AA)
                cv.putText(debug_image, "Hand Gesture UDP Control (Multi-Process)", (10, 60), 
                           cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 4, cv.LINE_AA)
                cv.putText(debug_image, "Hand Gesture UDP Control (Multi-Process)", (10, 60), 
                           cv.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv.LINE_AA)
                
                # 显示手指手势信息
                finger_gesture_text = shared_data['finger_gesture'].value.decode('utf-8').strip()
                gesture_info_text = f"Finger Gesture: {finger_gesture_text}"
                cv.putText(debug_image, gesture_info_text, (10, 90), 
                           cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 4, cv.LINE_AA)
                cv.putText(debug_image, gesture_info_text, (10, 90), 
                           cv.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv.LINE_AA)
                
                cv.putText(debug_image, "Press ESC to quit", (10, 120), 
                           cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 4, cv.LINE_AA)
                cv.putText(debug_image, "Press ESC to quit", (10, 120), 
                           cv.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv.LINE_AA)
                
                # 添加一行显示位置信息
                position_text = f"Position: ({last_valid_position[0]:.2f}, {last_valid_position[1]:.2f})"
                cv.putText(debug_image, position_text, (10, 150), 
                          cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 4, cv.LINE_AA)
                cv.putText(debug_image, position_text, (10, 150), 
                           cv.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv.LINE_AA)
                
                # 添加一行显示映射信息
                mapping_text = f"Mapping: Camera({x_min_range:.1f}-{x_max_range:.1f}) → Screen(0-1)"
                cv.putText(debug_image, mapping_text, (10, 180), 
                          cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 4, cv.LINE_AA)
                cv.putText(debug_image, mapping_text, (10, 180), 
                           cv.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv.LINE_AA)
                
                try:
                    # 显示图像
                    cv.imshow('Hand Gesture UDP Control', debug_image)
                except:
                    # 如果显示失败，可能窗口已关闭或最小化
                    window_visible = False
            else:
                # 尝试创建一个窗口 (如果窗口被关闭)
                try:
                    cv.namedWindow('Hand Gesture UDP Control', cv.WINDOW_AUTOSIZE)
                    window_visible = True
                except:
                    pass
            
            # 无论窗口是否可见，都检测ESC键退出
            key = cv.waitKey(1)  # 从10ms减少到1ms
            if key == 27:  # ESC
                break

    except KeyboardInterrupt:
        print("接收到键盘中断，程序即将退出")
    finally:
        # 设置退出标志
        exit_flag.value = True
        
        # 等待UDP进程结束
        print("正在等待UDP发送进程结束...")
        udp_process.join(timeout=2.0)
        if udp_process.is_alive():
            print("UDP进程未响应，强制终止")
            udp_process.terminate()
        
        # 关闭资源
        cap.release()
        cv.destroyAllWindows()
        print("程序已正常退出")


def calc_bounding_rect(image, landmarks):
    image_width, image_height = image.shape[1], image.shape[0]
    landmark_array = np.empty((0, 2), int)

    for _, landmark in enumerate(landmarks.landmark):
        landmark_x = min(int(landmark.x * image_width), image_width - 1)
        landmark_y = min(int(landmark.y * image_height), image_height - 1)
        landmark_point = [np.array((landmark_x, landmark_y))]
        landmark_array = np.append(landmark_array, landmark_point, axis=0)

    x, y, w, h = cv.boundingRect(landmark_array)
    return [x, y, x + w, y + h]


def calc_landmark_list(image, landmarks):
    image_width, image_height = image.shape[1], image.shape[0]
    landmark_point = []

    for _, landmark in enumerate(landmarks.landmark):
        landmark_x = min(int(landmark.x * image_width), image_width - 1)
        landmark_y = min(int(landmark.y * image_height), image_height - 1)
        landmark_point.append([landmark_x, landmark_y])

    return landmark_point


def pre_process_landmark(landmark_list):
    temp_landmark_list = copy.deepcopy(landmark_list)

    # 转换为相对坐标
    base_x, base_y = 0, 0
    for index, landmark_point in enumerate(temp_landmark_list):
        if index == 0:
            base_x, base_y = landmark_point[0], landmark_point[1]
        temp_landmark_list[index][0] = temp_landmark_list[index][0] - base_x
        temp_landmark_list[index][1] = temp_landmark_list[index][1] - base_y

    # 转换为一维列表
    temp_landmark_list = list(itertools.chain.from_iterable(temp_landmark_list))

    # 归一化
    max_value = max(list(map(abs, temp_landmark_list)))
    def normalize_(n):
        return n / max_value
    temp_landmark_list = list(map(normalize_, temp_landmark_list))

    return temp_landmark_list


def draw_landmarks(image, landmark_point):
    # 只绘制手腕点，移除其他关键点的绘制
    if len(landmark_point) > 0:
        # 绘制手腕点（作为控制点）
        wrist_point = landmark_point[0]  # 索引0是手腕点
        cv.circle(image, (wrist_point[0], wrist_point[1]), 12, (0, 0, 255), -1)  # 红色大圆点表示控制点
    return image


def draw_bounding_rect(image, brect):
    cv.rectangle(image, (brect[0], brect[1]), (brect[2], brect[3]),
                (0, 0, 0), 1)
    return image


def draw_info_text(image, brect, handedness, hand_sign_text, finger_gesture_text=""):
    cv.rectangle(image, (brect[0], brect[1]), (brect[2], brect[1] - 22),
                (0, 0, 0), -1)

    info_text = handedness
    if hand_sign_text != "":
        info_text = info_text + ': ' + hand_sign_text
    cv.putText(image, info_text, (brect[0] + 5, brect[1] - 4),
              cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv.LINE_AA)
    
    # 在手部边界框下方显示手指手势
    if finger_gesture_text != "" and finger_gesture_text != "None":
        cv.rectangle(image, (brect[0], brect[1] + 10), (brect[2], brect[1] + 40),
                    (0, 0, 0), -1)
        cv.putText(image, "Finger: " + finger_gesture_text, (brect[0] + 5, brect[1] + 30),
                  cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv.LINE_AA)
    
    return image


# 添加函数用于绘制历史点轨迹
def draw_point_history(image, point_history):
    for index, point in enumerate(point_history):
        if point[0] != 0 and point[1] != 0:
            cv.circle(image, (point[0], point[1]), 1 + int(index / 2),
                      (152, 251, 152), 2)
    return image


if __name__ == '__main__':
    main()