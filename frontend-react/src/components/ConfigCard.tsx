import React from 'react';
import Card from './Card';
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
    return (
        <Card title="Server & API Config" icon="⚙">
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
                        placeholder="Leave blank to use server's .env key"
                        value={apiKeyOverride}
                        onChange={(e) => setApiKeyOverride(e.target.value)}
                    />
                </div>
            </div>
        </Card>
    );
};

export default ConfigCard;
