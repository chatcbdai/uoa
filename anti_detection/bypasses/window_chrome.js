// Add a chrome object to window if missing (Headless detection)
if (!window.chrome) {
    window.chrome = {
        runtime: {},
        loadTimes: function() {},
        csi: function() {},
        app: {
            isInstalled: false,
        },
        webstore: {
            onInstallStageChanged: {},
            onDownloadProgress: {},
        },
    };
    
    // Make toString return the native code string
    const originalToString = window.chrome.toString;
    window.chrome.runtime.toString = function() {
        return '[object Object]';
    };
    
    // Add chrome properties
    try {
        window.chrome.runtime = {
            connect: function() {},
            id: null,
            onConnect: {
                addListener: function() {},
                hasListener: function() {},
                removeListener: function() {},
            },
            onMessage: {
                addListener: function() {},
                hasListener: function() {},
                removeListener: function() {},
            },
            sendMessage: function() {},
            getManifest: function() {
                return {
                    manifest_version: 3,
                    name: 'Chrome',
                    version: '112.0.0.0',
                };
            },
        };
    } catch (e) {}
}