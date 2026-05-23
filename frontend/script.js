const API_URL = "https://deployment-v6sv.onrender.com/api/parse";

async function uploadResume() {
  const fileInput = document.getElementById("fileInput");
  const file = fileInput.files[0];
  const resultBox = document.getElementById("result");
  const loading = document.getElementById("loading");

  if (!file) {
    alert("Please select a PDF file");
    return;
  }

  const formData = new FormData();
  formData.append("resume", file);

  try {
    loading.classList.remove("hidden");
    resultBox.innerText = "";

    const response = await fetch(API_URL, {
      method: "POST",
      body: formData
    });

    const data = await response.json();

    loading.classList.add("hidden");

    resultBox.innerText = JSON.stringify(data, null, 2);

  } catch (error) {
    loading.classList.add("hidden");
    resultBox.innerText = "Error uploading file";
    console.error(error);
  }
}