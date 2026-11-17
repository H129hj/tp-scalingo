import { afterEach, describe, expect, it, vi } from "vitest";

afterEach(() => vi.unstubAllEnvs());

describe("apiUrl", () => {
  it("construit l'URL depuis VITE_API_URL", async () => {
    vi.stubEnv("VITE_API_URL", "https://api.example.com/");
    vi.resetModules();
    const { apiUrl } = await import("./api");
    expect(apiUrl("/health")).toBe("https://api.example.com/health");
  });
  it("echoue si VITE_API_URL est absente", async () => {
    vi.stubEnv("VITE_API_URL", "");
    vi.resetModules();
    const { apiUrl } = await import("./api");
    expect(() => apiUrl("/health")).toThrow();
  });
});
