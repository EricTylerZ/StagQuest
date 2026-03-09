/**
 * Sentinel Ops API Client — Connects Stellar Virtue to EZ Merit Points
 *
 * Optional integration. If Sentinel Ops is unreachable, the game works offline.
 * Stores role_id and server URL in localStorage for persistence between sessions.
 */
const SentinelAPI = (() => {
  const STORAGE_KEY = 'sentinel_config';

  function getConfig() {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY)) || {};
    } catch { return {}; }
  }

  function saveConfig(config) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(config));
  }

  function getBaseUrl() {
    return getConfig().baseUrl || 'http://localhost:8000';
  }

  function getRoleId() {
    return getConfig().roleId || null;
  }

  async function request(method, path, body) {
    const res = await fetch(getBaseUrl() + path, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: body ? JSON.stringify(body) : undefined,
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || `HTTP ${res.status}`);
    return data;
  }

  return {
    configure(baseUrl) {
      const config = getConfig();
      config.baseUrl = baseUrl;
      saveConfig(config);
    },

    getRoleId,
    getBaseUrl,

    isLoggedIn() {
      return !!getRoleId();
    },

    async login(roleId) {
      const data = await request('GET', `/api/agents/${roleId}/profile`);
      const config = getConfig();
      config.roleId = roleId;
      config.roleName = data.name;
      saveConfig(config);
      return data;
    },

    async register(name, tosVersion) {
      const data = await request('POST', '/api/agents/register', {
        name,
        is_ai: false,
        tos_version: tosVersion || '1.0',
      });
      const config = getConfig();
      config.roleId = data.role_id;
      config.roleName = name;
      saveConfig(config);
      return data;
    },

    async submitMerit(points, gameSummary) {
      const roleId = getRoleId();
      if (!roleId) throw new Error('Not logged in');
      return request('POST', '/api/game/merit', {
        role_id: roleId,
        points_earned: points,
        game_summary: gameSummary,
      });
    },

    async getBalance() {
      const roleId = getRoleId();
      if (!roleId) throw new Error('Not logged in');
      return request('GET', `/api/wallet/${roleId}`);
    },

    getStoredName() {
      return getConfig().roleName || null;
    },

    logout() {
      const config = getConfig();
      delete config.roleId;
      delete config.roleName;
      saveConfig(config);
    },
  };
})();
