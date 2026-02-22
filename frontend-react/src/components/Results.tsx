import React, { useState, useEffect } from 'react';
import styles from './Results.module.css';
import { PipelineResult } from '../types';

interface ResultsProps {
    result: PipelineResult;
}

const Results: React.FC<ResultsProps> = ({ result }) => {
    const [copied, setCopied] = useState<string | null>(null);

    useEffect(() => {
        // Scroll to results on mount
        const element = document.getElementById('results-section');
        if (element) {
            element.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }, []);

    const copyToClipboard = (text: string, id: string) => {
        navigator.clipboard.writeText(text).then(() => {
            setCopied(id);
            setTimeout(() => setCopied(null), 1500);
        });
    };

    const icons = ['🎨', '📐', '💡', '👤', '✨'];

    return (
        <div id="results-section" className={styles.results}>
            <div className={styles.resultsHeader}>
                <div className={styles.badge}>✓ Complete</div>
                <h2 className={styles.title}>Your Ad Package</h2>
            </div>

            {/* Hook */}
            <div className={styles.rb}>
                <div className={styles.rh}>
                    Hook
                    <button
                        className={styles.cp}
                        onClick={() => copyToClipboard(result.hook, 'hook')}
                    >
                        {copied === 'hook' ? '✓' : 'Copy'}
                    </button>
                </div>
                <div className={styles.rbody}>
                    <div className={styles.hookTxt}>{result.hook}</div>
                </div>
            </div>

            {/* Caption */}
            <div className={styles.rb}>
                <div className={styles.rh}>
                    Caption
                    <button
                        className={styles.cp}
                        onClick={() => copyToClipboard(result.caption, 'caption')}
                    >
                        {copied === 'caption' ? '✓' : 'Copy'}
                    </button>
                </div>
                <div className={styles.rbody}>
                    <div className={styles.capTxt}>{result.caption}</div>
                </div>
            </div>

            {/* CTA */}
            <div className={styles.rb}>
                <div className={styles.rh}>Call-to-Action</div>
                <div className={styles.rbody}>
                    <div className={styles.ctaChip}>{result.cta}</div>
                </div>
            </div>

            {/* Visual Recommendations */}
            <div className={styles.rb}>
                <div className={styles.rh}>Visual Recommendations</div>
                <div className={styles.rbody}>
                    {result.visual_recommendations?.map((rec, i) => (
                        <div key={i} className={styles.visItem}>
                            <span>{icons[i] || '•'}</span>
                            <span>{rec}</span>
                        </div>
                    ))}
                </div>
            </div>

            {/* User Insights */}
            <div className={styles.rb}>
                <div className={styles.rh}>User Insights</div>
                <div className={styles.rbody}>
                    {result.user_insights?.pain_points && result.user_insights.pain_points.length > 0 && (
                        <div className={styles.insSection}>
                            <div className={styles.insLabel}>Pain Points</div>
                            <div className={styles.tagList}>
                                {result.user_insights.pain_points.map((p, i) => (
                                    <span key={i} className={`${styles.tag} ${styles.pain}`}>
                                        😤 {p}
                                    </span>
                                ))}
                            </div>
                        </div>
                    )}

                    {result.user_insights?.questions && result.user_insights.questions.length > 0 && (
                        <div className={styles.insSection}>
                            <div className={styles.insLabel}>Common Questions</div>
                            <div className={styles.tagList}>
                                {result.user_insights.questions.map((q, i) => (
                                    <span key={i} className={styles.tag}>
                                        ❓ {q}
                                    </span>
                                ))}
                            </div>
                        </div>
                    )}

                    {result.user_insights?.desired_features &&
                        result.user_insights.desired_features.length > 0 && (
                            <div className={styles.insSection}>
                                <div className={styles.insLabel}>Desired Features</div>
                                <div className={styles.tagList}>
                                    {result.user_insights.desired_features.map((f, i) => (
                                        <span key={i} className={`${styles.tag} ${styles.feat}`}>
                                            ✅ {f}
                                        </span>
                                    ))}
                                </div>
                            </div>
                        )}

                    {result.user_insights?.use_cases && result.user_insights.use_cases.length > 0 && (
                        <div className={styles.insSection}>
                            <div className={styles.insLabel}>Alternative Use Cases</div>
                            <div className={styles.tagList}>
                                {result.user_insights.use_cases.map((u, i) => (
                                    <span key={i} className={`${styles.tag} ${styles.uc}`}>
                                        🔍 {u}
                                    </span>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            </div>

            {/* Strategy */}
            <div className={styles.rb}>
                <div className={styles.rh}>Strategy</div>
                <div className={styles.rbody}>
                    <div className={styles.stratBox}>{result.strategy}</div>
                </div>
            </div>

            {/* Raw JSON */}
            <div className={styles.rb}>
                <div className={styles.rh}>
                    Raw JSON
                    <button
                        className={styles.cp}
                        onClick={() => copyToClipboard(JSON.stringify(result, null, 2), 'json')}
                    >
                        {copied === 'json' ? '✓' : 'Copy JSON'}
                    </button>
                </div>
                <div className={styles.rbody} style={{ padding: 0 }}>
                    <div className={styles.jsonOut}>{JSON.stringify(result, null, 2)}</div>
                </div>
            </div>
        </div>
    );
};

export default Results;
