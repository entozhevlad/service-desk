import { http } from "./http";

export type TicketStatus = "new" | "in_progress" | "done" | "closed";
export type TicketPriority = "low" | "medium" | "high" | "critical";

export interface Ticket {
  id: number;
  title: string;
  description: string;
  status: TicketStatus;
  priority: TicketPriority;
  created_at?: string;
  updated_at?: string;
}

export interface TicketCreate {
  title: string;
  description: string;
  priority: TicketPriority;
}

export interface TicketUpdate {
  title?: string;
  description?: string;
  status?: TicketStatus;
  priority?: TicketPriority;
}

export async function listTickets(params?: { status?: string; priority?: string }) {
  const search = new URLSearchParams();
  if (params?.status) search.set("status", params.status);
  if (params?.priority) search.set("priority", params.priority);
  const query = search.toString();
  const url = query ? `/tickets?${query}` : "/tickets";
  return http.get<Ticket[]>(url);
}

export function getTicket(id: number) {
  return http.get<Ticket>(`/tickets/${id}`);
}

export function createTicket(payload: TicketCreate) {
  return http.post<Ticket>("/ticket", payload);
}

export function updateTicket(id: number, payload: TicketUpdate) {
  return http.put<Ticket>(`/tickets/${id}`, payload);
}

export function deleteTicket(id: number) {
  return http.delete<void>(`/tickets/${id}`);
}
