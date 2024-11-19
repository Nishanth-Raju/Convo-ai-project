document.getElementById("uploadForm").addEventListener("submit", async function (e) {
  e.preventDefault();

  const fileInput = document.getElementById("audioFile");
  const formData = new FormData();
  formData.append("audioFile", fileInput.files[0]);

  try {
      const response = await fetch("/analyze-audio", {
          method: "POST",
          body: formData,
      });

      const result = await response.json();
      document.getElementById("result").textContent = `Transcription: ${result.transcription}\nSentiment: ${result.sentiment}`;
  } catch (error) {
      document.getElementById("result").textContent = "Error: " + error.message;
  }
});
