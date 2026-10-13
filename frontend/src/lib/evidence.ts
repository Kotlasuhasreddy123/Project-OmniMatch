/** Build PHI-minimized transcript anchors for approved entities.
 *
 * Raw transcript text remains in the browser session.  The server receives
 * the approved entity, offsets, and a SHA-256 digest of the cited text only.
 */

import type { ClinicalEntity, EvidenceSpan } from "@/types";

async function sha256(value: string): Promise<string> {
  const data = new TextEncoder().encode(value);
  const digest = await crypto.subtle.digest("SHA-256", data);
  return Array.from(new Uint8Array(digest))
    .map((byte) => byte.toString(16).padStart(2, "0"))
    .join("");
}

export async function buildEvidenceSpans(
  transcript: string,
  entities: ClinicalEntity[]
): Promise<EvidenceSpan[]> {
  const normalizedTranscript = transcript.toLocaleLowerCase();
  const approved = entities.filter(
    (entity) => entity.status === "approved" && !entity.negated && entity.context === "patient"
  );

  return Promise.all(
    approved.flatMap((entity) => {
      const start = normalizedTranscript.indexOf(entity.term.toLocaleLowerCase());
      if (start < 0) return [];
      const end = start + entity.term.length;
      return [{ entity, start, end }];
    }).map(async ({ entity, start, end }) => ({
      entity_term: entity.term,
      start_char: start,
      end_char: end,
      excerpt_sha256: await sha256(transcript.slice(start, end)),
      confidence: entity.confidence,
      human_verified: true,
    }))
  );
}
