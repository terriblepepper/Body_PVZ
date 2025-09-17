#include "gesturemousethread.h"
#include <QDebug>
#include <QWidget>
#include <QGuiApplication>
#include <QScreen>
#include <tuple> // 用于从 globalGestureState.getData() 返回

#ifdef Q_OS_WIN
#include <windows.h>
#endif

GestureMouseThread::GestureMouseThread(QObject* parent)
    : QThread(parent),
    m_stopped(false),
    m_paused(false), // 初始化为未暂停状态
    m_lastGesturePressed(false),
    m_firstUpdate(true),
    m_filteredX(0.5f),
    m_filteredY(0.5f)
{
}

GestureMouseThread::~GestureMouseThread()
{
    stop();
    wait(); // QThread::wait() 会等待 run() 执行完毕
}

void GestureMouseThread::stop()
{
    QMutexLocker locker(&m_internalMutex);
    m_stopped = true;
    m_paused = false; // 确保线程不会卡在暂停状态
    m_pauseCondition.wakeAll(); // 如果线程处于暂停状态，唤醒它，使其能够检查 m_stopped 标志
}

void GestureMouseThread::setGameView(QWidget* gameView)
{
    QMutexLocker locker(&m_internalMutex);
    m_gameView = gameView;
    updateCachedGameViewRect();
    if (m_cachedGameViewScreenRect.isValid() && GetSystemMetrics(SM_CXSCREEN) > 0 && GetSystemMetrics(SM_CYSCREEN) > 0) {
        m_filteredX = (float)m_cachedGameViewScreenRect.left() / GetSystemMetrics(SM_CXSCREEN) +
            ((float)m_cachedGameViewScreenRect.width() / GetSystemMetrics(SM_CXSCREEN)) * 0.5f;
        m_filteredY = (float)m_cachedGameViewScreenRect.top() / GetSystemMetrics(SM_CYSCREEN) +
            ((float)m_cachedGameViewScreenRect.height() / GetSystemMetrics(SM_CYSCREEN)) * 0.5f;
    }
    m_firstUpdate = true;
}

void GestureMouseThread::togglePause()
{
    QMutexLocker locker(&m_internalMutex);
    m_paused = !m_paused;
    if (!m_paused) {
        m_pauseCondition.wakeAll(); // 如果是从暂停状态恢复，则唤醒线程
        qDebug() << "手势鼠标线程已恢复";
    }
    else {
        qDebug() << "手势鼠标线程已暂停";
    }
}

void GestureMouseThread::pause()
{
    QMutexLocker locker(&m_internalMutex);
    if (!m_paused) {
        m_paused = true;
        qDebug() << "手势鼠标线程已暂停";
    }
}

void GestureMouseThread::resume()
{
    QMutexLocker locker(&m_internalMutex);
    if (m_paused) {
        m_paused = false;
        m_pauseCondition.wakeAll(); // 唤醒等待的线程
        qDebug() << "手势鼠标线程已恢复";
    }
}


void GestureMouseThread::updateCachedGameViewRect()
{
    // 此方法由 setGameView 调用，setGameView 受 m_internalMutex 保护
    // 或者如果从 run() 中调用，也需要确保同步。
    // 这里假设 m_gameView 的访问已由外部调用者（如 setGameView）或 run() 内部的锁保护。
    if (m_gameView) {
        m_cachedGameViewScreenRect = QRect(m_gameView->mapToGlobal(QPoint(0, 0)), m_gameView->size());
    }
    else {
        m_cachedGameViewScreenRect = QRect();
    }
}

