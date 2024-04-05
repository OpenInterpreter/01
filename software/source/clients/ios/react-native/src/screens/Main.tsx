import React, { useState, useEffect } from "react";
import { View, Text, TouchableOpacity, StyleSheet } from "react-native";
import { Audio } from "expo-av";

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
  const [recording, setRecording] = useState<Audio.Recording | null>(null);
  const [audioQueue, setAudioQueue] = useState<string[]>([]);

  useEffect(() => {
    const playNextAudio = async () => {
      if (audioQueue.length > 0) {
        const uri = audioQueue.shift();
        const { sound } = await Audio.Sound.createAsync(
          { uri: uri! },
          { shouldPlay: true }
        );
        sound.setOnPlaybackStatusUpdate(async (status) => {
          if (status.didJustFinish && !status.isLooping) {
            await sound.unloadAsync();
            playNextAudio();
          }
        });
      }
    };

    let websocket: WebSocket;
    try {
      console.log("Connecting to WebSocket at " + scannedData);
      websocket = new WebSocket(scannedData);

      websocket.onopen = () => {
        setConnectionStatus(`Connected to ${scannedData}`);
        console.log("WebSocket connected");
      };
      websocket.onmessage = async (e) => {
        console.log("Received message: ", e.data);
        setAudioQueue((prevQueue) => [...prevQueue, e.data]);
        if (audioQueue.length === 1) {
          playNextAudio();
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
  }, [scannedData, audioQueue]);

  const startRecording = async () => {
    if (recording) {
      console.log("A recording is already in progress.");
      return;
    }

    try {
      console.log("Requesting permissions..");
      await Audio.requestPermissionsAsync();
      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        playsInSilentModeIOS: true,
      });
      console.log("Starting recording..");
      const { recording: newRecording } = await Audio.Recording.createAsync(
        Audio.RECORDING_OPTIONS_PRESET_HIGH_QUALITY
      );
      setRecording(newRecording);
      console.log("Recording started");
    } catch (err) {
      console.error("Failed to start recording", err);
    }
  };

  const stopRecording = async () => {
    console.log("Stopping recording..");
    setRecording(null);
    if (recording) {
      await recording.stopAndUnloadAsync();
      const uri = recording.getURI();
      console.log("Recording stopped and stored at", uri);
      if (ws && uri) {
        ws.send(uri);
      }
    }
  };

  return (
    <View style={styles.container}>
      <Text
        style={[
          styles.statusText,
          { color: connectionStatus.startsWith("Connected") ? "green" : "red" },
        ]}
      >
        {connectionStatus}
      </Text>
      <TouchableOpacity
        style={styles.button}
        onPressIn={startRecording}
        onPressOut={stopRecording}
      >
        <View style={styles.circle}>
          <Text style={styles.buttonText}>Record</Text>
        </View>
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: "#fff",
  },
  circle: {
    width: 100,
    height: 100,
    borderRadius: 50,
    backgroundColor: "black",
    justifyContent: "center",
    alignItems: "center",
  },
  button: {
    width: 100,
    height: 100,
    borderRadius: 50,
    justifyContent: "center",
    alignItems: "center",
  },
  buttonText: {
    color: "white",
    fontSize: 16,
  },
  statusText: {
    marginBottom: 20,
    fontSize: 16,
  },
});

export default Main;
