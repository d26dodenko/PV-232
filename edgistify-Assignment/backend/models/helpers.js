const toId = (value) => {
  const id = Number(value);
  return Number.isInteger(id) && id > 0 ? id : null;
};

const normalizeImages = (images, fallback) => {
  if (Array.isArray(images)) {
    return images.filter(Boolean);
  }
  if (typeof images === "string" && images) {
    return [images];
  }
  if (typeof fallback === "string" && fallback) {
    return [fallback];
  }
  return [];
};

const parseJsonArray = (value) => {
  try {
    const parsed = JSON.parse(value);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
};

module.exports = { toId, normalizeImages, parseJsonArray };
