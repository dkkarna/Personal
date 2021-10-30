'use strict';
window.addEventListener('load', function () {
    document.getElementById('sign-out').onclick = function() {
    firebase.auth().signOut();
};
});
firebase.auth().onAuthStateChanged(function(user) {
    if(user) {
    document.getElementById('sign-out').hidden = false;
    var data = document.getElementsByClassName('hiddendata');
    for(var i=0;i<data.length;i++){
        data[i].hidden=false;
    }
    console.log('Signed in as ${user.displayName} (${user.email})');
    user.getIdToken().then(function(token) {
    document.cookie = "token=" + token + ";path=/";
    });
    } else {
    var ui = new firebaseui.auth.AuthUI(firebase.auth());
    ui.start('#firebase-auth-container', uiConfig);
    document.getElementById('sign-out').hidden = true;
    var data = document.getElementsByClassName('hiddendata');
    for(var i=0;i<data.length;i++){
        data[i].hidden=true;
    }
    document.cookie = "token=;path=/";
    }
    }, function(error) {
    console.log(error);
    alert('Unable to log in: ' + error);
});
var uiConfig = {
    signInSuccessUrl: '/',
    signInOptions: [
        firebase.auth.GoogleAuthProvider.PROVIDER_ID,
        firebase.auth.EmailAuthProvider.PROVIDER_ID
    ]
};
