// Link previews (og:image, 1200x630), made at build time with satori + resvg and saved as a small JPEG
// (WhatsApp and friends skip big preview images).
import { readFileSync } from "node:fs";
import { join } from "node:path";
import RobotoMonoBold from "@/assets/roboto-mono-700.ttf";
import { siteConfig } from "@/site.config";
import { Resvg } from "@resvg/resvg-js";
import satori from "satori";

type Node = { type: string; props: Record<string, unknown> };
// satori element tree, built directly (an HTML string with inline images is far too slow to parse)
const el = (type: string, style: Record<string, unknown>, children?: unknown, extra: Record<string, unknown> = {}): Node => ({
	type,
	props: { style: { display: "flex", ...style }, children, ...extra },
});
const img = (src: string, width: number, height: number, style: Record<string, unknown> = {}): Node => ({
	type: "img",
	props: { src, width, height, style },
});

async function render(tree: Node): Promise<Response> {
	const svg = await satori(tree as never, {
		width: 1200,
		height: 630,
		fonts: [{ data: Buffer.from(RobotoMonoBold), name: "Roboto Mono", style: "normal", weight: 700 }],
	});
	const png = new Resvg(svg).render().asPng();
	try {
		const { default: sharp } = await import("sharp");
		const jpeg = await sharp(png).jpeg({ quality: 82, mozjpeg: true }).toBuffer();
		return new Response(new Uint8Array(jpeg), { headers: { "Content-Type": "image/jpeg" } });
	} catch (error) {
		// sharp missing or broken on this machine: a (bigger) PNG still works as a preview
		console.warn("og image: no JPEG, sharp failed:", (error as Error).message.split("\n")[0]);
		return new Response(new Uint8Array(png), { headers: { "Content-Type": "image/png" } });
	}
}

// images as data URIs, so the preview never depends on another site being reachable
export async function imageData(url: string | undefined): Promise<string | null> {
	if (!url) return null;
	try {
		const response = await fetch(url, { headers: { "user-agent": "daandobber.nl build" }, signal: AbortSignal.timeout(15000) });
		if (!response.ok) return null;
		const type = response.headers.get("content-type") ?? "image/jpeg";
		return `data:${type};base64,${Buffer.from(await response.arrayBuffer()).toString("base64")}`;
	} catch {
		return null;
	}
}

// the first `count` urls that could be fetched
export async function firstImages(urls: (string | undefined)[], count: number): Promise<string[]> {
	const found: string[] = [];
	for (const url of urls) {
		if (found.length === count) break;
		const data = await imageData(url);
		if (data) found.push(data);
	}
	return found;
}

const background = "linear-gradient(135deg, #17507d 0%, #2f3f93 55%, #5b2c7e 100%)";
const footer = (left: string, right: string = siteConfig.title) =>
	el("div", { width: "100%", justifyContent: "space-between", padding: "0 56px 28px", fontSize: 24, color: "rgba(232,250,255,.8)" }, [
		el("div", {}, left),
		el("div", {}, right),
	]);

/** Two shelves with 6 covers each (cds, board games), title and count on top. */
export function shelfCard(title: string, countLabel: string, covers: string[]): Promise<Response> {
	const shelf = (items: string[]) =>
		el("div", { flexDirection: "column", width: "100%" }, [
			el("div", { width: "100%", justifyContent: "center", padding: "0 40px" },
				items.map((src) =>
					el("div", { width: 160, height: 148, margin: "0 8px", boxShadow: "0 6px 10px rgba(0,0,0,.55)" }, [
						el("div", { width: 14, height: 148, background: "#151515" }),
						img(src, 146, 148, { objectFit: "cover" }),
					]),
				),
			),
			el("div", { width: "100%", height: 16, background: "#303138" }),
			el("div", { width: "100%", height: 10, background: "#24252a" }),
		]);
	return render(
		el("div", { flexDirection: "column", width: "100%", height: "100%", background: "linear-gradient(165deg,#2e2f34,#1b1c1f)", fontFamily: "Roboto Mono" }, [
			el("div", { width: "100%", alignItems: "flex-end", justifyContent: "space-between", padding: "40px 56px 24px" }, [
				el("div", { fontSize: 60, fontWeight: 700, color: "#fff" }, title),
				el("div", { fontSize: 30, color: "#8ee2ff" }, countLabel),
			]),
			el("div", { flexDirection: "column", width: "100%", flex: 1, justifyContent: "space-around", paddingBottom: 24 }, [
				shelf(covers.slice(0, 6)),
				shelf(covers.slice(6, 12)),
			]),
			footer("daandobber.nl"),
		]),
	);
}

/** The general preview for every page without its own: Daan's avatar and the site name. */
export function siteCard(): Promise<Response> {
	const avatar = `data:image/jpeg;base64,${readFileSync(join(process.cwd(), "public", "daan-avatar.jpg")).toString("base64")}`;
	return render(
		el("div", { flexDirection: "column", width: "100%", height: "100%", background, fontFamily: "Roboto Mono" }, [
			el("div", { flex: 1, alignItems: "center", padding: "0 80px" }, [
				el("div", { width: 236, height: 236, borderRadius: 999, border: "6px solid rgba(255,255,255,.85)", overflow: "hidden", boxShadow: "0 18px 40px rgba(0,0,0,.35)" }, [
					img(avatar, 224, 224, { objectFit: "cover" }),
				]),
				el("div", { flexDirection: "column", marginLeft: 56, flex: 1 }, [
					el("div", { fontSize: 64, fontWeight: 700, color: "#fff", lineHeight: 1.15 }, siteConfig.title),
					el("div", { marginTop: 22, fontSize: 28, color: "#8ee2ff" }, "blog · cd's · bordspellen · projecten"),
				]),
			]),
			footer("daandobber.nl", ""),
		]),
	);
}
