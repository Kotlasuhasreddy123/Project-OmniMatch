import { fireEvent, render, screen } from "@testing-library/react";
import CredentialsPage from "@/app/credentials/page";
import { checkProfessionalRegistry } from "@/lib/apiClient";
let mockPortalMode = false;
jest.mock("@/lib/passwordless", () => ({get portalMode() { return mockPortalMode; }}));
jest.mock("@/lib/apiClient", () => ({ checkProfessionalRegistry: jest.fn() }));
test("registry results do not claim identity proof or account approval", async () => {
  (checkProfessionalRegistry as jest.Mock).mockResolvedValue({ status:"record_found", registry_name:"SYNTHETIC PROVIDER", specialty:"Synthetic specialty", message:"Public record found only", access_granted:false });
  render(<CredentialsPage />);
  fireEvent.change(screen.getByLabelText("10-digit NPI number"), {target:{value:"1234567893"}});
  fireEvent.click(screen.getByRole("button", {name:"Check record"}));
  expect(await screen.findByRole("status")).toHaveTextContent("identity not verified");
  expect(screen.getByRole("status")).toHaveTextContent("No account has been created");
  expect(checkProfessionalRegistry).toHaveBeenCalledWith("1234567893");
});

test("the static public portal sends users to CMS instead of a missing backend", () => {
  mockPortalMode = true;
  render(<CredentialsPage />);
  expect(screen.queryByRole("button", {name:"Check record"})).not.toBeInTheDocument();
  expect(screen.getByRole("link", {name:/Open the CMS registry/})).toHaveAttribute("href", "https://npiregistry.cms.hhs.gov/");
  mockPortalMode = false;
});
