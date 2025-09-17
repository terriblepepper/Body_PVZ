#pragma once
#include<tuple>
#include<QString>
#include<iostream>
#include<map>
#include<queue>
#include<QGraphicsScene>
#include <QMutex>     // 包含 QMutex
#include <QMutexLocker> // 包含 QMutexLocker (虽然通常在使用的地方包含，但这里也无妨)

struct sceneCast
{
    bool isValid;
    int count;
    int soundsCount;
};

struct GestureState
{
    // !!! 添加互斥锁成员 !!!
    // mutable 关键字允许在 const GestureState 对象上调用 lock/unlock (如果需要)
    // 但在这里 globalGestureState 不是 const，所以 mutable 不是必需的。
    // QMutex 本身不是可复制的，如果 GestureState 需要可复制，需要特殊处理，
    // 但作为全局变量，通常不需要复制。
    QMutex mutex;

    QString KeyPointState = "idle";
    QString HistoryPointState = "none";
    double x = 0.5;
    double y = 0.5;

    // 提供线程安全的访问方法（可选，但推荐封装）
    void setData(const QString& keyPointState, double newX, double newY) {
        QMutexLocker locker(&mutex);
        KeyPointState = keyPointState;
        x = newX;
        y = newY;
        // HistoryPointState 的更新逻辑根据你的需求来定
    }

    // 提供线程安全的读取方法（可选，但推荐封装）
    // 返回一个副本以避免在锁外持有数据引用
    std::tuple<QString, double, double> getData() {
        QMutexLocker locker(&mutex);
        return std::make_tuple(KeyPointState, x, y);
    }

    // 或者单独获取每个值
    QString getKeyPointState() {
        QMutexLocker locker(&mutex);
        return KeyPointState;
    }
    double getX() {
        QMutexLocker locker(&mutex);
        return x;
    }
    double getY() {
        QMutexLocker locker(&mutex);
        return y;
    }
};

extern int fpsIndex;
extern int musicVolume;
extern int itemVolume;
extern int maxSounds;
extern QString Difficulty;
extern bool GestureControl;
extern std::map<QGraphicsScene*, sceneCast> mapScenes;
extern GestureState globalGestureState; // 现在 GestureState 内部有 mutex
int difficultyIndex(QString diff);