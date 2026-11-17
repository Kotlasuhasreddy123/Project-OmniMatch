import { render, screen, fireEvent } from "@testing-library/react";
import "@testing-library/jest-dom";
import { AccountProfile } from "@/components/AccountProfile";
import { setToken } from "@/lib/apiClient";
jest.mock("@/lib/passwordless", () => ({accessConfigured: true, authClient: async () => ({getUser: () => ({email: "staff@example.test", firstName: "Staff", lastName: "User"})})}));
jest.mock("@/lib/auth", () => ({getCurrentUser: () => ({sub: "staff", role: "CLINICAL_STAFF"})}));

test("profile identifies the signed-in account without owner privileges", async () => {
  render(<AccountProfile />);
  const profile = await screen.findByLabelText("Signed in as staff@example.test");
  fireEvent.click(profile);
  expect(screen.getByText("staff@example.test")).toBeInTheDocument();
  expect(screen.getByText("Clinical staff · Personal workspace")).toBeInTheDocument();
});

test("changing accounts clears previous visit drafts but refreshing preserves them", () => {
  const token = (sub: string) => `header.${btoa(JSON.stringify({sub}))}.signature`;
  sessionStorage.clear();
  setToken(token("owner"));
  sessionStorage.setItem("omni_session_id", "owner-visit");
  sessionStorage.setItem("omni_entities", "private draft");
  setToken(token("owner"));
  expect(sessionStorage.getItem("omni_session_id")).toBe("owner-visit");
  setToken(token("staff"));
  expect(sessionStorage.getItem("omni_session_id")).toBeNull();
  expect(sessionStorage.getItem("omni_entities")).toBeNull();
  expect(sessionStorage.getItem("omni_account_sub")).toBe("staff");
});
