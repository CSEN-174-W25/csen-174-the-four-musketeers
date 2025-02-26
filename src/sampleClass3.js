class SampleClass3 {
    constructor() {
        this.property = 'initial value';
    }

    method1() {
        return `${this.property} processed`;
    }

    method2(input) {
        if (input === 'special case') {
            return 'special output';
        }
        return 'default output';
    }

    method3(input) {
        if (input === undefined) {
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

module.exports = SampleClass3;