// Standardize notification permission behavior
try {
    // Override permissions API
    const originalPermissions = navigator.permissions;
    if (originalPermissions && originalPermissions.query) {
        const originalQuery = originalPermissions.query;
        navigator.permissions.query = (parameters) => {
            return new Promise((resolve, reject) => {
                // For notification permissions specifically
                if (parameters && parameters.name && parameters.name.toLowerCase() === 'notifications') {
                    const result = {
                        // common state for regular browsers
                        state: 'prompt',
                        onchange: null,
                        addEventListener: function() {},
                        removeEventListener: function() {},
                        dispatchEvent: function() {
                            return true;
                        }
                    };
                    resolve(result);
                } else {
                    // Use original for everything else
                    originalQuery.call(navigator.permissions, parameters)
                        .then(resolve)
                        .catch(reject);
                }
            });
        };
    }
} catch (e) {
    console.error("Failed to override notification permissions", e);
}