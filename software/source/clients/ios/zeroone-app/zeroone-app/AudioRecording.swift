//
//  AudioRecording.swift
//  zeroone-app
//
//  Created by Elad Dekel on 2024-05-10.
//

import Foundation
import AVFoundation

class AudioRecording: NSObject, AVAudioRecorderDelegate {
    
    var recorder: AVAudioRecorder!
    var session: AVAudioSession!
    
    var isRecording = false
    
    func startRecording() {
        session = AVAudioSession()
        let audio = getDocumentsDirectory().appendingPathComponent("tempvoice.wav") // indicates where the audio data will be recording to
        let s: [String: Any] = [
            AVFormatIDKey: kAudioFormatLinearPCM,
            AVSampleRateKey: 16000.0, 
            AVNumberOfChannelsKey: 1,
            AVEncoderAudioQualityKey: AVAudioQuality.high.rawValue
        ]
        do {
            recorder = try AVAudioRecorder(url: audio, settings: s)
            try session.setActive(true)
            try session.setCategory(.playAndRecord, mode: .default)
            recorder!.delegate = self
            recorder!.record()
            isRecording = true

        } catch {
            print("Error recording")
            print(error.localizedDescription)
        }
        
    }
    
    func getDocumentsDirectory() -> URL { // big thanks to twostraws for this helper function (hackingwithswift.com)
        let paths = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)
        return paths[0]
    }
    
    
    func stopRecording() -> Data? {
        if isRecording && recorder != nil {
            recorder!.stop()
            let audio = getDocumentsDirectory().appendingPathComponent("tempvoice.wav")
            recorder = nil
            do {
                let data = try Data(contentsOf: audio) // sends raw audio data
                try FileManager.default.removeItem(at: audio) // deletes the file
                return data
            } catch {
                print(error.localizedDescription)
                return nil
            }
        } else {
            print("not recording")
            return nil
        }
    }
    
}
