const projectSelect = document.getElementById("project");
const statusSelect = document.getElementById("status");
const executorSelect = document.getElementById("executor");
const executorContainer = document.getElementById("executor-container");
const statusContainer = document.getElementById("status-container");

const disableSelect = () => {
  executorSelect.disabled = true;
  executorSelect.innerHTML = "";
  executorSelect.appendChild(new Option("---------", ""));
  executorContainer.classList.add("text-gray-400");
  executorContainer.title = "Select project";

  statusSelect.disabled = true;
  statusSelect.innerHTML = "";
  statusSelect.appendChild(new Option("---------", ""));
  statusContainer.classList.add("text-gray-400");
  statusContainer.title = "Select project";
};

projectSelect.addEventListener("change", function () {
  const projectId = this.value;

  if (!projectId) {
    disableSelect();
    return;
  }
  try {
    fetch(`/api/projects/${projectId}/selects/`)
      .then((res) => res.json())
      .then((data) => {
        statusSelect.disabled = false;
        statusSelect.innerHTML = "";
        if (data.statuses.length === 0) {
          statusSelect.appendChild(new Option("---------", ""));
        } else {
          data.statuses.forEach((status) => {
            statusSelect.appendChild(new Option(`${status.name}`, `${status.id}`));
          });
        }

        executorSelect.disabled = false;
        executorSelect.innerHTML = "";
        executorSelect.appendChild(new Option("---------", ""));
        data.members.forEach((member) => {
          executorSelect.appendChild(new Option(`${member.name}`, `${member.id}`));
        });
      });
    executorContainer.classList.remove("text-gray-400");
    executorContainer.title = "";

    statusContainer.classList.remove("text-gray-400");
    statusContainer.title = "";
  } catch (error) {
    disableSelect();
    alert("The list of project selects could not be retrieved. Please try again later.");
  }
});
