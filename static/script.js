const AUTH_USERNAME = "user";
const PASSWORD_KEY = "friendsPhotosPassword";

const authForm = document.getElementById("auth-form");
const authCard = document.getElementById("auth-card");
const passwordInput = document.getElementById("password-input");
const authBtn = document.getElementById("auth-btn");
const authStatus = document.getElementById("auth-status");
const protectedContent = document.getElementById("protected-content");
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

function getPassword() {
    return sessionStorage.getItem(PASSWORD_KEY) || "";
}

function setPassword(password) {
    sessionStorage.setItem(PASSWORD_KEY, password);
}

function clearPassword() {
    sessionStorage.removeItem(PASSWORD_KEY);
}

function authHeaders() {
    const password = getPassword();
    if (!password) {
        return {};
    }

    return {
        Authorization: `Basic ${btoa(`${AUTH_USERNAME}:${password}`)}`,
    };
}

function showProtectedContent() {
    authCard.hidden = true;
    protectedContent.hidden = false;
}

function showLogin(message = "") {
    clearPassword();
    authCard.hidden = false;
    protectedContent.hidden = true;
    passwordInput.value = "";
    setStatus(authStatus, message, message ? "error" : "");
}

async function verifyPassword(password) {
    const response = await fetch("/api/auth/check", {
        headers: {
            Authorization: `Basic ${btoa(`${AUTH_USERNAME}:${password}`)}`,
        },
    });

    if (response.status === 401) {
        throw new Error("Wrong password.");
    }

    if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        throw new Error(data.detail || "Authentication failed.");
    }
}

async function ensureAuthenticated(response) {
    if (response.status === 401) {
        showLogin("Session expired. Please enter the password again.");
        throw new Error("Authentication required.");
    }
}

authForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const password = passwordInput.value;
    if (!password) {
        setStatus(authStatus, "Please enter the password.", "error");
        return;
    }

    authBtn.disabled = true;
    setStatus(authStatus, "Checking password...", "info");

    try {
        await verifyPassword(password);
        setPassword(password);
        showProtectedContent();
        setStatus(authStatus, "", "");
    } catch (error) {
        setStatus(authStatus, error.message, "error");
    } finally {
        authBtn.disabled = false;
    }
});

uploadForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const files = photoInput.files;
    if (!files.length) {
        setStatus(uploadStatus, "Please choose at least one photo or video.", "error");
        return;
    }

    uploadBtn.disabled = true;
    setStatus(uploadStatus, `Uploading ${files.length} file${files.length === 1 ? "" : "s"}...`, "info");

    const formData = new FormData();
    for (const file of files) {
        formData.append("files", file);
    }

    try {
        const response = await fetch("/api/upload", {
            method: "POST",
            headers: authHeaders(),
            body: formData,
        });

        await ensureAuthenticated(response);

        const data = await response.json().catch(() => ({}));

        if (!response.ok) {
            throw new Error(data.detail || "Upload failed.");
        }

        setStatus(uploadStatus, data.message || "Upload complete.", "success");
        photoInput.value = "";
    } catch (error) {
        if (error.message !== "Authentication required.") {
            setStatus(uploadStatus, error.message, "error");
        }
    } finally {
        uploadBtn.disabled = false;
    }
});

// downloadBtn.addEventListener("click", async () => {
//     downloadBtn.disabled = true;
//     setStatus(downloadStatus, "Preparing archive...", "info");
//
//     try {
//         const response = await fetch("/api/download", {
//             headers: authHeaders(),
//         });
//
//         await ensureAuthenticated(response);
//
//         if (!response.ok) {
//             const data = await response.json().catch(() => ({}));
//             throw new Error(data.detail || "Download failed.");
//         }
//
//         const blob = await response.blob();
//         const url = URL.createObjectURL(blob);
//         const link = document.createElement("a");
//         link.href = url;
//         link.download = "friends-photos.zip";
//         document.body.appendChild(link);
//         link.click();
//         link.remove();
//         URL.revokeObjectURL(url);
//
//         setStatus(downloadStatus, "Archive downloaded.", "success");
//     } catch (error) {
//         if (error.message !== "Authentication required.") {
//             setStatus(downloadStatus, error.message, "error");
//         }
//     } finally {
//         downloadBtn.disabled = false;
//     }
// });

(async function restoreSession() {
    const password = getPassword();
    if (!password) {
        return;
    }

    try {
        await verifyPassword(password);
        showProtectedContent();
    } catch {
        clearPassword();
    }
})();
