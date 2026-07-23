<script lang="ts">
  import { onDestroy, onMount } from "svelte";

  export let embedded = false;

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
    imageUrl?: string;
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
      const imageUrl = rawTrack.image?.findLast((image) => Boolean(image['#text']))?.['#text'];

      status = {
        artist: artistName,
        title,
        album,
        nowPlaying,
        url: rawTrack.url ?? profileUrl ?? "https://www.last.fm/",
        playedAt,
        imageUrl,
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

  const separator = " \u2014 ";
  const label = "Laatst geluisterd";
  $: statusTitle = status
    ? `${status.nowPlaying ? "Luistert nu" : "Recent gespeeld"}: ${status.artist}${separator}${status.title}`
    : label;
</script>

{#if hasConfig}
  <a
    class:music-card--embedded={embedded}
    class="music-card"
    href={profileUrl ?? status?.url ?? "https://www.last.fm/"}
    rel="noopener noreferrer"
    target="_blank"
    title={statusTitle}
  >
    <span class="music-card__glass" aria-hidden="true"></span>
    <span class="music-card__content">
      <span class="music-card__eyebrow">
        <svg aria-hidden="true" fill="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path d="M18.936 13.446c-1.021 0-1.845.824-1.845 1.845 0 1.02.824 1.845 1.845 1.845s1.845-.825 1.845-1.845c0-1.021-.824-1.845-1.845-1.845zm-4.226.004c-1.733 0-3.011 1.084-3.359 2.878-.31 1.58-1.51 2.674-3.148 2.674-1.737 0-3.157-1.42-3.157-3.156 0-1.737 1.42-3.156 3.157-3.156.618 0 1.228.186 1.74.533l.51-2.178c-.71-.317-1.465-.481-2.25-.481-2.996 0-5.437 2.44-5.437 5.437 0 2.997 2.44 5.437 5.437 5.437 2.61 0 4.852-1.883 5.352-4.477.19-.964.867-1.832 2.115-1.832 1.02 0 1.845-.825 1.845-1.845 0-1.021-.825-1.845-1.845-1.845z" />
        </svg>
        <span class:music-card__live={status?.nowPlaying}></span>
        {status?.nowPlaying ? "Luistert nu" : label}
      </span>
      <strong>{status?.title ?? "Muziekprofiel openen"}</strong>
      <span class="music-card__artist">{status?.artist ?? "Last.fm"}</span>
      {#if status?.album}<span class="music-card__album">{status.album}</span>{/if}
    </span>
    <span class="music-card__art" aria-hidden="true">
      {#if status?.imageUrl}
        <img src={status.imageUrl} alt="" />
      {:else}
        <svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 3v10.55A4 4 0 1 0 14 17V7h4V3h-6Z" /></svg>
      {/if}
    </span>
    <span class="music-card__open" aria-hidden="true">↗</span>
  </a>
{/if}

<style>
  .music-card {
    position: relative;
    display: block;
    min-height: 4.55rem;
    overflow: hidden;
    border: 1px solid rgb(255 255 255 / 55%);
    border-radius: 1.25rem;
    background: linear-gradient(145deg, #22d3ee 0%, #4188dc 48%, #7657d7 100%);
    color: #082f49;
    perspective: 900px;
    box-shadow: 0 10px 22px rgb(30 91 139 / 18%), inset 0 1px 0 rgb(255 255 255 / 55%);
    transform-style: preserve-3d;
    transition: transform .4s cubic-bezier(.22, 1, .36, 1), box-shadow .4s ease;
  }

  .music-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 14px 26px rgb(48 76 146 / 24%);
  }

  .music-card--embedded {
    min-height: 4rem;
    border: 0;
    border-radius: 0;
    background: transparent;
    box-shadow: none;
  }

  .music-card--embedded:hover {
    transform: none;
    box-shadow: none;
  }

  .music-card--embedded .music-card__glass { display: none; }
  .music-card--embedded .music-card__content { padding-inline: .85rem; }
  .music-card--embedded .music-card__art { top: .5rem; right: .7rem; }

  .music-card:focus-visible { outline: 3px solid #fff; outline-offset: 3px; }

  .music-card__glass {
    position: absolute;
    inset: .3rem;
    border: 1px solid rgb(255 255 255 / 65%);
    border-radius: 1rem;
    background: linear-gradient(0deg, rgb(255 255 255 / 38%), rgb(255 255 255 / 78%));
    box-shadow: inset 0 1px 1px rgb(255 255 255 / 85%);
  }

  .music-card__content {
    position: relative;
    z-index: 3;
    display: flex;
    min-width: 0;
    max-width: calc(100% - 4.35rem);
    padding: .55rem .75rem;
    flex-direction: column;
  }

  .music-card__eyebrow { display: flex; align-items: center; gap: .3rem; margin-bottom: .12rem; color: rgb(8 47 73 / 70%); font-size: .51rem; font-weight: 800; letter-spacing: .08em; text-transform: uppercase; }
  .music-card__eyebrow svg { width: 1rem; height: 1rem; color: #b90024; }
  .music-card__eyebrow > span { width: .42rem; height: .42rem; border-radius: 50%; background: #66849a; }
  .music-card__eyebrow > .music-card__live { background: #ff315c; box-shadow: 0 0 0 4px rgb(255 49 92 / 15%), 0 0 12px #ff315c; animation: music-pulse 1.7s ease-in-out infinite; }
  .music-card__content strong { overflow: hidden; font-size: .8rem; line-height: 1.08; text-overflow: ellipsis; white-space: nowrap; }
  .music-card__artist { overflow: hidden; margin-top: .1rem; color: rgb(8 47 73 / 82%); font-size: .65rem; font-weight: 700; text-overflow: ellipsis; white-space: nowrap; }
  .music-card__album { display: none; }

  .music-card__art { position: absolute; top: .55rem; right: .65rem; z-index: 4; display: grid; width: 2.7rem; height: 2.7rem; overflow: hidden; place-items: center; border: 1px solid rgb(255 255 255 / 72%); border-radius: .55rem; background: rgb(255 255 255 / 32%); box-shadow: 0 5px 12px rgb(23 66 112 / 20%); clip-path: inset(0 round .55rem); }
  .music-card__art img { display: block; width: 100%; height: 100%; border-radius: .85rem; object-fit: cover; }
  .music-card__art svg { width: 2rem; color: rgb(255 255 255 / 85%); }
  .music-card__open { display: none; }

  @keyframes music-pulse { 50% { opacity: .45; transform: scale(.82); } }

  :global([data-theme="dark"]) .music-card { color: #e8faff; background: linear-gradient(145deg, rgb(7 89 133 / 72%), rgb(55 48 163 / 70%) 58%, rgb(112 26 117 / 66%)); }
  :global([data-theme="dark"]) .music-card--embedded { background: transparent; }
  :global([data-theme="dark"]) .music-card__glass { border-color: rgb(193 239 255 / 20%); background: linear-gradient(180deg, rgb(255 255 255 / 13%), rgb(12 20 48 / 52%)); }
  :global([data-theme="dark"]) .music-card__eyebrow,
  :global([data-theme="dark"]) .music-card__artist { color: rgb(226 247 255 / 78%); }
  :global([data-theme="dark"]) .music-card__album { color: rgb(226 247 255 / 55%); }

  @media (max-width: 480px) {
    .music-card { min-height: 4.45rem; border-radius: 1.15rem; }
    .music-card__glass { border-radius: .9rem; }
    .music-card__content { max-width: calc(100% - 4.2rem); padding: .55rem .7rem; }
    .music-card__art { top: .55rem; right: .6rem; width: 2.65rem; height: 2.65rem; border-radius: .55rem; clip-path: inset(0 round .55rem); }
    .music-card__art img { border-radius: .5rem; }
    .music-card--embedded { min-height: 4rem; }
  }
</style>
