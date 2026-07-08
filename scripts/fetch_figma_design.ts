import { randomUUID } from "crypto";
import WebSocket from "ws";
import { writeFileSync } from "fs";
import { join } from "path";

const CHANNEL = process.argv[2] || "159mqwp2";
const OUT = join(import.meta.dir, "..", "figma-website", "design-live.json");

function sendCommand(
  ws: WebSocket,
  channel: string,
  command: string,
  params: Record<string, unknown> = {},
  timeoutMs = 60000
): Promise<unknown> {
  return new Promise((resolve, reject) => {
    const id = randomUUID();
    const timer = setTimeout(() => reject(new Error(`Timeout: ${command}`)), timeoutMs);

    const onMessage = (raw: WebSocket.RawData) => {
      try {
        const data = JSON.parse(raw.toString());
        const msg = data.message;
        if (msg?.id === id) {
          clearTimeout(timer);
          ws.off("message", onMessage);
          if (msg.error) reject(new Error(msg.error));
          else resolve(msg.result);
        }
      } catch {
        /* ignore */
      }
    };

    ws.on("message", onMessage);
    ws.send(
      JSON.stringify({
        id,
        type: "message",
        channel,
        message: { id, command, params: { ...params, commandId: id } },
      })
    );
  });
}

async function main() {
  const ws = new WebSocket("ws://localhost:3055");

  await new Promise<void>((resolve, reject) => {
    ws.once("open", () => resolve());
    ws.once("error", reject);
  });

  await new Promise<void>((resolve, reject) => {
    const joinId = randomUUID();
    const timer = setTimeout(() => reject(new Error("Join timeout")), 10000);
    ws.on("message", function onJoin(raw) {
      const data = JSON.parse(raw.toString());
      if (
        data.type === "system" &&
        data.channel === CHANNEL &&
        data.message?.result
      ) {
        clearTimeout(timer);
        ws.off("message", onJoin);
        resolve();
      }
    });
    ws.send(JSON.stringify({ id: joinId, type: "join", channel: CHANNEL }));
  });

  console.log(`Joined channel: ${CHANNEL}`);

  const selection = await sendCommand(ws, CHANNEL, "get_selection");
  console.log("Selection:", JSON.stringify(selection));

  const design = await sendCommand(ws, CHANNEL, "read_my_design");
  writeFileSync(OUT, JSON.stringify({ selection, design }, null, 2), "utf-8");
  console.log(`Saved to ${OUT}`);

  ws.close();
}

main().catch((err) => {
  console.error(err.message || err);
  process.exit(1);
});
