import { useCallback, useEffect, useRef, useState } from "react";

interface VoiceRecorderProps {
  onRecordingComplete: (blob: Blob) => Promise<void> | void;
  disabled?: boolean;
  processing?: boolean;
}

export default function VoiceRecorder({
  onRecordingComplete,
  disabled = false,
  processing = false
}: VoiceRecorderProps) {
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const [isRecording, setIsRecording] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [supported, setSupported] = useState(false);

  useEffect(() => {
    setSupported(typeof window !== "undefined" && !!navigator.mediaDevices);
  }, []);

  const stopTracks = useCallback(() => {
    mediaRecorderRef.current?.stream.getTracks().forEach((track) => track.stop());
  }, []);

  const handleStop = useCallback(() => {
    const recorder = mediaRecorderRef.current;
    if (!recorder) {
      return;
    }
    recorder.stop();
  }, []);

  useEffect(() => {
    return () => {
      stopTracks();
    };
  }, [stopTracks]);

  const startRecording = async () => {
    if (!supported || disabled || processing || isRecording) {
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream, { mimeType: "audio/webm" });
      chunksRef.current = [];
      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };
      recorder.onstop = async () => {
        const blob = new Blob(chunksRef.current, { type: recorder.mimeType });
        stopTracks();
        setIsRecording(false);
        await onRecordingComplete(blob);
      };
      recorder.start();
      mediaRecorderRef.current = recorder;
      setIsRecording(true);
      setError(null);
    } catch (err) {
      console.error(err);
      setError(
        "Microphone access was denied. Please allow access and try again."
      );
      stopTracks();
    }
  };

  const stopRecording = () => {
    if (!isRecording) {
      return;
    }
    handleStop();
  };

  if (!supported) {
    return (
      <div className="recorder unavailable">
        <p>Your browser does not support audio recording.</p>
      </div>
    );
  }

  return (
    <div className="recorder">
      <div className="recorder-actions">
        <button
          type="button"
          className={`primary ${isRecording ? "danger" : ""}`}
          onClick={isRecording ? stopRecording : startRecording}
          disabled={disabled || processing}
        >
          {isRecording ? "Stop Recording" : "Start Recording"}
        </button>
        <span className="status-text">
          {processing
            ? "Processing response..."
            : isRecording
            ? "Recording..."
            : "Press start and speak clearly."}
        </span>
      </div>
      {error && <p className="error">{error}</p>}
    </div>
  );
}
