function renderChips(items, variant) {
  if (!items || items.length === 0) {
    return '<span class="text-muted">None identified</span>';
  }
  return items.map((item) => `<span class="chip ${variant}">${item}</span>`).join("");
}

function renderList(items) {
  if (!items || items.length === 0) {
    return '<p class="text-muted mb-0">None identified</p>';
  }
  return `<ul class="mb-0">${items.map((item) => `<li>${item}</li>`).join("")}</ul>`;
}

function renderAnalysisResult(data) {
  return `
    <div class="card">
      <div class="card-body">
        <div class="result-section">
          <h6>Summary</h6>
          <p>${data.summary}</p>
        </div>
        <div class="result-section">
          <h6>Detected Skills</h6>
          <div>${renderChips(data.detected_skills, "good")}</div>
        </div>
        <div class="result-section">
          <h6>Missing Skills</h6>
          <div>${renderChips(data.missing_skills, "missing")}</div>
        </div>
        <div class="result-section">
          <h6>Relevant Technologies</h6>
          <div>${renderChips(data.relevant_technologies, "good")}</div>
        </div>
        <div class="row">
          <div class="col-md-6 result-section">
            <h6>Strengths</h6>
            ${renderList(data.strengths)}
          </div>
          <div class="col-md-6 result-section">
            <h6>Areas to Improve</h6>
            ${renderList(data.improvement_areas)}
          </div>
        </div>
        <div class="result-section">
          <h6>Suggestions</h6>
          ${renderList(data.suggestions)}
        </div>
      </div>
    </div>`;
}

function renderMatchResult(data) {
  return `
    <div class="card">
      <div class="card-body">
        <div class="text-center result-section">
          <div class="alignment-ring">${data.alignment_percentage}%</div>
          <div class="text-muted">Approximate skill alignment</div>
        </div>
        <div class="result-section">
          <h6>Matching Skills</h6>
          <div>${renderChips(data.matching_skills, "good")}</div>
        </div>
        <div class="result-section">
          <h6>Missing Skills</h6>
          <div>${renderChips(data.missing_skills, "missing")}</div>
        </div>
        <div class="result-section">
          <h6>Relevant Technologies</h6>
          <div>${renderChips(data.relevant_technologies, "good")}</div>
        </div>
        <div class="result-section">
          <h6>Suggestions to Improve Preparation</h6>
          ${renderList(data.suggestions)}
        </div>
      </div>
    </div>`;
}

document.getElementById("analyzeBtn").addEventListener("click", async () => {
  const fileInput = document.getElementById("analyzeFileInput");
  const resultBox = document.getElementById("analyzeResult");
  const spinner = document.getElementById("analyzeSpinner");

  if (!fileInput.files.length) {
    alert("Please select a resume file.");
    return;
  }

  spinner.classList.remove("d-none");
  resultBox.innerHTML = "";

  try {
    const data = await Api.analyzeResume(fileInput.files[0]);
    resultBox.innerHTML = renderAnalysisResult(data);
  } catch (error) {
    resultBox.innerHTML = `<div class="alert alert-danger">${error.message}</div>`;
  } finally {
    spinner.classList.add("d-none");
  }
});

document.getElementById("matchBtn").addEventListener("click", async () => {
  const fileInput = document.getElementById("matchFileInput");
  const jobDescription = document.getElementById("jobDescriptionInput").value.trim();
  const resultBox = document.getElementById("matchResult");
  const spinner = document.getElementById("matchSpinner");

  if (!fileInput.files.length || !jobDescription) {
    alert("Please provide both a resume file and a job description.");
    return;
  }

  spinner.classList.remove("d-none");
  resultBox.innerHTML = "";

  try {
    const data = await Api.matchJob(fileInput.files[0], jobDescription);
    resultBox.innerHTML = renderMatchResult(data);
  } catch (error) {
    resultBox.innerHTML = `<div class="alert alert-danger">${error.message}</div>`;
  } finally {
    spinner.classList.add("d-none");
  }
});
