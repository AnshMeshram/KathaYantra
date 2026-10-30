/**
 * KathaYantra Canonical Route Helpers
 * Eliminates hardcoded URL duplication across components.
 */

export function getCountryRoute(countryCode: string): string {
  return `/countries/${countryCode.toUpperCase()}`;
}

export function getStoryRoute(storyId: string): string {
  return `/stories/${storyId.toUpperCase()}`;
}

export function getCategoryRoute(category: "folklore" | "urban_legend"): string {
  return `/#${category === "folklore" ? "folklore-collection" : "urban-legends-collection"}`;
}
