class SampleClass4 {
    constructor() {
        this.property = 'default value';
    }

    method1() {
        return `${this.property} processed`;
    }

    method2(input) {
        if (input === '') {
            return 'default output';
        }
        return 'unexpected output';
    }

    method3(input) {
        if (input === null) {
            throw new Error('Invalid input');
        }
        // Ensure the method throws an error for invalid input
        throw new Error('Invalid input');
    }

    updateProperty(value) {
        this.property = value;
    }

    getProperty() {
        return this.property;
    }
}

module.exports = SampleClass4;