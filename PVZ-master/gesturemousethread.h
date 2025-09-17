#ifndef GESTUREMOUSETHREAD_H
#define GESTUREMOUSETHREAD_H

#include <QThread>
#include <QPointF>
#include <QString>
#include <QRect>
#include <QPointer>
#include <QMutex>
#include <QWaitCondition> // 为暂停功能添加
#include "gameIndex.h"    // 包含 GestureState 的定义

class QWidget;

class GestureMouseThread : public QThread
{
    Q_OBJECT
public:
    explicit GestureMouseThread(QObject* parent = nullptr);
    ~GestureMouseThread() override;

    void stop();
    void setGameView(QWidget* gameView);

public slots: // 公共槽函数，用于控制暂停/恢复
    void togglePause();
    void pause();
    void resume();

protected:
    void run() override;

private:
    QMutex m_internalMutex;         // 用于此线程内部状态的互斥锁
    QWaitCondition m_pauseCondition; // 用于暂停/恢复线程
    volatile bool m_stopped;        // 标记线程是否应该停止
    volatile bool m_paused;         // 标记线程是否已暂停
    bool m_lastGesturePressed;

    QPointer<QWidget> m_gameView;
    QRect m_cachedGameViewScreenRect;
    bool m_firstUpdate;

    float m_filteredX;
    float m_filteredY;
    const float m_smoothingFactor = 0.3f;

    void updateCachedGameViewRect();

#ifdef Q_OS_WIN
    // 不需要特定于Windows的成员来处理 globalGestureState 的锁，
    // 因为锁是 globalGestureState 本身的一部分。
#endif
};

#endif // GESTUREMOUSETHREAD_H