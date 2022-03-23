export const FALLBACK_CONVERT = (v) => v;

export const TYPES = {
  uint8: {
    convert(value) {
      const n = Number(value);
      if (Number.isFinite(n)) {
        if (n < 0) {
          return 0;
        }
        if (n > 255) {
          return 255;
        }
        return Math.round(n);
      }
      return null;
    },
    rule(value) {
      const n = Number(value);
      if (!Number.isFinite(n)) {
        return 'Provided value is not a valid number';
      }
      if (!Number.isInteger(n)) {
        return 'Provided number is not an integer';
      }
      if (n < 0 || n > 255) {
        return 'Provided number is outside of the range [0, 255]';
      }
      return true;
    },
  },
  uint16: {
    convert(value) {
      const n = Number(value);
      if (Number.isFinite(n)) {
        if (n < 0) {
          return 0;
        }
        if (n > 65535) {
          return 65535;
        }
        return Math.round(n);
      }
      return null;
    },
    rule(value) {
      const n = Number(value);
      if (!Number.isFinite(n)) {
        return 'Provided value is not a valid number';
      }
      if (!Number.isInteger(n)) {
        return 'Provided number is not an integer';
      }
      if (n < 0 || n > 65535) {
        return 'Provided number is outside of the range [0, 65535]';
      }
      return true;
    },
  },
  uint32: {
    convert(value) {
      const n = Number(value);
      if (Number.isFinite(n)) {
        if (n < 0) {
          return 0;
        }
        if (n > 4294967295) {
          return 4294967295;
        }
        return Math.round(n);
      }
      return null;
    },
    rule(value) {
      const n = Number(value);
      if (!Number.isFinite(n)) {
        return 'Provided value is not a valid number';
      }
      if (!Number.isInteger(n)) {
        return 'Provided number is not an integer';
      }
      if (n < 0 || n > 4294967295) {
        return 'Provided number is outside of the range [0, 4294967295]';
      }
      return true;
    },
  },
  uint64: {
    convert(value) {
      const n = Number(value);
      if (Number.isFinite(n)) {
        if (n < 0) {
          return 0;
        }
        return Math.round(n);
      }
      return null;
    },
    rule(value) {
      const n = Number(value);
      if (!Number.isFinite(n)) {
        return 'Provided value is not a valid number';
      }
      if (!Number.isInteger(n)) {
        return 'Provided number is not an integer';
      }
      if (n < 0) {
        return 'Provided number is outside of the range [0, inf]';
      }
      return true;
    },
  },
  int8: {
    convert(value) {
      const n = Number(value);
      if (Number.isFinite(n)) {
        if (n < -128) {
          return -128;
        }
        if (n > 127) {
          return 127;
        }
        return Math.round(n);
      }
      return null;
    },
    rule(value) {
      const n = Number(value);
      if (!Number.isFinite(n)) {
        return 'Provided value is not a valid number';
      }
      if (!Number.isInteger(n)) {
        return 'Provided number is not an integer';
      }
      if (n < -128 || n > 127) {
        return 'Provided number is outside of the range [-128, 127]';
      }
      return true;
    },
  },
  int16: {
    convert(value) {
      const n = Number(value);
      if (Number.isFinite(n)) {
        if (n < -32768) {
          return -32768;
        }
        if (n > 32767) {
          return 32767;
        }
        return Math.round(n);
      }
      return null;
    },
    rule(value) {
      const n = Number(value);
      if (!Number.isFinite(n)) {
        return 'Provided value is not a valid number';
      }
      if (!Number.isInteger(n)) {
        return 'Provided number is not an integer';
      }
      if (n < -32768 || n > 32767) {
        return 'Provided number is outside of the range [-32768, 32767]';
      }
      return true;
    },
  },
  int32: {
    convert(value) {
      const n = Number(value);
      if (Number.isFinite(n)) {
        if (n < -2147483648) {
          return -2147483648;
        }
        if (n > 2147483647) {
          return 2147483647;
        }
        return Math.round(n);
      }
      return null;
    },
    rule(value) {
      const n = Number(value);
      if (!Number.isFinite(n)) {
        return 'Provided value is not a valid number';
      }
      if (!Number.isInteger(n)) {
        return 'Provided number is not an integer';
      }
      if (n < -2147483648 || n > 2147483647) {
        return 'Provided number is outside of the range [-2147483648, 2147483647]';
      }
      return true;
    },
  },
  int64: {
    convert(value) {
      const n = Number(value);
      if (Number.isFinite(n)) {
        return Math.round(n);
      }
      return null;
    },
    rule(value) {
      const n = Number(value);
      if (!Number.isFinite(n)) {
        return 'Provided value is not a valid number';
      }
      if (!Number.isInteger(n)) {
        return 'Provided number is not an integer';
      }
      return true;
    },
  },
  float32: {
    convert(value) {
      const n = Number(value);
      if (Number.isNaN(n)) {
        return null;
      }
      return n;
    },
    rule(value) {
      const n = Number(value);
      if (Number.isNaN(n)) {
        return 'Provided value is not a number';
      }
      return true;
    },
  },
  float64: {
    convert(value) {
      const n = Number(value);
      if (Number.isNaN(n)) {
        return null;
      }
      return n;
    },
    rule(value) {
      const n = Number(value);
      if (Number.isNaN(n)) {
        return 'Provided value is not a number';
      }
      return true;
    },
  },
  string: {
    convert(value) {
      return `${value}`;
    },
    rule() {
      return true;
    },
  },
  bool: {
    convert(value) {
      return !!value;
    },
    rule() {
      return true;
    },
  },
};
