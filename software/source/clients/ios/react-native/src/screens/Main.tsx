import React, { useState, useEffect } from "react";
import { View, Text, TouchableOpacity, StyleSheet } from "react-native";
import * as FileSystem from 'expo-file-system';
import { AVPlaybackStatus, Audio } from "expo-av";
import { Buffer } from "buffer";
import base64 from 'react-native-base64';

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
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const Buffer = require('buffer/').Buffer;

  const constructTempFilePath = async (buffer: Buffer) => {
    const tempFilePath = `${FileSystem.cacheDirectory}${Date.now()}` + "speech.mp3";
    await FileSystem.writeAsStringAsync(
      tempFilePath,
      buffer.toString("base64"),
      {
        encoding: FileSystem.EncodingType.Base64,
      }
    );

    return tempFilePath;
  };

  const playNextAudio = async () => {
    console.log("in playNextAudio audioQueue is", audioQueue);
    console.log("isPlaying is", isPlaying);

    if (audioQueue.length > 0) {
      const uri = audioQueue.shift() as string;
      console.log("load audio from", uri);
      setIsPlaying(true);

      try {
        const { sound } = await Audio.Sound.createAsync({ uri });
        await sound.playAsync();
        console.log("playing audio from", uri);

        sound.setOnPlaybackStatusUpdate(_onPlaybackStatusUpdate);
      } catch (error){
        console.log("Error playing audio", error);
        setIsPlaying(false);
        playNextAudio();
      }

    }
  };

  const _onPlaybackStatusUpdate = (status: AVPlaybackStatus) => {
    if (status.isLoaded && status.didJustFinish) {
      setIsPlaying(false);
      playNextAudio();
    }
  };

  useEffect(() => {
    let websocket: WebSocket;
    try {
      console.log("Connecting to WebSocket at " + scannedData);
      websocket = new WebSocket(scannedData);
      websocket.binaryType = "blob";

      websocket.onopen = () => {
        setConnectionStatus(`Connected to ${scannedData}`);
        console.log("WebSocket connected");
      };

      websocket.onmessage = async (e) => {
        const message = JSON.parse(e.data);

        if (message.content) {

          const parsedMessage = message.content.replace(/^b'|['"]|['"]$/g, "");
          const buffer = Buffer.from(parsedMessage, 'base64')
          console.log("parsed message", buffer.toString());

          const uri = await constructTempFilePath(buffer);
          setAudioQueue((prevQueue) => [...prevQueue, uri]);
        }

        if (message.format === "bytes.raw" && message.end) {
          console.log("calling playNextAudio");
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
  }, [scannedData]);

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
        const response = await fetch(uri);
        const blob = await response.blob();
        const reader = new FileReader();
        reader.readAsArrayBuffer(blob);
        reader.onloadend = () => {
          const audioBytes = reader.result;
          if (audioBytes) {
            ws.send(audioBytes);
            console.log("sent audio bytes to WebSocket");
          }
        };
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
