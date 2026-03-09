import { useState, useEffect, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import styles from './AuthPage.module.css';

interface AuthPageProps {
    serverBase: string;
}

export default function AuthPage({ serverBase }: AuthPageProps) {
    const { login } = useAuth();
    const [mode, setMode] = useState<'login' | 'signup'>('login');
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPw, setConfirmPw] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [showPw, setShowPw] = useState(false);
    const [successMsg, setSuccessMsg] = useState('');
    const canvasRef = useRef<HTMLCanvasElement>(null);

    // ── Particle canvas ──────────────────────────
    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;
        const ctx = canvas.getContext('2d')!;
        let raf: number;

        const resize = () => {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        };
        resize();
        window.addEventListener('resize', resize);

        type Particle = {
            x: number; y: number; r: number;
            vx: number; vy: number;
            alpha: number; color: string;
        };
        const COLORS = ['#7c3aed', '#4f46e5', '#2563eb', '#db2777', '#06b6d4'];
        const particles: Particle[] = Array.from({ length: 90 }, () => ({
            x: Math.random() * window.innerWidth,
            y: Math.random() * window.innerHeight,
            r: Math.random() * 2.5 + 0.5,
            vx: (Math.random() - 0.5) * 0.4,
            vy: (Math.random() - 0.5) * 0.4,
            alpha: Math.random() * 0.6 + 0.1,
            color: COLORS[Math.floor(Math.random() * COLORS.length)],
        }));

        const draw = () => {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            for (const p of particles) {
                p.x += p.vx;
                p.y += p.vy;
                if (p.x < 0) p.x = canvas.width;
                if (p.x > canvas.width) p.x = 0;
                if (p.y < 0) p.y = canvas.height;
                if (p.y > canvas.height) p.y = 0;
                ctx.beginPath();
                ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
                ctx.fillStyle = p.color;
                ctx.globalAlpha = p.alpha;
                ctx.fill();
            }
            // Draw connections
            ctx.globalAlpha = 1;
            for (let i = 0; i < particles.length; i++) {
                for (let j = i + 1; j < particles.length; j++) {
                    const dx = particles[i].x - particles[j].x;
                    const dy = particles[i].y - particles[j].y;
                    const dist = Math.sqrt(dx * dx + dy * dy);
                    if (dist < 120) {
                        ctx.beginPath();
                        ctx.strokeStyle = `rgba(124,58,237,${0.15 * (1 - dist / 120)})`;
                        ctx.lineWidth = 0.5;
                        ctx.moveTo(particles[i].x, particles[i].y);
                        ctx.lineTo(particles[j].x, particles[j].y);
                        ctx.stroke();
                    }
                }
            }
            raf = requestAnimationFrame(draw);
        };
        draw();

        return () => {
            cancelAnimationFrame(raf);
            window.removeEventListener('resize', resize);
        };
    }, []);

    // ── Submit ───────────────────────────────────
    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');

        if (mode === 'signup' && password !== confirmPw) {
            setError("Passwords don't match.");
            return;
        }
        if (mode === 'signup' && username.trim().length < 3) {
            setError('Username too short (min 3 chars).');
            return;
        }

        setLoading(true);
        try {
            const base = serverBase.replace(/\/$/, '');
            const endpoint = mode === 'signup' ? '/api/auth/signup' : '/api/auth/login';
            const body: Record<string, string> = { email, password };
            if (mode === 'signup') body.username = username;

            const res = await fetch(`${base}${endpoint}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body),
            });

            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || 'Something exploded');

            if (mode === 'signup') {
                // Show success and switch to login — don't auto-login
                setSuccessMsg(`Account created for ${data.user.username}! Now log in below.`);
                setMode('login');
                setUsername('');
                setPassword('');
                setConfirmPw('');
                // Keep email pre-filled for convenience
            } else {
                login(data.access_token, data.user);
            }
        } catch (err) {
            setError((err as Error).message);
        } finally {
            setLoading(false);
        }
    };

    const switchMode = () => {
        setMode(m => m === 'login' ? 'signup' : 'login');
        setError('');
        setSuccessMsg('');
        setUsername('');
        setEmail('');
        setPassword('');
        setConfirmPw('');
    };

    return (
        <div className={styles.root}>
            <canvas ref={canvasRef} className={styles.canvas} />

            {/* Background blobs */}
            <div className={styles.blob1} />
            <div className={styles.blob2} />
            <div className={styles.blob3} />

            {/* Logo area */}
            <div className={styles.logoWrap}>
                <div className={styles.logoGlyph}>⚡</div>
                <div className={styles.logoText}>
                    <span className={styles.logoAd}>Ad</span>
                    <span className={styles.logoForge}>Forge</span>
                </div>
                <div className={styles.logoTagline}>AI-Powered Ad Intelligence</div>
            </div>

            {/* Card */}
            <div className={styles.card}>
                {/* Glitch header */}
                <div className={styles.cardHeader}>
                    <h1
                        className={styles.glitchTitle}
                        data-text={mode === 'login' ? 'WELCOME BACK' : 'JOIN THE FORGE'}
                    >
                        {mode === 'login' ? 'WELCOME BACK' : 'JOIN THE FORGE'}
                    </h1>
                    <p className={styles.subtitle}>
                        {mode === 'login'
                            ? 'Your ads are waiting. Log in and let chaos begin.'
                            : 'Create your account. Unleash the machine.'}
                    </p>
                </div>

                {/* Mode toggle pills */}
                <div className={styles.modePills}>
                    <button
                        className={`${styles.pill} ${mode === 'login' ? styles.pillActive : ''}`}
                        onClick={() => switchMode()}
                        type="button"
                    >
                        Login
                    </button>
                    <button
                        className={`${styles.pill} ${mode === 'signup' ? styles.pillActive : ''}`}
                        onClick={() => switchMode()}
                        type="button"
                    >
                        Sign Up
                    </button>
                </div>

                <form onSubmit={handleSubmit} className={styles.form}>
                    {mode === 'signup' && (
                        <div className={styles.field}>
                            <label className={styles.label}>USERNAME</label>
                            <div className={styles.inputWrap}>
                                <span className={styles.inputIcon}>👤</span>
                                <input
                                    className={styles.input}
                                    type="text"
                                    placeholder="your_handle"
                                    value={username}
                                    onChange={e => setUsername(e.target.value)}
                                    required
                                    autoComplete="username"
                                />
                            </div>
                        </div>
                    )}

                    <div className={styles.field}>
                        <label className={styles.label}>EMAIL</label>
                        <div className={styles.inputWrap}>
                            <span className={styles.inputIcon}>✉️</span>
                            <input
                                className={styles.input}
                                type="email"
                                placeholder="you@adforge.ai"
                                value={email}
                                onChange={e => setEmail(e.target.value)}
                                required
                                autoComplete="email"
                            />
                        </div>
                    </div>

                    <div className={styles.field}>
                        <label className={styles.label}>PASSWORD</label>
                        <div className={styles.inputWrap}>
                            <span className={styles.inputIcon}>🔐</span>
                            <input
                                className={styles.input}
                                type={showPw ? 'text' : 'password'}
                                placeholder="••••••••••"
                                value={password}
                                onChange={e => setPassword(e.target.value)}
                                required
                                autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
                            />
                            <button
                                type="button"
                                className={styles.eyeBtn}
                                onClick={() => setShowPw(v => !v)}
                                tabIndex={-1}
                            >
                                {showPw ? '🙈' : '👁'}
                            </button>
                        </div>
                    </div>

                    {mode === 'signup' && (
                        <div className={styles.field}>
                            <label className={styles.label}>CONFIRM PASSWORD</label>
                            <div className={styles.inputWrap}>
                                <span className={styles.inputIcon}>🔑</span>
                                <input
                                    className={styles.input}
                                    type={showPw ? 'text' : 'password'}
                                    placeholder="••••••••••"
                                    value={confirmPw}
                                    onChange={e => setConfirmPw(e.target.value)}
                                    required
                                    autoComplete="new-password"
                                />
                            </div>
                        </div>
                    )}

                    {successMsg && (
                        <div className={styles.successBanner}>
                            <span className={styles.successIcon}>✅</span>
                            <span>{successMsg}</span>
                        </div>
                    )}

                    {error && (
                        <div className={styles.errorBanner}>
                            <span className={styles.errorIcon}>💥</span>
                            <span>{error}</span>
                        </div>
                    )}

                    <button
                        type="submit"
                        className={`${styles.submitBtn} ${loading ? styles.submitLoading : ''}`}
                        disabled={loading}
                    >
                        {loading ? (
                            <span className={styles.spinnerWrap}>
                                <span className={styles.spinner} />
                                {mode === 'login' ? 'Logging in...' : 'Creating account...'}
                            </span>
                        ) : (
                            <span>{mode === 'login' ? '⚡ LAUNCH INTO ADFORGE' : '🚀 CREATE MY ACCOUNT'}</span>
                        )}
                    </button>
                </form>

                <div className={styles.switchRow}>
                    {mode === 'login' ? "Don't have an account?" : 'Already forged an account?'}
                    <button className={styles.switchLink} onClick={switchMode} type="button">
                        {mode === 'login' ? 'Sign up →' : 'Login →'}
                    </button>
                </div>
            </div>

            {/* Footer badges */}
            <div className={styles.badges}>
                <span className={styles.badge}>🔒 JWT Auth</span>
                <span className={styles.badge}>🧠 RAG Engine</span>
                <span className={styles.badge}>⚡ 6-Step Pipeline</span>
                <span className={styles.badge}>📊 History Dashboard</span>
            </div>
        </div>
    );
}
