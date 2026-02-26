import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
    appId: 'com.dravis.mobile',
    appName: 'DRAVIS',
    webDir: 'dist',
    server: {
        // In production, the app loads from bundled files
        // For dev, you can set this to your desktop's IP running the backend
        // androidScheme: 'https'
    },
    plugins: {
        CapacitorHttp: {
            enabled: true // Allow HTTP requests to local backend
        }
    }
};

export default config;
