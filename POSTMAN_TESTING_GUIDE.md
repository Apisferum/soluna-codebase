# Postman API Testing Guide for Synestra Backend

This guide outlines how to import and use the Postman Collection to test all endpoints in the unified backend.

---

## 🚀 Getting Started

### 1. Import the Collection
1. Open **Postman**.
2. Click the **Import** button in the top left or top middle.
3. Select or drag-and-drop the generated file:
   [Synestra_API_Postman_Collection.json](file:///c:/Users/llith/OneDrive/Desktop/reorganized-ai-music/Synestra_API_Postman_Collection.json)
4. Confirm import as a **Collection**.

### 2. Configure Collection Variables
The collection uses variables to store domain names, dynamic IDs, and session tokens. 
To view or customize variables:
1. Click on the imported **Synestra Unified API** collection in the sidebar.
2. Navigate to the **Variables** tab.
3. You will see preset variables:
   * `baseUrl`: Default is `http://localhost:8000/api`. Update this if your server port differs.
   * `token` / `admin_token`: Empty by default.
   * `client_id`: A client label (default: `postman-test-client`) for WebSocket test instances.

---

## 🔑 Authentication & Token Management

The collection is designed to capture tokens automatically!

1. **User Flow**:
   * Navigate to the **Authentication** folder.
   * Trigger **Register User** or **Login User**.
   * Postman's **Test Script** runs automatically after receiving a successful response, saving the JWT to the `token` variable.
   * Subsequent endpoints requiring authorization (such as `/users/me` or `/generations`) automatically read `Bearer {{token}}` from the header.

2. **Admin Flow**:
   * Trigger **Admin Login**.
   * The test script captures the administrator token and saves it to `admin_token`.
   * Admin-only endpoints (`/admin/me`, `/admin/generations`) will read `Bearer {{admin_token}}` automatically.

---

## 🎵 Audio & Processing Endpoints

### 1. Audio Separation (2-Stem & 6-Stem)
* In the **Audio Separation** folder, you will find `Separate 2-Stem` and `Separate 6-Stem`.
* These endpoints are configured as `multipart/form-data`.
* **To run them**:
  1. Select the request in Postman.
  2. Navigate to the **Body** tab.
  3. For the key `file`, hover over the row and change the type from *Text* to *File*.
  4. Select a short sample audio file (e.g. WAV or MP3) from your local machine.
  5. Send the request.
* **Saving Sessions**:
  * Upon receiving a response, Postman extracts `session_id` and saves it as `separation_session_id` (or `stems_session_id`).
  * Once saved, you can immediately test the download endpoints (`Download 2-Stem Result` and `Download 6-Stem Result`) without copy-pasting the IDs!

### 2. Audio Analysis (Chord AI)
* **Analyze Uploaded File**: Similar to audio separation, change the `file` field type to *File* in the request **Body** tab, upload a sample audio file, and run it.
* **Analyze YouTube Video**: Paste a YouTube video URL into the `url` form field. Ensure the backend is run with internet access to retrieve video components.
* **Get YouTube Video Info**: Runs as a `GET` request and returns details such as thumbnails, titles, and video duration.

---

## 🔌 WebSocket Test

For real-time chord detection (`ws://localhost:8000/api/audio/ws/chords/{client_id}`):
1. Create a new **WebSocket Request** in Postman:
   * In Postman, click **New** -> **WebSocket**.
2. Set the address to:
   `ws://localhost:8000/api/audio/ws/chords/postman-test-client`
3. Click **Connect**.
4. To test sending audio frames:
   * Select **Binary** or **Text** payload (the endpoint accepts base64 PCM frames).
   * Check the socket logs below to observe real-time predictions.
