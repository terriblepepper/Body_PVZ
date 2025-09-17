#pragma once
#include <QGraphicsPixmapItem>
#include <QtWidgets>
#include <QPainter>
#include <QPixmap>
#include <QTimer>
#include"puzzleMode.h"

class hammer : public QGraphicsPixmapItem
{
public:
    enum { Type = UserType + 4 };
    hammer();
    int type() const override;
    void setHammerPosition(double x, double y); // 添加用于设置锤子位置的方法
    void setHammerState(QString isAttacking, double atkidx, bool mouseControl); // 添加用于设置锤子状态的方法
protected:
    QRectF boundingRect() const override;
    void mousePressEvent(QGraphicsSceneMouseEvent* event) override;
    void hoverMoveEvent(QGraphicsSceneHoverEvent* event) override;
private:
    QPixmap normalPixmap;
    QPixmap clickedPixmap;
    double atk;
    bool enableAtk;//用于限制攻击速度
};
