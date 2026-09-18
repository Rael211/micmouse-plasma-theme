// SPDX-FileCopyrightText: 2026 Orlin Chotev <meteoclock@obla.us>
// SPDX-License-Identifier: GPL-3.0-or-later

import QtQuick

Rectangle {
    id: root
    color: "#14110d"

    property int stage

    onStageChanged: {
        if (stage === 1) {
            introAnimation.running = true
        }
    }

    Image {
        id: logo
        anchors.horizontalCenter: parent.horizontalCenter
        y: Math.round(parent.height / 2 - height * 0.8)
        source: "images/logo.png"
        sourceSize.width: Math.round(Math.min(parent.width, parent.height) * 0.22)
        sourceSize.height: sourceSize.width
        opacity: 0
        smooth: true
    }

    Text {
        id: title
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: logo.bottom
        anchors.topMargin: Math.round(logo.height * 0.35)
        text: "Микрофон и мишка"
        color: "#f4efe6"
        opacity: 0
        // Bulgarian text is set in Cormac, which carries the Bulgarian forms.
        font.family: "Cormac"
        font.pixelSize: Math.round(logo.height * 0.2)
    }

    Rectangle {
        id: track
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: title.bottom
        anchors.topMargin: Math.round(logo.height * 0.45)
        width: Math.round(logo.width * 2.2)
        height: Math.max(2, Math.round(logo.height * 0.02))
        color: "#2c251d"
        opacity: 0

        Rectangle {
            id: bar
            height: parent.height
            width: 0
            color: "#ff6600"

            Behavior on width {
                NumberAnimation { duration: 800; easing.type: Easing.InOutQuad }
            }
        }
    }

    // The stage signal arrives in steps, so the bar is driven by it rather than
    // by a fake timer: it reaches the end when the session is actually ready.
    Binding {
        target: bar
        property: "width"
        value: Math.round(track.width * Math.min(1, root.stage / 6))
    }

    ParallelAnimation {
        id: introAnimation
        running: false

        NumberAnimation { target: logo; property: "opacity"; to: 1; duration: 700 }
        NumberAnimation { target: title; property: "opacity"; to: 1; duration: 900 }
        NumberAnimation { target: track; property: "opacity"; to: 1; duration: 900 }
    }
}
