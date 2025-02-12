class SampleClass2 {
    constructor() {
        this.property = 'default';
    }

    method1() {
        return 'expected value';
    }

    method2(input) {
        if (input === 'edge case input') {
            return 'expected output';
        }
        return 'unexpected output';
    }

    method3(input) {
        if (input === 'invalid input') {
            throw new Error('Invalid input');
        }
    }

    updateProperty(newValue) {
        this.property = newValue;
    }

    getProperty() {
        return this.property;
    }
}

module.exports = SampleClass2;
