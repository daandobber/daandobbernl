// Link preview for /cd-collectie: the 12 newest cds on two shelves.
import cdCollectionData from "@/data/cd_collection.json";
import type { Release } from "@/types";
import { firstImages, shelfCard } from "@/utils/ogCard";

const addedTime = (release: Release) => Date.parse(release.date_added ?? "") || 0;

export async function GET() {
	const releases: Release[] = [...(cdCollectionData?.releases ?? [])].sort((a, b) => addedTime(b) - addedTime(a));
	const covers = await firstImages(releases.map((release) => release.basic_information?.cover_image), 12);
	return shelfCard("CD-collectie", `${releases.length} cd's`, covers);
}
