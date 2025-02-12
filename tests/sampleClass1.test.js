const SampleClass1 = require('../src/sampleClass1');

describe('SampleClass1', () => {
    let instance;

    beforeEach(() => {
        instance = new SampleClass1();
    });

    test('should initialize instance correctly', () => {
        expect(instance).toBeDefined();
    });

    test('should return correct value from method1', () => {
        expect(instance.method1()).toBe('expected value');
    });

    test('should handle edge case input in method2', () => {
        expect(instance.method2('edge case input')).toBe('expected output');
    });

    test('should throw error for invalid input in method3', () => {
        expect(() => instance.method3('invalid input')).toThrow('Invalid input');
    });

    test('should update property value correctly', () => {
        instance.updateProperty('new value');
        expect(instance.getProperty()).toBe('new value');
    });
});
