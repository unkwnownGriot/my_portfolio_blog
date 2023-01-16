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


// Select Select Section On Display
function form_display(){
    let forms = document.getElementsByTagName("form")
    for (const form of forms){
        form.classList.add("remove_display")
    }

    const section_two = document.getElementsByClassName("section_two")
    for (const elem_child of section_two[0].children){
        elem_child.classList.add("remove_display")
    }

    // Education Records
    const education_records = document.querySelector(".education_record")
    education_records.classList.add("remove_display")

    // Companies Records
    const available_companies = document.getElementById("companies")
    available_companies.classList.add("remove_display")
}

form_display()
const welcome = document.querySelectorAll(".welcome_content")
welcome.forEach((welcome_element) => {
    welcome_element.classList.remove("remove_display")
})

const section_name = document.getElementById("section_name")
section_name.addEventListener("change", () =>{
    form_display()
    const elements_in_view = document.querySelectorAll(`.${section_name.value}`)
    elements_in_view.forEach((element_in_view) => {
        element_in_view.classList.toggle("remove_display")
    })
})


// Resume Introduction Preview
const welcome_textarea = document.getElementById("welcome_textarea")
const preview_content_text = document.querySelector(".hero_content")
const welcome_save_btn = document.querySelector(".welcome_save_btn")

// Display Content In Preview Section
function preview_content(preview_content,welcome_textarea){
    preview_content.innerText = welcome_textarea.value
}

// Preview Event Listener
welcome_textarea.addEventListener("input",() => {
    preview_content(preview_content_text,welcome_textarea)
})

// Show current welcome text
preview_content(preview_content_text,welcome_textarea)

// Save Welcome Text
welcome_save_btn.addEventListener("click", (e) => {
    e.preventDefault()

    const form = new FormData()
    form.append("csrf_token", csrf_token.value)
    form.append("welcome_text", welcome_textarea.value)

    const xhr = new XMLHttpRequest()
    xhr.open("POST","/blog/update_welcome_text",true)
    xhr.send(form)

    xhr.onload = () => {
        const data = JSON.parse(xhr.responseText)
        const message = data["message"].toLowerCase()
        const status = data["status"].toLowerCase()

        // Show response
        flash_response(message,status)
    }
})


// About Section Preview
const about_textarea = document.getElementById("about_textarea")
const about_intro = document.querySelector(".about_intro")
const about_save_btn = document.querySelector(".about_save_btn")

// Preview Event Listener
about_textarea.addEventListener("input",() => {
    preview_content(about_intro,about_textarea)
})

// Show current welcome text
preview_content(about_intro,about_textarea)

// Save Welcome Text
about_save_btn.addEventListener("click", (e) => {
    e.preventDefault()

    const form = new FormData()
    form.append("csrf_token", csrf_token.value)
    form.append("about_text", about_textarea.value)

    const xhr = new XMLHttpRequest()
    xhr.open("POST","/blog/update_about_text",true)
    xhr.send(form)

    xhr.onload = () => {
        const data = JSON.parse(xhr.responseText)
        const message = data["message"].toLowerCase()
        const status = data["status"].toLowerCase()

        // Show response
        flash_response(message,status)
    }
})


// Work Section Preview
const work_textarea = document.getElementById("work_textarea")
const work_intro = document.querySelector(".work_intro")
const work_save_btn = document.querySelector(".work_save_btn")

// Preview Event Listener
work_textarea.addEventListener("input",() => {
    preview_content(work_intro,work_textarea)
})

// Show current welcome text
preview_content(work_intro,work_textarea)

// Save Welcome Text
work_save_btn.addEventListener("click", (e) => {
    e.preventDefault()

    const form = new FormData()
    form.append("csrf_token", csrf_token.value)
    form.append("work_text", work_textarea.value)

    const xhr = new XMLHttpRequest()
    xhr.open("POST","/blog/update_work_text",true)
    xhr.send(form)

    xhr.onload = () => {
        const data = JSON.parse(xhr.responseText)
        const message = data["message"].toLowerCase()
        const status = data["status"].toLowerCase()

        // Show response
        flash_response(message,status)
    }
})


// Education Section
const clear_form_btn = document.getElementById("clear_btn")
const name_fied = document.getElementById("Name")
const location_field = document.getElementById("Location")
const start_date_field = document.getElementById("Start_Date")
const End_date_field = document.getElementById("End_Date")
const Qualification = document.getElementById("Qualification")
const Save_btn = document.querySelector(".education_btn")
const Edit_btn = document.querySelector(".edit_btn")

