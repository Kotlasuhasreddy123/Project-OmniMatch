/** Fictional labels only. Each visit keeps its own draft label. */
export const PATIENT_LABEL_PATTERN = /^DEMO-[A-Z0-9][A-Z0-9_-]{0,39}$/;
export function patientLabelKey(sessionId: string): string { return `omni_patient_${sessionId}`; }
export function getPatientLabel(sessionId: string): string {
  return typeof window === "undefined" ? "" : sessionStorage.getItem(patientLabelKey(sessionId)) ?? "";
}
export function savePatientLabel(sessionId: string, value: string): void {
  sessionStorage.setItem(patientLabelKey(sessionId), value);
  if (PATIENT_LABEL_PATTERN.test(value)) sessionStorage.setItem("omni_last_patient", value);
}
