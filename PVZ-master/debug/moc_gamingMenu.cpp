/****************************************************************************
** Meta object code from reading C++ file 'gamingMenu.h'
**
** Created by: The Qt Meta Object Compiler version 67 (Qt 5.14.2)
**
** WARNING! All changes made in this file will be lost!
*****************************************************************************/

#include <memory>
#include "../gamingMenu.h"
#include <QtCore/qbytearray.h>
#include <QtCore/qmetatype.h>
#if !defined(Q_MOC_OUTPUT_REVISION)
#error "The header file 'gamingMenu.h' doesn't include <QObject>."
#elif Q_MOC_OUTPUT_REVISION != 67
#error "This file was generated using the moc from 5.14.2. It"
#error "cannot be used with the include files from this version of Qt."
#error "(The moc has changed too much.)"
#endif

QT_BEGIN_MOC_NAMESPACE
QT_WARNING_PUSH
QT_WARNING_DISABLE_DEPRECATED
struct qt_meta_stringdata_gamingMenuDialog_t {
    QByteArrayData data[18];
    char stringdata0[208];
};
#define QT_MOC_LITERAL(idx, ofs, len) \
    Q_STATIC_BYTE_ARRAY_DATA_HEADER_INITIALIZER_WITH_OFFSET(len, \
    qptrdiff(offsetof(qt_meta_stringdata_gamingMenuDialog_t, stringdata0) + ofs \
        - idx * sizeof(QByteArrayData)) \
    )
static const qt_meta_stringdata_gamingMenuDialog_t qt_meta_stringdata_gamingMenuDialog = {
    {
QT_MOC_LITERAL(0, 0, 16), // "gamingMenuDialog"
QT_MOC_LITERAL(1, 17, 11), // "restartGame"
QT_MOC_LITERAL(2, 29, 0), // ""
QT_MOC_LITERAL(3, 30, 17), // "survivalGameMode*"
QT_MOC_LITERAL(4, 48, 2), // "t1"
QT_MOC_LITERAL(5, 51, 18), // "adventureGameMode*"
QT_MOC_LITERAL(6, 70, 2), // "t2"
QT_MOC_LITERAL(7, 73, 14), // "smallGameMode*"
QT_MOC_LITERAL(8, 88, 2), // "t3"
QT_MOC_LITERAL(9, 91, 11), // "puzzleMode*"
QT_MOC_LITERAL(10, 103, 2), // "t4"
QT_MOC_LITERAL(11, 106, 14), // "gameToMainMenu"
QT_MOC_LITERAL(12, 121, 12), // "changeVolume"
QT_MOC_LITERAL(13, 134, 15), // "onVolumeChanged"
QT_MOC_LITERAL(14, 150, 6), // "volume"
QT_MOC_LITERAL(15, 157, 16), // "onRestartClicked"
QT_MOC_LITERAL(16, 174, 17), // "onMainMenuClicked"
QT_MOC_LITERAL(17, 192, 15) // "onResumeClicked"

    },
    "gamingMenuDialog\0restartGame\0\0"
    "survivalGameMode*\0t1\0adventureGameMode*\0"
    "t2\0smallGameMode*\0t3\0puzzleMode*\0t4\0"
    "gameToMainMenu\0changeVolume\0onVolumeChanged\0"
    "volume\0onRestartClicked\0onMainMenuClicked\0"
    "onResumeClicked"
};
#undef QT_MOC_LITERAL

