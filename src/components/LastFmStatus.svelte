<script lang="ts">
  import { onDestroy, onMount } from "svelte";

  const API_KEY = import.meta.env.PUBLIC_LASTFM_API_KEY;
  const USERNAME = import.meta.env.PUBLIC_LASTFM_USERNAME;

  interface LastFmTrack {
    name?: string;
    artist?: { name?: string; ['#text']?: string } | string;
    url?: string;
    image?: { size?: string; ['#text']?: string }[];
    ['@attr']?: { nowplaying?: string };
    date?: { uts?: string; ['#text']?: string };
    album?: { ['#text']?: string };
  }

  interface NowPlayingStatus {
    artist: string;
    title: string;
    album?: string;
    url: string;
    nowPlaying: boolean;
    playedAt?: Date;
  }

  let status: NowPlayingStatus | null = null;
  const hasConfig = Boolean(API_KEY && USERNAME);
  const profileUrl = USERNAME ? `https://www.last.fm/user/${USERNAME}` : undefined;

  async function loadNowPlaying() {
    if (!hasConfig) {
      status = null;
      return;
    }

    try {
      const params = new URLSearchParams({
        method: "user.getrecenttracks",
        user: USERNAME,
        api_key: API_KEY,
        format: "json",
        limit: "1",
        extended: "1",
      });

      const response = await fetch(`https://ws.audioscrobbler.com/2.0/?${params.toString()}`);
      if (!response.ok) throw new Error(`Last.fm returned ${response.status}`);
      const data = await response.json();
      const rawTrack = Array.isArray(data?.recenttracks?.track)
        ? (data.recenttracks.track[0] as LastFmTrack | undefined)
        : (data?.recenttracks?.track as LastFmTrack | undefined);

      if (!rawTrack) {
        status = null;
        return;
      }

      const artistField = rawTrack.artist;
      const artistName = typeof artistField === "string"
        ? artistField
        : artistField?.name ?? artistField?.['#text'] ?? "Onbekende artiest";
      const title = rawTrack.name ?? "Onbekende track";
      const album = rawTrack.album?.['#text'];
      const nowPlaying = rawTrack['@attr']?.nowplaying === "true";
      const playedAt = !nowPlaying && rawTrack.date?.uts ? new Date(Number(rawTrack.date.uts) * 1000) : undefined;

      status = {
        artist: artistName,
        title,
        album,
        nowPlaying,
        url: rawTrack.url ?? profileUrl ?? "https://www.last.fm/",
        playedAt,
      };
    } catch (error) {
      if (import.meta.env.DEV) {
        console.error("Failed to load Last.fm status", error);
      }
      status = null;
    }
  }

  let intervalId: number | null = null;

  onMount(() => {
    loadNowPlaying();
    if (hasConfig) {
      intervalId = window.setInterval(loadNowPlaying, 60_000);
    }
  });

  onDestroy(() => {
    if (intervalId !== null) {
      window.clearInterval(intervalId);
    }
  });

  const bullet = "\u2022";
  const separator = " \u2014 ";
  const label = "Laatst geluisterd liedje";
  $: displayText = status
    ? `${label}${separator}${status.artist}${separator}${status.title}`
    : label;
  $: statusTitle = status
    ? `${status.nowPlaying ? "Luistert nu" : "Recent gespeeld"}: ${status.artist}${separator}${status.title}`
    : label;
</script>

{#if hasConfig}
  <a
    class="flex items-center gap-2 rounded-md border border-transparent px-2.5 py-1 text-sm text-accent transition hover:border-accent/40 hover:bg-accent/10 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2 focus-visible:ring-offset-transparent sm:flex"
    href={profileUrl ?? status?.url ?? "https://www.last.fm/"}
    rel="noopener noreferrer"
    target="_blank"
    title={statusTitle}
  >
    <svg aria-hidden="true" class="h-4 w-4 text-[#ba0000]" fill="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
      <path d="M18.936 13.446c-1.021 0-1.845.824-1.845 1.845 0 1.02.824 1.845 1.845 1.845s1.845-.825 1.845-1.845c0-1.021-.824-1.845-1.845-1.845zm-4.226.004c-1.733 0-3.011 1.084-3.359 2.878-.31 1.58-1.51 2.674-3.148 2.674-1.737 0-3.157-1.42-3.157-3.156 0-1.737 1.42-3.156 3.157-3.156.618 0 1.228.186 1.74.533l.51-2.178c-.71-.317-1.465-.481-2.25-.481-2.996 0-5.437 2.44-5.437 5.437 0 2.997 2.44 5.437 5.437 5.437 2.61 0 4.852-1.883 5.352-4.477.19-.964.867-1.832 2.115-1.832 1.02 0 1.845-.825 1.845-1.845 0-1.021-.825-1.845-1.845-1.845z" />
    </svg>
    <span aria-hidden="true">{bullet}</span>
    <span class="truncate" aria-hidden="true">{displayText}</span>
  </a>
{/if}

