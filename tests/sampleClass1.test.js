const SampleClass1 = require('../src/sampleClass1');

describe('SampleClass1', () => {
    let instance;

    beforeEach(() => {
        instance = new SampleClass1();
    });

    test('should initialize instance with initial property value', () => {
        expect(instance).toBeDefined();
        expect(instance.property).toBe('initial');
    });

    test('should return processed value from method1', () => {
        instance.property = 'test';
        expect(instance.method1()).toBe('test processed');
    });

    test('should return edge case output for edge input in method2', () => {
        expect(instance.method2('edge')).toBe('edge case output');
    });

    test('should throw error for invalid input in method3', () => {
        expect(() => instance.method3('invalid')).toThrow('Invalid input');
    });

    test('should update property value correctly', () => {
        instance.updateProperty('new value');
        expect(instance.getProperty()).toBe('new value');
    });
});
