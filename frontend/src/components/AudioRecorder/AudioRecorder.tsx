'use client';

/**
 * AudioRecorder — consent-gated ambient audio capture UI (REQ-01, REQ-08).
 * Disabled at the DOM level when consent is not granted.
 */

import { Mic, MicOff, Square } from "lucide-react";
import clsx from "clsx";
import { useAudioCapture } from "@/hooks/useAudioCapture";

interface AudioRecorderProps {
  consentGranted: boolean;
  onRecordingComplete: (blob: Blob) => void;
}

export function AudioRecorder({
  consentGranted,
  onRecordingComplete,
}: AudioRecorderProps) {
  const { recordingState, startRecording, stopRecording, error } =
    useAudioCapture({
      consentGranted,
      onRecordingComplete,
    });

  const isRecording = recordingState === "recording";
  const isProcessing = recordingState === "processing";
  const canRecord = consentGranted && recordingState === "idle";

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
      <h2 className="text-lg font-semibold text-gray-900">Ambient Audio Capture</h2>
      <p className="mt-1 text-sm text-gray-500">
        Audio is processed in memory only — no files are written to disk.
      </p>

      <div className="mt-5 flex flex-col items-center gap-4">
        {/* Record / Stop button */}
        {!isRecording ? (
          <button
            onClick={startRecording}
            disabled={!canRecord || isProcessing}
            aria-label={
              !consentGranted
                ? "Audio recording disabled — patient consent required"
                : "Start ambient audio recording"
            }
            aria-disabled={!canRecord || isProcessing}
            aria-busy={isProcessing}
            className={clsx(
              "flex h-20 w-20 items-center justify-center rounded-full transition-all",
              "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2",
              canRecord
                ? "bg-blue-600 text-white shadow-lg hover:bg-blue-700 active:scale-95"
                : "cursor-not-allowed bg-gray-200 text-gray-400",
              isProcessing && "animate-pulse"
            )}
          >
            <Mic className="h-8 w-8" aria-hidden="true" />
          </button>
        ) : (
          <button
            onClick={stopRecording}
            aria-label="Stop audio recording"
            className={clsx(
              "flex h-20 w-20 items-center justify-center rounded-full",
              "bg-red-600 text-white shadow-lg hover:bg-red-700 active:scale-95",
              "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-red-500 focus-visible:ring-offset-2",
              "animate-pulse"
            )}
          >
            <Square className="h-8 w-8" aria-hidden="true" />
          </button>
        )}

        {/* State label */}
        <p
          className="text-sm font-medium text-gray-600"
          aria-live="polite"
          aria-atomic="true"
        >
          {isRecording && (
            <span className="flex items-center gap-1 text-red-600">
              <span className="inline-block h-2 w-2 animate-pulse rounded-full bg-red-600" aria-hidden="true" />
              Recording…
            </span>
          )}
          {isProcessing && "Processing audio…"}
          {!isRecording && !isProcessing && !consentGranted && (
            <span className="flex items-center gap-2 text-gray-400">
              <MicOff className="h-4 w-4" aria-hidden="true" />
              Microphone disabled
            </span>
          )}
          {!isRecording && !isProcessing && consentGranted && "Ready to record"}
        </p>

        {/* Error message */}
        {error && (
          <p
            role="alert"
            className="max-w-sm text-center text-sm text-red-600"
          >
            {error}
          </p>
        )}

        {/* Accessibility: consent warning */}
        {!consentGranted && (
          <p
            className="text-xs text-amber-600 font-medium"
            aria-live="polite"
          >
            Enable the Patient Consent toggle above to unlock recording.
          </p>
        )}
      </div>
    </div>
  );
}
