/****************************************************************************
** Meta object code from reading C++ file 'adventureMode.h'
**
** Created by: The Qt Meta Object Compiler version 67 (Qt 5.14.2)
**
** WARNING! All changes made in this file will be lost!
*****************************************************************************/

#include <memory>
#include "../adventureMode.h"
#include <QtCore/qbytearray.h>
#include <QtCore/qmetatype.h>
#if !defined(Q_MOC_OUTPUT_REVISION)
#error "The header file 'adventureMode.h' doesn't include <QObject>."
#elif Q_MOC_OUTPUT_REVISION != 67
#error "This file was generated using the moc from 5.14.2. It"
#error "cannot be used with the include files from this version of Qt."
#error "(The moc has changed too much.)"
#endif

QT_BEGIN_MOC_NAMESPACE
QT_WARNING_PUSH
QT_WARNING_DISABLE_DEPRECATED
struct qt_meta_stringdata_adventureGameMode_t {
    QByteArrayData data[9];
    char stringdata0[116];
};
#define QT_MOC_LITERAL(idx, ofs, len) \
    Q_STATIC_BYTE_ARRAY_DATA_HEADER_INITIALIZER_WITH_OFFSET(len, \
    qptrdiff(offsetof(qt_meta_stringdata_adventureGameMode_t, stringdata0) + ofs \
        - idx * sizeof(QByteArrayData)) \
    )
static const qt_meta_stringdata_adventureGameMode_t qt_meta_stringdata_adventureGameMode = {
    {
QT_MOC_LITERAL(0, 0, 17), // "adventureGameMode"
QT_MOC_LITERAL(1, 18, 13), // "onBackClicked"
QT_MOC_LITERAL(2, 32, 0), // ""
QT_MOC_LITERAL(3, 33, 14), // "stopLoadingBGM"
QT_MOC_LITERAL(4, 48, 16), // "resumeLoadingBGM"
QT_MOC_LITERAL(5, 65, 10), // "gameFinish"
QT_MOC_LITERAL(6, 76, 14), // "checkGameState"
QT_MOC_LITERAL(7, 91, 9), // "addZombie"
QT_MOC_LITERAL(8, 101, 14) // "backFromSelect"

    },
    "adventureGameMode\0onBackClicked\0\0"
    "stopLoadingBGM\0resumeLoadingBGM\0"
    "gameFinish\0checkGameState\0addZombie\0"
    "backFromSelect"
};
#undef QT_MOC_LITERAL

static const uint qt_meta_data_adventureGameMode[] = {

 // content:
       8,       // revision
       0,       // classname
       0,    0, // classinfo
       7,   14, // methods
       0,    0, // properties
       0,    0, // enums/sets
       0,    0, // constructors
       0,       // flags
       4,       // signalCount

 // signals: name, argc, parameters, tag, flags
       1,    0,   49,    2, 0x06 /* Public */,
       3,    0,   50,    2, 0x06 /* Public */,
       4,    0,   51,    2, 0x06 /* Public */,
       5,    0,   52,    2, 0x06 /* Public */,

 // slots: name, argc, parameters, tag, flags
       6,    0,   53,    2, 0x0a /* Public */,
       7,    0,   54,    2, 0x0a /* Public */,
       8,    0,   55,    2, 0x0a /* Public */,

 // signals: parameters
    QMetaType::Void,
    QMetaType::Void,
    QMetaType::Void,
    QMetaType::Void,

 // slots: parameters
    QMetaType::Void,
    QMetaType::Void,
    QMetaType::Void,

       0        // eod
};

void adventureGameMode::qt_static_metacall(QObject *_o, QMetaObject::Call _c, int _id, void **_a)
{
    if (_c == QMetaObject::InvokeMetaMethod) {
        auto *_t = static_cast<adventureGameMode *>(_o);
        Q_UNUSED(_t)
        switch (_id) {
        case 0: _t->onBackClicked(); break;
        case 1: _t->stopLoadingBGM(); break;
        case 2: _t->resumeLoadingBGM(); break;
        case 3: _t->gameFinish(); break;
        case 4: _t->checkGameState(); break;
        case 5: _t->addZombie(); break;
        case 6: _t->backFromSelect(); break;
        default: ;
        }
    } else if (_c == QMetaObject::IndexOfMethod) {
        int *result = reinterpret_cast<int *>(_a[0]);
        {
            using _t = void (adventureGameMode::*)();
            if (*reinterpret_cast<_t *>(_a[1]) == static_cast<_t>(&adventureGameMode::onBackClicked)) {
                *result = 0;
                return;
            }
        }
        {
            using _t = void (adventureGameMode::*)();
            if (*reinterpret_cast<_t *>(_a[1]) == static_cast<_t>(&adventureGameMode::stopLoadingBGM)) {
                *result = 1;
                return;
            }
        }
        {
            using _t = void (adventureGameMode::*)();
            if (*reinterpret_cast<_t *>(_a[1]) == static_cast<_t>(&adventureGameMode::resumeLoadingBGM)) {
                *result = 2;
                return;
            }
        }
        {
            using _t = void (adventureGameMode::*)();
            if (*reinterpret_cast<_t *>(_a[1]) == static_cast<_t>(&adventureGameMode::gameFinish)) {
                *result = 3;
                return;
            }
        }
    }
    Q_UNUSED(_a);
}

QT_INIT_METAOBJECT const QMetaObject adventureGameMode::staticMetaObject = { {
    QMetaObject::SuperData::link<QWidget::staticMetaObject>(),
    qt_meta_stringdata_adventureGameMode.data,
    qt_meta_data_adventureGameMode,
    qt_static_metacall,
    nullptr,
    nullptr
} };


const QMetaObject *adventureGameMode::metaObject() const
{
    return QObject::d_ptr->metaObject ? QObject::d_ptr->dynamicMetaObject() : &staticMetaObject;
}

void *adventureGameMode::qt_metacast(const char *_clname)
{
    if (!_clname) return nullptr;
    if (!strcmp(_clname, qt_meta_stringdata_adventureGameMode.stringdata0))
        return static_cast<void*>(this);
    return QWidget::qt_metacast(_clname);
}

int adventureGameMode::qt_metacall(QMetaObject::Call _c, int _id, void **_a)
{
    _id = QWidget::qt_metacall(_c, _id, _a);
    if (_id < 0)
        return _id;
    if (_c == QMetaObject::InvokeMetaMethod) {
        if (_id < 7)
            qt_static_metacall(this, _c, _id, _a);
        _id -= 7;
    } else if (_c == QMetaObject::RegisterMethodArgumentMetaType) {
        if (_id < 7)
            *reinterpret_cast<int*>(_a[0]) = -1;
        _id -= 7;
    }
    return _id;
}

// SIGNAL 0
void adventureGameMode::onBackClicked()
{
    QMetaObject::activate(this, &staticMetaObject, 0, nullptr);
}

// SIGNAL 1
void adventureGameMode::stopLoadingBGM()
{
    QMetaObject::activate(this, &staticMetaObject, 1, nullptr);
}

// SIGNAL 2
void adventureGameMode::resumeLoadingBGM()
{
    QMetaObject::activate(this, &staticMetaObject, 2, nullptr);
}

// SIGNAL 3
void adventureGameMode::gameFinish()
{
    QMetaObject::activate(this, &staticMetaObject, 3, nullptr);
}
QT_WARNING_POP
QT_END_MOC_NAMESPACE
