import { beforeEach, describe, expect, it, vi } from "vitest";
import { http } from "../http";

beforeEach(() => {
  vi.restoreAllMocks();
});

describe("http client", () => {
  it("adds JSON headers and returns parsed payload", async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: vi.fn().mockResolvedValue({ ok: true }),
    } as any);

    const result = await http.post("/tickets", { title: "A" });

    expect(result).toEqual({ ok: true });
    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining("/tickets"),
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({ title: "A" }),
        headers: expect.objectContaining({ "Content-Type": "application/json" }),
      })
    );
  });

  it("throws response text for non-OK responses", async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 400,
      statusText: "Bad Request",
      text: vi.fn().mockResolvedValue("validation failed"),
    } as any);

    await expect(http.get("/tickets")).rejects.toThrow("validation failed");
  });

  it("returns undefined for 204 responses", async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 204,
      text: vi.fn().mockResolvedValue(""),
      json: vi.fn(),
    } as any);

    const result = await http.delete("/tickets/1");

    expect(result).toBeUndefined();
  });
});
