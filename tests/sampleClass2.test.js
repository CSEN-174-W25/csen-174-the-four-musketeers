const SampleClass2 = require('../src/sampleClass2');

describe('SampleClass2', () => {
    let instance;

    beforeEach(() => {
        instance = new SampleClass2();
    });

    test('should initialize instance with start property value', () => {
        expect(instance).toBeDefined();
        expect(instance.property).toBe('start value');
    });

    test('should return processed value from method1', () => {
        instance.property = 'value for method1';
        expect(instance.method1()).toBe('value for method1 processed');
    });

    test('should return edge output for edge input in method2', () => {
        expect(instance.method2('edge input')).toBe('edge output');
    });

    test('should throw error for bad input in method3', () => {
        expect(() => instance.method3('bad input')).toThrow('Invalid input');
    });

    test('should update property value correctly', () => {
        instance.updateProperty('changed value');
        expect(instance.getProperty()).toBe('changed value');
    });
});
