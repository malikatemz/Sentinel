import { mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";

const dataDirectory = path.join(process.cwd(), ".data");
const waitlistFile = path.join(dataDirectory, "waitlist.json");

async function readEntries() {
  try {
    const raw = await readFile(waitlistFile, "utf8");
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch (error) {
    if (error && typeof error === "object" && "code" in error && error.code === "ENOENT") {
      return [];
    }

    throw error;
  }
}

export async function saveWaitlistEntry(entry) {
  const normalizedEmail = entry.email.trim().toLowerCase();
  const entries = await readEntries();
  const existing = entries.find((item) => item.email === normalizedEmail);

  if (existing) {
    return {
      isNew: false,
      entry: existing,
      total: entries.length,
    };
  }

  const nextEntry = {
    email: normalizedEmail,
    source: entry.source || "sentinelapi-beta",
    submittedAt: entry.submittedAt || new Date().toISOString(),
    userAgent: entry.userAgent || null,
    ip: entry.ip || null,
  };

  await mkdir(dataDirectory, { recursive: true });
  await writeFile(waitlistFile, JSON.stringify([nextEntry, ...entries], null, 2));

  return {
    isNew: true,
    entry: nextEntry,
    total: entries.length + 1,
  };
}

export async function listWaitlistEntries() {
  return readEntries();
}

