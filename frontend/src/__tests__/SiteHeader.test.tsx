import { fireEvent, render, screen } from "@testing-library/react";
import { SiteHeader } from "@/components/SiteHeader";
let mockPublic = true;
let mockPath = "/preview/";
jest.mock("next/navigation", () => ({usePathname: () => mockPath}));
jest.mock("@/lib/passwordless", () => ({get portalMode() {return mockPublic;}}));
jest.mock("@/components/AccountProfile", () => ({AccountProfile: () => null}));

test("public navigation directs visitors to usable public pages", () => {
  mockPublic = true;
  render(<SiteHeader />);
  expect(screen.getByRole("link", {name:"Sample results"})).toHaveAttribute("aria-current", "page");
  expect(screen.getByRole("link", {name:"Setup guide"})).toHaveAttribute("href", "/guide");
  expect(screen.queryByRole("link", {name:"New visit"})).not.toBeInTheDocument();
  const menu = screen.getByRole("button", {name:"Open navigation"});
  expect(menu).toHaveAttribute("aria-expanded", "false");
  fireEvent.click(menu);
  expect(screen.getByRole("button", {name:"Close navigation"})).toHaveAttribute("aria-expanded", "true");
  fireEvent.click(screen.getByRole("link", {name:"Sample results"}));
  expect(screen.getByRole("button", {name:"Open navigation"})).toHaveAttribute("aria-expanded", "false");
});

test("installed app navigation exposes visit tasks and identifies the current page", () => {
  mockPublic = false; mockPath = "/inbox";
  render(<SiteHeader />);
  expect(screen.getByRole("link", {name:"Inbox"})).toHaveAttribute("aria-current", "page");
  expect(screen.getByRole("link", {name:"New visit"})).toHaveAttribute("href", "/session");
  expect(screen.getByRole("link", {name:"Patient history"})).toHaveAttribute("href", "/timeline");
});
