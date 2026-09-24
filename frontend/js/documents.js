function renderDocuments(documents) {
  const list = document.getElementById("documentsList");
  const emptyState = document.getElementById("documentsEmptyState");

  if (documents.length === 0) {
    list.innerHTML = "";
    emptyState.classList.remove("d-none");
    return;
  }

  emptyState.classList.add("d-none");
  list.innerHTML = documents
    .map(
      (doc) => `
    <div class="col-md-6 col-lg-4">
      <div class="card doc-card h-100">
        <div class="card-body">
          <h6 class="mb-2">${doc.filename}</h6>
          <p class="text-muted mb-2">${doc.chunk_count} chunks indexed</p>
          <p class="text-muted small mb-3">${new Date(doc.uploaded_at).toLocaleString()}</p>
          <button class="btn btn-sm btn-outline-danger" onclick="deleteDocument('${doc.id}')">Delete</button>
        </div>
      </div>
    </div>`
    )
    .join("");
}

async function loadDocuments() {
  try {
    const documents = await Api.getDocuments();
    renderDocuments(documents);
  } catch (error) {
    console.error("Failed to load documents", error);
  }
}

async function deleteDocument(id) {
  if (!confirm("Delete this document from the knowledge base?")) return;
  await Api.deleteDocument(id);
  loadDocuments();
}

document.getElementById("uploadBtn").addEventListener("click", async () => {
  const fileInput = document.getElementById("documentFileInput");
  const spinner = document.getElementById("uploadSpinner");
  const status = document.getElementById("uploadStatus");

  if (!fileInput.files.length) {
    alert("Please select a document to upload.");
    return;
  }

  spinner.classList.remove("d-none");
  status.innerHTML = "";

  try {
    await Api.uploadDocument(fileInput.files[0]);
    status.innerHTML = '<div class="alert alert-success">Document processed and indexed.</div>';
    fileInput.value = "";
    loadDocuments();
  } catch (error) {
    status.innerHTML = `<div class="alert alert-danger">${error.message}</div>`;
  } finally {
    spinner.classList.add("d-none");
  }
});

loadDocuments();
