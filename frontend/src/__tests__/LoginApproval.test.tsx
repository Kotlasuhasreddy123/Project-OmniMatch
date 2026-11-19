import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import LoginPage from "@/app/login/page";
import { getCurrentUser } from "@/lib/auth";

const mockReplace = jest.fn();
const mockRouter = { replace: mockReplace };
const mockAccessToken = jest.fn(async () => "provider-token");
jest.mock("next/navigation", () => ({ useRouter: () => mockRouter }));
jest.mock("@/lib/passwordless", () => ({
  accessConfigured: true, organizationId: "org_test", portalMode: false,
  authClient: async () => ({ getUser: () => ({ id: "user_test" }), getAccessToken: mockAccessToken }),
}));
jest.mock("@/lib/auth", () => ({ getCurrentUser: jest.fn(), storeToken: jest.fn() }));
jest.mock("@/lib/apiClient", () => ({ clearToken: jest.fn() }));

beforeEach(() => {
  jest.clearAllMocks();
  (getCurrentUser as jest.Mock).mockReturnValue(null);
});

test("verified unapproved users can open public resources without accepting sign-in terms", async () => {
  render(<LoginPage />);
  expect(await screen.findByRole("heading", { name: /workspace approval pending/i })).toBeInTheDocument();
  expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  expect(screen.getByRole("link", { name: /^Sample results/ })).toHaveAttribute("href", "/preview");
  expect(screen.getByRole("link", { name: /^Installation guide/ })).toHaveAttribute("href", "/guide");
  expect(screen.getByRole("link", { name: /^Models and data/ })).toHaveAttribute("href", "/models");
  expect(screen.queryByRole("checkbox")).not.toBeInTheDocument();
  expect(mockReplace).not.toHaveBeenCalled();
});

test("checking approval refreshes permissions and only opens the workspace after an access role exists", async () => {
  render(<LoginPage />);
  const button = await screen.findByRole("button", { name: "Check now" });
  fireEvent.click(button);
  await waitFor(() => expect(mockAccessToken).toHaveBeenCalledWith({ forceRefresh: true }));
  expect(mockReplace).not.toHaveBeenCalled();
  await waitFor(() => expect(button).not.toBeDisabled());
  (getCurrentUser as jest.Mock).mockReturnValue({ role: "CLINICAL_STAFF" });
  fireEvent.click(button);
  await waitFor(() => expect(mockReplace).toHaveBeenCalledWith("/session"));
});

test("pending approval is checked automatically without another email sign-in", async () => {
  jest.useFakeTimers();
  const view = render(<LoginPage />);
  await act(async () => { await Promise.resolve(); });
  expect(screen.getByRole("heading", { name: /workspace approval pending/i })).toBeInTheDocument();
  (getCurrentUser as jest.Mock).mockReturnValue({ role: "CLINICAL_STAFF" });
  await act(async () => { jest.advanceTimersByTime(15000); });
  expect(mockAccessToken).toHaveBeenCalledWith({ forceRefresh: true });
  expect(mockReplace).toHaveBeenCalledWith("/session");
  view.unmount();
  jest.useRealTimers();
});
