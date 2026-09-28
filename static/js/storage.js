(function (window) {
  'use strict';

  window.SamvidhanStorage = {
    read: function (key, fallback) {
      try {
        const value = window.localStorage.getItem(key);
        return value === null ? fallback : JSON.parse(value);
      } catch (error) {
        return fallback;
      }
    },
    write: function (key, value) {
      window.localStorage.setItem(key, JSON.stringify(value));
    },
    remove: function (key) {
      window.localStorage.removeItem(key);
    }
  };
}(window));