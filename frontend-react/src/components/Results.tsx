import React, { useState, useEffect } from 'react';
import styles from './Results.module.css';
import { PipelineResult } from '../types';

interface ResultsProps {
    result: PipelineResult;
}

const Results: React.FC<ResultsProps> = ({ result }) => {
    const [copied, setCopied] = useState<string | null>(null);

    useEffect(() => {
        const el = document.getElementById('results-section');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, []);

    const copy = (text: string, id: string) => {
        navigator.clipboard.writeText(text).then(() => {
            setCopied(id);
            setTimeout(() => setCopied(null), 1800);
        });
    };

    const visIcons = ['🎨', '📌', '✨', '👁️', '🔥'];

    return (
        <div id="results-section" className={styles.results}>

            {/* ── Badge ── */}
            <div className={styles.topRow}>
                <span className={styles.badge}>✓ Generated</span>
                <span className={styles.subBadge}>6 / 6 steps complete</span>
            </div>

            {/* ── Hook — HERO ── */}
            <div className={styles.hookHero}>
                <div className={styles.hookEyebrow}>Hook</div>
                <blockquote className={styles.hookText}>{result.hook}</blockquote>
                <button className={styles.copyBtn} onClick={() => copy(result.hook, 'hook')}>
                    {copied === 'hook' ? '✓ Copied' : '📋 Copy Hook'}
                </button>
            </div>

            {/* ── CTA pill ── */}
            <div className={styles.ctaRow}>
                <span className={styles.ctaEyebrow}>Call to Action</span>
                <div className={styles.ctaPill}>{result.cta}</div>
            </div>

            {/* ── Caption ── */}
            <div className={styles.block}>
                <div className={styles.blockHeader}>
                    <span className={styles.blockTitle}>Caption</span>
                    <button className={styles.copyBtn} onClick={() => copy(result.caption, 'caption')}>
                        {copied === 'caption' ? '✓ Copied' : '📋 Copy'}
                    </button>
                </div>
                <div className={styles.captionBox}>{result.caption}</div>
            </div>

            {/* ── Visual Recs ── */}
            {result.visual_recommendations?.length > 0 && (
                <div className={styles.block}>
                    <div className={styles.blockHeader}>
                        <span className={styles.blockTitle}>Visual Recommendations</span>
                    </div>
                    <div className={styles.visGrid}>
                        {result.visual_recommendations.map((rec, i) => (
                            <div key={i} className={styles.visCard}>
                                <span className={styles.visNum}>{visIcons[i] ?? '•'}</span>
                                <span>{rec}</span>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* ── Strategy ── */}
            {result.strategy && (
                <div className={styles.block}>
                    <div className={styles.blockHeader}>
                        <span className={styles.blockTitle}>Strategy</span>
                    </div>
                    <div className={styles.stratBox}>{result.strategy}</div>
                </div>
            )}

            {/* ── User Insights ── */}
            {result.user_insights && (
                <div className={styles.block}>
                    <div className={styles.blockHeader}>
                        <span className={styles.blockTitle}>User Insights</span>
                    </div>
                    <div className={styles.insightsGrid}>
                        {result.user_insights.pain_points?.length > 0 && (
                            <div className={styles.insGroup}>
                                <div className={styles.insGroupLabel}>💢 Pain Points</div>
                                {result.user_insights.pain_points.map((p, i) => (
                                    <div key={i} className={`${styles.insItem} ${styles.pain}`}>{p}</div>
                                ))}
                            </div>
                        )}
                        {result.user_insights.desired_features?.length > 0 && (
                            <div className={styles.insGroup}>
                                <div className={styles.insGroupLabel}>✅ Desired Features</div>
                                {result.user_insights.desired_features.map((f, i) => (
                                    <div key={i} className={`${styles.insItem} ${styles.feat}`}>{f}</div>
                                ))}
                            </div>
                        )}
                        {result.user_insights.questions?.length > 0 && (
                            <div className={styles.insGroup}>
                                <div className={styles.insGroupLabel}>❓ Questions</div>
                                {result.user_insights.questions.map((q, i) => (
                                    <div key={i} className={`${styles.insItem} ${styles.ques}`}>{q}</div>
                                ))}
                            </div>
                        )}
                        {result.user_insights.use_cases?.length > 0 && (
                            <div className={styles.insGroup}>
                                <div className={styles.insGroupLabel}>🔍 Use Cases</div>
                                {result.user_insights.use_cases.map((u, i) => (
                                    <div key={i} className={`${styles.insItem} ${styles.uc}`}>{u}</div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};

export default Results;
