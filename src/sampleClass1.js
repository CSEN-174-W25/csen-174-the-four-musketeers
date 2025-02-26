class SampleClass1 {
    constructor() {
        this.property = 'initial';
    }

    method1() {
        return `${this.property} processed`;
    }

    method2(input) {
        if (input === 'edge') {
            return 'edge case output';
        }
        return 'unexpected output';
    }

    method3(input) {
        if (input === 'invalid') {
            throw new Error('Invalid input');
        }
    }

    updateProperty(value) {
        this.property = value;
    }

    getProperty() {
        return this.property;
    }
}

module.exports = SampleClass1;
