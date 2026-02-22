// Type definitions for AdForge
export interface UploadedImage {
    b64: string;
    mime: string;
    dataUrl: string;
    file?: File;
}

export interface PipelineRequest {
    product_description: string;
    product_category: string;
    target_audience: string | null;
    messaging_angle: string;
    scrape_competitors: boolean;
    use_rag: boolean;
    competitor_images_b64: string[];
    image_mime_types: string[];
}

export interface PipelineResult {
    hook: string;
    caption: string;
    cta: string;
    visual_recommendations: string[];
    user_insights: {
        pain_points: string[];
        questions: string[];
        desired_features: string[];
        use_cases: string[];
    };
    strategy: string;
    [key: string]: any;
}

export interface SSEEvent {
    type: 'step' | 'complete' | 'error' | 'image_mismatch' | 'ping';
    step?: number;
    status?: 'start' | 'done' | 'error' | 'warn';
    message?: string;
    result?: PipelineResult;
    detected?: string;
    product?: string;
}

export type MessagingAngle =
    | 'auto'
    | 'problem-solution'
    | 'luxury'
    | 'ugc'
    | 'fear'
    | 'social-proof'
    | 'discount'
    | 'lifestyle';

export type LogLevel = 'info' | 'success' | 'warn' | 'error';

export interface LogEntry {
    timestamp: string;
    message: string;
    level: LogLevel;
}

export type PipelineStep = 1 | 2 | 3 | 4 | 5 | 6;
export type StepStatus = 'inactive' | 'active' | 'done' | 'error' | 'warn';