void GestureMouseThread::run()
{
    qDebug() << "手势鼠标线程已启动。";
    const int refresh_rate_hz = 120;
    const int sleep_duration_ms = 1000 / refresh_rate_hz;

    while (true)
    {
        { // 互斥锁 locker 的作用域
            QMutexLocker locker(&m_internalMutex);
            if (m_stopped) {
                break; // 如果已标记为停止，则退出循环
            }
            // 如果线程被标记为暂停，并且没有被标记为停止，则等待
            while (m_paused && !m_stopped) {
                // m_pauseCondition.wait 会原子地解锁互斥锁并等待信号
                // 当被唤醒时，它会重新锁定互斥锁
                m_pauseCondition.wait(&m_internalMutex);
            }
            // 再次检查 m_stopped，因为可能在等待期间被stop()调用
            if (m_stopped) {
                break;
            }

            // 如果未暂停，则继续执行
            // 如果 m_stopped 在等待时变为 true，则会在下一次迭代或唤醒后立即中断。

            if (!m_gameView) { // 如果视图被销毁
                m_cachedGameViewScreenRect = QRect();
            }
            // else { updateCachedGameViewRect(); } // 如果需要，定期更新
        } // 互斥锁在此处解锁


#ifdef Q_OS_WIN
        float rawGestureX;
        float rawGestureY;
        QString currentKeyPointState;

        // --- 从 globalGestureState 读取数据，使用其内部互斥锁 ---
        auto gestureData = globalGestureState.getData();
        currentKeyPointState = std::get<0>(gestureData);
        rawGestureX = std::get<1>(gestureData);
        rawGestureY = std::get<2>(gestureData);
        // --- globalGestureState 读取结束 ---


        { // 滤波器状态的临界区
            QMutexLocker locker(&m_internalMutex);
            if (m_firstUpdate) {
                m_filteredX = rawGestureX;
                m_filteredY = rawGestureY;
                m_firstUpdate = false;
            }
            else {
                m_filteredX = m_smoothingFactor * rawGestureX + (1.0f - m_smoothingFactor) * m_filteredX;
                m_filteredY = m_smoothingFactor * rawGestureY + (1.0f - m_smoothingFactor) * m_filteredY;
            }
        }

        long screen_width = GetSystemMetrics(SM_CXSCREEN);
        long screen_height = GetSystemMetrics(SM_CYSCREEN);

        if (screen_width == 0 || screen_height == 0) {
            qWarning() << "无法获取屏幕指标。";
            msleep(sleep_duration_ms);
            continue;
        }

        float targetNormX, targetNormY;
        QRect currentViewRect; // 局部变量以减少锁的持有时间
        { // 内部状态的临界区
            QMutexLocker locker(&m_internalMutex);
            targetNormX = m_filteredX;
            targetNormY = m_filteredY;
            currentViewRect = m_cachedGameViewScreenRect;
        }


        if (currentViewRect.isValid()) {
            float win_norm_left = (float)currentViewRect.left() / screen_width;
            float win_norm_right = (float)(currentViewRect.left() + currentViewRect.width()) / screen_width;
            float win_norm_top = (float)currentViewRect.top() / screen_height;
            float win_norm_bottom = (float)(currentViewRect.top() + currentViewRect.height()) / screen_height;

            if (win_norm_right < win_norm_left) win_norm_right = win_norm_left;
            if (win_norm_bottom < win_norm_top) win_norm_bottom = win_norm_top;

            targetNormX = qBound(win_norm_left, targetNormX, win_norm_right);
            targetNormY = qBound(win_norm_top, targetNormY, win_norm_bottom);
        }

        LONG absoluteX = static_cast<LONG>(targetNormX * 65535.0f);
        LONG absoluteY = static_cast<LONG>(targetNormY * 65535.0f);
        absoluteX = qBound(0L, absoluteX, 65535L);
        absoluteY = qBound(0L, absoluteY, 65535L);

        INPUT input[2];
        ZeroMemory(input, sizeof(input));
        int inputCount = 0;

        input[inputCount].type = INPUT_MOUSE;
        input[inputCount].mi.dwFlags = MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE;
        input[inputCount].mi.dx = absoluteX;
        input[inputCount].mi.dy = absoluteY;
        inputCount++;

        bool currentPressedIntent = (currentKeyPointState == "close");
        bool local_lastGesturePressed;
        {
            QMutexLocker locker(&m_internalMutex);
            local_lastGesturePressed = m_lastGesturePressed;
        }


        if (currentPressedIntent && !local_lastGesturePressed) {
            input[inputCount].type = INPUT_MOUSE;
            input[inputCount].mi.dwFlags = MOUSEEVENTF_LEFTDOWN;
            input[inputCount].mi.dx = absoluteX;
            input[inputCount].mi.dy = absoluteY;
            inputCount++;
        }
        else if (!currentPressedIntent && local_lastGesturePressed) {
            input[inputCount].type = INPUT_MOUSE;
            input[inputCount].mi.dwFlags = MOUSEEVENTF_LEFTUP;
            input[inputCount].mi.dx = absoluteX;
            input[inputCount].mi.dy = absoluteY;
            inputCount++;
        }

        if (inputCount > 0) {
            SendInput(inputCount, input, sizeof(INPUT));
        }

        {
            QMutexLocker locker(&m_internalMutex);
            m_lastGesturePressed = currentPressedIntent;
        }

#else
        // qDebug() << "此实现中，手势鼠标控制仅在Windows上受支持。";
#endif
        msleep(sleep_duration_ms);
    }
    qDebug() << "手势鼠标线程已结束。";
}