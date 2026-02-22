import React, { useState } from 'react';
import styles from './ConfigCard.module.css';

interface ConfigCardProps {
    serverBase: string;
    setServerBase: (value: string) => void;
    apiKeyOverride: string;
    setApiKeyOverride: (value: string) => void;
}

const ConfigCard: React.FC<ConfigCardProps> = ({
    serverBase,
    setServerBase,
    apiKeyOverride,
    setApiKeyOverride,
}) => {
    const [isOpen, setIsOpen] = useState(false);

    return (
        <div className={styles.wrapper}>
            <button className={styles.toggle} onClick={() => setIsOpen(p => !p)}>
                <span className={styles.toggleLeft}>
                    <span className={styles.toggleIcon}>⚙️</span>
                    <span className={styles.toggleLabel}>Server & API Config</span>
                </span>
                <span className={`${styles.chevron} ${isOpen ? styles.chevronOpen : ''}`}>›</span>
            </button>
            {isOpen && (
                <div className={styles.panel}>
                    <div className={styles.twoCol}>
                        <div>
                            <label className={styles.label}>Backend URL</label>
                            <input
                                type="text"
                                className={styles.input}
                                value={serverBase}
                                onChange={(e) => setServerBase(e.target.value)}
                            />
                        </div>
                        <div>
                            <label className={styles.label}>Groq API Key (optional override)</label>
                            <input
                                type="password"
                                className={styles.input}
                                placeholder="Leave blank to use server .env key"
                                value={apiKeyOverride}
                                onChange={(e) => setApiKeyOverride(e.target.value)}
                            />
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default ConfigCard;
