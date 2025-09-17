/****************************************************************************
** Meta object code from reading C++ file 'startpage.h'
**
** Created by: The Qt Meta Object Compiler version 67 (Qt 5.14.2)
**
** WARNING! All changes made in this file will be lost!
*****************************************************************************/

#include <memory>
#include "../startpage.h"
#include <QtCore/qbytearray.h>
#include <QtCore/qmetatype.h>
#if !defined(Q_MOC_OUTPUT_REVISION)
#error "The header file 'startpage.h' doesn't include <QObject>."
#elif Q_MOC_OUTPUT_REVISION != 67
#error "This file was generated using the moc from 5.14.2. It"
#error "cannot be used with the include files from this version of Qt."
#error "(The moc has changed too much.)"
#endif

QT_BEGIN_MOC_NAMESPACE
QT_WARNING_PUSH
QT_WARNING_DISABLE_DEPRECATED
struct qt_meta_stringdata_startpage_t {
    QByteArrayData data[22];
    char stringdata0[244];
};
#define QT_MOC_LITERAL(idx, ofs, len) \
    Q_STATIC_BYTE_ARRAY_DATA_HEADER_INITIALIZER_WITH_OFFSET(len, \
    qptrdiff(offsetof(qt_meta_stringdata_startpage_t, stringdata0) + ofs \
        - idx * sizeof(QByteArrayData)) \
    )
static const qt_meta_stringdata_startpage_t qt_meta_stringdata_startpage = {
    {
QT_MOC_LITERAL(0, 0, 9), // "startpage"
QT_MOC_LITERAL(1, 10, 17), // "startSurvivalGame"
QT_MOC_LITERAL(2, 28, 0), // ""
QT_MOC_LITERAL(3, 29, 8), // "goToHelp"
QT_MOC_LITERAL(4, 38, 18), // "openSettingsDialog"
QT_MOC_LITERAL(5, 57, 14), // "updateSettings"
QT_MOC_LITERAL(6, 72, 9), // "volumeBGM"
QT_MOC_LITERAL(7, 82, 10), // "volumeItem"
QT_MOC_LITERAL(8, 93, 10), // "difficulty"
QT_MOC_LITERAL(9, 104, 3), // "fps"
QT_MOC_LITERAL(10, 108, 7), // "gesture"
QT_MOC_LITERAL(11, 116, 12), // "updateVolume"
QT_MOC_LITERAL(12, 129, 20), // "handleGameToMainMenu"
QT_MOC_LITERAL(13, 150, 17), // "handleRestartGame"
QT_MOC_LITERAL(14, 168, 17), // "survivalGameMode*"
QT_MOC_LITERAL(15, 186, 2), // "g1"
QT_MOC_LITERAL(16, 189, 18), // "adventureGameMode*"
QT_MOC_LITERAL(17, 208, 2), // "g2"
QT_MOC_LITERAL(18, 211, 14), // "smallGameMode*"
QT_MOC_LITERAL(19, 226, 2), // "g3"
QT_MOC_LITERAL(20, 229, 11), // "puzzleMode*"
QT_MOC_LITERAL(21, 241, 2) // "g4"

    },
    "startpage\0startSurvivalGame\0\0goToHelp\0"
    "openSettingsDialog\0updateSettings\0"
    "volumeBGM\0volumeItem\0difficulty\0fps\0"
    "gesture\0updateVolume\0handleGameToMainMenu\0"
    "handleRestartGame\0survivalGameMode*\0"
    "g1\0adventureGameMode*\0g2\0smallGameMode*\0"
    "g3\0puzzleMode*\0g4"
};
#undef QT_MOC_LITERAL

static const uint qt_meta_data_startpage[] = {

 // content:
       8,       // revision
       0,       // classname
       0,    0, // classinfo
      10,   14, // methods
       0,    0, // properties
       0,    0, // enums/sets
       0,    0, // constructors
       0,       // flags
       1,       // signalCount

 // signals: name, argc, parameters, tag, flags
       1,    0,   64,    2, 0x06 /* Public */,

 // slots: name, argc, parameters, tag, flags
       3,    0,   65,    2, 0x0a /* Public */,
       4,    0,   66,    2, 0x0a /* Public */,
       5,    5,   67,    2, 0x0a /* Public */,
      11,    0,   78,    2, 0x0a /* Public */,
      12,    0,   79,    2, 0x0a /* Public */,
      13,    1,   80,    2, 0x0a /* Public */,
      13,    1,   83,    2, 0x0a /* Public */,
      13,    1,   86,    2, 0x0a /* Public */,
      13,    1,   89,    2, 0x0a /* Public */,

 // signals: parameters
    QMetaType::Void,

 // slots: parameters
    QMetaType::Void,
    QMetaType::Void,
    QMetaType::Void, QMetaType::Int, QMetaType::Int, QMetaType::QString, QMetaType::Int, QMetaType::Bool,    6,    7,    8,    9,   10,
    QMetaType::Void,
    QMetaType::Void,
    QMetaType::Void, 0x80000000 | 14,   15,
    QMetaType::Void, 0x80000000 | 16,   17,
    QMetaType::Void, 0x80000000 | 18,   19,
    QMetaType::Void, 0x80000000 | 20,   21,

       0        // eod
};

