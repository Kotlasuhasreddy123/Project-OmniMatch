'use client';

import { useState, useCallback, useEffect } from "react";
import { useRouter } from "next/navigation";
import { ConsentToggle } from "@/components/ConsentToggle/ConsentToggle";
import { AudioRecorder } from "@/components/AudioRecorder/AudioRecorder";
import { TranscriptHeatmap } from "@/components/TranscriptHeatmap/TranscriptHeatmap";
import { useConsent } from "@/hooks/useConsent";
import { transcribeAudio, extractEntities } from "@/lib/apiClient";
import { getOrCreateSessionId } from "@/lib/session";
import { getCurrentUser } from "@/lib/auth";
import { Loader2, ChevronRight } from "lucide-react";
import type { WordConfidence } from "@/types";

type SessionStep = "capture" | "transcribing" | "review" | "extracting";

export default function SessionPage() {
  const router = useRouter();
  const [sessionId, setSessionId] = useState<string>("");

  useEffect(() => {
    if (!getCurrentUser()) {
      router.replace("/login");
      return;
    }
    setSessionId(getOrCreateSessionId());
  }, [router]);

  const { consentGranted, toggleConsent, isLogging, error: consentError } =
    useConsent({ sessionId });

  const [step, setStep] = useState<SessionStep>("capture");
  const [transcription, setTranscription] = useState<string>("");
  const [wordConfidences, setWordConfidences] = useState<WordConfidence[]>([]);
  const [statusMessage, setStatusMessage] = useState<string>("");
  const [error, setError] = useState<string | null>(null);

  const handleRecordingComplete = useCallback(
    async (blob: Blob) => {
      if (!sessionId) return;
      setError(null);

      setStep("transcribing");
      setStatusMessage("Transcribing audio with Whisper…");
      let transcriptionText = "";
      let wordConf: WordConfidence[] = [];

      try {
        const result = await transcribeAudio(sessionId, blob);
        transcriptionText = result.transcription;
        wordConf = result.word_confidences ?? [];
        setTranscription(transcriptionText);
        setWordConfidences(wordConf);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Transcription failed.");
        setStep("capture");
        return;
      }

      setStep("review");
    },
    [sessionId]
  );

  const handleTranscriptCorrected = useCallback((corrected: string) => {
    setTranscription(corrected);
  }, []);

  const handleProceed = useCallback(async () => {
    if (!sessionId || !transcription.trim()) return;
    setError(null);
    setStep("extracting");
    setStatusMessage("Extracting clinical entities…");
    try {
      const nlpResult = await extractEntities(transcription, sessionId);
      sessionStorage.setItem("omni_entities", JSON.stringify(nlpResult.entities));
      sessionStorage.setItem("omni_transcription", transcription);
      sessionStorage.setItem("omni_word_confidences", JSON.stringify(wordConfidences));
      router.push("/verify");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Entity extraction failed.");
      setStep("review");
    }
  }, [sessionId, transcription, wordConfidences, router]);

  const isProcessing = step === "transcribing" || step === "extracting";

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">New Visit Session</h1>
        {sessionId && (
          <p className="mt-1 text-sm text-gray-500">
            Session ID: <code className="text-xs">{sessionId}</code>
          </p>
        )}
      </div>

      <ConsentToggle
        consentGranted={consentGranted}
        onToggle={toggleConsent}
        isLoading={isLogging}
        error={consentError}
      />

      <AudioRecorder
        consentGranted={consentGranted}
        onRecordingComplete={handleRecordingComplete}
      />

      {isProcessing && (
        <div
          className="flex items-center gap-3 rounded-xl border border-blue-200 bg-blue-50 px-5 py-4"
          role="status"
          aria-live="polite"
          aria-label={statusMessage}
        >
          <Loader2 className="h-5 w-5 animate-spin text-blue-600" aria-hidden="true" />
          <span className="text-sm font-medium text-blue-700">{statusMessage}</span>
        </div>
      )}

      {transcription && step === "review" && (
        <>
          <TranscriptHeatmap
            transcription={transcription}
            wordConfidences={wordConfidences}
            onCorrected={handleTranscriptCorrected}
          />
          <div className="flex justify-end">
            <button
              type="button"
              onClick={handleProceed}
              aria-label="Extract entities from reviewed transcript"
              className="flex items-center gap-1.5 text-sm font-medium text-blue-600 hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 rounded"
            >
              Proceed to Verification
              <ChevronRight className="h-4 w-4" aria-hidden="true" />
            </button>
          </div>
        </>
      )}

      {error && (
        <p role="alert" className="text-sm text-red-600">{error}</p>
      )}
    </div>
  );
}