// Clear Fields Data
function clear_form_fields(){
    name_fied.value = ""
    location_field.value = ""
    start_date_field.selectedIndex = 0;
    End_date_field.selectedIndex = 0;
    Qualification.value = ""

    Save_btn.classList.remove("remove_display")
    Edit_btn.classList.add("remove_display")
}

// Display Education Items
function display_education_items(item_list){
    const education_items = document.querySelector(".education_items")
    education_items.innerHTML = ""

    for(item of item_list){
        // Create Elements
        const education_item = document.createElement("div")
    
        const education_year = document.createElement("div")
        const year_paragraph = document.createElement("p")
    
        const education_instituition = document.createElement("div")
        const instituition_paragraph = document.createElement("p")
        const instituition_location = document.createElement("small")
    
        const award = document.createElement("div")
        
        // Create Qualifiation Element
        award.innerText = item["Qualification"]
        award.classList.add("education_award_name")

        // Create Instituition Element
        instituition_location.innerText = item["Location"]
        instituition_location.classList.add("education_location")
        instituition_paragraph.innerText = item["Instituition"]
        education_instituition.appendChild(instituition_paragraph)
        education_instituition.appendChild(instituition_location)
        education_instituition.classList.add("education_instituition")

        // Create Attendance Year Element
        year_paragraph.innerText = `${item["start_year"]} - ${item["end_year"]}`
        education_year.appendChild(year_paragraph)
        education_year.classList.add("education_year")

        // Create education element
        education_item.appendChild(education_year)
        education_item.appendChild(education_instituition)
        education_item.appendChild(award)

        education_items.appendChild(education_item)
    }
}

// Fetch Education Data
function fetch_education_records(){
    const new_promise = new Promise((resolve,reject) => {

        const xhr = new XMLHttpRequest()
        xhr.open("GET", "/blog/fetch_education_records", true)
        xhr.send()
        xhr.onload = () => {
            if (200 <= xhr.status && xhr.status < 300) {
                const data = JSON.parse(xhr.responseText)
                resolve(data)
            }
            else {
                reject("Unable to fetch saved records","failed")
            }
        }
    })
    .then((data) => {
        const status = data["status"].toLowerCase()

        // Show response
        if (status != "success"){
            const message = data["message"].toLowerCase()
            flash_response(message,status)
            return
        }

        // Clear Records List
        const edu_records = document.querySelector(".records_list")
        edu_records.innerHTML = ""

        // Create Elements
        const trash_element = document.createElement("div")
        const edit_element = document.createElement("div")

        trash_element.classList.add("trash_icon")
        trash_element.innerText = 'DELETE'

        edit_element.classList.add("edit_icon")
        edit_element.innerText = 'EDIT'

        // Display In Page
        for(const qualification of data["message"]["dict"]){
            const records_element = document.createElement("div")
            const qualification_element = document.createElement("div")

            records_element.classList.add("records")

            qualification_element.classList.add("credential")
            qualification_element.id = qualification["id"]
            qualification_element.innerText = qualification["Qualification"]

            const trash_element_clone = trash_element.cloneNode(true)
            const edit_element_clone = edit_element.cloneNode(true)

            // Add Event Listener to Edit Element
            edit_element_clone.addEventListener("click", () => {
                name_fied.value = qualification["Instituition"]
                location_field.value = qualification["Location"]
                Qualification.value = qualification["Qualification"]
                start_date_field.value = qualification["start_year"]
                End_date_field.value = qualification["end_year"]
            
                Save_btn.classList.add("remove_display")
                Edit_btn.classList.remove("remove_display")
                Edit_btn.id = qualification["id"]
            })

            // Add Event Listener To Trash Element
            trash_element_clone.addEventListener("click", () => {
                new Promise((resolve) => {
                    const record_id = qualification["id"]
                    const xhr = new XMLHttpRequest()
                    const form = new FormData()
    
                    form.append("csrf_token", csrf_token.value)
                    form.append("record_id",record_id)
    
                    xhr.open("POST","/blog/remove_education",true)
                    xhr.send(form)
                    xhr.onload = () => {
                        const data = JSON.parse(xhr.responseText)
                        const message = data["message"].toLowerCase()
                        const status = data["status"].toLowerCase()
                
                        // Show response
                        flash_response(message,status)
                    }
                    resolve()
                })

                .then(() => {
                    // Refresh Eduation Records
                    fetch_education_records()
                })
            })

            records_element.appendChild(qualification_element)
            records_element.appendChild(trash_element_clone)
            records_element.appendChild(edit_element_clone)

            edu_records.appendChild(records_element);
        }

        display_education_items(data["message"]["dict"])
    })
    .catch((message,status) => {
        flash_response(message,status)
    })
}

