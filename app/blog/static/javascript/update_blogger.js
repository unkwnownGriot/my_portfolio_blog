// Flash query response function
function flash_response(message, status){
    // Flash response
    const flashed = document.getElementById("flashes")
    let flash = `<li>
        <div class="alert alert-${status}">
            ${message}
            <input type="button" class="alert-cancel dismiss" id="alert-cancel" value="X">
        </div>
    </li>
    `
    flashed.innerHTML = flash

    const buttons = document.getElementsByClassName("dismiss")

    for (let i=0; i < buttons.length; i++){
        let button = buttons[i]

        button.addEventListener("click",() => {
            button.parentElement.style.display = "none"
        })
    }
}

// Form Navigator
const nav_buttons = document.querySelectorAll(".form_nav")
const password_form = document.querySelector(".password_form")
const email_form = document.querySelector(".email_form")
const name_form = document.querySelector(".name_form")

nav_buttons.forEach((nav_button) => {
    nav_button.addEventListener("click", () => {
        nav_buttons.forEach((_button) => {
            _button.classList.remove("viewing")
        })
        nav_button.classList.add("viewing")
        if (nav_button.innerText.toLowerCase() == "edit name"){
            name_form.classList.remove("remove_display")
            email_form.classList.add("remove_display")
            password_form.classList.add("remove_display")
        }

        else if (nav_button.innerText.toLowerCase() == "change email"){
            name_form.classList.add("remove_display")
            email_form.classList.remove("remove_display")
            password_form.classList.add("remove_display")
        }

        else if (nav_button.innerText.toLowerCase() == "update password"){
            name_form.classList.add("remove_display")
            email_form.classList.add("remove_display")
            password_form.classList.remove("remove_display")
        }
    })
})


// Update Blogger Name
const name_update_button = document.getElementById("name_button")

name_update_button.addEventListener("click",(e) => {
    e.preventDefault()
    const first_name = document.getElementById("fname").value
    const last_name = document.getElementById("lname").value
    const blogger_id = document.querySelector(".blogger_id").innerText

    if (first_name == ""){
        flash_response("First name cannot be empty","warning")
        return
    }

    else if (last_name == ""){
        flash_response("Last name cannot be empty","warning")
        return
    }

    const form = new FormData()

    form.append("csrf_token",csrf_token.value)
    form.append('id',blogger_id)
    form.append("first_name",first_name)
    form.append("last_name",last_name)

    let xhr = new XMLHttpRequest()
    xhr.open("POST","/blog/update_blogger_name",true)
    xhr.send(form)

    xhr.onload = () => {
        const data = JSON.parse(xhr.responseText)
        const message = data["message"].toLowerCase()
        const status = data["status"].toLowerCase()

        // Show response
        flash_response(message,status)
    }
})

// Update Blogger Email
const email_update_button = document.getElementById("email_button")

email_update_button.addEventListener("click", (e) => {
    e.preventDefault()

    const previous_email = document.getElementById("previousEmail").value
    const new_email = document.getElementById("newEmail").value
    const blogger_id = document.querySelector(".blogger_id").innerText

    if (previous_email == ""){
        flash_response("Previous email cannot be empty","warning")
        return
    }

    if (new_email == ""){
        flash_response("New email cannot be empty","warning")
        return
    }

    const form = new FormData()

    form.append("csrf_token",csrf_token.value)
    form.append("previous_mail",previous_email)
    form.append("new_mail",new_email)
    form.append("id",blogger_id)

    let xhr = new XMLHttpRequest()
    xhr.open("POST", "/blog/update_blogger_email", true)
    xhr.send(form)

    xhr.onload = () => {
        const data = JSON.parse(xhr.responseText)
        const message = data["message"].toLowerCase()
        const status = data["status"].toLowerCase()

        // Show response
        flash_response(message,status)
    }
})