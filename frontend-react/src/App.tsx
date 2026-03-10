import { useState, useCallback } from 'react';
import { UploadedImage, PipelineRequest, PipelineResult, SSEEvent, LogEntry, StepStatus, AuthUser } from './types';
import { useAuth } from './context/AuthContext';
import AuthPage from './pages/AuthPage';
import Dashboard from './pages/Dashboard';
import Header from './components/Header';
import ConfigCard from './components/ConfigCard';
import ProductForm from './components/ProductForm';
import ImageUploadCard from './components/ImageUploadCard';
import PipelineTracker from './components/PipelineTracker';
import LogPanel from './components/LogPanel';
import Results from './components/Results';
import styles from './App.module.css';

// -------------------------------------------------
// ForgeApp - main pipeline UI
// -------------------------------------------------
interface ForgeAppProps {
    token: string | null;
    user: AuthUser | null;
    onDashboard: () => void;
    onLogout: () => void;
}

function ForgeApp({ token, user, onDashboard, onLogout }: ForgeAppProps) {
    const [serverBase, setServerBase] = useState('http://localhost:8000');
    const [apiKeyOverride, setApiKeyOverride] = useState('');
    const [productDescription, setProductDescription] = useState('');
    const [productCategory, setProductCategory] = useState('');
    const [targetAudience, setTargetAudience] = useState('');
    const [messagingAngle, setMessagingAngle] = useState('auto');
    const [images, setImages] = useState<UploadedImage[]>([]);
    const [scrapeEnabled, setScrapeEnabled] = useState(true);
    const [ragEnabled, setRagEnabled] = useState(true);
    const [isRunning, setIsRunning] = useState(false);
    const [logs, setLogs] = useState<LogEntry[]>([]);
    const [stepStatuses, setStepStatuses] = useState<Record<number, StepStatus>>({
        1: 'inactive', 2: 'inactive', 3: 'inactive', 4: 'inactive', 5: 'inactive', 6: 'inactive'
    });
    const [result, setResult] = useState<PipelineResult | null>(null);
    const [imageMismatchMsg, setImageMismatchMsg] = useState<string | null>(null);

    const addLog = useCallback((message: string, level: LogEntry['level'] = 'info') => {
        const timestamp = new Date().toLocaleTimeString('en', { hour12: false });
        setLogs(prev => [...prev, { timestamp, message, level }]);
    }, []);

    const updateStepStatus = useCallback((step: number, status: StepStatus) => {
        setStepStatuses(prev => {
            const newStatuses = { ...prev };
            for (let i = 1; i < step; i++) {
                if (newStatuses[i] !== 'error' && newStatuses[i] !== 'warn') newStatuses[i] = 'done';
            }
            const current = newStatuses[step];
            if (current === 'warn' && status === 'done') { /* keep warn */ }
            else if (current === 'error' && (status === 'done' || status === 'warn')) { /* keep error */ }
            else { newStatuses[step] = status; }
            return newStatuses;
        });
    }, []);

    const markAllStepsDone = useCallback(() => {
        setStepStatuses(prev => {
            const r: Record<number, StepStatus> = {};
            for (let i = 1; i <= 6; i++) {
                r[i] = (prev[i] === 'warn' || prev[i] === 'error') ? prev[i] : 'done';
            }
            return r;
        });
    }, []);

    const handleSSEEvent = useCallback((event: SSEEvent): boolean => {
        if (event.type === 'ping') return false;
        if (event.type === 'image_mismatch' && event.message) {
            updateStepStatus(3, 'error');
            setImageMismatchMsg(event.message);
            addLog(`[BLOCKED] [S3] ${event.message}`, 'error');
            return true;
        }
        if (event.type === 'step' && event.step && event.message) {
            const icon = event.status === 'done' ? '[OK]' : event.status === 'error' ? '[ERR]' : event.status === 'warn' ? '[WARN]' : '->';
            const level = event.status === 'done' ? 'success' : event.status === 'error' ? 'error' : event.status === 'warn' ? 'warn' : 'info';
            addLog(`${icon} [S${event.step}] ${event.message}`, level);
            if (event.status === 'error') updateStepStatus(event.step, 'error');
            else if (event.status === 'warn') updateStepStatus(event.step, 'warn');
            else if (event.status === 'done') updateStepStatus(event.step, 'done');
            else updateStepStatus(event.step, 'active');
        } else if (event.type === 'complete' && event.result) {
            markAllStepsDone();
            addLog('Pipeline complete!', 'success');
            setResult(event.result);
        } else if (event.type === 'error' && event.message) {
            addLog(`Error: ${event.message}`, 'error');
        }
        return false;
    }, [addLog, updateStepStatus, markAllStepsDone]);

    const runPipeline = useCallback(async () => {
        if (!productDescription.trim()) { alert('Product description is required'); return; }
        if (!productCategory.trim()) { alert('Product category is required'); return; }
        setLogs([]); setResult(null); setImageMismatchMsg(null);
        setStepStatuses({ 1: 'inactive', 2: 'inactive', 3: 'inactive', 4: 'inactive', 5: 'inactive', 6: 'inactive' });
        setIsRunning(true);

        const body: PipelineRequest = {
            product_description: productDescription.trim(),
            product_category: productCategory.trim(),
            target_audience: targetAudience.trim() || null,
            messaging_angle: messagingAngle,
            scrape_competitors: scrapeEnabled,
            use_rag: ragEnabled,
            competitor_images_b64: images.map(i => i.b64),
            image_mime_types: images.map(i => i.mime),
        };

        let url = `${serverBase.replace(/\/$/, '')}/api/pipeline/generate/stream`;
        if (apiKeyOverride.trim()) url += `?api_key=${encodeURIComponent(apiKeyOverride.trim())}`;

        try {
            const headers: Record<string, string> = { 'Content-Type': 'application/json' };
            if (token) headers['Authorization'] = `Bearer ${token}`;

            const response = await fetch(url, { method: 'POST', headers, body: JSON.stringify(body) });
            if (!response.ok) {
                const err = await response.json().catch(() => ({}));
                throw new Error(err.detail || `HTTP ${response.status}`);
            }
            const reader = response.body?.getReader();
            if (!reader) throw new Error('No response body');
            const decoder = new TextDecoder();
            let buffer = '';
            let aborted = false;

            // eslint-disable-next-line @typescript-eslint/no-unnecessary-condition
            while (true) {
                const { value, done } = await reader.read();
                if (done || aborted) break;
                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n');
                buffer = lines.pop() || '';
                for (const line of lines) {
                    if (!line.startsWith('data:')) continue;
                    const raw = line.slice(5).trim();
                    if (!raw) continue;
                    try {
                        const event: SSEEvent = JSON.parse(raw);
                        const shouldAbort = handleSSEEvent(event);
                        if (shouldAbort) { aborted = true; reader.cancel(); break; }
                    } catch (e) { console.warn('Bad SSE line:', raw); }
                }
            }
        } catch (err) {
            addLog(`Error: ${(err as Error).message}`, 'error');
        } finally {
            setIsRunning(false);
        }
    }, [serverBase, apiKeyOverride, productDescription, productCategory, targetAudience, messagingAngle, scrapeEnabled, ragEnabled, images, token, addLog, handleSSEEvent]);

    return (
        <div className={styles.app}>
            {/* User toolbar */}
            <div style={{
                position: 'sticky', top: 0, zIndex: 50,
                display: 'flex', justifyContent: 'flex-end', alignItems: 'center',
                gap: '10px', padding: '10px 20px',
                background: 'rgba(8,8,16,0.9)', backdropFilter: 'blur(12px)',
                borderBottom: '1px solid rgba(255,255,255,0.06)',
            }}>
                <div style={{
                    width: 30, height: 30, borderRadius: '50%',
                    background: user?.avatar_color || '#7c3aed',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontWeight: 800, fontSize: 12, color: '#fff', flexShrink: 0,
                }}>
                    {user?.username?.[0]?.toUpperCase() ?? '?'}
                </div>
                <span style={{ fontSize: 12, color: 'rgba(255,255,255,0.5)', fontWeight: 600 }}>
                    {user?.username}
                </span>
                <button onClick={onDashboard} style={{
                    padding: '6px 14px', background: 'rgba(124,58,237,0.15)',
                    border: '1px solid rgba(124,58,237,0.35)', borderRadius: 8,
                    color: '#a78bfa', fontSize: 11, fontWeight: 700,
                    fontFamily: 'inherit', cursor: 'pointer', letterSpacing: '0.04em',
                }}>
                    Dashboard
                </button>
                <button onClick={onLogout} style={{
                    padding: '6px 12px', background: 'rgba(255,255,255,0.04)',
                    border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8,
                    color: 'rgba(255,255,255,0.4)', fontSize: 11, fontWeight: 600,
                    fontFamily: 'inherit', cursor: 'pointer',
                }}>
                    Logout
                </button>
            </div>

            <div className={styles.wrap}>
                <Header />
                <ConfigCard serverBase={serverBase} setServerBase={setServerBase} apiKeyOverride={apiKeyOverride} setApiKeyOverride={setApiKeyOverride} />
                <ProductForm
                    productDescription={productDescription} setProductDescription={setProductDescription}
                    productCategory={productCategory} setProductCategory={setProductCategory}
                    targetAudience={targetAudience} setTargetAudience={setTargetAudience}
                    messagingAngle={messagingAngle} setMessagingAngle={setMessagingAngle}
                />
                <ImageUploadCard images={images} setImages={setImages} scrapeEnabled={scrapeEnabled} setScrapeEnabled={setScrapeEnabled} ragEnabled={ragEnabled} setRagEnabled={setRagEnabled} />

                {imageMismatchMsg && (
                    <div className={styles.mismatchBanner}>
                        <div className={styles.mismatchIcon}>(!)</div>
                        <div className={styles.mismatchBody}>
                            <div className={styles.mismatchTitle}>Wrong Image</div>
                            <div className={styles.mismatchMsg}>{imageMismatchMsg}</div>
                            <div className={styles.mismatchHint}>Pipeline stopped. Fix your image and try again.</div>
                        </div>
                        <button className={styles.mismatchClose} onClick={() => setImageMismatchMsg(null)} title="Dismiss">x</button>
                    </div>
                )}

                <PipelineTracker stepStatuses={stepStatuses} />

                <button className="run-btn" onClick={runPipeline} disabled={isRunning} style={{
                    width: '100%', padding: '15px', background: 'var(--accent)',
                    border: 'none', borderRadius: '10px', color: 'white',
                    fontFamily: "'Syne', sans-serif", fontWeight: 800, fontSize: '14px',
                    letterSpacing: '0.05em', cursor: isRunning ? 'not-allowed' : 'pointer',
                    transition: 'all 0.2s', position: 'relative', overflow: 'hidden',
                    opacity: isRunning ? 0.5 : 1,
                }}>
                    {isRunning ? 'Pipeline running...' : 'Run Full Pipeline'}
                </button>

                <LogPanel logs={logs} />

                {result && (
                    <>
                        <div style={{ height: '1px', background: 'var(--border)', margin: '30px 0' }} />
                        <Results result={result} />
                    </>
                )}
            </div>
        </div>
    );
}

// -------------------------------------------------
// App - top-level router
// -------------------------------------------------
function App() {
    const { isAuthenticated, user, token, logout } = useAuth();
    const [view, setView] = useState<'forge' | 'dashboard'>('forge');

    if (!isAuthenticated) {
        return <AuthPage serverBase="http://localhost:8000" />;
    }

    if (view === 'dashboard') {
        return <Dashboard serverBase="http://localhost:8000" onGoToForge={() => setView('forge')} />;
    }

    return <ForgeApp token={token} user={user} onDashboard={() => setView('dashboard')} onLogout={logout} />;
}

export default App;