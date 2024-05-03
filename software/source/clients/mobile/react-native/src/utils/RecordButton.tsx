import React, { useEffect, useCallback } from "react";
import { TouchableOpacity, StyleSheet } from "react-native";
import { Audio } from "expo-av";
import { Animated } from "react-native";
import * as Haptics from "expo-haptics";

interface RecordButtonProps {
  playPip: () => void;
  playPop: () => void;
  recording: Audio.Recording | null;
  setRecording: (recording: Audio.Recording | null) => void;
  ws: WebSocket | null;
  buttonBackgroundColorAnim: Animated.Value;
  backgroundColorAnim: Animated.Value;
  backgroundColor: Animated.AnimatedInterpolation<string | number>;
  buttonBackgroundColor: Animated.AnimatedInterpolation<string | number>;
  setIsPressed: (isPressed: boolean) => void;
}

const styles = StyleSheet.create({
  circle: {
    width: 100,
    height: 100,
    borderRadius: 50,
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
});

const RecordButton: React.FC<RecordButtonProps> = ({
  playPip,
  playPop,
  recording,
  setRecording,
  ws,
  backgroundColorAnim,
  buttonBackgroundColorAnim,
  backgroundColor,
  buttonBackgroundColor,
  setIsPressed,
}: RecordButtonProps) => {
  const [permissionResponse, requestPermission] = Audio.usePermissions();

  useEffect(() => {
    if (permissionResponse?.status !== "granted") {
      requestPermission();
    }
  }, []);

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
        await requestPermission();
      }

      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        playsInSilentModeIOS: true,
      });

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
    if (recording) {
      await recording.stopAndUnloadAsync();
      await Audio.setAudioModeAsync({
        allowsRecordingIOS: false,
      });
      const uri = recording.getURI();
      setRecording(null);

      if (ws && uri) {
        const response = await fetch(uri);
        const blob = await response.blob();

        const reader = new FileReader();
        reader.readAsArrayBuffer(blob);
        reader.onloadend = () => {
          const audioBytes = reader.result;
          if (audioBytes) {
            ws.send(audioBytes);
          }
        };
      }
    }
  }, [recording]);

  const toggleRecording = (shouldPress: boolean) => {
    Animated.timing(backgroundColorAnim, {
      toValue: shouldPress ? 1 : 0,
      duration: 400,
      useNativeDriver: false,
    }).start();
    Animated.timing(buttonBackgroundColorAnim, {
      toValue: shouldPress ? 1 : 0,
      duration: 400,
      useNativeDriver: false,
    }).start();
  };

  return (
    <TouchableOpacity
      style={styles.button}
      onPressIn={() => {
        playPip();
        setIsPressed(true);
        toggleRecording(true);
        startRecording();
        Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Heavy);
      }}
      onPressOut={() => {
        playPop();
        setIsPressed(false);
        toggleRecording(false);
        stopRecording();
        Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Heavy);
      }}
    >
      <Animated.View
        style={[styles.circle, { backgroundColor: buttonBackgroundColor }]}
      />
    </TouchableOpacity>
  );
};

export default RecordButton;
