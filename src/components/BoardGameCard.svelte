<script lang="ts">
  import type { BoardGame } from "@/types";

  export let view: "grid" | "list" = "grid";
  export let game: BoardGame | undefined | null;

  function formatPlayers(min: number | null, max: number | null): string {
    if (min && max) return min === max ? `${min}` : `${min}-${max}`;
    if (min) return `${min}+`;
    if (max) return `1-${max}`;
    return "N/A";
  }

  function formatPlaytime(min: number | null, max: number | null, avg: number | null): string {
    if (min && max && max > min) return `${min}-${max} min`;
    if (avg && avg > 0) return `${avg} min`;
    if (max && max > 0) return `${max} min`;
    if (min && min > 0) return `${min} min`;
    return "N/A";
  }

  function formatWeight(weight: number | null): string {
    return weight ? weight.toFixed(2) : "N/A";
  }

  const name = game?.name ?? "Geen Naam";
  const year = game?.yearpublished;
  const placeholderImg = "/images/placeholder-cover.png";
  const thumbnail = game?.thumbnail ?? placeholderImg;
  const altText = `Cover van ${name}`;
  const bggLink = `https://boardgamegeek.com/boardgame/${game?.id ?? ""}`;
  const iconClass = "h-4 w-4 shrink-0 text-gray-400 dark:text-gray-500";

  const players = formatPlayers(game?.minplayers ?? null, game?.maxplayers ?? null);
  const playtime = formatPlaytime(
    game?.minplaytime ?? null,
    game?.maxplaytime ?? null,
    game?.playingtime ?? null,
  );
  const weightFormatted = formatWeight(game?.weight ?? null);
  const bestWith = game?.best_with_players ? `Best: ${game.best_with_players}` : "";

  const averageRating = game?.average_rating != null && !Number.isNaN(Number(game.average_rating))
    ? Number(game.average_rating).toFixed(1)
    : null;
  const myRating = game?.rating != null && !Number.isNaN(Number(game.rating))
    ? Number(game.rating).toFixed(1)
    : null;
</script>

