const DEFAULT_BACKEND = 'https://environmental-operation-system-h41o.onrender.com';

export class ApiClient {
  private baseUrl: string;

  constructor(url: string = DEFAULT_BACKEND) {
    this.baseUrl = url;
  }

  async getHealth() {
    const res = await fetch(`${this.baseUrl}/api/v1/health`);
    if (!res.ok) throw new Error('Backend health check failed');
    return res.json();
  }

  async getGhatsRanking() {
    const res = await fetch(`${this.baseUrl}/api/v1/ghats/ranking`);
    if (!res.ok) throw new Error('Failed to fetch ghats ranking');
    return res.json();
  }
}

export const api = new ApiClient();
