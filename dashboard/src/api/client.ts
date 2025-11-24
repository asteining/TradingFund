// Dashboard/src/api/client.ts

import axios from "axios";

const baseURL = process.env.REACT_APP_API_BASE || "http://localhost:8000";

export const api = axios.create({
  baseURL, // point to our FastAPI service
  timeout: 5000,
});
