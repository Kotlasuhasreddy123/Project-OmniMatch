import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import SessionPage from "@/app/session/page";
import { extractEntities, transcribeAudio } from "@/lib/apiClient";

const push = jest.fn();

jest.mock("next/navigation", () => ({ useRouter: () => ({ push, replace: jest.fn() }) }));
jest.mock("@/lib/auth", () => ({ getCurrentUser: () => ({ sub: "clinical_staff" }) }));
jest.mock("@/lib/session", () => ({ getOrCreateSessionId: () => "review-test" }));
jest.mock("@/hooks/useConsent", () => ({
  useConsent: () => ({ consentGranted: true, toggleConsent: jest.fn(), isLogging: false, error: null }),
}));
jest.mock("@/components/AudioRecorder/AudioRecorder", () => ({
  AudioRecorder: ({ onRecordingComplete }: { onRecordingComplete: (blob: Blob) => void }) => (
    <button onClick={() => onRecordingComplete(new Blob(["synthetic"], { type: "audio/wav" }))}>
      Finish synthetic recording
    </button>
  ),
}));
jest.mock("@/lib/apiClient", () => ({
  transcribeAudio: jest.fn(),
  extractEntities: jest.fn(),
}));

test("clinician correction is used for entity extraction before navigation", async () => {
  (transcribeAudio as jest.Mock).mockResolvedValue({
    transcription: "I have diabtes and take metformin.",
    word_confidences: [],
  });
  (extractEntities as jest.Mock).mockResolvedValue({ entities: [] });
  render(<SessionPage />);

  fireEvent.click(screen.getByRole("button", { name: "Finish synthetic recording" }));
  await screen.findByRole("button", { name: "Extract entities from reviewed transcript" });
  expect(extractEntities).not.toHaveBeenCalled();

  fireEvent.click(screen.getByRole("button", { name: "Edit transcript to correct low-confidence words" }));
  fireEvent.change(screen.getByRole("textbox", { name: "Edit transcript text" }), {
    target: { value: "I have diabetes and take metformin." },
  });
  fireEvent.click(screen.getByRole("button", { name: "Save corrected transcript" }));
  fireEvent.click(screen.getByRole("button", { name: "Extract entities from reviewed transcript" }));

  await waitFor(() => {
    expect(extractEntities).toHaveBeenCalledWith("I have diabetes and take metformin.", "review-test");
    expect(push).toHaveBeenCalledWith("/verify");
  });
});
