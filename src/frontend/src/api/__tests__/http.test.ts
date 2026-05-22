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
    expect(fetch).toHaveBeenCalledTimes(1);
    const [url, options] = (fetch as any).mock.calls[0];

    expect(url).toContain("/tickets");
    expect(options.method).toBe("POST");
    expect(options.body).toBe(JSON.stringify({ title: "A" }));
    expect(options.headers).toBeInstanceOf(Headers);
    expect(options.headers.get("Content-Type")).toBe("application/json");
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
