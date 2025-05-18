// firebase.js
import firebase from 'firebase/compat/app';
import 'firebase/compat/storage';

const firebaseConfig = {
    apiKey: "AIzaSyClMF7VO3rsNZ_vlcC1lpwTUTgIW-_jAKo",
    authDomain: "tesis-v1-database.firebaseapp.com",
    projectId: "tesis-v1-database",
    storageBucket: "tesis-v1-database.firebasestorage.app",
    messagingSenderId: "603286945614",
    appId: "1:603286945614:web:7fdf89fb4d1d32bc79e81f",
    measurementId: "G-X440MMSS9Y"
  };

firebase.initializeApp(firebaseConfig);
const storage = firebase.storage();

export { storage };
