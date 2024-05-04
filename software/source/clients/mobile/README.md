# iOS/Android Client

**_WORK IN PROGRESS_**

This repository contains the source code for the 01 iOS/Android app. Work in progress, we will continue to improve this application to get it working properly.

Feel free to improve this and make a pull request!

If you want to run it on your own, you will need to install Expo Go on your mobile device.

## Setup Instructions

Follow the **[software setup steps](https://github.com/OpenInterpreter/01?tab=readme-ov-file#software)** in the main repo's README first before you read this

```shell
cd software/source/clients/mobile/react-native  # cd into `react-native`
npm install                                  # install dependencies
npx expo start                               # start local development server
```

In **Expo Go** select _Scan QR code_ to scan the QR code produced by the `npx expo start` command

## Using the App

```shell
cd software                             # cd into `software`
poetry run 01 --mobile                  # exposes QR code for 01 Light server
```

In the app, select _Scan Code_ to scan the QR code produced by the `poetry run 01 --mobile` command

Press and hold the button to speak, release to make the request. To rescan the QR code, swipe left on the screen to go back.
