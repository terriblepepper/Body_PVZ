#include"hammer.h"
#include "zombie.h"
#include "gameIndex.h"
#include <QGraphicsSceneMouseEvent>
#include<QDebug>
hammer::hammer()
    : atk(350), enableAtk(true)
{
    if (!normalPixmap.load("./images/hammer1.png")) {
        qWarning() << "Failed to load normal image";
    }
    if (!clickedPixmap.load("./images/hammer2.png")) {
        qWarning() << "Failed to load clicked image";
    }
    setPixmap(normalPixmap);
    setFlag(QGraphicsItem::ItemIsMovable);
    setAcceptHoverEvents(true);
    setAcceptedMouseButtons(Qt::LeftButton);
}

int hammer::type() const
{
    return Type;
}

QRectF hammer::boundingRect() const
{
    return QRectF(0, 0, 80, 80);
}

void hammer::mousePressEvent(QGraphicsSceneMouseEvent* event)
{
    if (event->button() == Qt::LeftButton) {
        setHammerState("hammerdown",1.0,true);
    }
}

void hammer::hoverMoveEvent(QGraphicsSceneHoverEvent* event)
{
    setHammerPosition(event->scenePos().x(), event->scenePos().y());
}

void hammer::setHammerPosition(double x, double y)
{
    QPointF p(x - 30, y - 30);
    setPos(p);
}

void hammer::setHammerState(QString isAttacking,double atkidx,bool mouseControl)
{
    if (isAttacking=="hammerdown") {
        setPixmap(clickedPixmap);
        if (!GestureControl || mouseControl)
        {
            QTimer::singleShot(200, [this]() {
                if (!puzzleMode::willDelete) {
                    setPixmap(normalPixmap);
                    enableAtk = true;//恢复攻击
                }
                });
        }

        QList<QGraphicsItem*> items = collidingItems();
        if (!items.isEmpty())
        {
            // 当锤子与僵尸碰撞时
            zombie* zom = qgraphicsitem_cast<zombie*>(items[qrand() % items.size()]);
            if (zom && enableAtk)
            {
                zom->hp -= atk;
                enableAtk = false;//禁止攻击
            } // 减少僵尸的生命值，受到豌豆射手的攻击
            return;
        }
    }
    else {
        setPixmap(normalPixmap);
		if (GestureControl)enableAtk = true;//恢复攻击
    }
}
