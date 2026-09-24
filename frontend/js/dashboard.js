function formatCurrency(value) {
  return value ? value : "—";
}

function renderStats(stats) {
  document.getElementById("statTotal").textContent = stats.total;
  document.getElementById("statApplied").textContent = stats.applied;
  document.getElementById("statShortlisted").textContent = stats.shortlisted;
  document.getElementById("statInterview").textContent = stats.interview;
  document.getElementById("statSelected").textContent = stats.selected;
  document.getElementById("statRejected").textContent = stats.rejected;
}

function renderRecentApplications(applications) {
  const tbody = document.getElementById("recentApplicationsBody");
  const emptyState = document.getElementById("recentEmptyState");
  const recent = applications.slice(0, 5);

  if (recent.length === 0) {
    tbody.innerHTML = "";
    emptyState.classList.remove("d-none");
    return;
  }

  emptyState.classList.add("d-none");
  tbody.innerHTML = recent
    .map(
      (app) => `
    <tr>
      <td>${app.company}</td>
      <td>${app.role}</td>
      <td>${formatCurrency(app.package)}</td>
      <td>${app.application_date}</td>
      <td><span class="badge-status status-${app.status}">${app.status}</span></td>
    </tr>`
    )
    .join("");
}

async function loadDashboard() {
  try {
    const [stats, applications] = await Promise.all([
      Api.getStats(),
      Api.getApplications(),
    ]);
    renderStats(stats);
    renderRecentApplications(applications);
  } catch (error) {
    console.error("Failed to load dashboard", error);
  }
}

loadDashboard();
