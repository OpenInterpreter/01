//
//  ViewController.swift
//  zeroone-app
//
//  Created by Elad Dekel on 2024-05-09.
//

import UIKit
import Starscream
import AVFoundation


class ViewController: UIViewController, WebSocketDelegate {

    @IBOutlet weak var terminalFeed: UITextView!
    @IBOutlet weak var terminalButton: UIImageView!
    @IBOutlet weak var reconnectIcon: UIImageView!
    @IBOutlet weak var circle: UIImageView!
    @IBOutlet weak var settingsGear: UIImageView!
    @IBOutlet weak var infoText: UILabel!
    
    var audioRecordingInstance: AudioRecording?
    private var audioData = Data()
    private var audioPlayer: AVAudioPlayer?
    var address: String?
    var isConnected = false
    var recordingPermission = false
    var terminal = false
    var socket: WebSocket?

    
    override func viewDidLoad() {
        super.viewDidLoad()
        terminalFeed.layer.cornerRadius = 15
        infoText.text = "Hold to start once connected."
        // Create a gesture recognizer that tracks when the "button" is held
        let pressGesture = UILongPressGestureRecognizer(target: self, action: #selector(buttonPress(_:)))
        pressGesture.minimumPressDuration = 0.01
        circle.addGestureRecognizer(pressGesture)
        circle.isUserInteractionEnabled = true
        circle.translatesAutoresizingMaskIntoConstraints = false
        
        // Create a geature recognizer for the settings button
        let tapGesture = UITapGestureRecognizer(target: self, action: #selector(settingsGear(_:)))
        settingsGear.addGestureRecognizer(tapGesture)
        settingsGear.isUserInteractionEnabled = true
        
        
        let reconnectGesture = UITapGestureRecognizer(target: self, action: #selector(recconectIcon(_:)))
        reconnectIcon.addGestureRecognizer(reconnectGesture)
        reconnectIcon.isUserInteractionEnabled = true
        
        
        let terminal = UITapGestureRecognizer(target: self, action: #selector(terminalIcon(_:)))
        terminalButton.addGestureRecognizer(terminal)
        terminalButton.isUserInteractionEnabled = true
        
        
    }
    

    
    
    
    
    func checkRecordingPerms() {
        let sess = AVAudioSession.sharedInstance()
        switch (sess.recordPermission) {
        case.denied, .undetermined:
            sess.requestRecordPermission { (granted) in
                if granted {
                    self.recordingPermission = true
                } else {
                    let alert = UIAlertController(title: "Recording Not Permitted", message: "You must allow audio recording in order to send commands. Close the app and re-open it to try again.", preferredStyle: .alert)
                    let action = UIAlertAction(title: "Understood", style: .default)
                    alert.addAction(action)
                    self.present(alert, animated: true)
                }
            }
        case .granted:
            recordingPermission = true
        default:
            break
        }
    }
    
    override func viewDidAppear(_ animated: Bool) {
        if ((UserDefaults.standard.value(forKey: "IPINFO")) != nil) {
            print("here")
            address = UserDefaults.standard.string(forKey: "IPINFO")
            establishConnection()
        } else {
            print("there")
            setAddress()
        }
        checkRecordingPerms()
    }
    
    func receieved(data: String) {
        infoText.text = data
    }
    

    
    
    
    func setAddress() {
        let alert = UIAlertController(title: "Set the Address", message: "Input the address of the WebSocket (found in the terminal running 01 software)", preferredStyle: .alert)
        alert.addTextField { (field) in
            field.placeholder = "Enter Address Here"
        }
        let cancelButton = UIAlertAction(title: "Cancel", style: .cancel)
        alert.addAction(cancelButton)
        let submitButton = UIAlertAction(title: "Done", style: .default) { (_) in
            if let field = alert.textFields?.first, let text = field.text {
                UserDefaults.standard.setValue(text, forKey: "IPINFO")
                self.address = text
                self.establishConnection()
                // HAVE THE TEXT FIELD
            }
        }
        alert.addAction(submitButton)
        
        present(alert, animated: true)
    }
    
    @objc func recconectIcon(_ sender: UIGestureRecognizer) {
        infoText.text = ""
        self.establishConnection()
    }
    
    @objc func terminalIcon(_ sender: UIGestureRecognizer) {
        if (terminal) {
            UIView.animate(withDuration: 0.3) {
                self.terminalFeed.text = ""
                self.terminalFeed.alpha = 0
                let moveT = CGAffineTransform(translationX: 0, y: -190)
                self.appendTranslation(transform: moveT)
                self.terminalButton.image = UIImage(systemName: "apple.terminal")
            } completion: { done in
                self.terminal = false
            }
        } else {
            UIView.animate(withDuration: 0.3) {
                self.terminalFeed.alpha = 1
                let moveT = CGAffineTransform(translationX: 0, y: 190)
                self.appendTranslation(transform: moveT)
                self.terminalButton.image = UIImage(systemName: "apple.terminal.fill")
            } completion: { done in
                self.terminal = true
            }

        }
    }
    
    @objc func settingsGear(_ sender: UIGestureRecognizer) {
        infoText.text = ""
        setAddress()
    }
    
    func appendTranslation(transform: CGAffineTransform) {
        var currentTransform = self.circle.transform
        currentTransform = currentTransform.concatenating(transform)
        self.circle.transform = currentTransform
    }
    
    @objc func buttonPress(_ sender: UILongPressGestureRecognizer) {
        infoText.text = ""
        let feedback = UIImpactFeedbackGenerator(style: .medium)
        if sender.state == .began {
            socket?.connect()
            // check for recording permission, if exists
            // it began, start recording!
            if (isConnected && recordingPermission) {
                audioRecordingInstance = AudioRecording()
                audioRecordingInstance!.startRecording()
                infoText.text = ""
                UIView.animate(withDuration: 0.1) {
                    self.circle.tintColor = .green
                    let newT = CGAffineTransform(scaleX: 0.7, y: 0.7)
                    self.appendTranslation(transform: newT)
                    feedback.prepare()
                    feedback.impactOccurred()
                }
            } else {
                let errorFeedback = UIImpactFeedbackGenerator(style: .heavy)
                errorFeedback.prepare()
                errorFeedback.impactOccurred()
                if (isConnected && !recordingPermission) {
                    infoText.text = "Not recording permission. Please close and re-open the app."
                } else {
                    infoText.text = "Not connected."
                    establishConnection()
                }
                UIView.animate(withDuration: 0.5) {
                    self.circle.tintColor = .red
                } completion: { _ in
                    self.circle.tintColor = .systemYellow
                }
                

            }
        } else if sender.state == .ended {
            if (isConnected && recordingPermission) {
                if (audioRecordingInstance != nil) {
                    let response = audioRecordingInstance!.stopRecording()
                    if (response != nil) {
                        sendAudio(audio: response!)
                    }
                    UIView.animate(withDuration: 0.1) {
                        self.circle.tintColor = .systemYellow
                        let newT = CGAffineTransform(scaleX: 1.4, y: 1.4)
                        self.appendTranslation(transform: newT)
                        feedback.prepare()
                        feedback.impactOccurred()
                    }
                }
            }
            // stop recording and send the audio
        }
    }
    
    
    

    
    func establishConnection() { //connect to the web socket
        if (address != nil) {
            var request = URLRequest(url: URL(string: "http://\(address!)")!)
            request.timeoutInterval = 5
            socket = WebSocket(request: request)
            socket!.delegate = self
            socket!.connect()
        } else {
            setAddress()
        }
    }

    func didReceive(event: Starscream.WebSocketEvent, client: any Starscream.WebSocketClient) { // deal with receiving data from websocket
        switch event {
        case .connected( _):
                isConnected = true
            reconnectIcon.tintColor = .green
            case .disconnected(let reason, let code):
                isConnected = false
            reconnectIcon.tintColor = .red
            case .text(let string):
            if (terminal) {
                terminalFeed.text = terminalFeed.text + "\n>> \(string)"
                let range = NSMakeRange(terminalFeed.text.count - 1, 0)
                terminalFeed.scrollRangeToVisible(range)
            }
            if (string.contains("audio") && string.contains("bytes.raw") && string.contains("start")) {
                infoText.text = "Receiving response..."
                // it started collecting data!
                print("Audio is being receieved.")
            } else if (string.contains("audio") && string.contains("bytes.raw") && string.contains("end")) {
                infoText.text = ""
                print("Audio is no longer being receieved.")
                let wavHeader = createWAVHeader(audioDataSize: Int32(audioData.count - 44))
                // Combine header and data
                var completeWAVData = Data()
                completeWAVData.append(wavHeader)
                completeWAVData.append(audioData.subdata(in: 44..<audioData.count))
                do {
                    try audioPlayer = AVAudioPlayer(data: completeWAVData)
                    audioPlayer?.prepareToPlay()
                    audioPlayer?.play()
                } catch {
                    print("Error")
                }

            }
                print("Received text: \(string)")
            case .binary(let data):
            audioData.append(data)
            print("Received data: \(data.count)")

            case .ping(_):
                break
            case .pong(_):
                break
            case .viabilityChanged(_):
                break
            case .reconnectSuggested(_):
                break
            case .cancelled:
                isConnected = false
            reconnectIcon.tintColor = .red
        case .error(_):
                isConnected = false
            reconnectIcon.tintColor = .red
                case .peerClosed:
            isConnected = false
            reconnectIcon.tintColor = .red
                       break
            }
    }
    


    func createWAVHeader(audioDataSize: Int32) -> Data {
        let headerSize: Int32 = 44 // Standard WAV header size
        let chunkSize: Int32 = 36 + audioDataSize
        let sampleRate: Int32 = 16000 // From i2s_config
        let numChannels: Int16 = 1    // From i2s_config (mono)
        let bitsPerSample: Int16 = 16 // From i2s_config
        let byteRate: Int32 = sampleRate * Int32(numChannels) * Int32(bitsPerSample) / 8
        let blockAlign: Int16 = numChannels * bitsPerSample / 8

        var headerData = Data()

        // RIFF Chunk
        headerData.append(stringToData("RIFF")) // ChunkID
        headerData.append(int32ToData(chunkSize)) // ChunkSize
        headerData.append(stringToData("WAVE")) // Format

        // fmt Subchunk
        headerData.append(stringToData("fmt ")) // Subchunk1ID
        headerData.append(int32ToData(16)) // Subchunk1Size (16 for PCM)
        headerData.append(int16ToData(1)) // AudioFormat (1 for PCM)
        headerData.append(int16ToData(numChannels)) // NumChannels
        headerData.append(int32ToData(sampleRate)) // SampleRate
        headerData.append(int32ToData(byteRate)) // ByteRate
        headerData.append(int16ToData(blockAlign)) // BlockAlign
        headerData.append(int16ToData(bitsPerSample)) // BitsPerSample

        // data Subchunk
        headerData.append(stringToData("data")) // Subchunk2ID
        headerData.append(int32ToData(audioDataSize)) // Subchunk2Size

        return headerData
    }

    func stringToData(_ string: String) -> Data {
        return string.data(using: .utf8)!
    }

    func int16ToData(_ value: Int16) -> Data {
        var value = value.littleEndian
        return Data(bytes: &value, count: MemoryLayout<Int16>.size)
    }

    func int32ToData(_ value: Int32) -> Data {
        var value = value.littleEndian
        return Data(bytes: &value, count: MemoryLayout<Int32>.size)
    }

    
    func sendAudio(audio: Data) {
        if (isConnected) {
            socket!.write(string: "{\"role\": \"user\", \"type\": \"audio\", \"format\": \"bytes.raw\", \"start\": true}")
            socket!.write(data: audio)
            socket!.write(string: "{\"role\": \"user\", \"type\": \"audio\", \"format\": \"bytes.raw\", \"end\": true}")
        } else {
            print("Not connected!")
        }
    }
    

    

    
}


