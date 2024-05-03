import React, { useState, useEffect, useCallback, useRef } from "react";
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  BackHandler,
} from "react-native";
import * as FileSystem from "expo-file-system";
import { Audio } from "expo-av";
import { polyfill as polyfillEncoding } from "react-native-polyfill-globals/src/encoding";
import { create } from "zustand";
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

interface AudioQueueState {
  audioQueue: string[]; // Define the audio queue type
  addToQueue: (uri: string) => void; // Function to set audio queue
}

const useAudioQueueStore = create<AudioQueueState>((set) => ({
  audioQueue: [], // initial state
  addToQueue: (uri) =>
    set((state) => ({ audioQueue: [...state.audioQueue, uri] })), // action to set audio queue
}));

interface SoundState {
  sound: Audio.Sound | null; // Define the sound type
  setSound: (newSound: Audio.Sound | null) => void; // Function to set sound
}

const useSoundStore = create<SoundState>((set) => ({
  sound: null, // initial state
  setSound: (newSound) => set({ sound: newSound }), // action to set sound
}));

const Main: React.FC<MainProps> = ({ route }) => {
  const { scannedData } = route.params;
  const [connectionStatus, setConnectionStatus] =
    useState<string>("Connecting...");
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [wsUrl, setWsUrl] = useState("");
  const [rescan, setRescan] = useState(false);
  const [isPressed, setIsPressed] = useState(false);
  const [recording, setRecording] = useState<Audio.Recording | null>(null);
  const addToQueue = useAudioQueueStore((state) => state.addToQueue);
  const audioQueue = useAudioQueueStore((state) => state.audioQueue);
  const setSound = useSoundStore((state) => state.setSound);
  const sound = useSoundStore((state) => state.sound);
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

  async function dirExists() {
    /**
     * Checks if audio directory exists in device storage, if not creates it.
     */
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

  const playNextAudio = useCallback(async () => {
    if (audioQueue.length > 0 && sound == null) {
      const uri = audioQueue.shift() as string;

      try {
        const { sound: newSound } = await Audio.Sound.createAsync({ uri });
        setSound(newSound);
        setSoundUriMap(new Map(soundUriMap.set(newSound, uri)));
        await newSound.playAsync();
        newSound.setOnPlaybackStatusUpdate(_onPlayBackStatusUpdate);
      } catch (error) {
        console.log("Error playing audio", error);
        playNextAudio();
      }
    } else {
      // audioQueue is empty or sound is not null
      return;
    }
  }, [audioQueue, sound, soundUriMap]);

  const _onPlayBackStatusUpdate = useCallback(
    async (status: any) => {
      if (status.didJustFinish) {
        await sound?.unloadAsync();
        soundUriMap.delete(sound);
        setSoundUriMap(new Map(soundUriMap));
        setSound(null);
        playNextAudio();
      }
    },
    [sound, soundUriMap, playNextAudio]
  );

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

  useEffect(() => {
    if (audioQueue.length > 0 && !sound) {
      playNextAudio();
    }
  }, [audioQueue, sound, playNextAudio]);

  useEffect(() => {}, [sound]);

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

          if (message.content && message.type == "audio") {
            const buffer = message.content;
            if (buffer && buffer.length > 0) {
              const filePath = await constructTempFilePath(buffer);
              if (filePath !== null) {
                addToQueue(filePath);
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
      <View style={styles.middle}>
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
    position: "relative",
  },
  middle: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    padding: 10,
    position: "relative",
  },
  circle: {
    width: 100,
    height: 100,
    borderRadius: 50,
    justifyContent: "center",
    alignItems: "center",
  },
  qr: {
    position: "absolute",
    top: 30,
    left: 10,
    padding: 10,
    zIndex: 100,
  },
  icon: {
    height: 40,
    width: 40,
  },
  topBar: {
    height: 40,
    backgroundColor: "#000",
    paddingTop: 50,
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
});

export default Main;
