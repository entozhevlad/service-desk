import { flushPromises, mount } from "@vue/test-utils";
import { beforeEach, describe, expect, it, vi } from "vitest";
import TicketListView from "../TicketListView.vue";

const ticket = {
  id: 1,
  title: "Login issue",
  description: "Cannot sign in",
  status: "new",
  priority: "high",
};

const secondTicket = {
  id: 2,
  title: "Printer issue",
  description: "Paper jam",
  status: "done",
  priority: "low",
};

beforeEach(() => {
  vi.restoreAllMocks();
});

function mockFetchSequence(responses: Array<{ status?: number; body?: unknown; ok?: boolean }>) {
  global.fetch = vi.fn().mockImplementation(async () => {
    const next = responses.shift() ?? { status: 200, body: [] };
    const status = next.status ?? 200;
    const ok = next.ok ?? (status >= 200 && status < 300);
    return {
      ok,
      status,
      statusText: "Request failed",
      json: vi.fn().mockResolvedValue(next.body),
      text: vi.fn().mockResolvedValue(typeof next.body === "string" ? next.body : JSON.stringify(next.body ?? "")),
    } as any;
  });
}

describe("TicketListView", () => {
  it("loads and renders tickets on mount", async () => {
    mockFetchSequence([{ body: [ticket] }]);

    const wrapper = mount(TicketListView);
    await flushPromises();

    expect(fetch).toHaveBeenCalledWith(expect.stringContaining("/tickets"), expect.any(Object));
    expect(wrapper.text()).toContain("Login issue");
    expect(wrapper.text()).toContain("Filters: no filters");
  });

  it("filters rendered tickets by status on client side", async () => {
    mockFetchSequence([{ body: [ticket, secondTicket] }]);

    const wrapper = mount(TicketListView);
    await flushPromises();

    const statusFilter = wrapper.get("select");
    await statusFilter.setValue("done");
    await flushPromises();

    expect(fetch).toHaveBeenCalledTimes(1);
    expect(wrapper.text()).toContain("Printer issue");
    expect(wrapper.text()).not.toContain("Login issue");
  });

  it("creates a ticket from modal and reloads list", async () => {
    mockFetchSequence([
      { body: [] },
      { body: { ...ticket, title: "Printer broken" } },
      { body: [{ ...ticket, title: "Printer broken" }] },
    ]);

    const wrapper = mount(TicketListView);
    await flushPromises();

    const openCreateButton = wrapper.findAll("button").find((b) => b.text().includes("Create ticket"));
    await openCreateButton?.trigger("click");

    await wrapper.find("input[placeholder=\"e.g. Can't login\"]").setValue("Printer broken");
    await wrapper.find("textarea").setValue("Office printer is offline");

    const saveButton = wrapper.findAll("button").find((b) => b.text() === "Save");
    await saveButton?.trigger("click");
    await flushPromises();

    const postCall = (fetch as any).mock.calls.find((call: any[]) => call[1]?.method === "POST");
    expect(postCall[0]).toContain("/ticket");
    expect(JSON.parse(postCall[1].body)).toEqual({
      title: "Printer broken",
      description: "Office printer is offline",
      priority: "medium",
    });
    expect(wrapper.text()).toContain("Printer broken");
  });

  it("does not delete ticket when confirm is cancelled", async () => {
    mockFetchSequence([{ body: [ticket] }]);
    vi.stubGlobal("confirm", vi.fn().mockReturnValue(false));

    const wrapper = mount(TicketListView);
    await flushPromises();

    const deleteButton = wrapper.findAll("button").find((b) => b.text() === "Delete");
    await deleteButton?.trigger("click");

    expect(fetch).toHaveBeenCalledTimes(1);
    expect((confirm as any).mock.calls).toHaveLength(1);
  });

  it("updates ticket status inline and reloads list", async () => {
    mockFetchSequence([
      { body: [ticket] },
      { body: { ...ticket, status: "done" } },
      { body: [{ ...ticket, status: "done" }] },
    ]);

    const wrapper = mount(TicketListView);
    await flushPromises();

    const rowStatus = wrapper.find("tbody select");
    await rowStatus.setValue("done");
    await flushPromises();

    const putCall = (fetch as any).mock.calls.find((call: any[]) => call[1]?.method === "PUT");
    expect(putCall[0]).toContain("/tickets/1");
    expect(JSON.parse(putCall[1].body)).toEqual({ status: "done" });
  });
});
