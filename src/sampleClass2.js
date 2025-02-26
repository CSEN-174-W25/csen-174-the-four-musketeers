class SampleClass2 {
    constructor() {
        this.property = 'start value';
    }

    method1() {
        return `${this.property} processed`;
    }

    method2(input) {
        if (input === 'edge input') {
            return 'edge output';
        }
        return 'unexpected output';
    }

    method3(input) {
        if (input === 'bad input') {
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

module.exports = SampleClass2;
