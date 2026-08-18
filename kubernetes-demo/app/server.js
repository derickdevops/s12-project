const express = require("express");
const os = require("os");
const path = require("path");

const app = express();
const port = Number(process.env.PORT || 3000);
const startedAt = new Date();
let ready = false;

const config = {
  appName: process.env.APP_NAME || "Kubernetes Demo App",
  environment: process.env.APP_ENV || "development",
  version: process.env.APP_VERSION || "1.0.0",
  studentName: process.env.STUDENT_NAME || "Stecy",
  hostname: process.env.HOSTNAME || os.hostname(),
  kubernetesMessage: "The application is running on Kubernetes.",
  secretLoaded: Boolean(process.env.DEMO_SECRET)
};

app.use(express.static(path.join(__dirname, "public")));

app.get("/api/info", (_req, res) => {
  res.status(200).json({
    ...config,
    uptimeSeconds: Math.round(process.uptime()),
    startedAt: startedAt.toISOString()
  });
});

app.get("/health", (_req, res) => {
  res.status(200).json({ status: "ok" });
});

app.get("/ready", (_req, res) => {
  if (!ready) {
    res.status(503).json({ status: "starting" });
    return;
  }

  res.status(200).json({ status: "ready" });
});

app.listen(port, () => {
  ready = true;
  console.log(`${config.appName} listening on port ${port}`);
});
