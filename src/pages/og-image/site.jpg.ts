// The general link preview for every page that has no preview of its own.
import { siteCard } from "@/utils/ogCard";

export function GET() {
	return siteCard();
}