// Show Education Records
fetch_education_records()

// Clear Education Form Field
clear_form_btn.addEventListener("click", (e) => {
    e.preventDefault()
    clear_form_fields()
})


Save_btn.addEventListener("click", (e) => {
    e.preventDefault()

    new Promise((resolve) => {
        const form = new FormData()
        form.append("csrf_token", csrf_token.value)
        form.append("name", name_fied.value)
        form.append("location", location_field.value)
        form.append("start_date", start_date_field.value)
        form.append("end_date", End_date_field.value)
        form.append("qualification", Qualification.value)
    
        const xhr = new XMLHttpRequest()
        xhr.open("POST","/blog/add_education",true)
        xhr.send(form)
    
        xhr.onload = () => {
            const data = JSON.parse(xhr.responseText)
            const message = data["message"].toLowerCase()
            const status = data["status"].toLowerCase()
    
            // Show response
            flash_response(message,status)
        }
        resolve()
    })
    .then(() => {
        // Clear Form Fields
        clear_form_btn.click()
        
        // Refresh Saved Education data preview
        fetch_education_records()
    })
})

Edit_btn.addEventListener("click",(e) => {
    e.preventDefault()

    new Promise((resolve) => {
        const qualifiation_id = Edit_btn.id
        const form = new FormData()
    
        form.append("csrf_token", csrf_token.value)
        form.append("record_id", qualifiation_id)
        form.append("name", name_fied.value)
        form.append("location", location_field.value)
        form.append("start_date", start_date_field.value)
        form.append("end_date", End_date_field.value)
        form.append("qualification", Qualification.value)
    
        const xhr = new XMLHttpRequest()
        xhr.open("POST","/blog/update_education",true)
        xhr.send(form)
    
        xhr.onload = () => {
            const data = JSON.parse(xhr.responseText)
            const message = data["message"].toLowerCase()
            const status = data["status"].toLowerCase()
    
            // Show response
            flash_response(message,status)
        }
        resolve()
    })
    .then(() => {
        // Clear Form Fields
        clear_form_btn.click()

        // Refresh Saved Education data preview
        fetch_education_records()
    })
})


// Refresh Available companies
function refresh_available_companies(){
    const available_companies = document.querySelector(".available_companies")
    available_companies.innerHTML = ""
    let color_types = ["blue","green","red"]

    const xhr = new XMLHttpRequest()
    xhr.open("GET","/blog/fetch_companies",true)
    xhr.send()
    xhr.onload = () =>{
        console.log(xhr.responseText)
        const data = JSON.parse(xhr.responseText)
    
        for (const company of data["message"]["dict"]){
            const a = document.createElement("a")
            const div = document.createElement("div")
            const random_color = color_types[Math.floor(Math.random() * color_types.length)];
    
            div.classList.add("company",`${random_color}`)
            div.innerText = company["company_name"]
    
            a.appendChild(div)
            a.setAttribute("href",`${company["company_url"]}`)
    
            available_companies.appendChild(a)
        }
    }
}
refresh_available_companies()

// Add Company Section
const company_name = document.getElementById("company_name")
const company_url = document.getElementById("company_url")
const add_company_btn = document.getElementById("add_company_btn")
add_company_btn.addEventListener("click", (e) => {
    e.preventDefault()

    new Promise((resolve) => {
        const form = new FormData
        form.append("csrf_token", csrf_token.value)
        form.append("company_name", company_name.value)
        form.append("company_url", company_url.value)

        const xhr = new XMLHttpRequest()
        xhr.open("POST","/blog/add_company",true)
        xhr.send(form)

        xhr.onload = () => {
            const data = JSON.parse(xhr.responseText)
            const message = data["message"].toLowerCase()
            const status = data["status"].toLowerCase()
    
            // Show response
            flash_response(message,status)
        }
        resolve()
    })
    .then(() => {
        refresh_available_companies()
    })
})