{#if game}
  <a
    href={bggLink}
    target="_blank"
    rel="noopener noreferrer"
    class={view === "grid"
      ? "group flex h-full flex-col overflow-hidden rounded-lg border border-gray-300 bg-white shadow-md transition-shadow duration-200 ease-in-out hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:border-gray-700 dark:bg-gray-800 dark:focus:ring-offset-gray-900"
      : "group grid h-full grid-cols-[auto_1fr] items-start gap-x-3 overflow-hidden rounded-lg border border-gray-300 bg-white p-2 shadow-md transition-shadow duration-200 ease-in-out hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:border-gray-700 dark:bg-gray-800 dark:focus:ring-offset-gray-900"}
    aria-label={`Bekijk ${name} op BoardGameGeek`}
  >
    <div
      class={view === "grid"
        ? "aspect-square w-full flex-shrink-0 overflow-hidden bg-gray-200 dark:bg-gray-600"
        : "h-16 w-16 flex-shrink-0 overflow-hidden rounded bg-gray-200 dark:bg-gray-600"}
    >
      <img
        src={thumbnail}
        alt={altText}
        loading="lazy"
        width="200"
        height="200"
        class={view === "grid"
          ? "h-full w-full object-cover transition-transform duration-300 ease-in-out group-hover:scale-105"
          : "h-full w-full object-cover"}
        on:error={(event: Event) => {
          const target = event.target as HTMLImageElement;
          if (target) target.src = placeholderImg;
        }}
      />
    </div>

    <div class={view === "grid" ? "flex flex-grow flex-col p-3" : "min-w-0"}>
      <h2 class={view === "grid"
        ? "mb-1 line-clamp-2 text-sm font-semibold text-gray-900 dark:text-gray-100"
        : "mb-0.5 truncate text-sm font-semibold text-gray-900 dark:text-gray-100"} title={name}>
        {name}
      </h2>
      {#if year}
        <p class={view === "grid"
          ? "mb-2 text-xs text-gray-500 dark:text-gray-400"
          : "mb-1 text-xs text-gray-500 dark:text-gray-400"}>
          {year}
        </p>
      {/if}

      {#if view === "grid"}
        <div class="mt-auto space-y-1 pt-1 text-xs text-gray-700 dark:text-gray-300">
          <div class="flex items-center gap-1 whitespace-nowrap" title={`Spelers: ${players}`}>
            <span class="inline-flex w-4 justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class={iconClass} aria-hidden="true">
                <circle cx="8" cy="8" r="3" />
                <circle cx="16" cy="10" r="2.5" />
                <path stroke-linecap="round" stroke-linejoin="round" d="M4 18.5c0-2.485 2.239-4.5 5-4.5s5 2.015 5 4.5V20H4.75a.75.75 0 0 1-.75-.75Z" />
                <path stroke-linecap="round" stroke-linejoin="round" d="M13 18.5c0-1.933 1.79-3.5 4-3.5s4 1.567 4 3.5V20h-8Z" />
              </svg>
            </span>
            <span>{players}</span>
            {#if bestWith}
              <span class="ml-1 font-medium text-green-700 dark:text-green-400">({bestWith})</span>
            {/if}
          </div>
          <div class="flex items-center gap-1 whitespace-nowrap" title={`Speelduur: ${playtime}`}>
            <span class="inline-flex w-4 justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class={iconClass} aria-hidden="true">
                <circle cx="12" cy="12" r="8.25" />
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 7.5v5l3 1.75" />
              </svg>
            </span>
            <span>{playtime}</span>
          </div>
          <div class="flex items-center gap-1 whitespace-nowrap" title={`Complexiteit: ${weightFormatted} / 5`}>
            <span class="inline-flex w-4 justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class={iconClass} aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 5v4m0 0-7 3.75 7 3.75 7-3.75L12 9m-7 3.75C5 15.545 6.79 17.5 9 17.5s4-1.955 4-4.75m5 0c0 2.795-1.79 4.75-4 4.75" />
              </svg>
            </span>
            <span>{weightFormatted}</span>
          </div>
          {#if averageRating || myRating}
            <div class="flex items-center whitespace-nowrap">
              {#if averageRating}
                <span class="inline-flex items-center gap-1" title={`Gemiddelde BGG rating: ${averageRating}`}>
                  <span class="inline-flex w-4 justify-center">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class={iconClass} aria-hidden="true">
                      <path d="M12 3.5 14.572 8.7 20.25 9.54 16.125 13.5 17.144 19.75 12 16.9 6.856 19.75 7.875 13.5 3.75 9.54 9.428 8.7 12 3.5Z" />
                    </svg>
                  </span>
                  <span>{averageRating}</span>
                </span>
              {/if}
              {#if averageRating && myRating}
                <span class="mx-2 opacity-60" aria-hidden="true">|</span>
              {/if}
              {#if myRating}
                <span class="inline-flex items-center gap-1" title={`Mijn rating: ${myRating}`}>
                  <span class="inline-flex w-4 justify-center">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class={iconClass} aria-hidden="true">
                      <path d="M12 20.35 10.55 19C5.4 14.36 2 11.28 2 7.5 2 5 4 3 6.5 3c1.74 0 3.41 1.08 4.22 2.64.81-1.56 2.48-2.64 4.22-2.64C17.5 3 19.5 5 19.5 7.5c0 3.78-3.4 6.86-8.55 11.9Z" />
                    </svg>
                  </span>
                  <span>{myRating}</span>
                </span>
              {/if}
            </div>
          {/if}
        </div>
      {:else}
        <div class="mt-1 flex flex-wrap gap-x-3 gap-y-0 text-xs text-gray-700 dark:text-gray-300">
          <div class="flex items-center gap-1 whitespace-nowrap" title={`Spelers: ${players}`}>
            <span class="inline-flex w-4 justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class={iconClass} aria-hidden="true">
                <circle cx="8" cy="8" r="3" />
                <circle cx="16" cy="10" r="2.5" />
                <path stroke-linecap="round" stroke-linejoin="round" d="M4 18.5c0-2.485 2.239-4.5 5-4.5s5 2.015 5 4.5V20H4.75a.75.75 0 0 1-.75-.75Z" />
                <path stroke-linecap="round" stroke-linejoin="round" d="M13 18.5c0-1.933 1.79-3.5 4-3.5s4 1.567 4 3.5V20h-8Z" />
              </svg>
            </span>
            <span>{players}</span>
            {#if bestWith}
              <span class="ml-1 font-medium text-green-700 dark:text-green-400">({bestWith})</span>
            {/if}
          </div>
          <div class="flex items-center gap-1 whitespace-nowrap" title={`Speelduur: ${playtime}`}>
            <span class="inline-flex w-4 justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class={iconClass} aria-hidden="true">
                <circle cx="12" cy="12" r="8.25" />
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 7.5v5l3 1.75" />
              </svg>
            </span>
            <span>{playtime}</span>
          </div>
          <div class="flex items-center gap-1 whitespace-nowrap" title={`Complexiteit: ${weightFormatted} / 5`}>
            <span class="inline-flex w-4 justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class={iconClass} aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 5v4m0 0-7 3.75 7 3.75 7-3.75L12 9m-7 3.75C5 15.545 6.79 17.5 9 17.5s4-1.955 4-4.75m5 0c0 2.795-1.79 4.75-4 4.75" />
              </svg>
            </span>
            <span>{weightFormatted}</span>
          </div>
          {#if averageRating}
            <span class="inline-flex items-center gap-1" title={`Gemiddelde BGG rating: ${averageRating}`}>
              <span class="inline-flex w-4 justify-center">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class={iconClass} aria-hidden="true">
                  <path d="M12 3.5 14.572 8.7 20.25 9.54 16.125 13.5 17.144 19.75 12 16.9 6.856 19.75 7.875 13.5 3.75 9.54 9.428 8.7 12 3.5Z" />
                </svg>
              </span>
              <span>{averageRating}</span>
            </span>
          {/if}
          {#if myRating}
            <span class="inline-flex items-center gap-1" title={`Mijn rating: ${myRating}`}>
              <span class="inline-flex w-4 justify-center">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class={iconClass} aria-hidden="true">
                  <path d="M12 20.35 10.55 19C5.4 14.36 2 11.28 2 7.5 2 5 4 3 6.5 3c1.74 0 3.41 1.08 4.22 2.64.81-1.56 2.48-2.64 4.22-2.64C17.5 3 19.5 5 19.5 7.5c0 3.78-3.4 6.86-8.55 11.9Z" />
                </svg>
              </span>
              <span>{myRating}</span>
            </span>
          {/if}
        </div>
      {/if}
    </div>
  </a>
{/if}

<style>
  .line-clamp-2 {
    overflow: hidden;
    display: -webkit-box;
    -webkit-box-orient: vertical;
    -webkit-line-clamp: 2;
  }

  a {
    text-decoration: none;
    color: inherit;
  }
</style>
