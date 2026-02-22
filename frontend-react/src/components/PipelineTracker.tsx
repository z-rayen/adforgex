import React from 'react';
import styles from './PipelineTracker.module.css';
import { StepStatus } from '../types';

interface PipelineTrackerProps {
    stepStatuses: Record<number, StepStatus>;
}

const STEPS = [
    { id: 1, label: 'RAG + Analysis', short: 'S1' },
    { id: 2, label: 'Competitor Intel', short: 'S2' },
    { id: 3, label: 'Image Analysis', short: 'S3' },
    { id: 4, label: 'Sentiment', short: 'S4' },
    { id: 5, label: 'Strategy', short: 'S5' },
    { id: 6, label: 'Ad Generation', short: 'S6' },
];

const STATUS_ICON: Record<StepStatus, string> = {
    inactive: '',
    active: '',
    done: '✓',
    error: '✗',
    warn: '⚠',
};

const PipelineTracker: React.FC<PipelineTrackerProps> = ({ stepStatuses }) => {
    return (
        <div className={styles.tracker}>
            <div className={styles.label}>Pipeline</div>
            <div className={styles.steps}>
                {STEPS.map((step, index) => {
                    const status = stepStatuses[step.id] ?? 'inactive';
                    return (
                        <React.Fragment key={step.id}>
                            <div className={styles.stepCol}>
                                <div className={`${styles.circle} ${styles[status]}`}>
                                    {status === 'active' ? (
                                        <span className={styles.pulse} />
                                    ) : (
                                        <span className={styles.circleInner}>
                                            {STATUS_ICON[status] || step.short}
                                        </span>
                                    )}
                                </div>
                                <div className={`${styles.stepLabel} ${styles[status]}`}>
                                    {step.label}
                                </div>
                            </div>
                            {index < STEPS.length - 1 && (
                                <div className={`${styles.line} ${stepStatuses[step.id] === 'done' ? styles.lineDone :
                                        stepStatuses[step.id] === 'error' ? styles.lineError : ''
                                    }`} />
                            )}
                        </React.Fragment>
                    );
                })}
            </div>
        </div>
    );
};

export default PipelineTracker;
