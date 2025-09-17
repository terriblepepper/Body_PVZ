#!/usr/bin/env python
# -*- coding: utf-8 -*-
import cv2 as cv
import numpy as np
import mediapipe as mp
import copy
import itertools
import pyautogui  # 导入pyautogui库控制鼠标
import time
import screeninfo  # 用于更可靠地获取屏幕分辨率
import multiprocessing as mp_proc  # 导入多进程模块，使用不同的别名避免冲突
from multiprocessing import Process, Queue, Value, Array  # 导入多进程相关工具
import ctypes  # 用于共享内存类型定义
import queue  # 导入queue模块用于异常处理

from model import KeyPointClassifier
import csv


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


def mouse_control_process(command_queue, running):
    """
    专门负责鼠标控制的子进程 - 优化为低延迟模式
    
    参数:
        command_queue: 命令队列，用于接收主进程发送的坐标和点击指令
        running: 共享变量，用于控制进程退出
    """
    # 获取屏幕分辨率
    try:
        monitors = screeninfo.get_monitors()
        screen_width = monitors[0].width
        screen_height = monitors[0].height
    except:
        screen_width, screen_height = pyautogui.size()
    
    print(f"鼠标控制进程启动 - 屏幕分辨率: {screen_width}x{screen_height}")
    
    # 鼠标控制参数
    # 移除平滑参数，直接使用精确位置
    mouse_down = False  # 跟踪鼠标按下状态
    
    # 设置鼠标移动速度为最快
    pyautogui.MINIMUM_DURATION = 0  # 设置移动持续时间为0
    pyautogui.MINIMUM_SLEEP = 0     # 设置最小休眠时间为0
    pyautogui.PAUSE = 0             # 设置命令间暂停时间为0
    
    while running.value:
        try:
            # 非阻塞方式尝试获取命令
            try:
                cmd_data = command_queue.get(block=False)
                # 解析命令数据
                cmd_type = cmd_data["type"]
                
                if cmd_type == "move":
                    # 处理移动命令 - 直接移动到目标位置，不进行平滑
                    target_x = cmd_data["x"]
                    target_y = cmd_data["y"]
                    
                    # 直接移动鼠标到目标位置
                    pyautogui.moveTo(target_x, target_y)
                    
                elif cmd_type == "mouse_down":
                    # 鼠标按下命令
                    if not mouse_down:  # 避免重复按下
                        pyautogui.mouseDown()
                        mouse_down = True
                
                elif cmd_type == "mouse_up":
                    # 鼠标释放命令
                    if mouse_down:  # 避免重复释放
                        pyautogui.mouseUp()
                        mouse_down = False
                
            except (queue.Empty, Exception) as e:
                # 队列为空，继续执行，不做任何等待
                if not isinstance(e, queue.Empty):
                    print(f"命令处理错误: {e}")
                pass
                
            # 移除休眠，让进程持续以最高优先级处理命令
                
        except Exception as e:
            print(f"鼠标控制进程错误: {str(e)}")
    
    # 确保进程退出前释放鼠标按键
    if mouse_down:
        pyautogui.mouseUp()
    
    print("鼠标控制进程已退出")


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
    # 创建进程间通信的队列和共享变量
    command_queue = mp_proc.Queue()  # 修正: 使用mp_proc作为multiprocessing的别名
    running = mp_proc.Value(ctypes.c_bool, True)  # 修正: 使用mp_proc
    
    # 创建并启动鼠标控制进程
    mouse_process = Process(target=mouse_control_process, args=(command_queue, running))
    mouse_process.daemon = True  # 将进程设为守护进程，这样主进程结束时它会自动终止
    mouse_process.start()
    
    # 获取主屏幕分辨率 (使用screeninfo库获取更可靠)
    try:
        monitors = screeninfo.get_monitors()
        screen_width = monitors[0].width  # 主屏幕宽度
        screen_height = monitors[0].height  # 主屏幕高度
    except:
        # 如果screeninfo失败，回退到pyautogui获取屏幕分辨率
        screen_width, screen_height = pyautogui.size()
    
    print(f"主进程 - 屏幕分辨率: {screen_width}x{screen_height}")
    
    # 坐标映射参数
    x_min_range = 0.0  # 手部X坐标映射最小值 (比例)
    x_max_range = 1.0  # 手部X坐标映射最大值 (比例)
    y_min_range = 0.0  # 手部Y坐标映射最小值 (比例)
    y_max_range = 1.0  # 手部Y坐标映射最大值 (比例)
    
    # 初始化鼠标位置和状态变量
    prev_x, prev_y = pyautogui.position()  # 获取鼠标初始位置
    
    # 添加变量跟踪上一次的手势状态
    last_hand_gesture = ""  # 上一次检测到的手势
    mouse_button_down = False  # 当前鼠标按钮状态
    
    # 移动平均滤波器参数 (提高平滑度)
    positions_history = []  # 存储历史位置
    history_length = 5  # 增加历史位置数量
    smoothing_factor = 0.6  # 平滑因子 (0-1)，越大越平滑
    history_weight = 0.7   # 历史数据权重
    
    # 初始化摄像头，提高分辨率
    cap = cv.VideoCapture(0)  # 打开默认摄像头
    cap_width = 640  # 提高摄像头捕获分辨率
    cap_height = 360
    cap.set(cv.CAP_PROP_FRAME_WIDTH, cap_width)  # 设置宽度
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, cap_height)  # 设置高度
    
    # 获取实际设置的分辨率
    actual_width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
    actual_height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
    print(f"摄像头分辨率: {actual_width}x{actual_height}")

    # 设置摄像头帧率
    cap.set(cv.CAP_PROP_FPS, 60)  # 尝试设置高帧率
    actual_fps = cap.get(cv.CAP_PROP_FPS)
    print(f"摄像头帧率: {actual_fps}")

    # 初始化MediaPipe Hands，调整参数提高响应性
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

    # 读取标签
    with open('model/keypoint_classifier/keypoint_classifier_label.csv',
              encoding='utf-8-sig') as f:
        keypoint_classifier_labels = csv.reader(f)
        keypoint_classifier_labels = [
            row[0] for row in keypoint_classifier_labels
        ]

    # 性能计时器
    frame_count = 0  # 帧计数器
    start_time = time.time()  # 开始时间
    fps = 0  # 帧率
    
    # 增加处理频率控制，与摄像头实际帧率匹配
    process_every_n_frames = 1  # 每一帧都处理，确保最大响应速度
    
    # 添加一个窗口状态标志
    window_visible = True
    
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
        
        # 控制处理频率 - 仅在特定帧处理手势识别
        if frame_count % process_every_n_frames == 0:
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
                        
                        # 使用多进程方式控制鼠标移动
                        if wrist_point:
                            # 归一化坐标 (0-1范围)
                            x_ratio = wrist_point[0] / actual_width
                            y_ratio = wrist_point[1] / actual_height
                            
                            # 映射到屏幕坐标 (简化计算)
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
                            
                            # 通过队列发送鼠标移动命令到子进程
                            # 设置队列最大大小为1，确保总是处理最新的坐标
                            try:
                                # 如果队列已满，先清空它
                                while not command_queue.empty():
                                    _ = command_queue.get_nowait()
                                
                                # 放入最新的移动命令
                                command_queue.put({
                                    "type": "move",
                                    "x": target_x,
                                    "y": target_y
                                })
                            except:
                                pass
                        
                            # 如果窗口可见，显示原始点和滤波点用于调试
                            if window_visible and wrist_point:
                                # 绘制原始点 (红色)
                                cv.circle(debug_image, (wrist_point[0], wrist_point[1]), 
                                        12, (0, 0, 255), -1)
                                
                                # 显示文本标注
                                cv.putText(debug_image, "Control Point", (wrist_point[0]+10, wrist_point[1]),
                                       cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv.LINE_AA)
                                        
                                # 显示滤波后的映射坐标 (绿色)
                                # 将屏幕坐标映射回摄像头坐标空间进行可视化
                                cam_x = int((target_x / screen_width) * (x_max_range - x_min_range) * actual_width + x_min_range * actual_width)
                                cam_y = int((target_y / screen_height) * (y_max_range - y_min_range) * actual_height + y_min_range * actual_height)
                                cv.circle(debug_image, (cam_x, cam_y), 
                                        8, (0, 255, 0), -1)
                                
                                # 显示文本标注
                                cv.putText(debug_image, "Filtered Point", (cam_x+10, cam_y),
                                       cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv.LINE_AA)
                        
                        # 获取手势分类
                        pre_processed_landmark_list = pre_process_landmark(landmark_list)
                        hand_sign_id = keypoint_classifier(pre_processed_landmark_list)
                        current_hand_gesture = keypoint_classifier_labels[hand_sign_id]
                        
                        # 处理鼠标按钮状态变化
                        if current_hand_gesture == "Close" and last_hand_gesture != "Close":
                            # 手势从其他变为"Close"，发送鼠标按下命令
                            command_queue.put({
                                "type": "mouse_down"
                            })
                            mouse_button_down = True
                        elif current_hand_gesture != "Close" and last_hand_gesture == "Close":
                            # 手势从"Close"变为其他，发送鼠标释放命令
                            command_queue.put({
                                "type": "mouse_up"
                            })
                            mouse_button_down = False
                        
                        # 仅当窗口可见时执行绘制操作
                        if window_visible:
                            # 计算边界框
                            brect = calc_bounding_rect(debug_image, hand_landmarks)
                            
                            # 在图像上显示鼠标控制点
                            if wrist_point:
                                cv.circle(debug_image, (wrist_point[0], wrist_point[1]), 
                                        12, (0, 0, 255), -1)  # 红色大圆点表示控制点

                            # 绘制结果 (仅绘制中心点)
                            debug_image = draw_landmarks(debug_image, landmark_list)
                            debug_image = draw_info_text(
                                debug_image,
                                brect,
                                handedness.classification[0].label,
                                current_hand_gesture
                            )
            
            # 如果没有检测到手，但上次是"Close"状态，需要释放鼠标按键
            if not hand_detected and last_hand_gesture == "Close" and mouse_button_down:
                command_queue.put({
                    "type": "mouse_up"
                })
                mouse_button_down = False
                current_hand_gesture = ""
            
            # 更新上一次的手势状态
            last_hand_gesture = current_hand_gesture

        # 只有在窗口可见时才显示图像和信息
        if window_visible:
            # 显示FPS和控制提示
            cv.putText(debug_image, f"FPS: {fps:.1f}", (10, 30), 
                      cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 4, cv.LINE_AA)
            cv.putText(debug_image, f"FPS: {fps:.1f}", (10, 30), 
                       cv.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv.LINE_AA)
            cv.putText(debug_image, "Hand Gesture Mouse Control", (10, 60), 
                       cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 4, cv.LINE_AA)
            cv.putText(debug_image, "Hand Gesture Mouse Control", (10, 60), 
                       cv.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv.LINE_AA)
            cv.putText(debug_image, "'Close' gesture for mouse down", (10, 90), 
                       cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 4, cv.LINE_AA)
            cv.putText(debug_image, "'Close' gesture for mouse down", (10, 90), 
                       cv.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv.LINE_AA)
            cv.putText(debug_image, f"Mouse Down: {mouse_button_down}", (10, 120), 
                       cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 4, cv.LINE_AA)
            cv.putText(debug_image, f"Mouse Down: {mouse_button_down}", (10, 120), 
                       cv.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv.LINE_AA)
            cv.putText(debug_image, "Press ESC to quit", (10, 150), 
                       cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 4, cv.LINE_AA)
            cv.putText(debug_image, "Press ESC to quit", (10, 150), 
                       cv.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv.LINE_AA)
            
            try:
                # 显示图像
                cv.imshow('Hand Gesture Mouse Control', debug_image)
            except:
                # 如果显示失败，可能窗口已关闭或最小化
                window_visible = False
        else:
            # 尝试创建一个窗口 (如果窗口被关闭)
            try:
                cv.namedWindow('Hand Gesture Mouse Control', cv.WINDOW_AUTOSIZE)
                window_visible = True
            except:
                pass
        
        # 无论窗口是否可见，都检测ESC键退出
        key = cv.waitKey(1)  # 从10ms减少到1ms
        if key == 27:  # ESC
            break

    # 结束时，设置共享变量通知子进程退出
    running.value = False
    # 等待子进程完成
    mouse_process.join(timeout=1.0)
    
    cap.release()
    cv.destroyAllWindows()


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
        return 2 * n / max_value
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


def draw_info_text(image, brect, handedness, hand_sign_text):
    cv.rectangle(image, (brect[0], brect[1]), (brect[2], brect[1] - 22),
                (0, 0, 0), -1)

    info_text = handedness
    if hand_sign_text != "":
        info_text = info_text + ': ' + hand_sign_text
    cv.putText(image, info_text, (brect[0] + 5, brect[1] - 4),
              cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv.LINE_AA)
    return image


if __name__ == '__main__':
    # 适配Windows多进程
    mp_proc.freeze_support()  # 修正: 使用mp_proc
    main()