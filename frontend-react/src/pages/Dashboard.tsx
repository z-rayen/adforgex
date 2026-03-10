import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import { HistoryItem } from '../types';
import styles from './Dashboard.module.css';

interface DashboardProps {
    serverBase: string;
    onGoToForge: () => void;
}

export default function Dashboard({ serverBase, onGoToForge }: DashboardProps) {
    const { user, token, logout } = useAuth();
    const [history, setHistory] = useState<HistoryItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [expanded, setExpanded] = useState<number | null>(null);
    const [deleting, setDeleting] = useState<number | null>(null);
    const [stats, setStats] = useState({ total: 0 });

    const fetchHistory = useCallback(async () => {
        setLoading(true);
        try {
            const base = serverBase.replace(/\/$/, '');
            const res = await fetch(`${base}/api/auth/history?limit=50`, {
                headers: { Authorization: `Bearer ${token}` },
            });
            if (!res.ok) throw new Error('Failed to load history');
            const data: HistoryItem[] = await res.json();
            setHistory(data);
            setStats({ total: data.length });
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    }, [serverBase, token]);

    useEffect(() => {
        fetchHistory();
    }, [fetchHistory]);

    const deleteItem = async (id: number) => {
        setDeleting(id);
        try {
            const base = serverBase.replace(/\/$/, '');
            await fetch(`${base}/api/auth/history/${id}`, {
                method: 'DELETE',
                headers: { Authorization: `Bearer ${token}` },
            });
            setHistory(h => h.filter(x => x.id !== id));
            if (expanded === id) setExpanded(null);
        } catch (err) {
            console.error(err);
        } finally {
            setDeleting(null);
        }
    };

    const formatDate = (iso: string) => {
        const d = new Date(iso);
        return d.toLocaleString('en', {
            month: 'short', day: 'numeric',
            hour: '2-digit', minute: '2-digit',
        });
    };

    const angleEmoji: Record<string, string> = {
        auto: '🤖', 'problem-solution': '🛠', luxury: '💎',
        ugc: '📱', fear: '⚠️', 'social-proof': '👥',
        discount: '💸', lifestyle: '🌴',
    };

    // Compute category stats
    const categoryCount: Record<string, number> = {};
    history.forEach(h => {
        categoryCount[h.product_category] = (categoryCount[h.product_category] || 0) + 1;
    });
    const topCategories = Object.entries(categoryCount)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5);

    const avatarInitial = user?.username?.[0]?.toUpperCase() ?? '?';

    return (
        <div className={styles.root}>
            {/* Background */}
            <div className={styles.bg} />
            <div className={styles.bgGrid} />

            {/* Top nav */}
            <nav className={styles.nav}>
                <div className={styles.navLogo}>
                    <span className={styles.navGlyph}>⚡</span>
                    <span className={styles.navBrand}>
                        <span>Ad</span><span className={styles.navBrandForge}>Forge</span>
                    </span>
                </div>
                <div className={styles.navRight}>
                    <button className={styles.forgeBtn} onClick={onGoToForge}>
                        ⚡ Go to Forge
                    </button>
                    <div className={styles.avatarWrap}>
                        <div
                            className={styles.avatar}
                            style={{ background: user?.avatar_color || '#7c3aed' }}
                        >
                            {avatarInitial}
                        </div>
                        <div className={styles.avatarInfo}>
                            <span className={styles.avatarName}>{user?.username}</span>
                            <span className={styles.avatarEmail}>{user?.email}</span>
                        </div>
                    </div>
                    <button className={styles.logoutBtn} onClick={logout} title="Logout">
                        🚪 Logout
                    </button>
                </div>
            </nav>

            {/* Hero stats */}
            <div className={styles.heroStats}>
                <div className={styles.heroCard}>
                    <div className={styles.heroNum}>{stats.total}</div>
                    <div className={styles.heroLabel}>Total Predictions</div>
                    <div className={styles.heroGlow} style={{ background: '#7c3aed' }} />
                </div>
                <div className={styles.heroCard}>
                    <div className={styles.heroNum}>{topCategories.length}</div>
                    <div className={styles.heroLabel}>Categories Used</div>
                    <div className={styles.heroGlow} style={{ background: '#db2777' }} />
                </div>
                <div className={styles.heroCard}>
                    <div className={styles.heroNum}>
                        {history.reduce((s, h) => s + (h.rag_patterns || 0), 0)}
                    </div>
                    <div className={styles.heroLabel}>RAG Patterns Found</div>
                    <div className={styles.heroGlow} style={{ background: '#0891b2' }} />
                </div>
                <div className={styles.heroCard}>
                    <div className={styles.heroNum}>
                        {history.reduce((s, h) => s + (h.scraper_results || 0), 0)}
                    </div>
                    <div className={styles.heroLabel}>Competitor Scrapes</div>
                    <div className={styles.heroGlow} style={{ background: '#16a34a' }} />
                </div>
            </div>

            {/* Category bar chart */}
            {topCategories.length > 0 && (
                <div className={styles.section}>
                    <h2 className={styles.sectionTitle}>📊 Top Categories</h2>
                    <div className={styles.barChart}>
                        {topCategories.map(([cat, count]) => (
                            <div key={cat} className={styles.barRow}>
                                <span className={styles.barLabel}>{cat}</span>
                                <div className={styles.barTrack}>
                                    <div
                                        className={styles.barFill}
                                        style={{ width: `${(count / stats.total) * 100}%` }}
                                    />
                                </div>
                                <span className={styles.barCount}>{count}</span>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* History list */}
            <div className={styles.section}>
                <div className={styles.sectionHeader}>
                    <h2 className={styles.sectionTitle}>🕐 Prediction History</h2>
                    <span className={styles.historyCount}>{history.length} entries</span>
                </div>

                {loading && (
                    <div className={styles.loadingWrap}>
                        <div className={styles.loadingSpinner} />
                        <span>Loading history...</span>
                    </div>
                )}

                {!loading && history.length === 0 && (
                    <div className={styles.emptyState}>
                        <div className={styles.emptyGlyph}>🧪</div>
                        <h3>No predictions yet</h3>
                        <p>Run your first pipeline and watch history populate!</p>
                        <button className={styles.forgeBtn} onClick={onGoToForge}>
                            ⚡ Start Forging
                        </button>
                    </div>
                )}

                <div className={styles.historyList}>
                    {history.map(item => (
                        <div
                            key={item.id}
                            className={`${styles.historyCard} ${expanded === item.id ? styles.historyCardOpen : ''}`}
                        >
                            {/* Card header */}
                            <div
                                className={styles.historyCardHeader}
                                onClick={() => setExpanded(v => v === item.id ? null : item.id)}
                            >
                                <div className={styles.historyMeta}>
                                    <span className={styles.angleChip}>
                                        {angleEmoji[item.messaging_angle] || '📢'} {item.messaging_angle}
                                    </span>
                                    <span className={styles.categoryChip}>{item.product_category}</span>
                                </div>
                                <div className={styles.historyDesc}>
                                    {item.product_description.length > 80
                                        ? item.product_description.slice(0, 80) + '…'
                                        : item.product_description}
                                </div>
                                <div className={styles.historyFooter}>
                                    <span className={styles.historyDate}>{formatDate(item.created_at)}</span>
                                    <div className={styles.historyBadges}>
                                        {item.rag_patterns > 0 && (
                                            <span className={styles.miniBadge}>🧠 {item.rag_patterns} RAG</span>
                                        )}
                                        {item.scraper_results > 0 && (
                                            <span className={styles.miniBadge}>🕷 {item.scraper_results} scraped</span>
                                        )}
                                    </div>
                                    <span className={styles.expandIcon}>
                                        {expanded === item.id ? '▲' : '▼'}
                                    </span>
                                </div>
                            </div>

                            {/* Expanded result */}
                            {expanded === item.id && (
                                <div className={styles.historyExpanded}>
                                    <div className={styles.resultGrid}>
                                        <div className={styles.resultBlock}>
                                            <label>🎣 Hook</label>
                                            <p>{item.result.hook}</p>
                                        </div>
                                        <div className={styles.resultBlock}>
                                            <label>📣 CTA</label>
                                            <p>{item.result.cta}</p>
                                        </div>
                                        <div className={`${styles.resultBlock} ${styles.resultBlockFull}`}>
                                            <label>📝 Caption</label>
                                            <p>{item.result.caption}</p>
                                        </div>
                                        <div className={`${styles.resultBlock} ${styles.resultBlockFull}`}>
                                            <label>🧠 Strategy</label>
                                            <p>{item.result.strategy}</p>
                                        </div>
                                        {item.result.visual_recommendations?.length > 0 && (
                                            <div className={`${styles.resultBlock} ${styles.resultBlockFull}`}>
                                                <label>🎨 Visual Recommendations</label>
                                                <ul className={styles.resultList}>
                                                    {item.result.visual_recommendations.map((v, i) => (
                                                        <li key={i}>{v}</li>
                                                    ))}
                                                </ul>
                                            </div>
                                        )}
                                        {item.result.user_insights?.pain_points?.length > 0 && (
                                            <div className={`${styles.resultBlock} ${styles.resultBlockFull}`}>
                                                <label>😤 Pain Points</label>
                                                <ul className={styles.resultList}>
                                                    {item.result.user_insights.pain_points.map((v, i) => (
                                                        <li key={i}>{v}</li>
                                                    ))}
                                                </ul>
                                            </div>
                                        )}
                                    </div>
                                    <div className={styles.expandedActions}>
                                        <button
                                            className={styles.deleteBtn}
                                            onClick={() => deleteItem(item.id)}
                                            disabled={deleting === item.id}
                                        >
                                            {deleting === item.id ? '⏳ Deleting...' : '🗑 Delete'}
                                        </button>
                                    </div>
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
