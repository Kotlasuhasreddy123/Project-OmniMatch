import { fireEvent, render, screen } from "@testing-library/react";
import LoginPage from "@/app/login/page";
import ValidationPage from "@/app/validation/page";
import { PortalBoundary } from "@/components/PortalBoundary";

jest.mock("next/navigation", () => ({
  useRouter: () => ({ replace: jest.fn() }),
  usePathname: () => "/session",
}));
jest.mock("@/lib/passwordless", () => ({
  accessConfigured: false,
  authClient: jest.fn(),
  organizationId: "",
  portalMode: true,
}));

test("unconfigured access cannot submit or collect a password", () => {
  const { container } = render(<LoginPage />);
  expect(screen.getByRole("status")).toHaveTextContent(
    "Access requests are not open yet",
  );
  expect(container.querySelector('input[type="password"]')).toBeNull();
  fireEvent.click(screen.getByRole("checkbox"));
  expect(screen.getByRole("button", { name: "Request access" })).toBeDisabled();
  expect(screen.getByRole("button", { name: /Approved/ })).toBeDisabled();
});

test("changing a language never claims clinical validation", () => {
  render(<ValidationPage />);
  fireEvent.change(screen.getByLabelText("Specialty"), {
    target: { value: "Oncology" },
  });
  fireEvent.change(screen.getByLabelText("Language"), {
    target: { value: "Telugu" },
  });
  expect(screen.getByRole("status")).toHaveTextContent(
    "Oncology · Telugu: clinical validation not established",
  );
  expect(screen.getByRole("status")).toHaveTextContent(
    "No measured evaluation set",
  );
});

test("public portal does not mount the clinical workspace", () => {
  const previous = process.env.NEXT_PUBLIC_PORTAL_MODE;
  process.env.NEXT_PUBLIC_PORTAL_MODE = "true";
  render(
    <PortalBoundary>
      <div>Private recording controls</div>
    </PortalBoundary>,
  );
  expect(
    screen.queryByText("Private recording controls"),
  ).not.toBeInTheDocument();
  expect(
    screen.getByRole("heading", { name: "Open your local research workspace" }),
  ).toBeInTheDocument();
  if (previous === undefined) delete process.env.NEXT_PUBLIC_PORTAL_MODE;
  else process.env.NEXT_PUBLIC_PORTAL_MODE = previous;
});
