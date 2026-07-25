const OFFLINE_ATTENDANCE_KEY = 'ediv_offline_attendance';

export function saveAttendanceOffline(record) {
  const existing = getOfflineAttendance();
  existing.push({
    ...record,
    timestamp: new Date().toISOString(),
    synced: false,
  });
  localStorage.setItem(OFFLINE_ATTENDANCE_KEY, JSON.stringify(existing));
  return existing;
}

export function getOfflineAttendance() {
  try {
    return JSON.parse(localStorage.getItem(OFFLINE_ATTENDANCE_KEY) || '[]');
  } catch {
    return [];
  }
}

export function clearSyncedAttendance() {
  const all = getOfflineAttendance();
  const unsynced = all.filter((r) => !r.synced);
  localStorage.setItem(OFFLINE_ATTENDANCE_KEY, JSON.stringify(unsynced));
  return unsynced;
}

export function markSynced(index) {
  const all = getOfflineAttendance();
  if (all[index]) {
    all[index].synced = true;
    localStorage.setItem(OFFLINE_ATTENDANCE_KEY, JSON.stringify(all));
  }
}

export async function syncOfflineAttendance(apiClient) {
  const records = getOfflineAttendance();
  const unsynced = records.filter((r) => !r.synced);
  const results = { synced: 0, failed: 0 };

  for (let i = 0; i < records.length; i++) {
    if (records[i].synced) continue;
    try {
      await apiClient.post('/api/attendance/attendance/', {
        student_id: records[i].student_id,
        school_id: records[i].school_id,
        date: records[i].date,
        status: records[i].status,
        offline_sync: true,
      });
      markSynced(i);
      results.synced++;
    } catch {
      results.failed++;
    }
  }

  if (results.synced > 0) clearSyncedAttendance();
  return results;
}

export function isOnline() {
  return navigator.onLine;
}
