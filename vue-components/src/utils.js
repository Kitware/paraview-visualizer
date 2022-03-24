export function floatToHex2(value) {
  const integer = Math.round(value * 255);
  if (integer > 15) {
    return integer.toString(16);
  }
  return `0${integer.toString(16)}`;
}

const COLOR_EPSILON = 1 / 255;

export function areEquals(a, b) {
  if (a.length !== b.length) {
    return false;
  }

  return (
    Math.abs(a[0] - b[0]) <= COLOR_EPSILON &&
    Math.abs(a[1] - b[1]) <= COLOR_EPSILON &&
    Math.abs(a[2] - b[2]) <= COLOR_EPSILON
  );
}

export function debounce(func, wait = 100) {
  let timeout;
  const debounced = (...args) => {
    const context = this;
    const later = () => {
      timeout = null;
      func.apply(context, args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };

  debounced.cancel = () => clearTimeout(timeout);

  return debounced;
}
