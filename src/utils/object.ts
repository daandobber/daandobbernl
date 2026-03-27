export function getNestedValue<T = unknown>(source: unknown, path: string): T | null {
	if (!source || typeof path !== "string" || path.length === 0) {
		return null;
	}

	const segments = path.split(".");
	let cursor: unknown = source;

	for (const segment of segments) {
		if (cursor == null) {
			return null;
		}

		if (Array.isArray(cursor)) {
			const index = Number(segment);
			if (!Number.isInteger(index) || index < 0 || index >= cursor.length) {
				return null;
			}
			cursor = cursor[index];
			continue;
		}

		if (typeof cursor !== "object") {
			return null;
		}

		const value = (cursor as Record<string, unknown>)[segment];
		cursor = value === undefined ? null : value;
	}

	return (cursor ?? null) as T | null;
}

export function valueContainsTerm(value: unknown, term: string): boolean {
	if (!term) {
		return true;
	}

	const lowerTerm = term.toLowerCase();

	if (typeof value === "string") {
		return value.toLowerCase().includes(lowerTerm);
	}

	if (typeof value === "number") {
		return String(value).includes(lowerTerm);
	}

	if (Array.isArray(value)) {
		return value.some((item) => valueContainsTerm(item, term));
	}

	if (value && typeof value === "object") {
		return Object.values(value).some((item) => valueContainsTerm(item, term));
	}

	return false;
}
