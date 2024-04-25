import { useEffect, useState } from "react";
import { Audio, InterruptionModeAndroid, InterruptionModeIOS } from "expo-av";

const useSoundEffect = (soundFile) => {
  const [sound, setSound] = useState(null); // Explicitly set initial state to null

  useEffect(() => {
    const loadSound = async () => {
      //   await Audio.setAudioModeAsync({
      //     staysActiveInBackground: true,
      //     shouldDuckAndroid: true,
      //     playThroughEarpieceAndroid: false,
      //     interruptionModeIOS: InterruptionModeIOS.DoNotMix,
      //     interruptionModeAndroid: InterruptionModeAndroid.DoNotMix,
      //     allowsRecordingIOS: false,
      //     playsInSilentModeIOS: true,
      //   });
      const { sound: newSound } = await Audio.Sound.createAsync(soundFile);
      setSound(newSound);
    };

    loadSound();

    return () => {
      sound?.unloadAsync();
    };
  }, [soundFile, sound]); // Include sound in the dependency array

  const playSound = async () => {
    if (sound) {
      await sound.playAsync();
    }
  };

  return playSound;
};

export default useSoundEffect;
