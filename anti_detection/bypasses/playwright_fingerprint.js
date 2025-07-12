// Fix common Playwright fingerprint issues

// Override user-agent data
try {
    if (navigator.userAgentData) {
        // Override the platform property
        Object.defineProperty(navigator.userAgentData, 'platform', {
            get: () => 'Windows',
            configurable: true
        });
        
        // Override the mobile property
        Object.defineProperty(navigator.userAgentData, 'mobile', {
            get: () => false,
            configurable: true
        });
        
        // Override the brands
        const originalBrands = navigator.userAgentData.brands;
        const updatedBrands = [
            {brand: 'Google Chrome', version: '112'},
            {brand: 'Chromium', version: '112'},
            {brand: 'Not=A?Brand', version: '99'}
        ];
        
        Object.defineProperty(navigator.userAgentData, 'brands', {
            get: () => updatedBrands,
            configurable: true
        });
        
        // Override the getHighEntropyValues method
        const originalGetHighEntropyValues = navigator.userAgentData.getHighEntropyValues;
        navigator.userAgentData.getHighEntropyValues = function(keys) {
            return new Promise((resolve) => {
                const values = {};
                if (keys.includes('platform')) values.platform = 'Windows';
                if (keys.includes('platformVersion')) values.platformVersion = '10.0.0';
                if (keys.includes('architecture')) values.architecture = 'x86';
                if (keys.includes('model')) values.model = '';
                if (keys.includes('uaFullVersion')) values.uaFullVersion = '112.0.5615.138';
                if (keys.includes('bitness')) values.bitness = '64';
                if (keys.includes('fullVersionList')) {
                    values.fullVersionList = [
                        {brand: 'Google Chrome', version: '112.0.5615.138'},
                        {brand: 'Chromium', version: '112.0.5615.138'},
                        {brand: 'Not=A?Brand', version: '99.0.0.0'}
                    ];
                }
                if (keys.includes('wow64')) values.wow64 = false;
                resolve(values);
            });
        };
    }
} catch (e) {
    console.error('Failed to modify navigator.userAgentData', e);
}

// Fix webdriver flag
if ('webdriver' in navigator) {
    Object.defineProperty(navigator, 'webdriver', {
        get: () => false,
        configurable: true
    });
}

// Fix languages
if (navigator.languages && navigator.languages.length === 0) {
    Object.defineProperty(navigator, 'languages', {
        get: () => ['en-US', 'en'],
        configurable: true
    });
}

// Fix hardwareConcurrency to appear as normal device
if (navigator.hardwareConcurrency === 1) {
    Object.defineProperty(navigator, 'hardwareConcurrency', {
        get: () => 8,
        configurable: true
    });
}

// Fix deviceMemory to appear as normal device
if (navigator.deviceMemory === undefined || navigator.deviceMemory < 2) {
    Object.defineProperty(navigator, 'deviceMemory', {
        get: () => 8,
        configurable: true
    });
}