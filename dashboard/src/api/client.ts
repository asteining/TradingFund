// Dashboard/src/api/client.ts

import axios from "axios";

export const api = axios.create({
  baseURL: "http://localhost:8000", // point to our FastAPI service
  timeout: 5000,
});
