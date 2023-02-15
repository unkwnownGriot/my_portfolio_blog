// For Mobile
const mobile_messages = document.querySelectorAll(".mobile .message_menu")
mobile_messages.forEach((message) => {
    message.addEventListener("click", () => {

        // Display for small screens
        const parent = message.parentElement
        parent.children[1].classList.toggle("remove_display")

        // Save message as viewed
    })
})



// For Desktop
const desktop_messages = document.querySelectorAll(".desktop .message_menu")
desktop_messages.forEach((messageElement) => {

    messageElement.addEventListener("click", () => {
        // Display for larger screens
        const message_name = document.querySelector(".desktop .message_name")
        const message_email = document.getElementById("message_email")
        const message_message = document.querySelector(".desktop .message_message")

        const name = messageElement.querySelector(".name")
        const email = messageElement.querySelector(".email")
        const message = messageElement.querySelector(".message_hidden")

        message_name.innerHTML = `${name.innerHTML}`
        message_email.innerHTML = `(${email.innerHTML})`
        message_message.innerHTML = `${message.innerHTML}`

        // Save message as viewed
    })
})