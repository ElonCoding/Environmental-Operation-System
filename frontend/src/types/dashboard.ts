export interface GhatMetric {
  id: string;
  name: string;
  waterBody: string;
  riskScore: number;
  riskLevel: 'Critical' | 'High' | 'Moderate' | 'Good';
  eventsCount: number;
  avgDO: number;
  avgBOD: number;
  avgTurbidity: number;
  cpcbPassed: boolean;
  notes: string;
  recommendation: string;
}

export interface ParameterTrend {
  stage: string;
  DO: number;
  BOD: number;
  COD: number;
  thresholdDO: number;
}
