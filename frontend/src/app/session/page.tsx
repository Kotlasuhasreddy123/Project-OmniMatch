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
import { PatientIdentity } from "@/components/PatientIdentity/PatientIdentity";
import { getPatientLabel, savePatientLabel, PATIENT_LABEL_PATTERN } from "@/lib/patient";

type SessionStep = "capture" | "transcribing" | "review" | "extracting";

export default function SessionPage() {
  const router = useRouter();
  const [sessionId, setSessionId] = useState<string>("");

  useEffect(() => {
    if (!getCurrentUser()) {
      router.replace("/login");
      return;
    }
    const id = getOrCreateSessionId();
    const linked = new URLSearchParams(window.location.search).get("patient") ?? "";
    if (PATIENT_LABEL_PATTERN.test(linked) && !getPatientLabel(id)) savePatientLabel(id, linked);
    setSessionId(id);
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
    if (!PATIENT_LABEL_PATTERN.test(getPatientLabel(sessionId))) {
      setError("Enter a patient ID above, such as DEMO-001, before continuing.");
      return;
    }
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
    <div className="mx-auto max-w-3xl space-y-5">
      <header className="page-header">
        <p className="eyebrow">Your workspace</p>
        <h1>New visit</h1>
        <p>Add a patient ID, confirm consent, then record or enter a note. You will review the information before searching for studies.</p>
        <ol className="visit-progress" aria-label="Visit workflow">
          <li aria-current={step === "capture" || step === "transcribing" ? "step" : undefined}>1. Capture</li>
          <li aria-current={step === "review" || step === "extracting" ? "step" : undefined}>2. Check the note</li>
          <li>3. Approve terms</li><li>4. Review studies</li>
        </ol>
        {sessionId && <details className="text-xs text-slate-500"><summary className="cursor-pointer">Visit reference</summary><code className="mt-1 block break-all">{sessionId}</code></details>}
      </header>

      {sessionId && <PatientIdentity sessionId={sessionId} />}

      <ConsentToggle
        consentGranted={consentGranted}
        onToggle={toggleConsent}
        isLoading={isLogging}
        error={consentError}
      />

      {step === "capture" && <AudioRecorder
        consentGranted={consentGranted}
        onRecordingComplete={handleRecordingComplete}
      />}
      {step === "capture" && <details className="rounded-xl border bg-white p-4">
        <summary className="cursor-pointer font-medium focus-visible:ring-2 focus-visible:ring-blue-500">Add a written visit note instead</summary>
        <p className="my-2 text-sm text-gray-600">Use this for information mentioned after recording, or when a microphone is unavailable. It creates a new reviewed visit; it does not rewrite earlier results.</p>
        <label htmlFor="written-note" className="block text-sm font-medium">Visit note (synthetic details)</label>
        <textarea id="written-note" value={transcription} maxLength={50000} onChange={(e) => setTranscription(e.target.value)} className="my-2 w-full rounded border p-3 focus-visible:ring-2 focus-visible:ring-blue-500" rows={5} />
        <button disabled={!consentGranted || !transcription.trim()} onClick={() => { setWordConfidences([]); setStep("review"); }} className="rounded bg-blue-600 px-4 py-2 text-white disabled:opacity-50 focus-visible:ring-2 focus-visible:ring-blue-500">Review written note</button>
      </details>}

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
              Review extracted terms
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
