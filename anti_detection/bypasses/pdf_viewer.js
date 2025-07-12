// Add PDF viewer mimetype to prevent detection
if (!navigator.mimeTypes['application/pdf']) {
    // Create a temporary MimeType object
    const fakeMimeType = {
        description: 'Portable Document Format',
        suffixes: 'pdf',
        type: 'application/pdf'
    };
    
    // Create the plugin that contains the MimeType
    const pdfPlugin = Object.create(Plugin.prototype, {
        name: { value: 'PDF Viewer', enumerable: true },
        description: { value: 'Portable Document Format', enumerable: true },
        filename: { value: 'internal-pdf-viewer', enumerable: true }, 
        length: { value: 1, enumerable: true },
        item: { value: function() { return fakeMimeType; }, enumerable: false },
        namedItem: { value: function() { return fakeMimeType; }, enumerable: false },
        0: { value: fakeMimeType, enumerable: true },
    });
    
    // Add the PDF MimeType to navigator.mimeTypes
    Object.defineProperty(navigator.mimeTypes, 'application/pdf', {
        value: fakeMimeType,
        configurable: true,
        enumerable: true,
        writable: false
    });
    
    // Update length property
    Object.defineProperty(navigator.mimeTypes, 'length', {
        value: navigator.mimeTypes.length + 1,
        configurable: true,
        enumerable: false,
        writable: false
    });
}