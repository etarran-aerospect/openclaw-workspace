import { conwayRouter } from "./routes/conway.js";
import "dotenv/config";
import express from "express";
import cors from "cors";
import { creditsRouter } from "./routes/credits.js";
import { agentsRouter } from "./routes/agents.js";
import { replicationRouter } from "./routes/replication.js";
import { eventsRouter } from "./routes/events.js";
import { mobileConwayRouter } from "./routes/mobileConway.js";

const app = express();
app.use(cors());
app.use(express.json({ limit: "1mb" }));

app.get("/health", (_req, res) => res.json({ ok: true }));

app.use("/api", agentsRouter);
app.use("/api", creditsRouter);
app.use("/api", replicationRouter);
app.use("/api", eventsRouter);
app.use("/api", conwayRouter);
app.use("/api", mobileConwayRouter);

const port = Number(process.env.PORT ?? 8787);
app.listen(port, () => console.log(`API listening on http://localhost:${port}`));
