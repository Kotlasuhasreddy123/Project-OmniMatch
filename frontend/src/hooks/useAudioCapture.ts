'use client';

/**
 * useAudioCapture — consent-gated ambient audio recording hook.
 *
 * SECURITY (REQ-01): getUserMedia() is NEVER called unless consentGranted is true.
 * The hook enforces this at the code level — not just UI level.
 */

import { useCallback, useEffect, useRef, useState } from "react";

export type RecordingState = "idle" | "recording" | "processing" | "error";

interface UseAudioCaptureOptions {
  /** Must be true before any microphone access is attempted. */
  consentGranted: boolean;
  /** Called when a recording chunk is ready. */
  onChunkReady?: (blob: Blob) => void;
  /** Called when recording stops with the complete audio blob. */
  onRecordingComplete?: (blob: Blob) => void;
}

interface UseAudioCaptureReturn {
  recordingState: RecordingState;
  startRecording: () => Promise<void>;
  stopRecording: () => void;
  error: string | null;
}

export function useAudioCapture({
  consentGranted,
  onChunkReady,
  onRecordingComplete,
}: UseAudioCaptureOptions): UseAudioCaptureReturn {
  const [recordingState, setRecordingState] = useState<RecordingState>("idle");
  const [error, setError] = useState<string | null>(null);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  // Clean up stream on unmount
  useEffect(() => {
    return () => {
      streamRef.current?.getTracks().forEach((t) => t.stop());
    };
  }, []);

  const startRecording = useCallback(async () => {
    // HARD GUARD (REQ-01): refuse to access microphone without consent
    if (!consentGranted) {
      setError(
        "Patient consent is required before audio recording can begin. " +
          "Please enable the consent toggle first."
      );
      return;
    }

    setError(null);
    chunksRef.current = [];

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 16000,
        },
      });

      streamRef.current = stream;

      const mimeType = MediaRecorder.isTypeSupported("audio/webm;codecs=opus")
        ? "audio/webm;codecs=opus"
        : "audio/webm";

      const recorder = new MediaRecorder(stream, { mimeType });
      mediaRecorderRef.current = recorder;

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data);
          onChunkReady?.(e.data);
        }
      };

      recorder.onstop = () => {
        const fullBlob = new Blob(chunksRef.current, { type: mimeType });
        onRecordingComplete?.(fullBlob);
        // Release the stream
        stream.getTracks().forEach((t) => t.stop());
        streamRef.current = null;
        setRecordingState("idle");
      };

      recorder.start(3000); // emit chunk every 3 seconds
      setRecordingState("recording");
    } catch (err) {
      const msg =
        err instanceof Error ? err.message : "Microphone access denied.";
      setError(msg);
      setRecordingState("error");
    }
  }, [consentGranted, onChunkReady, onRecordingComplete]);

  const stopRecording = useCallback(() => {
    if (
      mediaRecorderRef.current &&
      mediaRecorderRef.current.state !== "inactive"
    ) {
      mediaRecorderRef.current.stop();
      setRecordingState("processing");
    }
  }, []);

  return { recordingState, startRecording, stopRecording, error };
}
