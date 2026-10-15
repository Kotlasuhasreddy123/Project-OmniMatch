'use client';

/**
 * TranscriptHeatmap — NEW FEATURE 6
 * Word-level confidence visualization for Whisper transcriptions.
 *
 * Words with confidence < 0.7 are highlighted amber so clinical staff
 * can manually correct potential transcription errors before NLP runs.
 */

import { useState, useCallback } from "react";
import clsx from "clsx";
import { Edit3, CheckCircle2 } from "lucide-react";

interface WordConfidence {
  word: string;
  confidence: number;
  start_time?: number;
}

interface TranscriptHeatmapProps {
  transcription: string;
  wordConfidences: WordConfidence[];
  onCorrected?: (correctedText: string) => void;
}

const LOW_CONFIDENCE_THRESHOLD = 0.7;
const VERY_LOW_CONFIDENCE_THRESHOLD = 0.5;

export function TranscriptHeatmap({
  transcription,
  wordConfidences,
  onCorrected,
}: TranscriptHeatmapProps) {
  const [editMode, setEditMode] = useState(false);
  const [editedText, setEditedText] = useState(transcription);
  const [saved, setSaved] = useState(false);

  const lowConfidenceCount = wordConfidences.filter(
    (w) => w.confidence < LOW_CONFIDENCE_THRESHOLD
  ).length;

  const handleSave = useCallback(() => {
    onCorrected?.(editedText);
    setSaved(true);
    setEditMode(false);
  }, [editedText, onCorrected]);

  // Build word-highlighted display
  const confidenceMap = new Map(
    wordConfidences.map((w) => [w.word.toLowerCase().replace(/[^a-z]/g, ""), w.confidence])
  );

  const words = transcription.split(/(\s+)/);

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold text-gray-700">Transcription</h2>
        <div className="flex items-center gap-3">
          {lowConfidenceCount > 0 && (
            <span
              className="rounded-full bg-amber-100 px-2.5 py-0.5 text-xs font-medium text-amber-700"
              aria-label={`${lowConfidenceCount} low-confidence words detected`}
            >
              {lowConfidenceCount} low-confidence word{lowConfidenceCount !== 1 ? "s" : ""}
            </span>
          )}
          <button
            onClick={() => setEditMode((p) => !p)}
            aria-label="Edit transcript to correct low-confidence words"
            className={clsx(
              "flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-xs font-medium transition-colors",
              "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500",
              editMode
                ? "border-blue-300 bg-blue-50 text-blue-700"
                : "border-gray-200 text-gray-600 hover:bg-gray-50"
            )}
          >
            <Edit3 className="h-3.5 w-3.5" aria-hidden="true" />
            {editMode ? "Cancel" : "Edit"}
          </button>
        </div>
      </div>

      {/* Legend */}
      {wordConfidences.length > 0 && (
        <div className="flex flex-wrap gap-3 text-xs text-gray-500">
          <span className="flex items-center gap-1">
            <span className="inline-block h-3 w-3 rounded bg-green-100" aria-hidden="true" /> High confidence (&gt;70%)
          </span>
          <span className="flex items-center gap-1">
            <span className="inline-block h-3 w-3 rounded bg-amber-200" aria-hidden="true" /> Low confidence (50–70%)
          </span>
          <span className="flex items-center gap-1">
            <span className="inline-block h-3 w-3 rounded bg-red-200" aria-hidden="true" /> Very low (&lt;50%) — review before NLP
          </span>
        </div>
      )}

      {/* Heatmap display (read mode) */}
      {!editMode && (
        <p
          className="text-sm text-gray-700 leading-relaxed"
          aria-label="Transcription with confidence highlighting"
        >
          {words.map((segment, i) => {
            if (/^\s+$/.test(segment)) return segment;
            const key = segment.toLowerCase().replace(/[^a-z]/g, "");
            const conf = confidenceMap.get(key);
            return (
              <span
                key={i}
                title={conf !== undefined ? `Confidence: ${Math.round(conf * 100)}%` : undefined}
                className={clsx(
                  "rounded px-0.5",
                  conf !== undefined && conf < VERY_LOW_CONFIDENCE_THRESHOLD
                    ? "bg-red-200 text-red-800"
                    : conf !== undefined && conf < LOW_CONFIDENCE_THRESHOLD
                    ? "bg-amber-200 text-amber-800"
                    : conf !== undefined
                    ? "bg-green-50"
                    : ""
                )}
              >
                {segment}
              </span>
            );
          })}
        </p>
      )}

      {/* Edit mode */}
      {editMode && (
        <div className="space-y-2">
          <label htmlFor="transcript-edit" className="sr-only">
            Edit transcript text
          </label>
          <textarea
            id="transcript-edit"
            value={editedText}
            onChange={(e) => setEditedText(e.target.value)}
            rows={5}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm text-gray-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
            aria-describedby="transcript-edit-hint"
          />
          <p id="transcript-edit-hint" className="text-xs text-gray-400">
            Correct any highlighted words before entity extraction. Verify every clinical term yourself.
          </p>
          <button
            onClick={handleSave}
            className="flex items-center gap-1.5 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 transition-colors"
            aria-label="Save corrected transcript"
          >
            <CheckCircle2 className="h-4 w-4" aria-hidden="true" />
            Save Correction
          </button>
        </div>
      )}

      {saved && (
        <p role="status" className="flex items-center gap-1.5 text-xs text-green-700">
          <CheckCircle2 className="h-3.5 w-3.5" aria-hidden="true" />
          Transcript correction saved for entity extraction.
        </p>
      )}
    </div>
  );
}
