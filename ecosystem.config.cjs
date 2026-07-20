/**
 * PM2 process file for Farzana (local or EC2).
 *   pm2 start ecosystem.config.cjs
 */
const path = require("path");
const root = __dirname;
const isWin = process.platform === "win32";
const venvBin = isWin
  ? path.join(root, ".venv", "Scripts")
  : path.join(root, ".venv", "bin");
const uvicorn = path.join(venvBin, isWin ? "uvicorn.exe" : "uvicorn");
const celery = path.join(venvBin, isWin ? "celery.exe" : "celery");

module.exports = {
  apps: [
    {
      name: "farzana-api",
      cwd: root,
      script: uvicorn,
      args: "farzana.main:app --host 0.0.0.0 --port 8000",
      interpreter: "none",
      env: { PYTHONPATH: "src" },
    },
    {
      name: "farzana-worker",
      cwd: root,
      script: celery,
      args: isWin
        ? "-A farzana.workers.celery_app.celery_app worker --loglevel=INFO --concurrency=1 --pool=solo"
        : "-A farzana.workers.celery_app.celery_app worker --loglevel=INFO --concurrency=1",
      interpreter: "none",
      env: { PYTHONPATH: "src" },
    },
  ],
};
