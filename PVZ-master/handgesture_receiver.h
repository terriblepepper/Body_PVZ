#ifndef HANDGESTURERECEIVER_H
#define HANDGESTURERECEIVER_H

#include <QObject>
#include <QUdpSocket>
#include <QJsonDocument>
#include <QJsonObject>
#include <QDebug>
#include <QThread>
// #include <QTimer> // QTimer 似乎没有被使用，可以考虑移除
#include "gameIndex.h" // 包含 globalGestureState 和 GestureState 的定义

// 手势状态更新线程类
// 注意：当前的 GestureUpdateThread 实现似乎并没有做太多实际工作，
// QUdpSocket 的 readyRead 信号是在主线程（或创建 socket 的线程）中触发的，
// 除非你将 socket 移到 GestureUpdateThread 中。
// 如果 readPendingDatagrams 是在主线程（或 HandGestureReceiver 所在的线程）执行，
// 那么 GestureUpdateThread 的作用需要重新评估。
// 但为了演示锁的用法，我们假设 readPendingDatagrams 可能在不同线程。
// 如果 readPendingDatagrams 确实在 socket 创建的线程（通常是主线程）中，
// 那么 GestureUpdateThread 可能不是必需的，或者其目的需要澄清。
class GestureUpdateThread : public QThread
{
    Q_OBJECT
public:
    explicit GestureUpdateThread(QObject* parent = nullptr);
    ~GestureUpdateThread() override;
    bool isRunning;
protected:
    void run() override;

public slots:
    void stopThread();

private:
    // volatile bool isRunning; // 如果在多个线程中访问，volatile 可能有帮助，但 QMutex 通常更安全
};

class HandGestureReceiver : public QObject
{
    Q_OBJECT
public:
    HandGestureReceiver(QObject* parent = nullptr);
    ~HandGestureReceiver();

    void startUpdateThread();
    void stopUpdateThread();

private slots:
    void readPendingDatagrams();

signals:
    void stopThreadSignal(); // 用于停止 GestureUpdateThread

private:
    QUdpSocket* socket;
    GestureUpdateThread* updateThread; // 如果 HandGestureReceiver 和 socket 都在主线程，这个线程可能用途不大
};

#endif // HANDGESTURERECEIVER_H