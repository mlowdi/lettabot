import { describe, expect, it } from 'vitest';
import { sleep, sleepSync, formatRelativeTime, InvalidTimestampError } from './time.js';

describe('sleep', () => {
  it('waits asynchronously', async () => {
    const start = Date.now();
    await sleep(10);
    expect(Date.now() - start).toBeGreaterThanOrEqual(8);
  });
});

describe('sleepSync', () => {
  it('does not throw for zero delay', () => {
    expect(() => sleepSync(0)).not.toThrow();
  });
});

describe('formatRelativeTime', () => {
  const now = new Date('2026-04-17T13:00:00Z');

  // --- Past: just now ---
  it('returns "just now" for 0 seconds ago', () => {
    expect(formatRelativeTime('2026-04-17T13:00:00Z', now)).toBe('just now');
  });

  it('returns "just now" for 30 seconds ago', () => {
    expect(formatRelativeTime('2026-04-17T12:59:30Z', now)).toBe('just now');
  });

  it('returns "just now" for 59 seconds ago', () => {
    expect(formatRelativeTime('2026-04-17T12:59:01Z', now)).toBe('just now');
  });

  // --- Past: minutes ---
  it('returns singular minute', () => {
    expect(formatRelativeTime('2026-04-17T12:59:00Z', now)).toBe('1 minute ago');
  });

  it('returns minutes ago', () => {
    expect(formatRelativeTime('2026-04-17T12:50:00Z', now)).toBe('10 minutes ago');
  });

  it('returns 59 minutes ago', () => {
    expect(formatRelativeTime('2026-04-17T12:01:00Z', now)).toBe('59 minutes ago');
  });

  // --- Past: hours ---
  it('returns singular hour', () => {
    expect(formatRelativeTime('2026-04-17T12:00:00Z', now)).toBe('1 hour ago');
  });

  it('returns hours ago', () => {
    expect(formatRelativeTime('2026-04-17T10:00:00Z', now)).toBe('3 hours ago');
  });

  it('returns 23 hours ago', () => {
    expect(formatRelativeTime('2026-04-16T14:00:00Z', now)).toBe('23 hours ago');
  });

  // --- Past: yesterday ---
  it('returns "yesterday at HH:MM" for 1 day ago', () => {
    // Note: timestamp rendering uses local timezone, so just check the pattern
    expect(formatRelativeTime('2026-04-16T13:00:00Z', now)).toMatch(/^yesterday at \d{2}:\d{2}$/);
  });

  it('returns yesterday even for ~25 hours ago', () => {
    const result = formatRelativeTime('2026-04-16T12:00:00Z', now);
    expect(result).toContain('yesterday at');
  });

  // --- Past: days ---
  it('returns days ago (2-6 days)', () => {
    expect(formatRelativeTime('2026-04-15T10:00:00Z', now)).toBe('2 days ago');
  });

  it('returns "6 days ago"', () => {
    expect(formatRelativeTime('2026-04-11T13:00:00Z', now)).toBe('6 days ago');
  });

  // --- Past: weeks ---
  it('returns singular week for 7-13 days', () => {
    expect(formatRelativeTime('2026-04-10T13:00:00Z', now)).toBe('1 week ago');
  });

  it('returns weeks ago for 14-29 days', () => {
    expect(formatRelativeTime('2026-04-03T13:00:00Z', now)).toBe('2 weeks ago');
  });

  it('returns "4 weeks ago" for ~28 days', () => {
    expect(formatRelativeTime('2026-03-20T13:00:00Z', now)).toBe('4 weeks ago');
  });

  // --- Past: same year, older than a month ---
  it('returns "Month Day" for same-year dates older than a month', () => {
    expect(formatRelativeTime('2026-02-17T13:00:00Z', now)).toBe('February 17');
  });

  it('returns "January 5" for early same-year dates', () => {
    expect(formatRelativeTime('2026-01-05T13:00:00Z', now)).toBe('January 5');
  });

  // --- Past: last year ---
  it('returns "last year in Month" for previous calendar year', () => {
    expect(formatRelativeTime('2025-06-15T13:00:00Z', now)).toBe('last year in June');
  });

  it('returns "last year in December" for late last year', () => {
    expect(formatRelativeTime('2025-12-31T13:00:00Z', now)).toBe('last year in December');
  });

  it('returns "last year in January" for early last year', () => {
    expect(formatRelativeTime('2025-01-01T13:00:00Z', now)).toBe('last year in January');
  });

  // --- Past: a long time ago ---
  it('returns "a long time ago" for 2+ years ago', () => {
    expect(formatRelativeTime('2024-04-17T13:00:00Z', now)).toBe('a long time ago');
  });

  it('returns "a long time ago" for 5 years ago', () => {
    expect(formatRelativeTime('2021-04-17T13:00:00Z', now)).toBe('a long time ago');
  });

  it('returns "a long time ago" for 2020', () => {
    expect(formatRelativeTime('2020-01-01T00:00:00Z', now)).toBe('a long time ago');
  });

  // --- Future: seconds ---
  it('returns "in a few seconds" for <60 seconds in the future', () => {
    expect(formatRelativeTime('2026-04-17T13:00:30Z', now)).toBe('in a few seconds');
  });

  it('returns "in a few seconds" for 1 second in the future', () => {
    expect(formatRelativeTime('2026-04-17T13:00:01Z', now)).toBe('in a few seconds');
  });

  // --- Future: minutes ---
  it('returns "in N minutes" for future minutes', () => {
    expect(formatRelativeTime('2026-04-17T13:10:00Z', now)).toBe('in 10 minutes');
  });

  it('returns "in 1 minute" for singular', () => {
    expect(formatRelativeTime('2026-04-17T13:01:00Z', now)).toBe('in 1 minute');
  });

  // --- Future: hours ---
  it('returns "in N hours" for future hours', () => {
    expect(formatRelativeTime('2026-04-17T16:00:00Z', now)).toBe('in 3 hours');
  });

  it('returns "in 1 hour" for singular', () => {
    expect(formatRelativeTime('2026-04-17T14:00:00Z', now)).toBe('in 1 hour');
  });

  // --- Future: tomorrow ---
  it('returns "tomorrow at HH:MM" for 1 day ahead', () => {
    expect(formatRelativeTime('2026-04-18T13:00:00Z', now)).toMatch(/^tomorrow at \d{2}:\d{2}$/);
  });

  // --- Future: days ---
  it('returns "in N days" for 2-6 days ahead', () => {
    expect(formatRelativeTime('2026-04-19T13:00:00Z', now)).toBe('in 2 days');
  });

  // --- Future: weeks ---
  it('returns "in N weeks" for 1-4 weeks ahead', () => {
    expect(formatRelativeTime('2026-04-24T13:00:00Z', now)).toBe('in 1 week');
  });

  it('returns "in 2 weeks" for ~14 days ahead', () => {
    expect(formatRelativeTime('2026-05-01T13:00:00Z', now)).toBe('in 2 weeks');
  });

  // --- Future: next month ---
  it('returns "next month" for 30-59 days ahead', () => {
    expect(formatRelativeTime('2026-05-17T13:00:00Z', now)).toBe('next month');
  });

  // --- Future: named month ---
  it('returns "in Month Year" within next calendar year', () => {
    expect(formatRelativeTime('2026-12-17T13:00:00Z', now)).toBe('in December 2026');
  });

  it('returns "in Month Year" for next calendar year', () => {
    expect(formatRelativeTime('2027-03-17T13:00:00Z', now)).toBe('in March 2027');
  });

  // --- Future: far future ---
  it('returns "in the future" for beyond next calendar year', () => {
    expect(formatRelativeTime('2028-04-17T13:00:00Z', now)).toBe('in the future');
  });

  it('returns "in the future" for 2030', () => {
    expect(formatRelativeTime('2030-01-01T00:00:00Z', now)).toBe('in the future');
  });

  // --- Input types ---
  it('accepts Date objects', () => {
    expect(formatRelativeTime(new Date('2026-04-17T12:55:00Z'), now)).toBe('5 minutes ago');
  });

  it('accepts Date objects for future', () => {
    expect(formatRelativeTime(new Date('2026-04-17T13:05:00Z'), now)).toBe('in 5 minutes');
  });

  // --- Malformed timestamps ---
  it('throws InvalidTimestampError for garbage strings', () => {
    expect(() => formatRelativeTime('not a date', now)).toThrow(InvalidTimestampError);
  });

  it('throws InvalidTimestampError for empty string', () => {
    expect(() => formatRelativeTime('', now)).toThrow(InvalidTimestampError);
  });

  it('throws InvalidTimestampError for partial date', () => {
    expect(() => formatRelativeTime('2026-13-45', now)).toThrow(InvalidTimestampError);
  });

  it('includes the bad input in the error message', () => {
    expect(() => formatRelativeTime('garbage', now)).toThrow(/"garbage"/);
  });
});
