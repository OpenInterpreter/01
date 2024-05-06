import React, { useState, useEffect, useCallback, useRef } from "react";
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  BackHandler,
  ScrollView,
} from "react-native";
import * as FileSystem from "expo-file-system";
import { Audio } from "expo-av";
import { polyfill as polyfillEncoding } from "react-native-polyfill-globals/src/encoding";
import { Animated } from "react-native";
import useSoundEffect from "../utils/useSoundEffect";
import RecordButton from "../utils/RecordButton";
import { useNavigation } from "@react-navigation/core";

interface MainProps {
  route: {
    params: {
      scannedData: string;
    };
  };
}

const Main: React.FC<MainProps> = ({ route }) => {
  const { scannedData } = route.params;
  const [connectionStatus, setConnectionStatus] =
    useState<string>("Connecting...");
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [wsUrl, setWsUrl] = useState("");
  const [rescan, setRescan] = useState(false);
  const [isPressed, setIsPressed] = useState(false);
  const [recording, setRecording] = useState<Audio.Recording | null>(null);
  const audioQueueRef = useRef<String[]>([]);
  const soundRef = useRef<Audio.Sound | null>(null);
  const [soundUriMap, setSoundUriMap] = useState<Map<Audio.Sound, string>>(
    new Map()
  );
  const audioDir = FileSystem.documentDirectory + "01/audio/";
  const [permissionResponse, requestPermission] = Audio.usePermissions();
  polyfillEncoding();
  const backgroundColorAnim = useRef(new Animated.Value(0)).current;
  const buttonBackgroundColorAnim = useRef(new Animated.Value(0)).current;
  const playPip = useSoundEffect(require("../../assets/pip.mp3"));
  const playPop = useSoundEffect(require("../../assets/pop.mp3"));
  const navigation = useNavigation();
  const backgroundColor = backgroundColorAnim.interpolate({
    inputRange: [0, 1],
    outputRange: ["black", "white"],
  });
  const buttonBackgroundColor = backgroundColorAnim.interpolate({
    inputRange: [0, 1],
    outputRange: ["white", "black"],
  });
  const [accumulatedMessage, setAccumulatedMessage] = useState<string>("");
  const scrollViewRef = useRef<ScrollView>(null);

  /**
   * Checks if audioDir exists in device storage, if not creates it.
   */
  async function dirExists() {
    try {
      const dirInfo = await FileSystem.getInfoAsync(audioDir);
      if (!dirInfo.exists) {
        console.error("audio directory doesn't exist, creating...");
        await FileSystem.makeDirectoryAsync(audioDir, { intermediates: true });
      }
    } catch (error) {
      console.error("Error checking or creating directory:", error);
    }
  }

  /**
   * Writes the buffer to a temp file in audioDir in base64 encoding.
   *
   * @param {string} buffer
   * @returns tempFilePath or null
   */
  const constructTempFilePath = async (buffer: string) => {
    try {
      await dirExists();
      if (!buffer) {
        console.log("Buffer is undefined or empty.");
        return null;
      }
      const tempFilePath = `${audioDir}${Date.now()}.wav`;

      await FileSystem.writeAsStringAsync(tempFilePath, buffer, {
        encoding: FileSystem.EncodingType.Base64,
      });

      return tempFilePath;
    } catch (error) {
      console.log("Failed to construct temp file path:", error);
      return null; // Return null to prevent crashing, error is logged
    }
  };

  /**
   * Plays the next audio in audioQueue if the queue is not empty
   * and there is no currently playing audio.
   */
  const playNextAudio = useCallback(async () => {
    if (audioQueueRef.current.length > 0 && soundRef.current == null) {
      const uri = audioQueueRef.current.at(0) as string;

      try {
        const { sound: newSound } = await Audio.Sound.createAsync({ uri });
        soundRef.current = newSound;
        setSoundUriMap(new Map(soundUriMap.set(newSound, uri)));
        await newSound.playAsync();
        newSound.setOnPlaybackStatusUpdate(_onPlayBackStatusUpdate);
      } catch (error) {
        console.log("Error playing audio", error);
      }
    } else {
      // audioQueue is empty or sound is not null
      return;
    }
  },[]);

  /**
   * Queries the currently playing Expo Audio.Sound object soundRef
   * for playback status. When the status denotes soundRef has finished
   * playback, we unload the sound and call playNextAudio().
   */
  const _onPlayBackStatusUpdate = useCallback(
    async (status: any) => {
      if (status.didJustFinish) {
        audioQueueRef.current.shift();
        await soundRef.current?.unloadAsync();
        if (soundRef.current) {
          soundUriMap.delete(soundRef.current);
          setSoundUriMap(new Map(soundUriMap));
        }
        soundRef.current = null;
        playNextAudio();
      }
    },[]);

  /**
   * Single swipe to return to the Home screen from the Main page.
   */
  useEffect(() => {
    const backAction = () => {
      navigation.navigate("Home"); // Always navigate back to Home
      return true; // Prevent default action
    };

    // Add event listener for hardware back button on Android
    const backHandler = BackHandler.addEventListener(
      "hardwareBackPress",
      backAction
    );

    return () => backHandler.remove();
  }, [navigation]);

  /**
   * Handles all WebSocket events
   */
  useEffect(() => {
    let websocket: WebSocket;
    try {
      // console.log("Connecting to WebSocket at " + scannedData);
      setWsUrl(scannedData);
      websocket = new WebSocket(scannedData);
      websocket.binaryType = "blob";

      websocket.onopen = () => {
        setConnectionStatus(`Connected`);
      };

      websocket.onmessage = async (e) => {
        try {
          const message = JSON.parse(e.data);
          if (message.content && message.type == "message" && message.role == "assistant"){
            setAccumulatedMessage((prevMessage) => prevMessage + message.content);
            scrollViewRef.current?.scrollToEnd({ animated: true });
          }

          if (message.content && message.type == "audio") {
            const buffer = message.content;
            if (buffer && buffer.length > 0) {
              const filePath = await constructTempFilePath(buffer);
              if (filePath !== null) {
                audioQueueRef.current.push(filePath);

                if (audioQueueRef.current.length == 1) {
                  playNextAudio();
                }
              } else {
                console.error("Failed to create file path");
              }
            } else {
              console.error("Received message is empty or undefined");
            }
          }
        } catch (error) {
          console.error("Error handling WebSocket message:", error);
        }
      };

      websocket.onerror = (error) => {
        setConnectionStatus("Error connecting to WebSocket.");
        console.error("WebSocket error: ", error);
      };

      websocket.onclose = () => {
        setConnectionStatus("Disconnected.");
      };

      setWs(websocket);
    } catch (error) {
      console.log(error);
      setConnectionStatus("Error creating WebSocket.");
    }

    return () => {
      if (websocket) {
        websocket.close();
      }
    };
  }, [scannedData, rescan]);

  return (
    <Animated.View style={[styles.container, { backgroundColor }]}>
      <View style={{flex: 6, alignItems: "center", justifyContent: "center",}}>
        <ScrollView
          ref={scrollViewRef}
          style={styles.scrollViewContent}
          showsVerticalScrollIndicator={false}
        >
          <Text style={styles.accumulatedMessage}>
            {accumulatedMessage}
          </Text>
        </ScrollView>
      </View>
      <View style={{flex: 2, justifyContent: "center", alignItems: "center",}}>
        <RecordButton
          playPip={playPip}
          playPop={playPop}
          recording={recording}
          setRecording={setRecording}
          ws={ws}
          backgroundColorAnim={backgroundColorAnim}
          buttonBackgroundColorAnim={buttonBackgroundColorAnim}
          backgroundColor={backgroundColor}
          buttonBackgroundColor={buttonBackgroundColor}
          setIsPressed={setIsPressed}
        />
      </View>
      <View style={{flex: 1}}>
        <TouchableOpacity
          style={styles.statusButton}
          onPress={() => {
            setRescan(!rescan);
          }}
        >
          <Text
            style={[
              styles.statusText,
              {
                color: connectionStatus.startsWith("Connected")
                  ? "green"
                  : "red",
              },
            ]}
          >
            {connectionStatus}
          </Text>
        </TouchableOpacity>
      </View>
    </Animated.View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  statusText: {
    fontSize: 12,
    fontWeight: "bold",
  },
  statusButton: {
    position: "absolute",
    bottom: 20,
    alignSelf: "center",
  },
  accumulatedMessage: {
    margin: 20,
    fontSize: 15,
    textAlign: "left",
    color: "white",
    paddingBottom: 30,
    fontFamily: "monospace",
  },
  scrollViewContent: {
    padding: 25,
    width: "90%",
    maxHeight: "80%",
    borderWidth: 5,
    borderColor: "white",
    borderRadius: 10,
  },
});

export default Main;
