document.getElementById('loginForm').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent the default form submission
    handleLogin();
});

document.getElementById('registerForm').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent the default form submission
    handleRegister();
});

function handleRegister() {
    'use strict';

}

function handleLogin() {
    'use strict';
}



function showRegister() {
    document.getElementById('register').style.display = 'block';
    document.getElementById('login').style.display = 'none';
}
function showLogin() {
    document.getElementById('register').style.display = 'none';
    document.getElementById('login').style.display = 'block';
}