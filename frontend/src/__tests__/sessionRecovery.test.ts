import { getInbox, clearToken } from "@/lib/apiClient";
import { providerToken } from "@/lib/passwordless";

jest.mock("@/lib/passwordless", () => ({ providerToken: jest.fn() }));
const token = providerToken as jest.Mock;
const fetchMock = jest.fn();
const originalClient = process.env.NEXT_PUBLIC_WORKOS_CLIENT_ID;
const response = (status: number) => ({ ok: status === 200, status, json: async () => status === 200 ? { items: [] } : { detail: "Denied" } });

beforeEach(() => {
  jest.clearAllMocks(); clearToken();
  process.env.NEXT_PUBLIC_WORKOS_CLIENT_ID = "client_test";
  global.fetch = fetchMock;
  token.mockResolvedValue("old");
});
afterAll(() => {
  if (originalClient === undefined) delete process.env.NEXT_PUBLIC_WORKOS_CLIENT_ID;
  else process.env.NEXT_PUBLIC_WORKOS_CLIENT_ID = originalClient;
});

test("refreshes a rejected token once and completes the request", async () => {
  token.mockResolvedValueOnce("old").mockResolvedValueOnce("renewed");
  fetchMock.mockResolvedValueOnce(response(401)).mockResolvedValueOnce(response(200));
  await expect(getInbox()).resolves.toEqual({ items: [] });
  expect(token).toHaveBeenLastCalledWith(true);
  expect(fetchMock).toHaveBeenCalledTimes(2);
  expect(fetchMock.mock.calls[1][1].headers.Authorization).toBe("Bearer renewed");
});
test("does not loop when the renewed token is rejected", async () => {
  fetchMock.mockResolvedValue(response(401));
  await expect(getInbox()).rejects.toMatchObject({ status: 401 });
  expect(fetchMock).toHaveBeenCalledTimes(2);
});
test("does not refresh forbidden access", async () => {
  fetchMock.mockResolvedValue(response(403));
  await expect(getInbox()).rejects.toMatchObject({ status: 403 });
  expect(fetchMock).toHaveBeenCalledTimes(1);
  expect(token).toHaveBeenCalledTimes(1);
});
test("explains a connection failure without automatically resending", async () => {
  fetchMock.mockRejectedValue(new TypeError("Failed to fetch"));
  await expect(getInbox()).rejects.toMatchObject({ status: 0, message: expect.stringContaining("outcome is unknown") });
  expect(fetchMock).toHaveBeenCalledTimes(1);
});
