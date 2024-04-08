# Development Setup for Jetson Nano

1. Go through the tutorial here: https://developer.nvidia.com/embedded/learn/get-started-jetson-nano-devkit#intro

2. At the end of that guide, you should have a Jetson running off a power supply or micro USB.

3. Get network connectivity. The Jetson does not have a WiFi module so you will need to plug in ethernet.
    If you have a laptop, you can share internet access over Ethernet.

    To do this with Mac, do the following:

    a. Plug a cable from the Jetson Ethernet port to your Mac (you can use a Ethernet -> USB converter for your Mac).

    b. Go to General->Sharing, then click the little `(i)` icon next to "Internet Sharing", and check all the options.

    ![](mac-share-internet.png)

    c. Go back to General->Sharing, and turn on "Internet Sharing".

    ![](mac-share-internet-v2.png)

    d. Now the Jetson should have connectivity!
