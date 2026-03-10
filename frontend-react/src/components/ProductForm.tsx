import React from 'react';
import Card from './Card';
import styles from './ProductForm.module.css';


interface ProductFormProps {
    productDescription: string;
    setProductDescription: (value: string) => void;
    productCategory: string;
    setProductCategory: (value: string) => void;
    targetAudience: string;
    setTargetAudience: (value: string) => void;
    messagingAngle: string;
    setMessagingAngle: (value: string) => void;
}

const ProductForm: React.FC<ProductFormProps> = ({
    productDescription,
    setProductDescription,
    productCategory,
    setProductCategory,
    targetAudience,
    setTargetAudience,
    messagingAngle,
    setMessagingAngle,
}) => {
    return (
        <Card title="Product Information" icon="1">
            <label className={styles.label}>Product Description *</label>
            <textarea
                className={styles.textarea}
                placeholder="e.g. A pocket-sized UV-C water purifier that kills 99.9% of bacteria in 60 seconds..."
                value={productDescription}
                onChange={(e) => setProductDescription(e.target.value)}
            />
            <div className={styles.twoCol} style={{ marginTop: 0 }}>
                <div>
                    <label className={styles.label}>Category *</label>
                    <input
                        type="text"
                        className={styles.input}
                        placeholder="e.g. Travel Gadgets"
                        value={productCategory}
                        onChange={(e) => setProductCategory(e.target.value)}
                    />
                </div>
                <div>
                    <label className={styles.label}>Target Audience</label>
                    <input
                        type="text"
                        className={styles.input}
                        placeholder="e.g. Hikers aged 25-40"
                        value={targetAudience}
                        onChange={(e) => setTargetAudience(e.target.value)}
                    />
                </div>
            </div>
            <label className={styles.label}>Messaging Angle</label>
            <select
                className={styles.select}
                value={messagingAngle}
                onChange={(e) => setMessagingAngle(e.target.value)}
            >
                <option value="auto">🤖 Auto-detect best angle</option>
                <option value="problem-solution">🔧 Problem → Solution</option>
                <option value="luxury">💎 Luxury / Premium</option>
                <option value="ugc">📱 UGC / Authentic</option>
                <option value="fear">⚠️ Fear / Risk Aversion</option>
                <option value="social-proof">⭐ Social Proof</option>
                <option value="discount">💸 Discount / Value</option>
                <option value="lifestyle">🌅 Lifestyle / Aspiration</option>
            </select>
        </Card>
    );
};

export default ProductForm;
