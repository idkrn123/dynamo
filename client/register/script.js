document.getElementById('registerForm').addEventListener('submit', function(event) {
    event.preventDefault();

    var username = document.getElementById('username').value;
    var password = document.getElementById('password').value;
    var recaptcha = grecaptcha.getResponse();

    var data = {
        username: username,
        password: password,
        recaptcha: recaptcha
    };

    fetch('http://voidsociety.com/api/auth/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (!response.ok && response.status === 400) { 
            location.reload(); 
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        alert(data.message);
        if (data.message === 'Registered successfully') {
            window.location.href = "/client/chat";
        }
    })
    .catch((error) => {
        console.error('Error:', error);
    });
});