void startpage::qt_static_metacall(QObject *_o, QMetaObject::Call _c, int _id, void **_a)
{
    if (_c == QMetaObject::InvokeMetaMethod) {
        auto *_t = static_cast<startpage *>(_o);
        Q_UNUSED(_t)
        switch (_id) {
        case 0: _t->startSurvivalGame(); break;
        case 1: _t->goToHelp(); break;
        case 2: _t->openSettingsDialog(); break;
        case 3: _t->updateSettings((*reinterpret_cast< int(*)>(_a[1])),(*reinterpret_cast< int(*)>(_a[2])),(*reinterpret_cast< const QString(*)>(_a[3])),(*reinterpret_cast< int(*)>(_a[4])),(*reinterpret_cast< bool(*)>(_a[5]))); break;
        case 4: _t->updateVolume(); break;
        case 5: _t->handleGameToMainMenu(); break;
        case 6: _t->handleRestartGame((*reinterpret_cast< survivalGameMode*(*)>(_a[1]))); break;
        case 7: _t->handleRestartGame((*reinterpret_cast< adventureGameMode*(*)>(_a[1]))); break;
        case 8: _t->handleRestartGame((*reinterpret_cast< smallGameMode*(*)>(_a[1]))); break;
        case 9: _t->handleRestartGame((*reinterpret_cast< puzzleMode*(*)>(_a[1]))); break;
        default: ;
        }
    } else if (_c == QMetaObject::RegisterMethodArgumentMetaType) {
        switch (_id) {
        default: *reinterpret_cast<int*>(_a[0]) = -1; break;
        case 6:
            switch (*reinterpret_cast<int*>(_a[1])) {
            default: *reinterpret_cast<int*>(_a[0]) = -1; break;
            case 0:
                *reinterpret_cast<int*>(_a[0]) = qRegisterMetaType< survivalGameMode* >(); break;
            }
            break;
        case 7:
            switch (*reinterpret_cast<int*>(_a[1])) {
            default: *reinterpret_cast<int*>(_a[0]) = -1; break;
            case 0:
                *reinterpret_cast<int*>(_a[0]) = qRegisterMetaType< adventureGameMode* >(); break;
            }
            break;
        case 8:
            switch (*reinterpret_cast<int*>(_a[1])) {
            default: *reinterpret_cast<int*>(_a[0]) = -1; break;
            case 0:
                *reinterpret_cast<int*>(_a[0]) = qRegisterMetaType< smallGameMode* >(); break;
            }
            break;
        case 9:
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
            using _t = void (startpage::*)();
            if (*reinterpret_cast<_t *>(_a[1]) == static_cast<_t>(&startpage::startSurvivalGame)) {
                *result = 0;
                return;
            }
        }
    }
}

QT_INIT_METAOBJECT const QMetaObject startpage::staticMetaObject = { {
    QMetaObject::SuperData::link<QWidget::staticMetaObject>(),
    qt_meta_stringdata_startpage.data,
    qt_meta_data_startpage,
    qt_static_metacall,
    nullptr,
    nullptr
} };


const QMetaObject *startpage::metaObject() const
{
    return QObject::d_ptr->metaObject ? QObject::d_ptr->dynamicMetaObject() : &staticMetaObject;
}

void *startpage::qt_metacast(const char *_clname)
{
    if (!_clname) return nullptr;
    if (!strcmp(_clname, qt_meta_stringdata_startpage.stringdata0))
        return static_cast<void*>(this);
    return QWidget::qt_metacast(_clname);
}

int startpage::qt_metacall(QMetaObject::Call _c, int _id, void **_a)
{
    _id = QWidget::qt_metacall(_c, _id, _a);
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
void startpage::startSurvivalGame()
{
    QMetaObject::activate(this, &staticMetaObject, 0, nullptr);
}
QT_WARNING_POP
QT_END_MOC_NAMESPACE
