const uploadForm = document.getElementById("upload-form");
const photoInput = document.getElementById("photo-input");
const uploadBtn = document.getElementById("upload-btn");
const uploadStatus = document.getElementById("upload-status");
const downloadBtn = document.getElementById("download-btn");
const downloadStatus = document.getElementById("download-status");

function setStatus(element, message, type = "") {
    element.textContent = message;
    element.className = `status ${type}`.trim();
}

uploadForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const file = photoInput.files[0];
    if (!file) {
        setStatus(uploadStatus, "Please choose a photo first.", "error");
        return;
    }

    uploadBtn.disabled = true;
    setStatus(uploadStatus, "Uploading...", "info");

    const formData = new FormData();
    formData.append("file", file);

    try {
        const response = await fetch("/api/upload", {
            method: "POST",
            body: formData,
        });

        const data = await response.json().catch(() => ({}));

        if (!response.ok) {
            throw new Error(data.detail || "Upload failed.");
        }

        setStatus(uploadStatus, data.message || "Upload complete.", "success");
        photoInput.value = "";
    } catch (error) {
        setStatus(uploadStatus, error.message, "error");
    } finally {
        uploadBtn.disabled = false;
    }
});

downloadBtn.addEventListener("click", async () => {
    downloadBtn.disabled = true;
    setStatus(downloadStatus, "Preparing archive...", "info");

    try {
        const response = await fetch("/api/download");

        if (!response.ok) {
            const data = await response.json().catch(() => ({}));
            throw new Error(data.detail || "Download failed.");
        }

        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = "friends-photos.zip";
        document.body.appendChild(link);
        link.click();
        link.remove();
        URL.revokeObjectURL(url);

        setStatus(downloadStatus, "Archive downloaded.", "success");
    } catch (error) {
        setStatus(downloadStatus, error.message, "error");
    } finally {
        downloadBtn.disabled = false;
    }
});
