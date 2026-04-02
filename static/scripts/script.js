const signupDiv = document.getElementById("signup")
const loginDiv = document.getElementById("login")
const depositDiv = document.getElementById('deposit')
const withdrawDiv = document.getElementById('withdraw')

    function signup() {
        signupDiv.style.display = "block"
        loginDiv.style.display = "none"
    }

    function login() {
        loginDiv.style.display = "block"
        signupDiv.style.display = "none"
    }

    function deposit() {
        depositDiv.style.display = "block"
        withdrawDiv.style.display = "none"
    }

    function withdraw() {
        withdrawDiv.style.display = "block"
        depositDiv.style.display = "none"
    }