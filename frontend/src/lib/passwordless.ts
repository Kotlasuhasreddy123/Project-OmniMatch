import { createClient } from "@workos-inc/authkit-js";

export const clientId = process.env.NEXT_PUBLIC_WORKOS_CLIENT_ID || "";
export const organizationId = process.env.NEXT_PUBLIC_WORKOS_ORG_ID || "";
export const portalMode = process.env.NEXT_PUBLIC_PORTAL_MODE === "true";
export const basePath = process.env.NEXT_PUBLIC_BASE_PATH || "";
export const operatorContact =
  process.env.NEXT_PUBLIC_OPERATOR_CONTACT || "suhasreddykotla222@gmail.com";
export const accessConfigured = Boolean(
  clientId &&
    organizationId &&
    /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(operatorContact),
);

let instance: ReturnType<typeof createClient> | null = null;
export async function authClient() {
  if (!accessConfigured)
    throw new Error(
      "Account access is awaiting owner configuration. Explore the preview and installation guide in the meantime.",
    );
  if (!instance) {
    instance = createClient(clientId, {
      redirectUri: `${window.location.origin}${basePath}/login/`,
      // Explicit free browser mode: WorkOS stores refresh state in browser storage.
      // The public portal processes account information only, never visit/audio data.
      devMode: true,
      onRedirectCallback: () =>
        window.history.replaceState({}, "", `${basePath}/login/`),
    }).catch((error) => {
      instance = null;
      throw error;
    });
  }
  return instance;
}

export async function providerToken(): Promise<string> {
  const client = await authClient();
  return client.getAccessToken();
}
