import QtQuick
import MCUTool

Window {
    width: mainScreen.width
    height: mainScreen.height

    visible: true
    title: "MCUTool"

    Screen01 {
        id: mainScreen

        anchors.centerIn: parent
    }

}

