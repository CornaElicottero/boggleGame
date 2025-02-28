import CryptoJS from 'crypto-js';

const ENCRYPTION_KEY = process.env.REACT_APP_ENCRYPTION_KEY;

export const setItem = (key, value) => {
    console.log(ENCRYPTION_KEY)
    const encryptedValue = CryptoJS.AES.encrypt(JSON.stringify(value), ENCRYPTION_KEY).toString();
    localStorage.setItem(key, encryptedValue);
};

export const getItem = (key) => {
    const encryptedValue = localStorage.getItem(key);
    if (encryptedValue) {
        const decryptedBytes = CryptoJS.AES.decrypt(encryptedValue, ENCRYPTION_KEY);
        const decryptedValue = decryptedBytes.toString(CryptoJS.enc.Utf8);
        return JSON.parse(decryptedValue);
    }
    return null;
};
