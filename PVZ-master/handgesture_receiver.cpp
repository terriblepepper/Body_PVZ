#include "handgesture_receiver.h"
#include <QMutexLocker> // !!! 包含 QMutexLocker !!!

// 实现手势状态更新线程
GestureUpdateThread::GestureUpdateThread(QObject* parent) : QThread(parent), isRunning(true)
{
}

GestureUpdateThread::~GestureUpdateThread()
{
    stopThread(); // 确保线程被请求停止
    wait();       // 等待线程实际结束
}

void GestureUpdateThread::run()
{
    // 当前 run 方法只是调用 exec()，这意味着它启动了一个事件循环。
    // 如果 socket 的操作（如 readPendingDatagrams）希望在这个线程中运行，
    // 你需要将 socket 的父对象设为 nullptr，然后调用 socket->moveToThread(this)。
    // 否则，readyRead 信号将在创建 socket 的线程中触发。
    exec();
}

void GestureUpdateThread::stopThread()
{
    isRunning = false; // 这个标志目前在 run() 中没有直接使用来退出循环
    quit(); // 请求事件循环退出
}

// 实现HandGestureReceiver
HandGestureReceiver::HandGestureReceiver(QObject* parent) : QObject(parent), updateThread(nullptr)
{
    // 创建UDP socket
    socket = new QUdpSocket(this); // socket 的父对象是 HandGestureReceiver

    // 绑定到本地端口
    if (socket->bind(QHostAddress::LocalHost, 12345)) {
        qDebug() << "成功绑定到端口12345";
    }
    else {
        qDebug() << "绑定到端口12345失败: " << socket->errorString();
    }

    // 连接readyRead信号到槽函数
    // 这个 connect 意味着 readPendingDatagrams() 将在 socket 所在的线程中被调用。
    // 由于 socket 的父对象是 HandGestureReceiver，它通常与 HandGestureReceiver 在同一线程。
    connect(socket, &QUdpSocket::readyRead, this, &HandGestureReceiver::readPendingDatagrams);

    // 如果启用了手势控制，则自动启动更新线程
    if (GestureControl) {
        // 注意：如果 readPendingDatagrams 在 HandGestureReceiver 的线程（例如主线程）执行，
        // GestureUpdateThread 的当前作用可能不是处理UDP数据，其用途需要明确。
        // startUpdateThread(); // 暂时注释掉，除非其用途明确且必要
    }
}

HandGestureReceiver::~HandGestureReceiver() {
    // stopUpdateThread(); // 如果线程没有启动，或其目的不同，则相应处理
    delete socket; // socket 会在析构时自动解绑
}

void HandGestureReceiver::startUpdateThread()
{
    if (!updateThread) {
        updateThread = new GestureUpdateThread(this); // 线程父对象是 HandGestureReceiver
        // 将 HandGestureReceiver 的信号连接到线程的槽
        connect(this, &HandGestureReceiver::stopThreadSignal, updateThread, &GestureUpdateThread::stopThread, Qt::QueuedConnection);
        updateThread->start();
        qDebug() << "GestureUpdateThread started.";
    }
}

void HandGestureReceiver::stopUpdateThread()
{
    if (updateThread) {
        emit stopThreadSignal(); // 发送信号请求线程停止
        if (updateThread->isRunning) { // 检查线程是否仍在运行
            updateThread->wait(5000); // 等待线程结束，设置超时
        }
        delete updateThread;
        updateThread = nullptr;
        qDebug() << "GestureUpdateThread stopped and deleted.";
    }
}

void HandGestureReceiver::readPendingDatagrams()
{
    while (socket->hasPendingDatagrams()) {
        QByteArray datagram;
        datagram.resize(socket->pendingDatagramSize());
        QHostAddress sender;
        quint16 senderPort;

        socket->readDatagram(datagram.data(), datagram.size(), &sender, &senderPort);

        QJsonDocument doc = QJsonDocument::fromJson(datagram);
        if (!doc.isNull() && doc.isObject()) {
            QJsonObject obj = doc.object();

            // --- 关键修改：在更新 globalGestureState 之前加锁 ---
            // 方法1：使用封装的 setter (在 gameIndex.h 中定义)
            globalGestureState.setData(
                obj["hand_gesture"].toString(),
                obj["x"].toDouble(),
                obj["y"].toDouble()
            );
            // 如果 HistoryPointState 也需要通过 setData 更新，请修改 setData 方法
            // 或者单独设置（也需要加锁）：
            // {
            //     QMutexLocker locker(&globalGestureState.mutex);
            //     globalGestureState.HistoryPointState = obj["finger_gesture"].toString();
            // }


            // 方法2：直接访问成员，手动加锁 (如果未使用封装的 setter)
            /*
            { // 创建一个作用域，以便 QMutexLocker 自动解锁
                QMutexLocker locker(&globalGestureState.mutex);
                globalGestureState.x = obj["x"].toDouble();
                globalGestureState.y = obj["y"].toDouble();
                globalGestureState.KeyPointState = obj["hand_gesture"].toString();
                globalGestureState.HistoryPointState = obj["finger_gesture"].toString();
            }
            */
            // --- globalGestureState 更新结束，锁已释放 ---

            // 为了调试，读取受保护的数据也应该通过 getter 或加锁
            QString currentHandGesture, currentFingerGesture;
            double currentX, currentY;
            std::tie(currentHandGesture, currentX, currentY) = globalGestureState.getData(); // 使用 getter
            // 如果还需要 HistoryPointState 用于调试，也应类似获取
            // QMutexLocker locker(&globalGestureState.mutex); // 如果直接访问
            // currentFingerGesture = globalGestureState.HistoryPointState;
            // locker.unlock(); // 手动解锁或等待作用域结束

            qDebug() << "接收到数据: x =" << currentX
                << "y =" << currentY
                << "hand_gesture =" << currentHandGesture;
            // << "\nfinger_gesture =" << globalGestureState.HistoryPointState; // 如果需要打印，确保线程安全
        }
        else {
            qDebug() << "接收到无效的JSON数据";
        }
    }
}