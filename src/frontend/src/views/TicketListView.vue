<script setup lang="ts">
import { onMounted, ref, computed } from "vue";
import {
  listTickets,
  createTicket,
  updateTicket,
  deleteTicket,
  type Ticket,
  type TicketPriority,
  type TicketStatus,
} from "../api/tickets";

const tickets = ref<Ticket[]>([]);
const loading = ref(false);
const error = ref<string | null>(null);

const statusFilter = ref<string>("");
const priorityFilter = ref<string>("");

const statuses: TicketStatus[] = ["new", "in_progress", "done", "closed"];
const priorities: TicketPriority[] = ["low", "medium", "high", "critical"];

const formOpen = ref(false);
const editId = ref<number | null>(null);

const formTitle = ref("");
const formDescription = ref("");
const formStatus = ref<TicketStatus>("new");
const formPriority = ref<TicketPriority>("medium");
const formAssignee = ref<string>("");

async function load() {
  loading.value = true;
  error.value = null;
  try {
    tickets.value = await listTickets({
      status: statusFilter.value || undefined,
      priority: priorityFilter.value || undefined,
    });
  } catch (e: any) {
    error.value = e?.message ?? "Failed to load tickets";
  } finally {
    loading.value = false;
  }
}

function openCreate() {
  editId.value = null;
  formTitle.value = "";
  formDescription.value = "";
  formStatus.value = "new";
  formPriority.value = "medium";
  formAssignee.value = "";
  formOpen.value = true;
}

function openEdit(t: Ticket) {
  editId.value = t.id;
  formTitle.value = t.title;
  formDescription.value = t.description;
  formStatus.value = t.status;
  formPriority.value = t.priority;
  formAssignee.value = t.assignee ?? "";
  formOpen.value = true;
}

async function submit() {
  error.value = null;
  try {
    if (editId.value === null) {
      await createTicket({
        title: formTitle.value,
        description: formDescription.value,
        priority: formPriority.value,
        assignee: formAssignee.value ? formAssignee.value : null,
      });
    } else {
      await updateTicket(editId.value, {
        title: formTitle.value,
        description: formDescription.value,
        status: formStatus.value,
        priority: formPriority.value,
        assignee: formAssignee.value ? formAssignee.value : null,
      });
    }
    formOpen.value = false;
    await load();
  } catch (e: any) {
    error.value = e?.message ?? "Failed to save ticket";
  }
}

async function remove(id: number) {
  if (!confirm("Delete ticket?")) return;
  error.value = null;
  try {
    await deleteTicket(id);
    await load();
  } catch (e: any) {
    error.value = e?.message ?? "Failed to delete ticket";
  }
}

async function quickStatusUpdate(t: Ticket) {
  try {
    await updateTicket(t.id, { status: t.status });
    await load();
  } catch (e: any) {
    error.value = e?.message ?? "Failed to update status";
  }
}

onMounted(load);

const filteredHint = computed(() => {
  const parts = [];
  if (statusFilter.value) parts.push(`status=${statusFilter.value}`);
  if (priorityFilter.value) parts.push(`priority=${priorityFilter.value}`);
  return parts.length ? parts.join(", ") : "no filters";
});
</script>

<template>
  <main style="max-width: 1000px; margin: 0 auto; padding: 24px">
    <h1 style="margin-bottom: 12px">Mini Service Desk</h1>

    <section style="display: flex; gap: 12px; align-items: end; margin-bottom: 16px; flex-wrap: wrap">
      <div>
        <label>Status</label><br />
        <select v-model="statusFilter" @change="load">
          <option value="">All</option>
          <option v-for="s in statuses" :key="s" :value="s">{{ s }}</option>
        </select>
      </div>

      <div>
        <label>Priority</label><br />
        <select v-model="priorityFilter" @change="load">
          <option value="">All</option>
          <option v-for="p in priorities" :key="p" :value="p">{{ p }}</option>
        </select>
      </div>

      <button style="margin-left: auto" @click="openCreate">+ Create ticket</button>
    </section>

    <p style="opacity: 0.7; margin-top: -8px; margin-bottom: 12px">Filters: {{ filteredHint }}</p>

    <p v-if="loading">Loading…</p>
    <p v-else-if="error" style="color: #b00020; white-space: pre-wrap">{{ error }}</p>

    <table v-else border="1" cellpadding="8" style="border-collapse: collapse; width: 100%">
      <thead>
      <tr>
        <th>ID</th>
        <th>Title</th>
        <th>Status</th>
        <th>Priority</th>
        <th>Assignee</th>
        <th style="width: 220px">Actions</th>
      </tr>
      </thead>
      <tbody>
      <tr v-for="t in tickets" :key="t.id">
        <td>{{ t.id }}</td>
        <td>{{ t.title }}</td>
        <td>
          <select v-model="t.status" @change="quickStatusUpdate(t)">
            <option v-for="s in statuses" :key="s" :value="s">{{ s }}</option>
          </select>
        </td>
        <td>{{ t.priority }}</td>
        <td>{{ t.assignee ?? "-" }}</td>
        <td>
          <button @click="openEdit(t)">Edit</button>
          <button style="margin-left: 8px" @click="remove(t.id)">Delete</button>
        </td>
      </tr>
      <tr v-if="tickets.length === 0">
        <td colspan="6" style="text-align: center; opacity: 0.7">No tickets</td>
      </tr>
      </tbody>
    </table>

    <div v-if="formOpen" style="position: fixed; inset: 0; background: rgba(0,0,0,.4); display: grid; place-items: center">
      <div style="background: white; padding: 16px; width: 520px; border-radius: 8px">
        <h2 style="margin-top: 0">{{ editId === null ? "Create ticket" : "Edit ticket" }}</h2>

        <div style="display: grid; gap: 10px">
          <div>
            <label>Title</label><br />
            <input v-model="formTitle" style="width: 100%" />
          </div>

          <div>
            <label>Description</label><br />
            <textarea v-model="formDescription" rows="4" style="width: 100%"></textarea>
          </div>

          <div style="display: flex; gap: 12px">
            <div style="flex: 1">
              <label>Priority</label><br />
              <select v-model="formPriority" style="width: 100%">
                <option v-for="p in priorities" :key="p" :value="p">{{ p }}</option>
              </select>
            </div>

            <div style="flex: 1">
              <label>Status</label><br />
              <select v-model="formStatus" style="width: 100%">
                <option v-for="s in statuses" :key="s" :value="s">{{ s }}</option>
              </select>
            </div>
          </div>

          <div>
            <label>Assignee</label><br />
            <input v-model="formAssignee" style="width: 100%" placeholder="optional" />
          </div>

          <div style="display: flex; gap: 8px; justify-content: end">
            <button @click="formOpen = false">Cancel</button>
            <button @click="submit" :disabled="!formTitle || !formDescription">Save</button>
          </div>
        </div>
      </div>
    </div>
  </main>
</template>
