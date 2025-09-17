//utf8
#pragma once
#include<qdebug.h>
#include <QWidget>
#include <QGraphicsView>
#include <QGraphicsScene>
#include <QTimer>
#include <QMediaPlayer>
#include <QMediaPlaylist>
#include <QTime>
#include <QPixmap>
#include <QKeyEvent>
#include "shop.h"
#include "map.h"
#include "shovel.h"
#include "basiczombie.h"
#include "conezombie.h"
#include "bucketzombie.h"
#include "screenzombie.h"
#include "footballzombie.h"
#include"gargantuarzombie.h"
#include"flagzombie.h"
#include"smallzombie.h"
#include"yetizombie.h"
#include"icetrackerzombie.h"
#include"apolozombie.h"
#include"cleopatrazombie.h"
#include"pharaohzombie.h"
#include"pyramidzombie.h"
#include "zombie.h"
#include "mower.h"
#include"gameIndex.h"
#include"gamingMenu.h"
#include "highprecesionQtimer.h" // 包含高精度定时器的头文件.
#include "gesturemousethread.h"

class gamingMenuDialog;
class HandGestureReceiver;
class survivalGameMode : public QWidget {
    Q_OBJECT
public:
    explicit survivalGameMode(QWidget* parent = nullptr);
    ~survivalGameMode() override;
    void getGamingMenu(gamingMenuDialog* menuG);
    void checkGameState();
    void addZombie();
    void goToGamingMenu();
    gamingMenuDialog* gamingMenu;
    QMediaPlayer* gamingBGM;
    QMediaPlaylist* gamingBGM_List;
    TimerThread* mQTimer; // 使用高精度定时器
    QGraphicsView* view;
    QGraphicsScene* scene;
protected:
    void keyPressEvent(QKeyEvent* event) override;
public slots:
    void handleVolumeChange();
    void initTimer();
signals:
    void gameOver();
private:
    void bgmPlay();
    void initIndex();
    void createMenuButton();
    QPushButton* gameOverButton;
    QPushButton* menuButton;
    QGraphicsProxyWidget* gamingWidgetsProxy;
    int low;
    int high;
    int maxtime;//初始最大出僵尸间隔时间
    int time;
    int counter;

    // 如果启用了手势控制，创建一个全局的HandGestureReceiver实例
    HandGestureReceiver* gestureReceiver = nullptr;
    GestureMouseThread* m_gestureMouseThread = nullptr;
};

// SURVIVALGAMEMODE_H


