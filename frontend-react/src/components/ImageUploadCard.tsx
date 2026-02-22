import React, { useRef, useState } from 'react';
import Card from './Card';
import styles from './ImageUploadCard.module.css';
import { UploadedImage } from '../types';

interface ImageUploadCardProps {
    images: UploadedImage[];
    setImages: React.Dispatch<React.SetStateAction<UploadedImage[]>>;
    scrapeEnabled: boolean;
    setScrapeEnabled: (value: boolean) => void;
    ragEnabled: boolean;
    setRagEnabled: (value: boolean) => void;
}

const ImageUploadCard: React.FC<ImageUploadCardProps> = ({
    images,
    setImages,
    scrapeEnabled,
    setScrapeEnabled,
    ragEnabled,
    setRagEnabled,
}) => {
    const [isDragging, setIsDragging] = useState(false);
    const inputRef = useRef<HTMLInputElement>(null);

    const handleFiles = (files: File[]) => {
        files
            .filter((f) => f.type.startsWith('image/'))
            .forEach((file) => {
                const reader = new FileReader();
                reader.onload = (e) => {
                    const dataUrl = e.target?.result as string;
                    const b64 = dataUrl.split(',')[1];
                    setImages((prev) => [
                        ...prev,
                        { b64, mime: file.type, dataUrl, file },
                    ]);
                };
                reader.readAsDataURL(file);
            });
    };

    const handleDragOver = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = () => {
        setIsDragging(false);
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
        handleFiles([...e.dataTransfer.files]);
    };

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files) {
            handleFiles([...e.target.files]);
        }
    };

    const removeImage = (index: number) => {
        setImages((prev) => prev.filter((_, i) => i !== index));
    };

    return (
        <Card title="Competitor Images & Scraper Options" icon="2">
            <div
                className={`${styles.uploadArea} ${isDragging ? styles.dragover : ''}`}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                onClick={() => inputRef.current?.click()}
            >
                <input
                    ref={inputRef}
                    type="file"
                    multiple
                    accept="image/*"
                    style={{ display: 'none' }}
                    onChange={handleInputChange}
                />
                <div className={styles.uploadIcon}>📸</div>
                <div className={styles.uploadText}>
                    Drop competitor ad images here or click to browse
                    <br />
                    <small>Analyzed by Llama 4 Scout vision model</small>
                </div>
            </div>

            {images.length > 0 && (
                <div className={styles.previews}>
                    {images.map((img, i) => (
                        <div key={i} className={styles.prevItem}>
                            <img src={img.dataUrl} alt={`Preview ${i + 1}`} />
                            <button className={styles.rmBtn} onClick={(e) => {
                                e.stopPropagation();
                                removeImage(i);
                            }}>
                                ×
                            </button>
                        </div>
                    ))}
                </div>
            )}

            <div className={styles.toggleRow}>
                <div
                    className={`${styles.toggle} ${scrapeEnabled ? styles.on : ''}`}
                    onClick={() => setScrapeEnabled(!scrapeEnabled)}
                >
                    <div className={styles.toggleThumb} />
                </div>
                <span className={styles.toggleLabel}>
                    Enable Playwright web scraper (Google, Amazon, Reddit, Facebook Ads)
                </span>
            </div>

            <div className={styles.toggleRow}>
                <div
                    className={`${styles.toggle} ${ragEnabled ? styles.on : ''}`}
                    onClick={() => setRagEnabled(!ragEnabled)}
                >
                    <div className={styles.toggleThumb} />
                </div>
                <span className={styles.toggleLabel}>Enable RAG knowledge base retrieval</span>
            </div>

            <div className={styles.infoTip}>
                💡 The scraper requires <code>playwright install chromium</code> on the server. If
                disabled, the LLM simulates competitor intelligence.
            </div>
        </Card>
    );
};

export default ImageUploadCard;
