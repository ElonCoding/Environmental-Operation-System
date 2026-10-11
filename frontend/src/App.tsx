import { useState } from 'react';
import { 
  Activity, 
  AlertTriangle, 
  CheckCircle2, 
  Droplets, 
  FileText, 
  MapPin, 
  RefreshCw, 
  ShieldAlert, 
  TrendingUp, 
  Waves
} from 'lucide-react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ReferenceLine
} from 'recharts';

interface GhatData {
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

const GHATS_DATA: GhatData[] = [
  {
    id: 'khatlapura-ghat',
    name: 'Khatlapura Ghat',
    waterBody: 'Lower Lake',
    riskScore: 84,
    riskLevel: 'Critical',
    eventsCount: 18,
    avgDO: 3.8,
    avgBOD: 9.4,
    avgTurbidity: 32.5,
    cpcbPassed: false,
    notes: 'Major idol immersion pressure point. Severe dissolved oxygen depletion post-visarjan.',
    recommendation: 'Immediate deployment of floating surface aerators and mandatory containment barricades.'
  },
  {
    id: 'sheetal-das-ki-bagiya',
    name: 'Sheetal Das Ki Bagiya',
    waterBody: 'Upper Lake',
    riskScore: 78,
    riskLevel: 'High',
    eventsCount: 18,
    avgDO: 4.4,
    avgBOD: 7.6,
    avgTurbidity: 28.0,
    cpcbPassed: false,
    notes: 'Historic prominent Upper Lake site. High organic sediment accumulation.',
    recommendation: 'Divert heavy idol immersions to artificial kunds; post-festival silt suction.'
  },
  {
    id: 'rani-kamlapati-kamla-park',
    name: 'Rani Kamlapati / Kamla Park',
    waterBody: 'Lower Lake',
    riskScore: 72,
    riskLevel: 'High',
    eventsCount: 18,
    avgDO: 4.1,
    avgBOD: 6.8,
    avgTurbidity: 25.2,
    cpcbPassed: false,
    notes: 'High organic loading during festival peaks between Upper and Lower Lake bottleneck.',
    recommendation: 'Deploy micro-bubble oxygenators 48h prior to festival culmination.'
  },
  {
    id: 'prempura-ghat',
    name: 'Prempura Ghat',
    waterBody: 'Upper Lake',
    riskScore: 61,
    riskLevel: 'Moderate',
    eventsCount: 18,
    avgDO: 5.2,
    avgBOD: 5.1,
    avgTurbidity: 19.4,
    cpcbPassed: true,
    notes: 'Transitioned heavily to artificial kunds following NGT regulatory directives.',
    recommendation: 'Maintain bio-remedial dosing and enforce artificial tank segregation.'
  },
  {
    id: 'shahpura-lake',
    name: 'Shahpura Lake Ghat',
    waterBody: 'Shahpura Lake',
    riskScore: 88,
    riskLevel: 'Critical',
    eventsCount: 15,
    avgDO: 3.2,
    avgBOD: 11.2,
    avgTurbidity: 41.0,
    cpcbPassed: false,
    notes: 'High nutrient runoff and stagnation; severe biological oxygen demand exceeding Class B.',
    recommendation: 'Strict enforcement of eco-friendly idols and round-the-clock water skimming.'
  },
  {
    id: 'bairagarh-sant-hirdaram-kund',
    name: 'Bairagarh (Sant Hirdaram) Kund',
    waterBody: 'Upper Lake Shore',
    riskScore: 48,
    riskLevel: 'Moderate',
    eventsCount: 15,
    avgDO: 5.8,
    avgBOD: 4.2,
    avgTurbidity: 14.8,
    cpcbPassed: true,
    notes: 'Dedicated artificial kund setup substantially reduced direct lake load.',
    recommendation: 'Routine water exchange and neutralization of alkaline slurry after immersion.'
  },
  {
    id: 'hathaikheda-dam',
    name: 'Hathaikheda Dam Site',
    waterBody: 'Hathaikheda Reservoir',
    riskScore: 54,
    riskLevel: 'Moderate',
    eventsCount: 12,
    avgDO: 5.5,
    avgBOD: 4.8,
    avgTurbidity: 16.2,
    cpcbPassed: true,
    notes: 'Moderate perimeter impact; rapid post-monsoon natural dilution buffer.',
    recommendation: 'Post-immersion solid debris cleanup within 24 hours.'
  }
];

const TREND_DATA = [
  { stage: 'Pre-Immersion', DO: 6.4, BOD: 3.2, COD: 12.0, thresholdDO: 5.0 },
  { stage: 'Immersion Day 1', DO: 4.9, BOD: 5.8, COD: 22.4, thresholdDO: 5.0 },
  { stage: 'Peak Visarjan', DO: 3.6, BOD: 9.8, COD: 38.6, thresholdDO: 5.0 },
  { stage: 'Post 24h', DO: 4.1, BOD: 8.2, COD: 31.0, thresholdDO: 5.0 },
  { stage: 'Post 7 Days', DO: 5.3, BOD: 4.9, COD: 18.2, thresholdDO: 5.0 }
];

export default function App() {
  const [selectedGhat, setSelectedGhat] = useState<GhatData>(GHATS_DATA[0]);
  const backendUrl = 'https://environmental-operation-system-backend.onrender.com';
  const [activeTab, setActiveTab] = useState<'matrix' | 'trends' | 'briefing'>('matrix');
  const [backendStatus, setBackendStatus] = useState<'online' | 'connecting' | 'standby'>('standby');

  const checkBackend = async () => {
    setBackendStatus('connecting');
    try {
      const res = await fetch(`${backendUrl}/api/v1/health`, { method: 'GET' });
      if (res.ok) {
        setBackendStatus('online');
      } else {
        setBackendStatus('standby');
      }
    } catch {
      setBackendStatus('standby');
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      {/* Top Navigation */}
      <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur sticky top-0 z-50 px-6 py-4">
        <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-emerald-500 to-teal-400 flex items-center justify-center shadow-lg shadow-emerald-500/20">
              <Waves className="h-6 w-6 text-slate-950" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="font-bold text-lg text-white tracking-tight">Environmental Operation System</h1>
                <span className="text-xs font-semibold px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  OES v1.0
                </span>
              </div>
              <p className="text-xs text-slate-400">Bhopal Water Quality Intelligence & Ghat Monitoring Platform</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800/80 border border-slate-700/60 text-xs">
              <span className={`h-2 w-2 rounded-full ${backendStatus === 'online' ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400'}`} />
              <span className="text-slate-300">
                {backendStatus === 'online' ? 'Render Backend Live' : 'Embedded Data Mode'}
              </span>
              <button 
                onClick={checkBackend} 
                title="Ping Backend"
                className="ml-1 text-slate-400 hover:text-white"
              >
                <RefreshCw className="h-3.5 w-3.5" />
              </button>
            </div>

            <a
              href={`${backendUrl}/docs`}
              target="_blank"
              rel="noreferrer"
              className="text-xs font-medium px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 transition border border-slate-700"
            >
              API Docs
            </a>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-6 space-y-6">
        
        {/* Metric Cards Row */}
        <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800/80 shadow-sm">
            <div className="flex items-center justify-between text-slate-400 text-xs font-medium mb-2">
              <span>MONITORED GHATS</span>
              <MapPin className="h-4 w-4 text-emerald-400" />
            </div>
            <div className="text-2xl font-bold text-white">7 Canonical</div>
            <p className="text-xs text-slate-400 mt-1">Upper Lake, Lower Lake, Shahpura</p>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800/80 shadow-sm">
            <div className="flex items-center justify-between text-slate-400 text-xs font-medium mb-2">
              <span>CRITICAL HOTSPOTS</span>
              <ShieldAlert className="h-4 w-4 text-rose-400" />
            </div>
            <div className="text-2xl font-bold text-rose-400">3 Priority Sites</div>
            <p className="text-xs text-slate-400 mt-1">DO &lt; 4.0 mg/L post-immersion</p>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800/80 shadow-sm">
            <div className="flex items-center justify-between text-slate-400 text-xs font-medium mb-2">
              <span>CPCB CLASS B BENCHMARK</span>
              <Activity className="h-4 w-4 text-cyan-400" />
            </div>
            <div className="text-2xl font-bold text-cyan-300">DO ≥ 5.0 mg/L</div>
            <p className="text-xs text-slate-400 mt-1">Organized Outdoor Bathing Standard</p>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800/80 shadow-sm">
            <div className="flex items-center justify-between text-slate-400 text-xs font-medium mb-2">
              <span>OFFICIAL REPORTS</span>
              <FileText className="h-4 w-4 text-amber-400" />
            </div>
            <div className="text-2xl font-bold text-amber-300">2023–2025</div>
            <p className="text-xs text-slate-400 mt-1">MPPCB Official Post-Visarjan Data</p>
          </div>
        </section>

        {/* Navigation Tabs */}
        <div className="flex items-center gap-2 border-b border-slate-800 pb-2">
          <button
            onClick={() => setActiveTab('matrix')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
              activeTab === 'matrix' 
                ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30' 
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Ghat Risk Matrix
          </button>
          <button
            onClick={() => setActiveTab('trends')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
              activeTab === 'trends' 
                ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30' 
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Water Quality Impact Trends
          </button>
          <button
            onClick={() => setActiveTab('briefing')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
              activeTab === 'briefing' 
                ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30' 
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Officer Action Brief
          </button>
        </div>

        {/* View 1: Ghat Risk Matrix */}
        {activeTab === 'matrix' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Table of 7 Ghats */}
            <div className="lg:col-span-2 rounded-xl bg-slate-900/60 border border-slate-800/80 overflow-hidden shadow-sm">
              <div className="p-4 border-b border-slate-800 flex items-center justify-between">
                <div>
                  <h2 className="font-semibold text-white text-base">Bhopal Monitored Immersion Ghats</h2>
                  <p className="text-xs text-slate-400">Click any site to inspect water parameters & civic actions</p>
                </div>
                <span className="text-xs text-slate-400">7 Sites</span>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead className="bg-slate-950/40 text-slate-400 text-xs uppercase tracking-wider border-b border-slate-800">
                    <tr>
                      <th className="py-3 px-4">Ghat Name</th>
                      <th className="py-3 px-4">Water Body</th>
                      <th className="py-3 px-4 text-center">Avg DO (mg/L)</th>
                      <th className="py-3 px-4 text-center">Risk Score</th>
                      <th className="py-3 px-4">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60">
                    {GHATS_DATA.map((ghat) => (
                      <tr
                        key={ghat.id}
                        onClick={() => setSelectedGhat(ghat)}
                        className={`cursor-pointer transition hover:bg-slate-800/40 ${
                          selectedGhat.id === ghat.id ? 'bg-emerald-500/5 border-l-2 border-emerald-400' : ''
                        }`}
                      >
                        <td className="py-3 px-4 font-medium text-white">{ghat.name}</td>
                        <td className="py-3 px-4 text-slate-400 text-xs">{ghat.waterBody}</td>
                        <td className="py-3 px-4 text-center font-mono text-xs">
                          <span className={ghat.avgDO < 5.0 ? 'text-rose-400 font-bold' : 'text-emerald-400'}>
                            {ghat.avgDO}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-center">
                          <span className="font-mono text-xs font-semibold px-2 py-0.5 rounded bg-slate-800 text-slate-200">
                            {ghat.riskScore}/100
                          </span>
                        </td>
                        <td className="py-3 px-4">
                          <span
                            className={`inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full font-medium ${
                              ghat.riskLevel === 'Critical'
                                ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                                : ghat.riskLevel === 'High'
                                ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                                : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                            }`}
                          >
                            {ghat.riskLevel === 'Critical' && <AlertTriangle className="h-3 w-3" />}
                            {ghat.riskLevel === 'High' && <ShieldAlert className="h-3 w-3" />}
                            {ghat.riskLevel === 'Moderate' && <CheckCircle2 className="h-3 w-3" />}
                            {ghat.riskLevel}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Selected Ghat Details Card */}
            <div className="rounded-xl bg-slate-900/60 border border-slate-800/80 p-5 space-y-5 shadow-sm">
              <div className="border-b border-slate-800 pb-3">
                <span className="text-xs uppercase tracking-wider text-emerald-400 font-semibold">Ghat Detail Focus</span>
                <h3 className="text-xl font-bold text-white mt-1">{selectedGhat.name}</h3>
                <p className="text-xs text-slate-400 flex items-center gap-1 mt-0.5">
                  <MapPin className="h-3.5 w-3.5 text-slate-500" />
                  {selectedGhat.waterBody} • 18 Monitored Sampling Cycles
                </p>
              </div>

              <div className="grid grid-cols-3 gap-2 text-center">
                <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800/60">
                  <span className="text-[10px] text-slate-400 block uppercase">Avg DO</span>
                  <span className={`text-base font-bold font-mono ${selectedGhat.avgDO < 5 ? 'text-rose-400' : 'text-emerald-400'}`}>
                    {selectedGhat.avgDO} <span className="text-[10px] font-normal text-slate-500">mg/L</span>
                  </span>
                </div>
                <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800/60">
                  <span className="text-[10px] text-slate-400 block uppercase">Avg BOD</span>
                  <span className="text-base font-bold font-mono text-amber-400">
                    {selectedGhat.avgBOD} <span className="text-[10px] font-normal text-slate-500">mg/L</span>
                  </span>
                </div>
                <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800/60">
                  <span className="text-[10px] text-slate-400 block uppercase">Turbidity</span>
                  <span className="text-base font-bold font-mono text-cyan-400">
                    {selectedGhat.avgTurbidity} <span className="text-[10px] font-normal text-slate-500">NTU</span>
                  </span>
                </div>
              </div>

              <div className="space-y-2">
                <h4 className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
                  <Droplets className="h-3.5 w-3.5 text-teal-400" />
                  Environmental Assessment
                </h4>
                <p className="text-xs text-slate-400 leading-relaxed bg-slate-950/40 p-3 rounded-lg border border-slate-800/40">
                  {selectedGhat.notes}
                </p>
              </div>

              <div className="space-y-2">
                <h4 className="text-xs font-semibold text-emerald-400 flex items-center gap-1.5">
                  <TrendingUp className="h-3.5 w-3.5" />
                  BMC Operational Recommendation
                </h4>
                <p className="text-xs text-slate-300 leading-relaxed bg-emerald-950/20 p-3 rounded-lg border border-emerald-500/20">
                  {selectedGhat.recommendation}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* View 2: Water Quality Impact Trends */}
        {activeTab === 'trends' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="rounded-xl bg-slate-900/60 border border-slate-800/80 p-5 space-y-4">
              <div>
                <h3 className="font-semibold text-white text-base">Dissolved Oxygen (DO) Degradation Curve</h3>
                <p className="text-xs text-slate-400">Comparison across immersion festival stages vs CPCB Class B threshold</p>
              </div>
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={TREND_DATA}>
                    <defs>
                      <linearGradient id="colorDO" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#10b981" stopOpacity={0.4}/>
                        <stop offset="95%" stopColor="#10b981" stopOpacity={0.0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis dataKey="stage" stroke="#94a3b8" tick={{ fontSize: 11 }} />
                    <YAxis stroke="#94a3b8" tick={{ fontSize: 11 }} unit=" mg/L" domain={[0, 8]} />
                    <Tooltip 
                      contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.5rem', fontSize: '12px' }} 
                    />
                    <ReferenceLine y={5.0} stroke="#ef4444" strokeDasharray="4 4" label={{ value: 'CPCB Min (5.0)', fill: '#ef4444', fontSize: 11 }} />
                    <Area type="monotone" dataKey="DO" stroke="#10b981" strokeWidth={2} fillOpacity={1} fill="url(#colorDO)" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
              <p className="text-xs text-slate-400 italic">
                *Note steep drop during Peak Visarjan where DO breaches the 5.0 mg/L minimum threshold.
              </p>
            </div>

            <div className="rounded-xl bg-slate-900/60 border border-slate-800/80 p-5 space-y-4">
              <div>
                <h3 className="font-semibold text-white text-base">Biochemical Oxygen Demand (BOD) Spike</h3>
                <p className="text-xs text-slate-400">Organic pollution indicator throughout immersion timeline</p>
              </div>
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={TREND_DATA}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis dataKey="stage" stroke="#94a3b8" tick={{ fontSize: 11 }} />
                    <YAxis stroke="#94a3b8" tick={{ fontSize: 11 }} unit=" mg/L" />
                    <Tooltip 
                      contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.5rem', fontSize: '12px' }} 
                    />
                    <ReferenceLine y={3.0} stroke="#f59e0b" strokeDasharray="4 4" label={{ value: 'Class B Max (3.0)', fill: '#f59e0b', fontSize: 11 }} />
                    <Bar dataKey="BOD" fill="#38bdf8" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
              <p className="text-xs text-slate-400 italic">
                *BOD reaches maximum during festival peak due to organic offerings, flower residues, and clay dissolve.
              </p>
            </div>
          </div>
        )}

        {/* View 3: Officer Action Brief */}
        {activeTab === 'briefing' && (
          <div className="max-w-4xl mx-auto rounded-xl bg-slate-900/60 border border-slate-800/80 p-6 space-y-6">
            <div className="border-b border-slate-800 pb-4 flex items-center justify-between">
              <div>
                <span className="text-xs uppercase tracking-widest text-emerald-400 font-bold">
                  Bhopal Municipal Corporation • Track 2
                </span>
                <h2 className="text-xl font-bold text-white mt-1">
                  Environmental Operation System (OES) — Executive Water Action Brief
                </h2>
                <p className="text-xs text-slate-400 mt-0.5">
                  Target Planning Window: Durga Visarjan (October 2026) Operations
                </p>
              </div>
              <button
                onClick={() => window.print()}
                className="px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold flex items-center gap-1.5 transition"
              >
                <FileText className="h-3.5 w-3.5" />
                Print / Save PDF
              </button>
            </div>

            <div className="space-y-4 text-xs text-slate-300 leading-relaxed">
              <div className="p-4 rounded-lg bg-slate-950/50 border border-slate-800">
                <h4 className="font-semibold text-white text-sm mb-1">Executive Summary</h4>
                <p>
                  Analysis of 2023–2025 MPPCB official post-visarjan reports demonstrates acute, recurring localized oxygen depletion across Khatlapura Ghat (Lower Lake), Sheetal Das Ki Bagiya (Upper Lake), and Shahpura Lake. Immediate operational mitigation must focus on artificial tank diversion and mandatory aeration grids prior to major immersion dates.
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 rounded-lg bg-slate-950/50 border border-slate-800">
                  <h4 className="font-semibold text-emerald-400 mb-2">Priority Immediate Actions</h4>
                  <ul className="list-disc list-inside space-y-1.5 text-slate-300">
                    <li>Divert 100% of plaster-of-paris idols to reinforced artificial kunds.</li>
                    <li>Install 6 floating surface aspirating aerators at Khatlapura and Sheetal Das Ki Bagiya.</li>
                    <li>Set up barrier netting 20 meters from ghat perimeter to capture floating flora within 2 hours.</li>
                  </ul>
                </div>

                <div className="p-4 rounded-lg bg-slate-950/50 border border-slate-800">
                  <h4 className="font-semibold text-cyan-400 mb-2">Post-Festival Remediation Protocol</h4>
                  <ul className="list-disc list-inside space-y-1.5 text-slate-300">
                    <li>Commence hydraulic suction dredging for heavy sediment hotspots within 48h.</li>
                    <li>Conduct daily dissolved oxygen monitoring across 7 canonical sites for 7 days post-event.</li>
                    <li>Submit compliance report to MPPCB and National Green Tribunal (NGT) bench.</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-slate-950/80 px-6 py-4 mt-auto text-xs text-slate-500">
        <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-2">
          <span>Environmental Operation System (OES) © 2026. Built with React, Vite & Tailwind CSS.</span>
          <div className="flex items-center gap-4">
            <span>CPCB Class B Standard (DO ≥ 5.0 mg/L)</span>
            <span>MPPCB 2023–2025 Monitoring Dataset</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
