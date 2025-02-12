const SampleClass3 = require('../src/sampleClass3');

describe('SampleClass3', () => {
    let instance;

    beforeEach(() => {
        instance = new SampleClass3();
    });

    test('should initialize instance with initial property value', () => {
        expect(instance).toBeDefined();
        expect(instance.property).toBe('initial value');
    });

    test('should return processed value from method1', () => {
        instance.property = 'another value';
        expect(instance.method1()).toBe('another value processed');
    });

    test('should return special output for special case input in method2', () => {
        expect(instance.method2('special case')).toBe('special output');
    });

    test('should throw error for undefined input in method3', () => {
        expect(() => instance.method3(undefined)).toThrow('Invalid input');
    });

    test('should update property value correctly', () => {
        instance.updateProperty('new property value');
        expect(instance.getProperty()).toBe('new property value');
    });
});