static const uint qt_meta_data_gamingMenuDialog[] = {

 // content:
       8,       // revision
       0,       // classname
       0,    0, // classinfo
      10,   14, // methods
       0,    0, // properties
       0,    0, // enums/sets
       0,    0, // constructors
       0,       // flags
       6,       // signalCount

 // signals: name, argc, parameters, tag, flags
       1,    1,   64,    2, 0x06 /* Public */,
       1,    1,   67,    2, 0x06 /* Public */,
       1,    1,   70,    2, 0x06 /* Public */,
       1,    1,   73,    2, 0x06 /* Public */,
      11,    0,   76,    2, 0x06 /* Public */,
      12,    0,   77,    2, 0x06 /* Public */,

 // slots: name, argc, parameters, tag, flags
      13,    1,   78,    2, 0x08 /* Private */,
      15,    0,   81,    2, 0x08 /* Private */,
      16,    0,   82,    2, 0x08 /* Private */,
      17,    0,   83,    2, 0x08 /* Private */,

 // signals: parameters
    QMetaType::Void, 0x80000000 | 3,    4,
    QMetaType::Void, 0x80000000 | 5,    6,
    QMetaType::Void, 0x80000000 | 7,    8,
    QMetaType::Void, 0x80000000 | 9,   10,
    QMetaType::Void,
    QMetaType::Void,

 // slots: parameters
    QMetaType::Void, QMetaType::Int,   14,
    QMetaType::Void,
    QMetaType::Void,
    QMetaType::Void,

       0        // eod
};

void gamingMenuDialog::qt_static_metacall(QObject *_o, QMetaObject::Call _c, int _id, void **_a)
{
    if (_c == QMetaObject::InvokeMetaMethod) {
        auto *_t = static_cast<gamingMenuDialog *>(_o);
        Q_UNUSED(_t)
        switch (_id) {
        case 0: _t->restartGame((*reinterpret_cast< survivalGameMode*(*)>(_a[1]))); break;
        case 1: _t->restartGame((*reinterpret_cast< adventureGameMode*(*)>(_a[1]))); break;
        case 2: _t->restartGame((*reinterpret_cast< smallGameMode*(*)>(_a[1]))); break;
        case 3: _t->restartGame((*reinterpret_cast< puzzleMode*(*)>(_a[1]))); break;
        case 4: _t->gameToMainMenu(); break;
        case 5: _t->changeVolume(); break;
        case 6: _t->onVolumeChanged((*reinterpret_cast< int(*)>(_a[1]))); break;
        case 7: _t->onRestartClicked(); break;
        case 8: _t->onMainMenuClicked(); break;
        case 9: _t->onResumeClicked(); break;
        default: ;
        }
    } else if (_c == QMetaObject::RegisterMethodArgumentMetaType) {
        switch (_id) {
        default: *reinterpret_cast<int*>(_a[0]) = -1; break;
        case 0:
            switch (*reinterpret_cast<int*>(_a[1])) {
            default: *reinterpret_cast<int*>(_a[0]) = -1; break;
            case 0:
                *reinterpret_cast<int*>(_a[0]) = qRegisterMetaType< survivalGameMode* >(); break;
            }
            break;
        case 1:
            switch (*reinterpret_cast<int*>(_a[1])) {
            default: *reinterpret_cast<int*>(_a[0]) = -1; break;
            case 0:
                *reinterpret_cast<int*>(_a[0]) = qRegisterMetaType< adventureGameMode* >(); break;
            }
            break;
        case 2:
            switch (*reinterpret_cast<int*>(_a[1])) {
            default: *reinterpret_cast<int*>(_a[0]) = -1; break;
            case 0:
                *reinterpret_cast<int*>(_a[0]) = qRegisterMetaType< smallGameMode* >(); break;
            }
            break;
        case 3:
            switch (*reinterpret_cast<int*>(_a[1])) {
            default: *reinterpret_cast<int*>(_a[0]) = -1; break;
            case 0:
                *reinterpret_cast<int*>(_a[0]) = qRegisterMetaType< puzzleMode* >(); break;
            }
            break;
        }
    } else if (_c == QMetaObject::IndexOfMethod) {
        int *result = reinterpret_cast<int *>(_a[0]);
        {
            using _t = void (gamingMenuDialog::*)(survivalGameMode * );
            if (*reinterpret_cast<_t *>(_a[1]) == static_cast<_t>(&gamingMenuDialog::restartGame)) {
                *result = 0;
                return;
            }
        }
        {
            using _t = void (gamingMenuDialog::*)(adventureGameMode * );
            if (*reinterpret_cast<_t *>(_a[1]) == static_cast<_t>(&gamingMenuDialog::restartGame)) {
                *result = 1;
                return;
            }
        }
        {
            using _t = void (gamingMenuDialog::*)(smallGameMode * );
            if (*reinterpret_cast<_t *>(_a[1]) == static_cast<_t>(&gamingMenuDialog::restartGame)) {
                *result = 2;
                return;
            }
        }
        {
            using _t = void (gamingMenuDialog::*)(puzzleMode * );
            if (*reinterpret_cast<_t *>(_a[1]) == static_cast<_t>(&gamingMenuDialog::restartGame)) {
                *result = 3;
                return;
            }
        }
        {
            using _t = void (gamingMenuDialog::*)();
            if (*reinterpret_cast<_t *>(_a[1]) == static_cast<_t>(&gamingMenuDialog::gameToMainMenu)) {
                *result = 4;
                return;
            }
        }
        {
            using _t = void (gamingMenuDialog::*)();
            if (*reinterpret_cast<_t *>(_a[1]) == static_cast<_t>(&gamingMenuDialog::changeVolume)) {
                *result = 5;
                return;
            }
        }
    }
}

