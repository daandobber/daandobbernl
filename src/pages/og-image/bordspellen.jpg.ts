// Link preview for /bordspellen: 12 games from the collection on two shelves.
import bggCollectionData from "@/data/bgg_collection.json";
import { firstImages, shelfCard } from "@/utils/ogCard";

type Game = { thumbnail?: string; image?: string; status?: { own?: boolean } };

export async function GET() {
	const games = ((bggCollectionData as { games?: Game[] }).games ?? []).filter((game) => game.status?.own !== false);
	// spread over the whole (alphabetical) collection, so it isn't four times Agricola
	const spread = Array.from({ length: 12 }, (_, index) => games[Math.floor((index * games.length) / 12)]);
	const ordered = [...spread, ...games.filter((game) => !spread.includes(game))];
	const covers = await firstImages(ordered.map((game) => game?.thumbnail ?? game?.image), 12);
	return shelfCard("Bordspellen", `${games.length} spellen`, covers);
}
