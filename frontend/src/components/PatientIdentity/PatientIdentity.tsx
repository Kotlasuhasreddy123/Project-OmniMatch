'use client';

import { useEffect, useState } from "react";
import { getPatientLabel, savePatientLabel, PATIENT_LABEL_PATTERN } from "@/lib/patient";

export function PatientIdentity({ sessionId }: { sessionId: string }) {
  const [value, setValue] = useState("");
  useEffect(() => { setValue(getPatientLabel(sessionId)); }, [sessionId]);
  const valid = !value || PATIENT_LABEL_PATTERN.test(value);
  return (
    <section className="rounded-xl border border-gray-200 bg-white p-5 space-y-2" aria-labelledby="patient-label-heading">
      <h2 id="patient-label-heading" className="font-semibold">1. Give this fictional patient a label</h2>
      <label className="block text-sm font-medium" htmlFor="patient-label">Demo patient ID</label>
      <input id="patient-label" value={value} maxLength={45} placeholder="DEMO-001"
        onChange={(e) => { const next = e.target.value.toUpperCase().trim(); setValue(next); savePatientLabel(sessionId, next); }}
        aria-describedby="patient-label-help patient-label-error" aria-invalid={!valid}
        className="w-full rounded-lg border border-gray-300 px-3 py-2 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500" />
      <p id="patient-label-help" className="text-sm text-gray-600">
        Use an invented label, not a name, medical-record number, or other real identifier. You can enter or change it after recording, before sending the visit. Use the same label for a repeat visit to the same fictional patient.
      </p>
      <p id="patient-label-error" role={!valid ? "alert" : undefined} className="text-sm text-red-700">
        {!valid && "Start with DEMO- and use letters, numbers, hyphens or underscores, for example DEMO-001."}
      </p>
      <p className="text-xs text-gray-500">The patient label links visits. The separate session ID identifies this one visit.</p>
    </section>
  );
}
