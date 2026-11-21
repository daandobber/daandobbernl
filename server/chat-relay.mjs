// Chat relay for daandobber.nl: the browser talks to /api/chat/*, this service talks to Matrix.
// The bot token stays on the server; a visitor only gets a random secret key that opens their own
// conversation (one Matrix room per visitor, with Daan invited). No dependencies, Node 24.
//
//   POST /api/chat/start     { nickname }            -> { key }
//   POST /api/chat/send      { key, text?, nudge? }  -> { ok: true }
//   GET  /api/chat/messages?key=...                  -> { messages: [{ mine, text, ts }] }
//
// Settings in /home/daandobber/chat/chat.env: MATRIX_HOMESERVER, MATRIX_BOT_TOKEN, MATRIX_OWNER_ID (+ PORT).
import { createServer } from "node:http";
import { randomBytes, randomUUID } from "node:crypto";
import { readFileSync, writeFileSync, renameSync, existsSync } from "node:fs";

const DIR = "/home/daandobber/chat";
process.loadEnvFile(`${DIR}/chat.env`);
const HOMESERVER = (process.env.MATRIX_HOMESERVER ?? "").replace(/\/+$/, "");
const TOKEN = process.env.MATRIX_BOT_TOKEN ?? "";
const OWNER = process.env.MATRIX_OWNER_ID ?? "";
const PORT = Number(process.env.PORT ?? 4410);
if (!HOMESERVER || !TOKEN || !OWNER) throw new Error("chat.env is missing MATRIX_HOMESERVER, MATRIX_BOT_TOKEN or MATRIX_OWNER_ID");

// key -> { room, nickname, created }
const STORE = `${DIR}/rooms.json`;
let rooms = existsSync(STORE) ? JSON.parse(readFileSync(STORE, "utf8")) : {};
const save = () => {
	writeFileSync(`${STORE}.tmp`, JSON.stringify(rooms));
	renameSync(`${STORE}.tmp`, STORE);
};

// simple rate limits (in memory)
const hits = new Map();
function limited(bucket, max, windowMs) {
	const now = Date.now();
	const list = (hits.get(bucket) ?? []).filter((t) => now - t < windowMs);
	if (list.length >= max) return true;
	list.push(now);
	hits.set(bucket, list);
	return false;
}
setInterval(() => hits.clear(), 3600_000).unref();

async function matrix(path, options = {}) {
	const response = await fetch(`${HOMESERVER}/_matrix/client/v3${path}`, {
		...options,
		headers: { "content-type": "application/json", authorization: `Bearer ${TOKEN}` },
	});
	if (!response.ok) throw new Error(`Matrix ${response.status} on ${path.split("?")[0]}`);
	return response.json();
}

const json = (res, status, body) => {
	res.writeHead(status, { "content-type": "application/json", "cache-control": "no-store" });
	res.end(JSON.stringify(body));
};

async function readBody(req) {
	let size = 0;
	const chunks = [];
	for await (const chunk of req) {
		size += chunk.length;
		if (size > 8192) throw Object.assign(new Error("too large"), { status: 413 });
		chunks.push(chunk);
	}
	try {
		return JSON.parse(Buffer.concat(chunks).toString("utf8") || "{}");
	} catch {
		throw Object.assign(new Error("bad json"), { status: 400 });
	}
}

const clean = (value, max) => String(value ?? "").replace(/[\u0000-\u0008\u000b-\u001f\u007f]/g, "").trim().slice(0, max);

createServer(async (req, res) => {
	const url = new URL(req.url ?? "/", "http://localhost");
	const ip = String(req.headers["x-real-ip"] ?? req.socket.remoteAddress ?? "?");
	try {
		if (req.method === "POST" && url.pathname === "/api/chat/start") {
			if (limited(`start:${ip}`, 5, 3600_000)) return json(res, 429, { error: "too_many" });
			const body = await readBody(req);
			const nickname = clean(body.nickname, 24) || "Bezoeker";
			const room = await matrix("/createRoom", {
				method: "POST",
				body: JSON.stringify({
					visibility: "private",
					preset: "trusted_private_chat",
					is_direct: true,
					invite: [OWNER],
					name: `Website chat — ${nickname}`,
					topic: `Bericht via daandobber.nl — IP: ${ip}`,
				}),
			});
			await matrix(`/rooms/${encodeURIComponent(room.room_id)}/send/m.room.message/${randomUUID()}`, {
				method: "PUT",
				body: JSON.stringify({ msgtype: "m.notice", body: `🌐 Nieuw gesprek met ${nickname} — IP van bezoeker: ${ip}` }),
			}).catch(() => {});
			const key = randomBytes(24).toString("hex");
			rooms[key] = { room: room.room_id, nickname, created: new Date().toISOString() };
			save();
			return json(res, 200, { key });
		}

		const key = req.method === "GET" ? url.searchParams.get("key") : null;
		if (req.method === "POST" && url.pathname === "/api/chat/send") {
			const body = await readBody(req);
			const entry = rooms[String(body.key ?? "")];
			if (!entry) return json(res, 404, { error: "unknown_conversation" });
			if (limited(`send:${body.key}`, 10, 60_000) || limited(`sendip:${ip}`, 30, 60_000)) return json(res, 429, { error: "too_many" });
			const nickname = clean(body.nickname, 24) || entry.nickname;
			const text = body.nudge ? `*${nickname} stuurt je een nudge!* 👊` : clean(body.text, 2000);
			if (!text) return json(res, 400, { error: "empty" });
			await matrix(`/rooms/${encodeURIComponent(entry.room)}/send/m.room.message/${randomUUID()}`, {
				method: "PUT",
				body: JSON.stringify({ msgtype: "m.text", body: body.nudge ? text : `${nickname}: ${text}` }),
			});
			return json(res, 200, { ok: true });
		}

		if (req.method === "GET" && url.pathname === "/api/chat/messages") {
			const entry = rooms[String(key ?? "")];
			if (!entry) return json(res, 404, { error: "unknown_conversation" });
			if (limited(`read:${key}`, 60, 60_000)) return json(res, 429, { error: "too_many" });
			const data = await matrix(`/rooms/${encodeURIComponent(entry.room)}/messages?dir=b&limit=60`);
			const messages = (data.chunk ?? [])
				.filter((event) => event.type === "m.room.message" && event.content?.msgtype !== "m.notice")
				.reverse()
				.map((event) => ({ mine: event.sender !== OWNER, text: String(event.content?.body ?? ""), ts: event.origin_server_ts }));
			return json(res, 200, { messages });
		}

		return json(res, 404, { error: "not_found" });
	} catch (error) {
		const status = error.status ?? 502;
		if (status === 502) console.error(new Date().toISOString(), error.message);
		return json(res, status, { error: status === 502 ? "chat_unavailable" : error.message });
	}
}).listen(PORT, "127.0.0.1", () => console.log(`chat relay on 127.0.0.1:${PORT}`));
