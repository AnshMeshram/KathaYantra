/**
 * KathaYantra Canonical Route & Locale Helpers
 * Eliminates hardcoded URL duplication across components.
 */

export function getCountryRoute(countryCode: string): string {
  return `/countries/${countryCode.toUpperCase()}`;
}

export function getStoryRoute(storyId: string): string {
  return `/stories/${storyId.toUpperCase()}`;
}

export function getCategoryRoute(categorySlug: string): string {
  return `/categories/${categorySlug.toLowerCase()}`;
}

export function getCountryFlag(code: string): string {
  if (!code || code.length !== 2) return "🏛️";
  const upper = code.toUpperCase();
  try {
    return String.fromCodePoint(
      upper.charCodeAt(0) + 127397,
      upper.charCodeAt(1) + 127397
    );
  } catch {
    return "🏛️";
  }
}
