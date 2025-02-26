const SampleClass4 = require('../src/sampleClass4');

describe('SampleClass4', () => {
    let instance;

    beforeEach(() => {
        instance = new SampleClass4();
    });

    test('should initialize instance with default property value', () => {
        expect(instance).toBeDefined();
        expect(instance.property).toBe('default value');
    });

    test('should return processed value from method1', () => {
        instance.property = 'test value';
        expect(instance.method1()).toBe('test value processed');
    });

    test('should return default output for empty input in method2', () => {
        expect(instance.method2('')).toBe('default output');
    });

    test('should throw error for null input in method3', () => {
        expect(() => instance.method3(null)).toThrow('Invalid input');
    });

    test('should update property value correctly', () => {
        instance.updateProperty('updated value');
        expect(instance.getProperty()).toBe('updated value');
    });
});
