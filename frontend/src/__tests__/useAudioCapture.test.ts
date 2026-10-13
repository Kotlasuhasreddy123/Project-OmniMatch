/**
 * useAudioCapture hook tests — consent-gated microphone access (REQ-01).
 * Critical: getUserMedia must NEVER be called when consentGranted=false.
 */

import { renderHook, act } from "@testing-library/react";
import "@testing-library/jest-dom";
import { useAudioCapture } from "@/hooks/useAudioCapture";

const mockGetUserMedia = jest.fn();
const mockMediaRecorder = {
  start: jest.fn(),
  stop: jest.fn(),
  state: "inactive",
  ondataavailable: null as any,
  onstop: null as any,
};

beforeAll(() => {
  Object.defineProperty(global.navigator, "mediaDevices", {
    writable: true,
    value: { getUserMedia: mockGetUserMedia },
  });
  (global as any).MediaRecorder = jest.fn().mockImplementation(() => mockMediaRecorder);
  (global as any).MediaRecorder.isTypeSupported = jest.fn().mockReturnValue(true);
});

beforeEach(() => jest.clearAllMocks());

describe("useAudioCapture — consent gate (REQ-01)", () => {
  it("NEVER calls getUserMedia when consentGranted=false", async () => {
    const { result } = renderHook(() =>
      useAudioCapture({ consentGranted: false })
    );
    await act(async () => { await result.current.startRecording(); });
    expect(mockGetUserMedia).not.toHaveBeenCalled();
    expect(result.current.error).toBeTruthy();
    expect(result.current.error).toMatch(/consent/i);
  });

  it("calls getUserMedia when consentGranted=true", async () => {
    const mockStream = {
      getTracks: jest.fn().mockReturnValue([{ stop: jest.fn() }]),
    };
    mockGetUserMedia.mockResolvedValueOnce(mockStream);

    const { result } = renderHook(() =>
      useAudioCapture({ consentGranted: true })
    );
    await act(async () => { await result.current.startRecording(); });
    expect(mockGetUserMedia).toHaveBeenCalledTimes(1);
  });

  it("starts in idle state", () => {
    const { result } = renderHook(() =>
      useAudioCapture({ consentGranted: false })
    );
    expect(result.current.recordingState).toBe("idle");
    expect(result.current.error).toBeNull();
  });

  it("sets error state when getUserMedia denied", async () => {
    mockGetUserMedia.mockRejectedValueOnce(new Error("Permission denied"));
    const { result } = renderHook(() =>
      useAudioCapture({ consentGranted: true })
    );
    await act(async () => { await result.current.startRecording(); });
    expect(result.current.recordingState).toBe("error");
    expect(result.current.error).toMatch(/Permission denied/i);
  });
});
