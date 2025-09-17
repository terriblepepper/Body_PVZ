#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv
import numpy as np
from sklearn.metrics import accuracy_score, recall_score, precision_score, f1_score, confusion_matrix
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import matplotlib
import datetime
import json
from collections import Counter

# 设置matplotlib支持中文显示
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'KaiTi', 'SimSun', 'Arial Unicode MS']  # 中文字体
matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

from model import KeyPointClassifier
from model import PointHistoryClassifier


def load_labels(model_type):
    """
    加载标签文件
    """
    if model_type == "keypoint":
        label_path = 'model/keypoint_classifier/keypoint_classifier_label.csv'
    else:
        label_path = 'model/point_history_classifier/point_history_classifier_label.csv'
    
    with open(label_path, encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        labels = [row[0] for row in reader]
    
    return labels


def create_evaluation_directory(model_type):
    """
    创建日志文件夹，用于存放评估结果
    """
    # 生成时间戳
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    directory = f'evaluation/eval_{model_type}_{timestamp}'
    
    # 创建目录
    os.makedirs(directory, exist_ok=True)
    
    return directory


def evaluate_model(y_true, y_pred, labels, model_type, csv_path):
    """
    评估模型性能并保存结果
    """
    # 创建评估结果文件夹
    eval_dir = create_evaluation_directory(model_type)
    
    # 获取CSV文件的绝对路径
    csv_absolute_path = os.path.abspath(csv_path)
    
    # 计算总体指标
    accuracy = accuracy_score(y_true, y_pred)
    recall = recall_score(y_true, y_pred, average='macro', zero_division=0)
    precision = precision_score(y_true, y_pred, average='macro', zero_division=0)
    f1 = f1_score(y_true, y_pred, average='macro', zero_division=0)
    
    # 统计样本数量
    sample_total = len(y_true)
    sample_counts = Counter(y_true)
    
    print(f"测试集样本总量: {sample_total}")
    print(f"准确率(Accuracy): {accuracy:.4f}")
    print(f"召回率(Recall): {recall:.4f}")
    print(f"精确率(Precision): {precision:.4f}")
    print(f"F1分数: {f1:.4f}")
    
    # 计算混淆矩阵
    cm = confusion_matrix(y_true, y_pred)
    
    # ===== 保存评估结果数据 =====
    # 整体评估结果
    results = {
        "model_type": model_type,
        "csv_relative_path": csv_path,
        "csv_absolute_path": csv_absolute_path,
        "sample_total": sample_total,
        "sample_counts_by_class": {labels[class_id]: int(count) for class_id, count in sample_counts.items()},
        "accuracy": float(accuracy),
        "recall": float(recall),
        "precision": float(precision),
        "f1_score": float(f1),
        "evaluation_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "class_metrics": {}
    }
    
    # 计算每个类别的指标
    print("\n各类别评估指标:")
    for i, label in enumerate(labels):
        # 将当前类别视为正类，其他所有类别视为负类
        true_binary = [1 if t == i else 0 for t in y_true]
        pred_binary = [1 if p == i else 0 for p in y_pred]
        
        # 计算该类别的指标
        class_precision = precision_score(true_binary, pred_binary, zero_division=0)
        class_recall = recall_score(true_binary, pred_binary, zero_division=0)
        class_f1 = f1_score(true_binary, pred_binary, zero_division=0)
        
        # 获取该类别的样本数量
        class_count = sample_counts.get(i, 0)
        
        print(f"类别 '{label}' (样本数: {class_count}):")
        print(f"  精确率: {class_precision:.4f}")
        print(f"  召回率: {class_recall:.4f}")
        print(f"  F1分数: {class_f1:.4f}")
        
        # 添加到结果字典
        results["class_metrics"][label] = {
            "sample_count": int(class_count),
            "precision": float(class_precision),
            "recall": float(class_recall),
            "f1_score": float(class_f1)
        }
    
    # 保存结果到JSON文件
    with open(f'{eval_dir}/evaluation_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
    
    # 保存验证类型和评估结果到文本文件
    with open(f'{eval_dir}/evaluation_summary.txt', 'w', encoding='utf-8') as f:
        f.write(f"验证类型: {model_type}\n")
        f.write(f"验证时间: {results['evaluation_time']}\n")
        f.write(f"测试数据文件相对路径: {csv_path}\n")
        f.write(f"测试数据文件绝对路径: {csv_absolute_path}\n\n")
        
        f.write("测试集样本统计:\n")
        f.write(f"样本总量: {sample_total}\n")
        f.write("各类别样本数量:\n")
        for i, label in enumerate(labels):
            count = sample_counts.get(i, 0)
            percentage = (count / sample_total) * 100 if sample_total > 0 else 0
            f.write(f"  {label}: {count} ({percentage:.1f}%)\n")
        f.write("\n")
        
        f.write(f"整体评估指标:\n")
        f.write(f"准确率(Accuracy): {accuracy:.4f}\n")
        f.write(f"召回率(Recall): {recall:.4f}\n")
        f.write(f"精确率(Precision): {precision:.4f}\n")
        f.write(f"F1分数: {f1:.4f}\n\n")
        
        f.write("各类别评估指标:\n")
        for label, metrics in results["class_metrics"].items():
            f.write(f"类别 '{label}' (样本数: {metrics['sample_count']}):\n")
            f.write(f"  精确率: {metrics['precision']:.4f}\n")
            f.write(f"  召回率: {metrics['recall']:.4f}\n")
            f.write(f"  F1分数: {metrics['f1_score']:.4f}\n\n")
    
    # ===== 绘制并保存混淆矩阵 =====
    # 1. 原始混淆矩阵
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=labels,
                yticklabels=labels)
    plt.xlabel('Predicted Label')
    plt.ylabel('True Label')
    plt.title('Confusion Matrix')
    plt.tight_layout()
    plt.savefig(f'{eval_dir}/confusion_matrix.png')
    plt.close()
    
    # 2. 归一化混淆矩阵
    # 按行归一化，每行的总和为1
    cm_normalized = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
    cm_normalized = np.nan_to_num(cm_normalized)  # 处理除以0的情况
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm_normalized, annot=True, fmt='.2f', cmap='Blues',
                xticklabels=labels,
                yticklabels=labels)
    plt.xlabel('Predicted Label')
    plt.ylabel('True Label')
    plt.title('Normalized Confusion Matrix')
    plt.tight_layout()
    plt.savefig(f'{eval_dir}/confusion_matrix_normalized.png')
    plt.close()
    
    print(f"\n评估结果已保存至目录: {eval_dir}")
    return eval_dir


