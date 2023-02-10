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


// Save Message Function
function save_message(){
    const name = document.getElementById("name")
    const email = document.getElementById("email")
    const message = document.getElementById("message")

    const form = new FormData()
    form.append("csrf_token", csrf_token.value)
    form.append("name", name.value)
    form.append("email", email.value)
    form.append("message", message.value)

    const xhr = new XMLHttpRequest()
    xhr.open("POST","/save_message",true)
    xhr.send(form)
    xhr.onload = () => {
        const data = JSON.parse(xhr.responseText)
        const message = data["message"]
        const status = data["status"]

        flash_response(message,status)
    }
}


// Save Message Button
const btn = document.querySelector(".contact_btn")
btn.addEventListener("click",(e) => {
    e.preventDefault()
    save_message()
})