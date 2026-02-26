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

async function load() {
  loading.value = true;
  error.value = null;

  try {
    tickets.value = await listTickets();
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
  formOpen.value = true;
}

function openEdit(t: Ticket) {
  editId.value = t.id;
  formTitle.value = t.title;
  formDescription.value = t.description;
  formStatus.value = t.status;
  formPriority.value = t.priority;
  formOpen.value = true;
}

function closeModal() {
  formOpen.value = false;
}

async function submit() {
  error.value = null;
  try {
    if (editId.value === null) {
      await createTicket({
        title: formTitle.value,
        description: formDescription.value,
        priority: formPriority.value,
      });
    } else {
      await updateTicket(editId.value, {
        title: formTitle.value,
        description: formDescription.value,
        status: formStatus.value,
        priority: formPriority.value,
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
  const parts: string[] = [];
  if (statusFilter.value) parts.push(`status=${statusFilter.value}`);
  if (priorityFilter.value) parts.push(`priority=${priorityFilter.value}`);
  return parts.length ? parts.join(", ") : "no filters";
});

const visibleTickets = computed(() =>
  tickets.value.filter((ticket) => {
    if (statusFilter.value && ticket.status !== statusFilter.value) return false;
    if (priorityFilter.value && ticket.priority !== priorityFilter.value) return false;
    return true;
  })
);

const modalTitle = computed(() => (editId.value === null ? "Create ticket" : "Edit ticket"));
</script>

<template>
  <div class="container">
    <div class="card" style="padding: 24px">
      <div
        style="
          display: flex;
          align-items: flex-end;
          justify-content: space-between;
          gap: 16px;
          flex-wrap: wrap;
        "
      >
        <div>
          <h1 class="h1">Mini Service Desk</h1>
        </div>

        <button class="btn btn-primary" @click="openCreate">+ Create ticket</button>
      </div>

      <hr class="hr" />

      <div class="control-row">
        <div class="controls-left">
          <div class="field">
            <label>Status</label>
            <select v-model="statusFilter">
              <option value="">All</option>
              <option v-for="s in statuses" :key="s" :value="s">{{ s }}</option>
            </select>
          </div>

          <div class="field">
            <label>Priority</label>
            <select v-model="priorityFilter">
              <option value="">All</option>
              <option v-for="p in priorities" :key="p" :value="p">{{ p }}</option>
            </select>
          </div>

          <span class="badge">Filters: {{ filteredHint }}</span>
        </div>
      </div>

      <div style="margin-top: 16px">
        <p v-if="loading" class="subtle">Loading…</p>

        <p v-else-if="error" style="color: #b00020; white-space: pre-wrap; margin: 0">
          {{ error }}
        </p>

        <div v-else class="table-wrap">
          <table>
            <thead>
            <tr>
              <th style="width: 80px">ID</th>
              <th>Title</th>
              <th style="width: 180px">Status</th>
              <th style="width: 140px">Priority</th>
              <th style="width: 220px">Actions</th>
            </tr>
            </thead>

            <tbody>
            <tr v-for="t in visibleTickets" :key="t.id">
              <td>{{ t.id }}</td>

              <td>
                <div style="font-weight: 650">{{ t.title }}</div>
                <div class="subtle" style="margin-top: 4px; max-width: 520px">
                  {{ t.description }}
                </div>
              </td>

              <td>
                <select v-model="t.status" @change="quickStatusUpdate(t)">
                  <option v-for="s in statuses" :key="s" :value="s">{{ s }}</option>
                </select>
              </td>

              <td>
                <span class="badge">{{ t.priority }}</span>
              </td>

              <td>
                <div class="actions">
                  <button class="btn" @click="openEdit(t)">Edit</button>
                  <button class="btn btn-danger" @click="remove(t.id)">Delete</button>
                </div>
              </td>
            </tr>

            <tr v-if="visibleTickets.length === 0">
              <td colspan="6" style="text-align: center; padding: 28px">
                <div style="font-weight: 650">No tickets yet</div>
                <div class="subtle" style="margin-top: 6px">
                  Create your first ticket to start tracking requests.
                </div>
                <div style="margin-top: 14px">
                  <button class="btn btn-primary" @click="openCreate">+ Create ticket</button>
                </div>
              </td>
            </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Modal -->
    <div
      v-if="formOpen"
      class="modal-overlay"
      @click.self="closeModal"
      style="
        position: fixed;
        inset: 0;
        background: rgba(17, 24, 39, 0.35);
        display: grid;
        place-items: center;
        padding: 18px;
      "
    >
      <div
        class="card"
        style="
          width: min(560px, 100%);
          padding: 20px;
        "
      >
        <div style="display: flex; align-items: flex-start; justify-content: space-between; gap: 12px">
          <div>
            <h2 style="margin: 0; font-size: 20px; letter-spacing: -0.01em">{{ modalTitle }}</h2>
            <div class="subtle" style="margin-top: 4px">Keep it short and clear.</div>
          </div>

          <button class="btn" @click="closeModal">✕</button>
        </div>

        <hr class="hr" />

        <div style="display: grid; gap: 12px">
          <div>
            <label class="subtle" style="display:block; margin-bottom: 6px">Title</label>
            <input v-model="formTitle" style="width: 100%" placeholder="e.g. Can't login" />
          </div>

          <div>
            <label class="subtle" style="display:block; margin-bottom: 6px">Description</label>
            <textarea
              v-model="formDescription"
              rows="4"
              style="width: 100%"
              placeholder="What happened? Steps to reproduce? Expected behavior?"
            ></textarea>
          </div>

          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px">
            <div>
              <label class="subtle" style="display:block; margin-bottom: 6px">Priority</label>
              <select v-model="formPriority" style="width: 100%">
                <option v-for="p in priorities" :key="p" :value="p">{{ p }}</option>
              </select>
            </div>

            <div>
              <label class="subtle" style="display:block; margin-bottom: 6px">Status</label>
              <select v-model="formStatus" style="width: 100%">
                <option v-for="s in statuses" :key="s" :value="s">{{ s }}</option>
              </select>
            </div>
          </div>

          <div style="display: flex; gap: 10px; justify-content: flex-end; margin-top: 6px">
            <button class="btn" @click="closeModal">Cancel</button>
            <button class="btn btn-primary" @click="submit" :disabled="!formTitle || !formDescription">
              Save
            </button>
          </div>

          <p v-if="error" style="color:#b00020; margin: 4px 0 0; white-space: pre-wrap">
            {{ error }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