def main():
    # 直接在代码中指定路径和模型类型
    # 修改下面的路径来验证不同的模型
    
    #对于手势关键点分类器 (KeyPointClassifier)
    #csv_path = 'model/keypoint_classifier/keypoint_test2.csv'
    #model_type = 'keypoint'
    
    # 如果要验证点历史分类器，取消下面注释并注释上面两行
    csv_path = 'model/point_history_classifier/point_history_test2.csv'
    model_type = 'point_history'
    
    # 加载标签
    labels = load_labels(model_type)
    
    # 加载CSV数据
    print(f"正在从文件加载数据: {csv_path}")
    data = []
    with open(csv_path, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) > 0:  # 确保行不为空
                data.append(row)
    
    if not data:
        print("数据为空，请检查CSV文件")
        return
    
    # 分离标签和特征
    y_true = []
    X = []
    for row in data:
        y_true.append(int(row[0]))  # 第一列作为标签
        X.append([float(x) for x in row[1:]])  # 其余列作为特征
    
    # 加载模型
    if model_type == "keypoint":
        model = KeyPointClassifier()
    else:
        model = PointHistoryClassifier()
    
    # 进行预测
    print("正在进行预测...")
    y_pred = []
    for x in X:
        y_pred.append(model(x))
    
    # 评估模型
    print("\n模型评估结果:")
    evaluate_model(y_true, y_pred, labels, model_type, csv_path)


if __name__ == "__main__":
    main()
