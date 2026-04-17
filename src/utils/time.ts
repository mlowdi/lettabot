/**
 * Shared timing helpers used across startup and persistence paths.
 */

const SLEEP_BUFFER = new Int32Array(new SharedArrayBuffer(4));
let warnedAboutBusyWait = false;

export function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export function sleepSync(ms: number, onBusyWait?: () => void): void {
  if (typeof Atomics.wait === 'function') {
    Atomics.wait(SLEEP_BUFFER, 0, 0, ms);
    return;
  }
  if (!warnedAboutBusyWait) {
    onBusyWait?.();
    warnedAboutBusyWait = true;
  }
  const end = Date.now() + ms;
  while (Date.now() < end) {
    // Busy-wait fallback -- should not be reached in standard Node.js (v8+)
  }
}

/**
 * Thrown when formatRelativeTime receives an unparseable timestamp.
 */
export class InvalidTimestampError extends Error {
  constructor(input: string) {
    super(`Invalid timestamp: "${input}"`);
    this.name = 'InvalidTimestampError';
  }
}

/**
 * Format a timestamp as a human-readable relative time string.
 *
 * Past:  "just now", "5 minutes ago", "yesterday at 15:42",
 *        "last year in March", "a long time ago"
 * Future: "in a few seconds", "in 5 minutes", "next month", "in the future"
 *
 * @throws {InvalidTimestampError} if the string cannot be parsed as a date
 */
export function formatRelativeTime(timestamp: string | Date, now: Date = new Date()): string {
  const date = typeof timestamp === 'string' ? new Date(timestamp) : timestamp;

  if (isNaN(date.getTime())) {
    throw new InvalidTimestampError(typeof timestamp === 'string' ? timestamp : '(Date object)');
  }

  const diffMs = now.getTime() - date.getTime();
  const diffSec = Math.floor(Math.abs(diffMs) / 1000);
  const diffMin = Math.floor(diffSec / 60);
  const diffHour = Math.floor(diffMin / 60);
  const diffDay = Math.floor(diffHour / 24);

  const past = diffMs >= 0;
  if (!past) {
    if (diffSec < 60) return 'in a few seconds';
    if (diffMin < 60) return `in ${diffMin} minute${diffMin !== 1 ? 's' : ''}`;
    if (diffHour < 24) return `in ${diffHour} hour${diffHour !== 1 ? 's' : ''}`;
    if (diffDay === 1) {
      const time = date.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' });
      return `tomorrow at ${time}`;
    }
    if (diffDay < 7) return `in ${diffDay} day${diffDay !== 1 ? 's' : ''}`;
    if (diffDay < 30) {
      const weeks = Math.floor(diffDay / 7);
      return `in ${weeks} week${weeks !== 1 ? 's' : ''}`;
    }
    if (diffDay < 60) return 'next month';

    // Check if it's still within the next calendar year
    const currentYear = now.getFullYear();
    if (date.getFullYear() <= currentYear + 1) {
      const month = date.toLocaleDateString(undefined, { month: 'long' });
      return `in ${month} ${date.getFullYear()}`;
    }

    return 'in the future';
  }

  // --- Past timestamps ---
  if (diffSec < 60) return 'just now';
  if (diffMin < 60) return `${diffMin} minute${diffMin !== 1 ? 's' : ''} ago`;
  if (diffHour < 24) return `${diffHour} hour${diffHour !== 1 ? 's' : ''} ago`;
  if (diffDay === 1) {
    const time = date.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' });
    return `yesterday at ${time}`;
  }
  if (diffDay < 7) return `${diffDay} day${diffDay !== 1 ? 's' : ''} ago`;
  if (diffDay < 30) {
    const weeks = Math.floor(diffDay / 7);
    return `${weeks} week${weeks !== 1 ? 's' : ''} ago`;
  }

  // "last year" covers the entire previous calendar year
  const currentYear = now.getFullYear();
  if (date.getFullYear() === currentYear - 1) {
    const month = date.toLocaleDateString(undefined, { month: 'long' });
    return `last year in ${month}`;
  }

  // Anything older than last year
  if (date.getFullYear() < currentYear - 1) {
    return 'a long time ago';
  }

  // Same year but older than a month — show month + date
  return date.toLocaleDateString(undefined, {
    month: 'long',
    day: 'numeric',
  });
}
