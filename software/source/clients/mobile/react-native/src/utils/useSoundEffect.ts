import { useEffect, useState } from "react";
import { Audio } from "expo-av";

const useSoundEffect = (soundFile: any) => {
  const [sound, setSound] = useState<Audio.Sound | null>(null); // Explicitly set initial state to null

  useEffect(() => {
    const loadSound = async () => {
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