QT_INIT_METAOBJECT const QMetaObject gamingMenuDialog::staticMetaObject = { {
    QMetaObject::SuperData::link<QDialog::staticMetaObject>(),
    qt_meta_stringdata_gamingMenuDialog.data,
    qt_meta_data_gamingMenuDialog,
    qt_static_metacall,
    nullptr,
    nullptr
} };


const QMetaObject *gamingMenuDialog::metaObject() const
{
    return QObject::d_ptr->metaObject ? QObject::d_ptr->dynamicMetaObject() : &staticMetaObject;
}

void *gamingMenuDialog::qt_metacast(const char *_clname)
{
    if (!_clname) return nullptr;
    if (!strcmp(_clname, qt_meta_stringdata_gamingMenuDialog.stringdata0))
        return static_cast<void*>(this);
    return QDialog::qt_metacast(_clname);
}

int gamingMenuDialog::qt_metacall(QMetaObject::Call _c, int _id, void **_a)
{
    _id = QDialog::qt_metacall(_c, _id, _a);
    if (_id < 0)
        return _id;
    if (_c == QMetaObject::InvokeMetaMethod) {
        if (_id < 10)
            qt_static_metacall(this, _c, _id, _a);
        _id -= 10;
    } else if (_c == QMetaObject::RegisterMethodArgumentMetaType) {
        if (_id < 10)
            qt_static_metacall(this, _c, _id, _a);
        _id -= 10;
    }
    return _id;
}

// SIGNAL 0
void gamingMenuDialog::restartGame(survivalGameMode * _t1)
{
    void *_a[] = { nullptr, const_cast<void*>(reinterpret_cast<const void*>(std::addressof(_t1))) };
    QMetaObject::activate(this, &staticMetaObject, 0, _a);
}

// SIGNAL 1
void gamingMenuDialog::restartGame(adventureGameMode * _t1)
{
    void *_a[] = { nullptr, const_cast<void*>(reinterpret_cast<const void*>(std::addressof(_t1))) };
    QMetaObject::activate(this, &staticMetaObject, 1, _a);
}

// SIGNAL 2
void gamingMenuDialog::restartGame(smallGameMode * _t1)
{
    void *_a[] = { nullptr, const_cast<void*>(reinterpret_cast<const void*>(std::addressof(_t1))) };
    QMetaObject::activate(this, &staticMetaObject, 2, _a);
}

// SIGNAL 3
void gamingMenuDialog::restartGame(puzzleMode * _t1)
{
    void *_a[] = { nullptr, const_cast<void*>(reinterpret_cast<const void*>(std::addressof(_t1))) };
    QMetaObject::activate(this, &staticMetaObject, 3, _a);
}

// SIGNAL 4
void gamingMenuDialog::gameToMainMenu()
{
    QMetaObject::activate(this, &staticMetaObject, 4, nullptr);
}

// SIGNAL 5
void gamingMenuDialog::changeVolume()
{
    QMetaObject::activate(this, &staticMetaObject, 5, nullptr);
}
QT_WARNING_POP
QT_END_MOC_NAMESPACE
