let applicationModal;

function openCreateModal() {
  document.getElementById("modalTitle").textContent = "Add Application";
  document.getElementById("applicationForm").reset();
  document.getElementById("applicationId").value = "";
}

function openEditModal(application) {
  document.getElementById("modalTitle").textContent = "Edit Application";
  document.getElementById("applicationId").value = application.id;
  document.getElementById("companyInput").value = application.company;
  document.getElementById("roleInput").value = application.role;
  document.getElementById("packageInput").value = application.package || "";
  document.getElementById("dateInput").value = application.application_date;
  document.getElementById("statusInput").value = application.status;
  document.getElementById("notesInput").value = application.notes || "";
  applicationModal.show();
}

function renderApplications(applications) {
  const tbody = document.getElementById("applicationsBody");
  const emptyState = document.getElementById("emptyState");

  if (applications.length === 0) {
    tbody.innerHTML = "";
    emptyState.classList.remove("d-none");
    return;
  }

  emptyState.classList.add("d-none");
  tbody.innerHTML = applications
    .map(
      (app) => `
    <tr>
      <td>${app.company}</td>
      <td>${app.role}</td>
      <td>${app.package || "—"}</td>
      <td>${app.application_date}</td>
      <td><span class="badge-status status-${app.status}">${app.status}</span></td>
      <td>
        <button class="btn btn-sm btn-outline-light me-1" onclick='editApplication(${JSON.stringify(app)})'>Edit</button>
        <button class="btn btn-sm btn-outline-danger" onclick="deleteApplication('${app.id}')">Delete</button>
      </td>
    </tr>`
    )
    .join("");
}

function editApplication(application) {
  openEditModal(application);
}

async function deleteApplication(id) {
  if (!confirm("Delete this application?")) return;
  await Api.deleteApplication(id);
  loadApplications();
}

async function loadApplications() {
  const search = document.getElementById("searchInput").value.trim();
  const status = document.getElementById("statusFilter").value;
  const params = {};
  if (search) params.search = search;
  if (status) params.status = status;

  try {
    const applications = await Api.getApplications(params);
    renderApplications(applications);
  } catch (error) {
    console.error("Failed to load applications", error);
  }
}

document.getElementById("applicationForm").addEventListener("submit", async (event) => {
  event.preventDefault();

  const id = document.getElementById("applicationId").value;
  const payload = {
    company: document.getElementById("companyInput").value.trim(),
    role: document.getElementById("roleInput").value.trim(),
    package: document.getElementById("packageInput").value.trim() || null,
    application_date: document.getElementById("dateInput").value,
    status: document.getElementById("statusInput").value,
    notes: document.getElementById("notesInput").value.trim() || null,
  };

  try {
    if (id) {
      await Api.updateApplication(id, payload);
    } else {
      await Api.createApplication(payload);
    }
    applicationModal.hide();
    loadApplications();
  } catch (error) {
    alert(`Failed to save application: ${error.message}`);
  }
});

document.addEventListener("DOMContentLoaded", () => {
  applicationModal = new bootstrap.Modal(document.getElementById("applicationModal"));
  loadApplications();
});
