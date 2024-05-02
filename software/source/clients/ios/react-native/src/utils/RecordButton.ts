import React, { useState, useEffect, useCallback, useRef } from "react";
import { View, Text, TouchableOpacity, StyleSheet, Image, Touchable } from "react-native";
import * as FileSystem from "expo-file-system";
import { AVPlaybackStatus, AVPlaybackStatusSuccess, Audio } from "expo-av";
import { create } from "zustand";
import useStore from "../utils/state";
import { Animated } from "react-native";
import * as Haptics from "expo-haptics";
import useSoundEffect from "../utils/useSoundEffect";

import { useNavigation } from "@react-navigation/native";

interface RecordButtonProps {
    playPip: () => void;
    playPop: () => void;
    recording: Audio.Recording | null;
    setRecording: (recording: Audio.Recording | null) => void;
    ws: WebSocket | null;
    backgroundColorAnim: Animated.Value;
    buttonBackgroundColorAnim: Animated.Value;
    setIsPressed: (isPressed: boolean) => void;
}


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


const RecordButton = ({ playPip, playPop, recording, setRecording, ws, backgroundColorAnim, buttonBackgroundColorAnim, setIsPressed}: RecordButtonProps) => {
    const [permissionResponse, requestPermission] = Audio.usePermissions();

    useEffect(() => {
        console.log("Permission Response:", permissionResponse);
        if (permissionResponse?.status !== "granted") {
        console.log("Requesting permission..");
        requestPermission();
        }
    }, []);

    const startRecording = useCallback(async () => {
        if (recording) {
          console.log("A recording is already in progress.");
          return;
        }

        try {
          console.log("🌶️🌶️🌶️🌶️🌶️🌶️🌶️🌶️🌶️🌶️");

          console.log(permissionResponse);

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
          // console.log("recording uri at ", uri);
          setRecording(null);

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
    );
};

export default RecordButton;
