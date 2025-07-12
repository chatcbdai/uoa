// Make sure screen properties show standard values
// Most bot detection checks for rounded values which are common in headless browsers
const overrideScreenProperties = () => {
    try {
        const originalScreen = window.screen;
        Object.defineProperty(window, 'screen', {
            get: function() {
                const screenObj = originalScreen;
                
                // Override screen width and height
                Object.defineProperties(screenObj, {
                    width: { value: 1920, configurable: true, writable: false },
                    height: { value: 1080, configurable: true, writable: false },
                    availWidth: { value: 1920, configurable: true, writable: false },
                    availHeight: { value: 1040, configurable: true, writable: false },
                    availLeft: { value: 0, configurable: true, writable: false },
                    availTop: { value: 40, configurable: true, writable: false },
                    colorDepth: { value: 24, configurable: true, writable: false },
                    pixelDepth: { value: 24, configurable: true, writable: false },
                });
                
                return screenObj;
            },
            configurable: true
        });
    } catch (e) {
        console.error("Failed to override screen properties", e);
    }
};

overrideScreenProperties();