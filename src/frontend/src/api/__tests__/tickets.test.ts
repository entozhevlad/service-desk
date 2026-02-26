import { describe, it, expect, vi, beforeEach } from "vitest";
import { listTickets, getTicket, createTicket, updateTicket, deleteTicket } from "../tickets";

beforeEach(() => {
  vi.restoreAllMocks();
});

function mockFetch(data: any, status = 200) {
  global.fetch = vi.fn().mockResolvedValue({
    ok: status >= 200 && status < 300,
    status,
    json: vi.fn().mockResolvedValue(data),
    text: vi.fn().mockResolvedValue(typeof data === "string" ? data : JSON.stringify(data)),
  } as any);
}

describe("tickets api (fetch)", () => {
  it("listTickets calls /tickets with query params", async () => {
    mockFetch([]);
    await listTickets({ status: "new", priority: "high" });

    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining("/tickets?status=new&priority=high"),
      expect.any(Object)
    );
  });

  it("getTicket calls /tickets/{id}", async () => {
    mockFetch({ id: 1 });
    await getTicket(1);

    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining("/tickets/1"),
      expect.any(Object)
    );
  });

  it("createTicket calls POST /ticket", async () => {
    mockFetch({ id: 1 });
    await createTicket({ title: "A", description: "B", priority: "medium" });

    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining("/ticket"),
      expect.objectContaining({ method: "POST" })
    );
  });

  it("updateTicket calls PUT /tickets/{id}", async () => {
    mockFetch({ id: 1 });
    await updateTicket(1, { status: "done" });

    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining("/tickets/1"),
      expect.objectContaining({ method: "PUT" })
    );
  });

  it("deleteTicket calls DELETE /tickets/{id}", async () => {
    // для delete может быть 204
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 204,
      json: vi.fn(),
      text: vi.fn().mockResolvedValue(""),
    } as any);

    await deleteTicket(5);

    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining("/tickets/5"),
      expect.objectContaining({ method: "DELETE" })
    );
  });
});
