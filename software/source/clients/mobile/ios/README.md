# iOS/iPadOS Native Client

This repository contains the source code for the 01 iOS/iPadOS Native app. It is a work in progress and currently has a dedicated development button.

Feel free to improve this and make a pull request!

To run it on your own, you can either install the app directly through the current TestFlight [here](https://testflight.apple.com/join/v8SyuzMT), or build from the source code files in Xcode on your Mac.

## Instructions

Follow the **[software setup steps](https://github.com/OpenInterpreter/01?tab=readme-ov-file#software)** in the main repo's README first before you read this

In Xcode, open the 'zerooone-app' project file in the project folder, change the Signing Team and Bundle Identifier, and build.

## Using the App

To use the app there are four features:

### 1. The speak "Button"
Made to emulate the button on the hardware models of 01, the big, yellow circle in the middle of the screen is what you hold when you want to speak to the model, and let go when you're finished speaking.

### 2. The settings button
Tapping the settings button will allow you to input your websocket address so that the app can properly connect to your computer. If you're not sure how to obtain this, read the **'How to Install'** section below!

### 3. The reconnect button
The arrow will be RED when the websocket connection is not live, and GREEN when it is. If you're making some changes you can easily reconnect by simply tapping the arrow button (or you can just start holding the speak button, too!).

### 4. The terminal button
The terminal button allows you to see all response text coming in from the server side of the 01. You can toggle it by tapping on the button, and each toggle clears the on-device cache of text.
