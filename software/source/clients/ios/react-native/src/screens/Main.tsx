import React, { useState, useEffect, useCallback, useRef } from "react";
import { View, Text, TouchableOpacity, StyleSheet, Image } from "react-native";
import * as FileSystem from "expo-file-system";
import { AVPlaybackStatus, AVPlaybackStatusSuccess, Audio } from "expo-av";
import { polyfill as polyfillEncoding } from "react-native-polyfill-globals/src/encoding";
import { create } from "zustand";
import useStore from "../lib/state";
import { Animated } from "react-native";
import * as Haptics from "expo-haptics";
import useSoundEffect from "../lib/useSoundEffect";
import IconImage from "../../assets/qr.png";
import { useNavigation } from "@react-navigation/native";

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
    outputRange: ["black", "white"], // Change as needed
  });
  const buttonBackgroundColor = backgroundColorAnim.interpolate({
    inputRange: [0, 1],
    outputRange: ["white", "black"], // Inverse of the container
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
    console.log(
      `in playNextAudio audioQueue is ${audioQueue.length} and sound is ${sound}`
    );

    if (audioQueue.length > 0 && sound == null) {
      const uri = audioQueue.shift() as string;
      console.log("load audio from", uri);

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
      console.log("audioQueue is empty or sound is not null");
      return;
    }
  }, [audioQueue, sound, soundUriMap]);

  const _onPlayBackStatusUpdate = useCallback(
    async (status) => {
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

  const isAVPlaybackStatusSuccess = (
    status: AVPlaybackStatus
  ): status is AVPlaybackStatusSuccess => {
    return (status as AVPlaybackStatusSuccess).isLoaded !== undefined;
  };

  // useEffect(() => {
  //   console.log("audioQueue has been updated:", audioQueue.length);
  //   if (audioQueue.length == 1) {
  //     playNextAudio();
  //   }
  // }, [audioQueue]);
  useEffect(() => {
    if (audioQueue.length > 0 && !sound) {
      playNextAudio();
    }
  }, [audioQueue, sound, playNextAudio]);
  useEffect(() => {
    console.log("sound has been updated:", sound);
  }, [sound]);

  useEffect(() => {
    let websocket: WebSocket;
    try {
      console.log("Connecting to WebSocket at " + scannedData);
      websocket = new WebSocket(scannedData);
      websocket.binaryType = "blob";

      websocket.onopen = () => {
        setConnectionStatus(`Connected`);
        // setConnectionStatus(`Connected to ${scannedData}`);
        console.log("WebSocket connected");
      };

      websocket.onmessage = async (e) => {
        try {
          const message = JSON.parse(e.data);

          if (message.content && typeof message.content === "string") {
            console.log("✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅ Audio message");

            const buffer = message.content;
            console.log(buffer.length);
            if (buffer && buffer.length > 0) {
              const filePath = await constructTempFilePath(buffer);
              if (filePath !== null) {
                addToQueue(filePath);
                console.log("audio file written to", filePath);
              } else {
                console.error("Failed to create file path");
              }
            } else {
              console.error("Received message is empty or undefined");
            }
          } else {
            // console.log(typeof message);
            // console.log(typeof message.content);
            console.log("Received message content is not a string.");
            console.log(message);
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
        console.log("WebSocket disconnected");
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
  }, [scannedData]);

  const startRecording = useCallback(async () => {
    if (recording) {
      console.log("A recording is already in progress.");
      return;
    }

    try {
      if (
        permissionResponse !== null &&
        permissionResponse.status !== `granted`
      ) {
        console.log("Requesting permission..");
        await requestPermission();
      }

      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        playsInSilentModeIOS: true,
      });

      console.log("Starting recording..");
      const newRecording = new Audio.Recording();
      await newRecording.prepareToRecordAsync(
        Audio.RecordingOptionsPresets.HIGH_QUALITY
      );
      await newRecording.startAsync();

      setRecording(newRecording);
    } catch (err) {
      console.error("Failed to start recording", err);
    }
  }, []);

  const stopRecording = useCallback(async () => {
    console.log("Stopping recording..");

    if (recording) {
      await recording.stopAndUnloadAsync();
      await Audio.setAudioModeAsync({
        allowsRecordingIOS: false,
      });
      const uri = recording.getURI();
      console.log("recording uri at ", uri);
      setRecording(null);

      // sanity check play the audio recording locally
      // recording is working fine; is the server caching the audio file somewhere?
      /**
      if (uri) {
        const { sound } = await Audio.Sound.createAsync({ uri });
        sound.playAsync();
        console.log("playing audio recording from", uri);
      }
       */

      if (ws && uri) {
        const response = await fetch(uri);
        // console.log("fetched audio file", response);
        const blob = await response.blob();

        const reader = new FileReader();
        reader.readAsArrayBuffer(blob);
        reader.onloadend = () => {
          const audioBytes = reader.result;
          if (audioBytes) {
            ws.send(audioBytes);
            const audioArray = new Uint8Array(audioBytes as ArrayBuffer);
            const decoder = new TextDecoder("utf-8");
            console.log(
              "sent audio bytes to WebSocket",
              decoder.decode(audioArray).slice(0, 50)
            );
          }
        };
      }
    }
  }, [recording]);

  const toggleRecording = (shouldPress: boolean) => {
    Animated.timing(backgroundColorAnim, {
      toValue: shouldPress ? 1 : 0,
      duration: 400,
      useNativeDriver: false, // 'backgroundColor' does not support native driver
    }).start();
    Animated.timing(buttonBackgroundColorAnim, {
      toValue: shouldPress ? 1 : 0,
      duration: 400,
      useNativeDriver: false, // 'backgroundColor' does not support native driver
    }).start();
  };
  return (
    <Animated.View style={[styles.container, { backgroundColor }]}>
      {/* <TouchableOpacity
        onPress={() => {
          console.log("hi!");

          navigation.navigate("Camera");
        }}
      >
        <Animated.View style={styles.qr}>
          <Image source={IconImage} style={styles.icon} />
        </Animated.View>
      </TouchableOpacity> */}
      {/* <View style={styles.topBar}></View> */}
      <View style={styles.middle}>
        <Text
          style={[
            styles.statusText,
            {
              color: connectionStatus.startsWith("Connected") ? "green" : "red",
            },
          ]}
        >
          {connectionStatus}
        </Text>
        <TouchableOpacity
          style={styles.button}
          onPressIn={() => {
            playPip();
            setIsPressed(true);
            toggleRecording(true); // Pass true when pressed
            startRecording();
            Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Heavy);
          }}
          onPressOut={() => {
            playPop();
            setIsPressed(false);
            toggleRecording(false); // Pass false when released
            stopRecording();
            Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Heavy);
          }}
        >
          <Animated.View
            style={[styles.circle, { backgroundColor: buttonBackgroundColor }]}
          >
            {/* <Text
              style={
                recording ? styles.buttonTextRecording : styles.buttonTextDefault
              }
            >
              Record
            </Text> */}
          </Animated.View>
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

  button: {
    width: 100,
    height: 100,
    borderRadius: 50,
    justifyContent: "center",
    alignItems: "center",
  },
  buttonTextDefault: {
    color: "black",
    fontSize: 16,
  },
  buttonTextRecording: {
    color: "white",
    fontSize: 16,
  },
  statusText: {
    position: "absolute",
    bottom: 20,
    alignSelf: "center",
    fontSize: 12,
    fontWeight: "bold",
  },
});

export default Main;
